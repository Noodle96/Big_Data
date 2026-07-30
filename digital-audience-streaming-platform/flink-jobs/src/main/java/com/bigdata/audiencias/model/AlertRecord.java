package com.bigdata.audiencias.model;

import java.io.Serializable;

/**
 * Alerta genérica -- unifica las dos fuentes de alertas del diseño original
 * (anomalía de ventana: ADD_CART sin PURCHASE, y transición de audiencia a
 * un estado de riesgo/interés), ambas terminan en la misma tabla `alertas`.
 */
public class AlertRecord implements Serializable {

    private static final long serialVersionUID = 1L;

    public String tipo;
    public String mensaje;
    public String userId;

    public AlertRecord() {
    }

    public AlertRecord(String tipo, String mensaje, String userId) {
        this.tipo = tipo;
        this.mensaje = mensaje;
        this.userId = userId;
    }
}
