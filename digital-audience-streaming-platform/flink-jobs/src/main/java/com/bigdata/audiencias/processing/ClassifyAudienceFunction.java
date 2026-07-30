package com.bigdata.audiencias.processing;

import com.bigdata.audiencias.model.AlertRecord;
import com.bigdata.audiencias.model.AudienceRecord;
import com.bigdata.audiencias.model.Event;
import org.apache.flink.api.common.functions.OpenContext;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;

import java.util.HashMap;
import java.util.Map;

/**
 * Adaptado de jobsCompa/ (pe.unsa.processing.ClassifyAudienceFunction) --
 * misma lógica de clasificación (estado acumulado por usuario vía
 * ValueState), pero en vez de serializar a JSON y mandar a un tópico Kafka,
 * emite un AudienceRecord tipado (para el sink JDBC a la tabla `audiencias`)
 * y un AlertRecord por el side output (para la tabla `alertas`).
 */
public class ClassifyAudienceFunction extends KeyedProcessFunction<String, Event, AudienceRecord> {

    private final OutputTag<AlertRecord> alertTag;
    private transient ValueState<Map<String, Long>> countsState;
    private transient ValueState<String> lastAudienceState;

    public ClassifyAudienceFunction(OutputTag<AlertRecord> alertTag) {
        this.alertTag = alertTag;
    }

    @Override
    public void open(OpenContext openContext) {
        countsState = getRuntimeContext().getState(
                new ValueStateDescriptor<>("counts", Types.MAP(Types.STRING, Types.LONG)));
        lastAudienceState = getRuntimeContext().getState(
                new ValueStateDescriptor<>("lastAudience", Types.STRING));
    }

    @Override
    public void processElement(Event value, Context ctx, Collector<AudienceRecord> out) throws Exception {
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

        out.collect(new AudienceRecord(
                value.getTimestamp(),
                value.getUser_id(),
                value.getAgent_type(),
                audiencia,
                counts.getOrDefault("total", 0L)));

        // Alerta solo cuando el usuario CAMBIA a un estado de riesgo (evita spam)
        String previous = lastAudienceState.value();
        if (!audiencia.equals(previous) &&
                (audiencia.equals("riesgo_abandono") || audiencia.equals("alta_intencion_compra"))) {
            ctx.output(alertTag, new AlertRecord(
                    "audiencia",
                    "Usuario " + value.getUser_id() + " cambio a audiencia: " + audiencia,
                    value.getUser_id()));
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
