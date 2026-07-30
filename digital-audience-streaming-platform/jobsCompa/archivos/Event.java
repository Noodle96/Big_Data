package pe.unsa.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.io.Serializable;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Event implements Serializable {

    private String timestamp;
    private String user_id;
    private String event;
    private String product;
    private String category;
    private String city;
    private double price;
    private String agent_type;
    private String source;

    public Event() {}

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

    public String getUser_id() { return user_id; }
    public void setUser_id(String user_id) { this.user_id = user_id; }

    public String getEvent() { return event; }
    public void setEvent(String event) { this.event = event; }

    public String getProduct() { return product; }
    public void setProduct(String product) { this.product = product; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    public String getAgent_type() { return agent_type; }
    public void setAgent_type(String agent_type) { this.agent_type = agent_type; }

    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }

    @Override
    public String toString() {
        return "Event{" + "timestamp='" + timestamp + '\'' +
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