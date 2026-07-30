package com.bigdata.audiencias.model;

import java.io.Serializable;

/**
 * Resultado del join vista/compra (ViewPurchaseJoinFunction): un producto
 * visto y comprado por usuarios distintos en la misma ventana. No es uno de
 * los 10 paneles pedidos por el enunciado, se conserva como dato extra del
 * diseño original de jobsCompa/.
 */
public class RelatedProductRecord implements Serializable {

    private static final long serialVersionUID = 1L;

    public String product;
    public String viewedBy;
    public String purchasedBy;

    public RelatedProductRecord() {
    }

    public RelatedProductRecord(String product, String viewedBy, String purchasedBy) {
        this.product = product;
        this.viewedBy = viewedBy;
        this.purchasedBy = purchasedBy;
    }
}
