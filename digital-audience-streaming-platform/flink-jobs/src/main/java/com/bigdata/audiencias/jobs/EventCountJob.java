package com.bigdata.audiencias.jobs;

import com.bigdata.audiencias.model.Event;
import com.bigdata.audiencias.model.EventDeserializer;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.connector.jdbc.JdbcConnectionOptions;
import org.apache.flink.connector.jdbc.JdbcExecutionOptions;
import org.apache.flink.connector.jdbc.core.datastream.sink.JdbcSink;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.connector.kafka.source.reader.deserializer.KafkaRecordDeserializationSchema;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;

import java.sql.Timestamp;
import java.time.Duration;

/**
 * Fase 4 -- Job 1 de 3 ("separados por responsabilidad").
 *
 * Consume user-events y purchase-events, cuenta eventos por tipo en
 * ventanas de 30 segundos (tumbling, tiempo de procesamiento), y escribe
 * el resultado a la tabla eventos_por_tipo en PostgreSQL/TimescaleDB.
 *
 * Envío al cluster real (no "java -jar", ver reference-kafka-flink-validated-stack):
 *   flink run -c com.bigdata.audiencias.jobs.EventCountJob target/flink-jobs-1.0.0.jar
 *
 * El conteo usa un ProcessWindowFunction (en vez de un simple .sum()) porque
 * necesitamos el límite real de cada ventana (context.window().getStart())
 * para poblar window_start con precisión, no solo el conteo agregado.
 */
public class EventCountJob {

    public static void main(String[] args) throws Exception {
        String bootstrapServers = getArg(args, "--bootstrap-servers",
                "10.30.1.11:9092,10.30.1.12:9092,10.30.1.13:9092");
        String jdbcUrl = getArg(args, "--jdbc-url",
                "jdbc:postgresql://10.30.1.30:5432/audiencias");
        String jdbcUser = getArg(args, "--jdbc-user", "flink");
        String jdbcPassword = getArg(args, "--jdbc-password", "AudienciasLab2026!");

        KafkaSource<Event> source = KafkaSource.<Event>builder()
                .setBootstrapServers(bootstrapServers)
                .setTopics("user-events", "purchase-events")
                .setGroupId("event-count-job")
                .setStartingOffsets(OffsetsInitializer.latest())
                .setDeserializer(KafkaRecordDeserializationSchema.valueOnly(new EventDeserializer()))
                .build();

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        DataStream<Event> events = env.fromSource(
                source, WatermarkStrategy.noWatermarks(), "kafka-user-purchase-events");

        // Conteo por tipo de evento, ventana tumbling de 30s (tiempo de procesamiento).
        // Tuple3: (inicio real de la ventana en epoch millis, tipo de evento, conteo)
        DataStream<Tuple3<Long, String, Long>> counts = events
                .map((MapFunction<Event, Tuple2<String, Long>>) ev -> Tuple2.of(ev.event, 1L))
                .returns(Types.TUPLE(Types.STRING, Types.LONG))
                .keyBy(t -> t.f0)
                .window(TumblingProcessingTimeWindows.of(Duration.ofSeconds(30)))
                .process(new CountEventsWindowFunction())
                .returns(Types.TUPLE(Types.LONG, Types.STRING, Types.LONG));

        JdbcSink<Tuple3<Long, String, Long>> postgresSink = JdbcSink.<Tuple3<Long, String, Long>>builder()
                .withQueryStatement(
                        "INSERT INTO eventos_por_tipo (window_start, event_type, event_count) VALUES (?, ?, ?)",
                        (statement, count) -> {
                            statement.setTimestamp(1, new Timestamp(count.f0));
                            statement.setString(2, count.f1);
                            statement.setLong(3, count.f2);
                        })
                .withExecutionOptions(JdbcExecutionOptions.builder()
                        .withBatchSize(50)
                        .withBatchIntervalMs(2000)
                        .withMaxRetries(3)
                        .build())
                .buildAtLeastOnce(new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
                        .withUrl(jdbcUrl)
                        .withDriverName("org.postgresql.Driver")
                        .withUsername(jdbcUser)
                        .withPassword(jdbcPassword)
                        .build());

        counts.sinkTo(postgresSink);

        env.execute("EventCountJob -- conteo de eventos por tipo");
    }

    private static String getArg(String[] args, String name, String defaultValue) {
        for (int i = 0; i < args.length - 1; i++) {
            if (args[i].equals(name)) {
                return args[i + 1];
            }
        }
        return defaultValue;
    }

    /**
     * Cuenta los elementos de cada ventana y emite (inicio real de la
     * ventana, tipo de evento, conteo). A diferencia de .sum(1), este
     * enfoque sí tiene acceso a los metadatos de la ventana vía
     * context.window().getStart().
     */
    private static class CountEventsWindowFunction
            extends ProcessWindowFunction<Tuple2<String, Long>, Tuple3<Long, String, Long>, String, TimeWindow> {

        @Override
        public void process(
                String eventType,
                Context context,
                Iterable<Tuple2<String, Long>> elements,
                Collector<Tuple3<Long, String, Long>> out) {
            long count = 0L;
            for (Tuple2<String, Long> ignored : elements) {
                count++;
            }
            out.collect(Tuple3.of(context.window().getStart(), eventType, count));
        }
    }
}
