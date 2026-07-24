package pe.edu.unsa.bigdata.lab07;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

/**
 * Laboratorio 07: FLINK (Big Data, 1705157).
 *
 * Consume eventos desde el topic "ecommerce-events" de Kafka (el mismo
 * productor/topic usados en el laboratorio de Kafka) y aplica, en orden,
 * las 5 actividades de la guía:
 *
 *   2.1 Consumir desde Kafka y mostrar continuamente los eventos.
 *   2.2 Filtrar eventos de compra (PURCHASE, ADD_CART).
 *   2.3 Transformar: agregar hora, día, mes y fin de semana.
 *   2.4 Conteo de eventos por tipo (ventanas de 30s).
 *   2.5 Agrupamiento por producto: actividad por producto (ventanas de 30s).
 *
 * Se ejecuta en modo local (sin clúster de Flink separado): al llamar
 * getExecutionEnvironment() sin apuntar a un cluster remoto, Flink arranca
 * un MiniCluster embebido en este mismo proceso.
 *
 * Uso:
 *   java -jar flink-lab07-ecommerce.jar \
 *       --bootstrap-server 10.20.1.11:9092,10.20.1.12:9092,10.20.1.13:9092 \
 *       --topic ecommerce-events \
 *       --group-id flink-lab07
 */
public class EcommerceEventJob {

    public static void main(String[] args) throws Exception {
        Map<String, String> params = parseArgs(args);
        String bootstrapServers = params.getOrDefault("bootstrap-server", "10.20.1.11:9092,10.20.1.12:9092,10.20.1.13:9092");
        String topic = params.getOrDefault("topic", "ecommerce-events");
        String groupId = params.getOrDefault("group-id", "flink-lab07");

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        // Paralelismo explícito para el MiniCluster local (no requiere
        // varios TaskManagers/EC2, corre como varios hilos en esta máquina).
        env.setParallelism(2);

        KafkaSource<String> source = KafkaSource.<String>builder()
                .setBootstrapServers(bootstrapServers)
                .setTopics(topic)
                .setGroupId(groupId)
                .setStartingOffsets(OffsetsInitializer.latest())
                .setValueOnlyDeserializer(new SimpleStringSchema())
                .build();

        DataStream<String> rawStream = env.fromSource(
                source, WatermarkStrategy.noWatermarks(), "kafka-source-ecommerce-events");

        // ---------------------------------------------------------------
        // 2.1 Preparar Flink para consumir eventos desde Kafka.
        // ---------------------------------------------------------------
        DataStream<EcommerceEvent> events = rawStream.map(new JsonToEventMapper());

        events.map(e -> "[2.1 RECIBIDO] " + e.event + " | " + e.product + " | " + e.user)
                .print();

        // ---------------------------------------------------------------
        // 2.3 Transformación de datos (se aplica sobre todos los eventos,
        // antes de filtrar, para que también quede disponible para el
        // conteo y el agrupamiento de las secciones 2.4 y 2.5).
        // ---------------------------------------------------------------
        DataStream<EcommerceEvent> enriched = events.map(new EnrichWithDateFieldsMapper());

        enriched.map(e -> "[2.3 TRANSFORMADO] " + e.toString())
                .print();

        // ---------------------------------------------------------------
        // 2.2 Filtrar eventos de compra (purchase, add_cart).
        // ---------------------------------------------------------------
        DataStream<EcommerceEvent> purchaseEvents = enriched.filter(
                e -> "PURCHASE".equals(e.event) || "ADD_CART".equals(e.event));

        purchaseEvents.map(e -> "[2.2 FILTRADO] " + e.event + " | " + e.product + " | " + e.user)
                .print();

        // ---------------------------------------------------------------
        // 2.4 Conteo de eventos: número de búsquedas, compras, productos
        // vistos y agregados al carrito, en ventanas de 30 segundos.
        // ---------------------------------------------------------------
        enriched
                .map(e -> Tuple2.of(e.event, 1L))
                .returns(Types.TUPLE(Types.STRING, Types.LONG))
                .keyBy(t -> t.f0)
                .window(TumblingProcessingTimeWindows.of(Duration.ofSeconds(30)))
                .sum(1)
                .map(t -> "[2.4 CONTEO 30s] " + t.f0 + " = " + t.f1)
                .print();

        // ---------------------------------------------------------------
        // 2.5 Agrupamiento por producto: actividad total por producto,
        // en ventanas de 30 segundos.
        // ---------------------------------------------------------------
        enriched
                .map(e -> Tuple2.of(e.product, 1L))
                .returns(Types.TUPLE(Types.STRING, Types.LONG))
                .keyBy(t -> t.f0)
                .window(TumblingProcessingTimeWindows.of(Duration.ofSeconds(30)))
                .sum(1)
                .map(t -> "[2.5 PRODUCTO 30s] " + t.f0 + " = " + t.f1 + " interacciones")
                .print();

        env.execute("Laboratorio 07 - Flink + Kafka (ecommerce-events)");
    }

    /**
     * Parseo simple de argumentos tipo "--clave valor" a un mapa.
     *
     * Se implementa a mano porque ParameterTool (org.apache.flink.api.java.utils)
     * pertenecía al módulo flink-java, ligado a la antigua DataSet API que
     * Flink 2.0 eliminó por completo.
     */
    private static Map<String, String> parseArgs(String[] args) {
        Map<String, String> result = new HashMap<>();
        for (int i = 0; i < args.length - 1; i++) {
            if (args[i].startsWith("--")) {
                result.put(args[i].substring(2), args[i + 1]);
            }
        }
        return result;
    }
}
