package pe.edu.unsa.bigdata.lab07;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.api.common.functions.MapFunction;

/**
 * Paso 2.1: parsea cada línea JSON recibida de Kafka a un EcommerceEvent.
 *
 * ObjectMapper de Jackson es serializable, así que puede vivir como campo
 * de esta función sin necesidad de inicializarlo en un open() (RichFunction).
 */
public class JsonToEventMapper implements MapFunction<String, EcommerceEvent> {

    private final ObjectMapper mapper = new ObjectMapper();

    @Override
    public EcommerceEvent map(String json) throws Exception {
        return mapper.readValue(json, EcommerceEvent.class);
    }
}
