package pe.unsa;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;

import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.util.OutputTag;

import pe.unsa.model.Event;
import pe.unsa.model.WindowSummary;
import pe.unsa.processing.ClassifyAudienceFunction;
import pe.unsa.processing.ViewPurchaseJoinFunction;
import pe.unsa.processing.WindowSummaryFunction;
import pe.unsa.serialization.EventDeserializer;

import java.util.HashMap;
import java.util.Map;

public class Main {

    private static final String BOOTSTRAP_SERVERS =
            "172.31.19.149:9092,172.31.30.49:9092,172.31.22.115:9092";
    private static final String SOURCE_TOPIC = "eventos";
    private static final String GROUP_ID = "flink-audiencias-group";
    private static final Time WINDOW_SIZE = Time.seconds(10);
    private static final ObjectMapper MAPPER = new ObjectMapper();

    public static void main(String[] args) throws Exception {

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(3);

        KafkaSource<Event> source = KafkaSource.<Event>builder()
                .setBootstrapServers(BOOTSTRAP_SERVERS)
                .setTopics(SOURCE_TOPIC)
                .setGroupId(GROUP_ID)
                .setStartingOffsets(OffsetsInitializer.latest())
                .setValueOnlyDeserializer(new EventDeserializer())
                .build();

        DataStream<Event> raw = env.fromSource(
                source, WatermarkStrategy.noWatermarks(), "kafka-eventos");

        // ---------- LIMPIEZA / VALIDACION ----------
        DataStream<Event> events = raw.filter(e ->
                e != null &&
                e.getUser_id() != null && !e.getUser_id().isEmpty() &&
                e.getEvent() != null && !e.getEvent().isEmpty() &&
                e.getPrice() >= 0
        ).name("validacion-eventos");

        // ---------- VENTANAS + AGREGACIONES -> todo va a "metrics" ----------
        DataStream<WindowSummary> summaries = events
                .windowAll(TumblingProcessingTimeWindows.of(WINDOW_SIZE))
                .process(new WindowSummaryFunction())
                .name("agregaciones-ventana");

        DataStream<String> metricsJson = summaries.map(s -> {
            long views = s.getEventCounts().getOrDefault("VIEW_PRODUCT", 0L);
            long purchases = s.getEventCounts().getOrDefault("PURCHASE", 0L);
            double conversion = views == 0 ? 0.0 : (purchases / (double) views);
            double eventosPorSegundo = s.getTotalEvents() / (double) (WINDOW_SIZE.toMilliseconds() / 1000);

            Map<String, Object> out = new HashMap<>();
            out.put("tipo", "resumen_ventana");
            out.put("windowStart", s.getWindowStart());
            out.put("windowEnd", s.getWindowEnd());
            out.put("eventos_por_segundo", eventosPorSegundo);
            out.put("eventos_por_tipo", s.getEventCounts());
            out.put("usuarios_activos", s.getDistinctUsers());
            out.put("productos_vistos", s.getViewsByProduct());
            out.put("productos_comprados", s.getPurchasesByProduct());
            out.put("compras_por_region", s.getPurchasesByCity());
            out.put("conversion", conversion);
            return MAPPER.writeValueAsString(out);
        }).name("map-metrics-json");

        metricsJson.sinkTo(makeSink("metrics")).name("sink-metrics");

        // Alerta simple sobre agregados: muchos ADD_CART sin PURCHASE en la ventana
        DataStream<String> alertasVentana = summaries.map(s -> {
            long addCart = s.getEventCounts().getOrDefault("ADD_CART", 0L);
            long purchase = s.getEventCounts().getOrDefault("PURCHASE", 0L);
            if (addCart >= 5 && purchase == 0) {
                Map<String, Object> out = new HashMap<>();
                out.put("tipo", "anomalia_ventana");
                out.put("mensaje", "Muchos ADD_CART (" + addCart + ") sin ninguna compra en la ventana");
                out.put("windowEnd", s.getWindowEnd());
                return MAPPER.writeValueAsString(out);
            }
            return null;
        }).filter(v -> v != null).name("alertas-ventana");

        alertasVentana.sinkTo(makeSink("alertas")).name("sink-alertas-ventana");

        // ---------- AUDIENCIAS POR USUARIO (con side output de alertas) ----------
        OutputTag<String> alertTag = new OutputTag<String>("alertas-audiencia"){};

        SingleOutputStreamOperator<String> audienceStream = events
                .keyBy(Event::getUser_id)
                .process(new ClassifyAudienceFunction(alertTag))
                .name("clasificacion-audiencias");

        audienceStream.sinkTo(makeSink("audiencias")).name("sink-audiencias");
        audienceStream.getSideOutput(alertTag)
                .sinkTo(makeSink("alertas")).name("sink-alertas-audiencia");

        // ---------- JOIN: productos vistos y comprados en la misma ventana -> "metrics" ----------
        DataStream<Event> viewed = events.filter(e -> "VIEW_PRODUCT".equals(e.getEvent()));
        DataStream<Event> purchased = events.filter(e -> "PURCHASE".equals(e.getEvent()));

        viewed.join(purchased)
                .where(Event::getProduct)
                .equalTo(Event::getProduct)
                .window(TumblingProcessingTimeWindows.of(WINDOW_SIZE))
                .apply(new ViewPurchaseJoinFunction())
                .sinkTo(makeSink("metrics"))
                .name("sink-join-vista-compra");


        env.execute("flink-audiencias-digitales");
    }

    private static KafkaSink<String> makeSink(String topic) {
        return KafkaSink.<String>builder()
                .setBootstrapServers(BOOTSTRAP_SERVERS)
                .setRecordSerializer(
                        KafkaRecordSerializationSchema.builder()
                                .setTopic(topic)
                                .setValueSerializationSchema(new SimpleStringSchema())
                                .build())
                .build();
    }
}