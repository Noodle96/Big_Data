package pe.unsa.processing;

import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;
import com.fasterxml.jackson.databind.ObjectMapper;
import pe.unsa.model.Event;

import java.util.HashMap;
import java.util.Map;

public class ClassifyAudienceFunction extends KeyedProcessFunction<String, Event, String> {

    private final OutputTag<String> alertTag;
    private transient ValueState<Map<String, Long>> countsState;
    private transient ValueState<String> lastAudienceState;
    private transient ObjectMapper mapper;

    public ClassifyAudienceFunction(OutputTag<String> alertTag) {
        this.alertTag = alertTag;
    }

    @Override
    public void open(Configuration parameters) {
        countsState = getRuntimeContext().getState(
                new ValueStateDescriptor<>("counts", Types.MAP(Types.STRING, Types.LONG)));
        lastAudienceState = getRuntimeContext().getState(
                new ValueStateDescriptor<>("lastAudience", Types.STRING));
        mapper = new ObjectMapper();
    }

    @Override
    public void processElement(Event value, Context ctx, Collector<String> out) throws Exception {
        Map<String, Long> counts = countsState.value();
        if (counts == null) {
            counts = new HashMap<>();
            counts.put("SEARCH", 0L);
            counts.put("VIEW_PRODUCT", 0L);
            counts.put("ADD_CART", 0L);
            counts.put("PURCHASE", 0L);
            counts.put("total", 0L);
        }
        counts.merge(value.getEvent(), 1L, Long::sum);
        counts.merge("total", 1L, Long::sum);
        countsState.update(counts);

        String audiencia = classify(counts);

        Map<String, Object> payload = new HashMap<>();
        payload.put("user_id", value.getUser_id());
        payload.put("agent_type", value.getAgent_type());
        payload.put("audiencia", audiencia);
        payload.put("counts", counts);
        payload.put("timestamp", value.getTimestamp());
        out.collect(mapper.writeValueAsString(payload));

        // Alerta solo cuando el usuario CAMBIA a un estado de riesgo (evita spam)
        String previous = lastAudienceState.value();
        if (!audiencia.equals(previous) &&
                (audiencia.equals("riesgo_abandono") || audiencia.equals("alta_intencion_compra"))) {
            Map<String, Object> alert = new HashMap<>();
            alert.put("tipo", "audiencia");
            alert.put("user_id", value.getUser_id());
            alert.put("mensaje", "Usuario " + value.getUser_id() + " cambio a audiencia: " + audiencia);
            alert.put("timestamp", value.getTimestamp());
            ctx.output(alertTag, mapper.writeValueAsString(alert));
        }
        lastAudienceState.update(audiencia);
    }

    private static String classify(Map<String, Long> c) {
        long purchase = c.getOrDefault("PURCHASE", 0L);
        long addCart = c.getOrDefault("ADD_CART", 0L);
        long view = c.getOrDefault("VIEW_PRODUCT", 0L);
        long total = c.getOrDefault("total", 0L);

        if (purchase >= 3) return "cliente_frecuente";
        if (addCart >= 3 && purchase == 0) return "riesgo_abandono";
        if (view >= 5 && purchase == 0 && addCart > 0) return "alta_intencion_compra";
        if (view >= 5 && purchase == 0) return "explorador";
        if (purchase >= 1 && total < 5) return "premium_potencial";
        return "usuario_general";
    }
}