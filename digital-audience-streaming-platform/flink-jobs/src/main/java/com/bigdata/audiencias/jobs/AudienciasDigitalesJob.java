package com.bigdata.audiencias.jobs;

import com.bigdata.audiencias.model.AlertRecord;
import com.bigdata.audiencias.model.AudienceRecord;
import com.bigdata.audiencias.model.Event;
import com.bigdata.audiencias.model.EventDeserializer;
import com.bigdata.audiencias.model.RelatedProductRecord;
import com.bigdata.audiencias.model.WindowSummary;
import com.bigdata.audiencias.processing.ClassifyAudienceFunction;
import com.bigdata.audiencias.processing.ViewPurchaseJoinFunction;
import com.bigdata.audiencias.processing.WindowSummaryFunction;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.connector.jdbc.JdbcConnectionOptions;
import org.apache.flink.connector.jdbc.JdbcExecutionOptions;
import org.apache.flink.connector.jdbc.core.datastream.sink.JdbcSink;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.connector.kafka.source.reader.deserializer.KafkaRecordDeserializationSchema;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.util.OutputTag;

import java.io.Serializable;
import java.sql.Timestamp;
import java.time.Duration;
import java.util.Map;

/**
 * Fase 4 -- job único de Flink para audiencias digitales, adaptado del
 * diseño original del compañero de equipo (ver jobsCompa/, antes de que se
 * eliminara la carpeta). Misma lógica de procesamiento; el único cambio real
 * es el destino de los datos: el original mandaba todo a 3 tópicos Kafka
 * (metrics/alertas/audiencias), acá se cambia por sinks JDBC a Postgres para
 * alimentar el dashboard de Grafana ya construido (Fase 6, ver dashboard/).
 *
 * Ramas del pipeline (todas parten del mismo stream de entrada, 2 tópicos):
 *  1. Agregación por ventana (10s, windowAll) -&gt; resumen_ventana,
 *     eventos_por_tipo, productos_vistos, productos_comprados,
 *     compras_por_region, y alerta de ADD_CART sin PURCHASE.
 *  2. Clasificación de audiencia por usuario (keyBy + estado acumulado)
 *     -&gt; audiencias, con alerta cuando un usuario cambia a un estado de
 *     riesgo/interés.
 *  3. Join vista/compra por ventana -&gt; productos_relacionados (informativo,
 *     no es uno de los 10 paneles pedidos, se conserva del diseño original).
 *
 * Envío al cluster real:
 *   flink run -c com.bigdata.audiencias.jobs.AudienciasDigitalesJob target/flink-jobs-1.0.0.jar
 */
public class AudienciasDigitalesJob {

    private static final Duration WINDOW_SIZE = Duration.ofSeconds(10);

    public static void main(String[] args) throws Exception {
        String bootstrapServers = getArg(args, "--bootstrap-servers",
                "10.30.1.11:9092,10.30.1.12:9092,10.30.1.13:9092");
        String jdbcUrl = getArg(args, "--jdbc-url",
                "jdbc:postgresql://10.30.1.30:5432/audiencias");
        String jdbcUser = getArg(args, "--jdbc-user", "flink");
        String jdbcPassword = getArg(args, "--jdbc-password", "AudienciasLab2026!");

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(3);

        KafkaSource<Event> source = KafkaSource.<Event>builder()
                .setBootstrapServers(bootstrapServers)
                .setTopics("user-events", "purchase-events")
                .setGroupId("flink-audiencias-group")
                .setStartingOffsets(OffsetsInitializer.latest())
                .setDeserializer(KafkaRecordDeserializationSchema.valueOnly(new EventDeserializer()))
                .build();

        DataStream<Event> raw = env.fromSource(source, WatermarkStrategy.noWatermarks(), "kafka-eventos");

        // ---------- LIMPIEZA / VALIDACION ----------
        DataStream<Event> events = raw.filter(e ->
                e != null &&
                e.getUser_id() != null && !e.getUser_id().isEmpty() &&
                e.getEvent() != null && !e.getEvent().isEmpty() &&
                e.getPrice() >= 0
        ).name("validacion-eventos");

        // ---------- VENTANAS + AGREGACIONES ----------
        DataStream<WindowSummary> summaries = events
                .windowAll(TumblingProcessingTimeWindows.of(WINDOW_SIZE))
                .process(new WindowSummaryFunction())
                .name("agregaciones-ventana");

        // resumen_ventana: métricas escalares por ventana (usuarios activos,
        // eventos/segundo, conversión) -- calculadas directo en el statement
        // builder del sink, sin necesidad de un map intermedio.
        summaries.sinkTo(makeResumenVentanaSink(jdbcUrl, jdbcUser, jdbcPassword))
                .name("sink-resumen-ventana");

        // eventos_por_tipo / productos_vistos / productos_comprados /
        // compras_por_region: cada uno sale de "explotar" el mapa
        // correspondiente de WindowSummary en filas (window_start, key, count).
        explodeMap(summaries, WindowSummary::getEventCounts, "explode-eventos-por-tipo")
                .sinkTo(makeTuple3Sink(
                        "INSERT INTO eventos_por_tipo (window_start, event_type, event_count) VALUES (?, ?, ?)",
                        jdbcUrl, jdbcUser, jdbcPassword))
                .name("sink-eventos-por-tipo");

        explodeMap(summaries, WindowSummary::getViewsByProduct, "explode-productos-vistos")
                .sinkTo(makeTuple3Sink(
                        "INSERT INTO productos_vistos (window_start, product, views_count) VALUES (?, ?, ?)",
                        jdbcUrl, jdbcUser, jdbcPassword))
                .name("sink-productos-vistos");

        explodeMap(summaries, WindowSummary::getPurchasesByProduct, "explode-productos-comprados")
                .sinkTo(makeTuple3Sink(
                        "INSERT INTO productos_comprados (window_start, product, purchases_count) VALUES (?, ?, ?)",
                        jdbcUrl, jdbcUser, jdbcPassword))
                .name("sink-productos-comprados");

        explodeMap(summaries, WindowSummary::getPurchasesByCity, "explode-compras-por-region")
                .sinkTo(makeTuple3Sink(
                        "INSERT INTO compras_por_region (window_start, city, purchases_count) VALUES (?, ?, ?)",
                        jdbcUrl, jdbcUser, jdbcPassword))
                .name("sink-compras-por-region");

        // Alerta simple sobre agregados: muchos ADD_CART sin PURCHASE en la ventana
        DataStream<AlertRecord> alertasVentana = summaries.flatMap(
                (WindowSummary s, org.apache.flink.util.Collector<AlertRecord> out) -> {
                    long addCart = s.getEventCounts().getOrDefault("ADD_CART", 0L);
                    long purchase = s.getEventCounts().getOrDefault("PURCHASE", 0L);
                    if (addCart >= 5 && purchase == 0) {
                        out.collect(new AlertRecord(
                                "anomalia_ventana",
                                "Muchos ADD_CART (" + addCart + ") sin ninguna compra en la ventana",
                                null));
                    }
                }).returns(Types.POJO(AlertRecord.class)).name("alertas-ventana");

        // ---------- AUDIENCIAS POR USUARIO (con side output de alertas) ----------
        OutputTag<AlertRecord> alertTag = new OutputTag<AlertRecord>("alertas-audiencia") {};

        SingleOutputStreamOperator<AudienceRecord> audienceStream = events
                .keyBy(Event::getUser_id)
                .process(new ClassifyAudienceFunction(alertTag))
                .name("clasificacion-audiencias");

        audienceStream.sinkTo(makeAudienceSink(jdbcUrl, jdbcUser, jdbcPassword))
                .name("sink-audiencias");

        DataStream<AlertRecord> alertasAudiencia = audienceStream.getSideOutput(alertTag);

        // Ambas fuentes de alertas van a la misma tabla.
        alertasVentana.union(alertasAudiencia)
                .sinkTo(makeAlertSink(jdbcUrl, jdbcUser, jdbcPassword))
                .name("sink-alertas");

        // ---------- JOIN: productos vistos y comprados en la misma ventana ----------
        DataStream<Event> viewed = events.filter(e -> "VIEW_PRODUCT".equals(e.getEvent()));
        DataStream<Event> purchased = events.filter(e -> "PURCHASE".equals(e.getEvent()));

        viewed.join(purchased)
                .where(Event::getProduct)
                .equalTo(Event::getProduct)
                .window(TumblingProcessingTimeWindows.of(WINDOW_SIZE))
                .apply(new ViewPurchaseJoinFunction())
                .sinkTo(makeRelatedSink(jdbcUrl, jdbcUser, jdbcPassword))
                .name("sink-productos-relacionados");

        env.execute("flink-audiencias-digitales");
    }

    /** Convierte un WindowSummary en filas (window_start, clave, conteo) a partir de uno de sus mapas. */
    private static DataStream<Tuple3<Long, String, Long>> explodeMap(
            DataStream<WindowSummary> summaries, MapExtractor extractor, String name) {
        return summaries.flatMap((WindowSummary s, org.apache.flink.util.Collector<Tuple3<Long, String, Long>> out) -> {
            for (Map.Entry<String, Long> e : extractor.extract(s).entrySet()) {
                out.collect(Tuple3.of(s.getWindowStart(), e.getKey(), e.getValue()));
            }
        }).returns(Types.TUPLE(Types.LONG, Types.STRING, Types.LONG)).name(name);
    }

    private interface MapExtractor extends Serializable {
        Map<String, Long> extract(WindowSummary s);
    }

    private static JdbcSink<WindowSummary> makeResumenVentanaSink(String jdbcUrl, String jdbcUser, String jdbcPassword) {
        return JdbcSink.<WindowSummary>builder()
                .withQueryStatement(
                        "INSERT INTO resumen_ventana (window_start, window_end, total_events, usuarios_activos, eventos_por_segundo, conversion) VALUES (?, ?, ?, ?, ?, ?)",
                        (statement, s) -> {
                            long views = s.getEventCounts().getOrDefault("VIEW_PRODUCT", 0L);
                            long purchases = s.getEventCounts().getOrDefault("PURCHASE", 0L);
                            double conversion = views == 0 ? 0.0 : (purchases / (double) views);
                            double eventosPorSegundo = s.getTotalEvents() / (double) WINDOW_SIZE.getSeconds();
                            statement.setTimestamp(1, new Timestamp(s.getWindowStart()));
                            statement.setTimestamp(2, new Timestamp(s.getWindowEnd()));
                            statement.setLong(3, s.getTotalEvents());
                            statement.setLong(4, s.getDistinctUsers());
                            statement.setDouble(5, eventosPorSegundo);
                            statement.setDouble(6, conversion);
                        })
                .withExecutionOptions(defaultExecutionOptions())
                .buildAtLeastOnce(connectionOptions(jdbcUrl, jdbcUser, jdbcPassword));
    }

    private static JdbcSink<Tuple3<Long, String, Long>> makeTuple3Sink(
            String insertSql, String jdbcUrl, String jdbcUser, String jdbcPassword) {
        return JdbcSink.<Tuple3<Long, String, Long>>builder()
                .withQueryStatement(insertSql, (statement, t) -> {
                    statement.setTimestamp(1, new Timestamp(t.f0));
                    statement.setString(2, t.f1);
                    statement.setLong(3, t.f2);
                })
                .withExecutionOptions(defaultExecutionOptions())
                .buildAtLeastOnce(connectionOptions(jdbcUrl, jdbcUser, jdbcPassword));
    }

    private static JdbcSink<AudienceRecord> makeAudienceSink(String jdbcUrl, String jdbcUser, String jdbcPassword) {
        return JdbcSink.<AudienceRecord>builder()
                .withQueryStatement(
                        "INSERT INTO audiencias (event_time, user_id, agent_type, audiencia, total_events) VALUES (?, ?, ?, ?, ?)",
                        (statement, a) -> {
                            // event_time = momento en que Flink proceso el evento (no el
                            // timestamp original del simulador, que llega como String y no
                            // se parsea aqui para evitar depender de su formato exacto).
                            statement.setTimestamp(1, new Timestamp(System.currentTimeMillis()));
                            statement.setString(2, a.userId);
                            statement.setString(3, a.agentType);
                            statement.setString(4, a.audiencia);
                            statement.setLong(5, a.totalEvents);
                        })
                .withExecutionOptions(defaultExecutionOptions())
                .buildAtLeastOnce(connectionOptions(jdbcUrl, jdbcUser, jdbcPassword));
    }

    private static JdbcSink<AlertRecord> makeAlertSink(String jdbcUrl, String jdbcUser, String jdbcPassword) {
        return JdbcSink.<AlertRecord>builder()
                .withQueryStatement(
                        "INSERT INTO alertas (created_at, tipo, mensaje, user_id) VALUES (?, ?, ?, ?)",
                        (statement, a) -> {
                            statement.setTimestamp(1, new Timestamp(System.currentTimeMillis()));
                            statement.setString(2, a.tipo);
                            statement.setString(3, a.mensaje);
                            statement.setString(4, a.userId);
                        })
                .withExecutionOptions(defaultExecutionOptions())
                .buildAtLeastOnce(connectionOptions(jdbcUrl, jdbcUser, jdbcPassword));
    }

    private static JdbcSink<RelatedProductRecord> makeRelatedSink(String jdbcUrl, String jdbcUser, String jdbcPassword) {
        return JdbcSink.<RelatedProductRecord>builder()
                .withQueryStatement(
                        "INSERT INTO productos_relacionados (detected_at, product, viewed_by, purchased_by) VALUES (?, ?, ?, ?)",
                        (statement, r) -> {
                            statement.setTimestamp(1, new Timestamp(System.currentTimeMillis()));
                            statement.setString(2, r.product);
                            statement.setString(3, r.viewedBy);
                            statement.setString(4, r.purchasedBy);
                        })
                .withExecutionOptions(defaultExecutionOptions())
                .buildAtLeastOnce(connectionOptions(jdbcUrl, jdbcUser, jdbcPassword));
    }

    private static JdbcExecutionOptions defaultExecutionOptions() {
        return JdbcExecutionOptions.builder()
                .withBatchSize(50)
                .withBatchIntervalMs(2000)
                .withMaxRetries(3)
                .build();
    }

    private static JdbcConnectionOptions connectionOptions(String jdbcUrl, String jdbcUser, String jdbcPassword) {
        return new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
                .withUrl(jdbcUrl)
                .withDriverName("org.postgresql.Driver")
                .withUsername(jdbcUser)
                .withPassword(jdbcPassword)
                .build();
    }

    private static String getArg(String[] args, String name, String defaultValue) {
        for (int i = 0; i < args.length - 1; i++) {
            if (args[i].equals(name)) {
                return args[i + 1];
            }
        }
        return defaultValue;
    }
}
