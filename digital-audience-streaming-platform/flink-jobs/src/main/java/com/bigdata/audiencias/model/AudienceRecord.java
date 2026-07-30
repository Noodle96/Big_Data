package com.bigdata.audiencias.model;

import java.io.Serializable;

/**
 * Resultado de clasificar un usuario en una audiencia (ClassifyAudienceFunction).
 * En el diseño original de jobsCompa/ esto se serializaba a JSON y se mandaba
 * a un tópico Kafka; aquí queda como POJO tipado para que el sink JDBC pueda
 * enlazar cada campo directo a una columna de la tabla `audiencias`.
 */
public class AudienceRecord implements Serializable {

    private static final long serialVersionUID = 1L;

    public String eventTime;
    public String userId;
    public String agentType;
    public String audiencia;
    public long totalEvents;

    public AudienceRecord() {
    }

    public AudienceRecord(String eventTime, String userId, String agentType, String audiencia, long totalEvents) {
        this.eventTime = eventTime;
        this.userId = userId;
        this.agentType = agentType;
        this.audiencia = audiencia;
        this.totalEvents = totalEvents;
    }
}
