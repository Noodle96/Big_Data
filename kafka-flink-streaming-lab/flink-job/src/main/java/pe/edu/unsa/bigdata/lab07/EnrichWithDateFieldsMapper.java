package pe.edu.unsa.bigdata.lab07;

import org.apache.flink.api.common.functions.MapFunction;

import java.time.DayOfWeek;
import java.time.LocalDateTime;

/**
 * Paso 2.3: Transformación de datos.
 *
 * Agrega a cada evento los atributos derivados pedidos por la guía: Hora,
 * Día, Mes y si el evento ocurrió en Fin de Semana, calculados a partir del
 * campo "timestamp" (formato ISO local, ej: 2026-07-24T21:50:57).
 */
public class EnrichWithDateFieldsMapper implements MapFunction<EcommerceEvent, EcommerceEvent> {

    @Override
    public EcommerceEvent map(EcommerceEvent event) throws Exception {
        LocalDateTime dt = LocalDateTime.parse(event.timestamp);

        event.hora = dt.getHour();
        event.dia = dt.getDayOfMonth();
        event.mes = dt.getMonthValue();
        event.finDeSemana = dt.getDayOfWeek() == DayOfWeek.SATURDAY
                || dt.getDayOfWeek() == DayOfWeek.SUNDAY;

        return event;
    }
}
