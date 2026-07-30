package com.bigdata.audiencias.processing;

import com.bigdata.audiencias.model.Event;
import com.bigdata.audiencias.model.RelatedProductRecord;
import org.apache.flink.api.common.functions.JoinFunction;

/**
 * Adaptado de jobsCompa/ (pe.unsa.processing.ViewPurchaseJoinFunction) --
 * misma lógica de join, pero emite un RelatedProductRecord tipado en vez de
 * un JSON String, para el sink JDBC a la tabla `productos_relacionados`.
 */
public class ViewPurchaseJoinFunction implements JoinFunction<Event, Event, RelatedProductRecord> {

    @Override
    public RelatedProductRecord join(Event viewed, Event purchased) {
        return new RelatedProductRecord(viewed.getProduct(), viewed.getUser_id(), purchased.getUser_id());
    }
}
