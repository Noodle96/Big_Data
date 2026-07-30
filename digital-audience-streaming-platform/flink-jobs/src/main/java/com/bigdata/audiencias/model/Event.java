package com.bigdata.audiencias.model;

import java.io.Serializable;

/**
 * Evento JSON tal como lo publica agentes-simulador (ver
 * agentes-simulador/src/schema.py::Event -- mismos campos, mismos nombres).
 *
 * POJO simple con campos públicos: es lo que Flink necesita para
 * reconocerlo como tipo POJO (constructor vacío + campos/getters públicos),
 * y Jackson lo deserializa directo desde el JSON sin configuración extra.
 */
public class Event implements Serializable {

    private static final long serialVersionUID = 1L;

    public String timestamp;
    public String user_id;
    public String event;
    public String product;
    public String category;
    public String city;
    public int price;
    public String agent_type;
    public String source;

    /** Constructor vacío requerido por Flink (POJO) y Jackson. */
    public Event() {
    }

    @Override
    public String toString() {
        return "Event{" +
                "timestamp='" + timestamp + '\'' +
                ", user_id='" + user_id + '\'' +
                ", event='" + event + '\'' +
                ", product='" + product + '\'' +
                ", category='" + category + '\'' +
                ", city='" + city + '\'' +
                ", price=" + price +
                ", agent_type='" + agent_type + '\'' +
                ", source='" + source + '\'' +
                '}';
    }
}
