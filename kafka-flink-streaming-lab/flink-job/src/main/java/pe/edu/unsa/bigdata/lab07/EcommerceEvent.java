package pe.edu.unsa.bigdata.lab07;

import java.io.Serializable;

/**
 * Representa un evento de e-commerce consumido desde Kafka, con el esquema
 * de las especificaciones del laboratorio:
 * {user, event, product, category, city, price, timestamp}
 *
 * Los últimos 4 campos (hora, dia, mes, finDeSemana) no vienen en el JSON
 * original: se calculan en el paso 2.3 (Transformación de datos).
 *
 * Debe ser un POJO válido para Flink: constructor público sin argumentos
 * y campos públicos (o getters/setters), para que el serializador de Flink
 * lo reconozca como POJO en vez de caer a serialización genérica (Kryo).
 */
public class EcommerceEvent implements Serializable {

    public String user;
    public String event;
    public String product;
    public String category;
    public String city;
    public double price;
    public String timestamp;

    // Atributos derivados, agregados en la transformación (2.3).
    public Integer hora;
    public Integer dia;
    public Integer mes;
    public Boolean finDeSemana;

    public EcommerceEvent() {
        // Constructor vacío requerido por Flink para reconocer esta clase
        // como POJO.
    }

    @Override
    public String toString() {
        return "user=" + user
                + " event=" + event
                + " product=" + product
                + " category=" + category
                + " city=" + city
                + " price=" + price
                + " timestamp=" + timestamp
                + " hora=" + hora
                + " dia=" + dia
                + " mes=" + mes
                + " finDeSemana=" + finDeSemana;
    }
}
