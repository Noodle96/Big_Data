package pe.unsa.model;

import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;

public class WindowSummary implements Serializable {

    private long windowStart;
    private long windowEnd;
    private long totalEvents;
    private Map<String, Long> eventCounts = new HashMap<>();
    private long distinctUsers;
    private Map<String, Long> purchasesByCity = new HashMap<>();
    private Map<String, Long> viewsByProduct = new HashMap<>();
    private Map<String, Long> purchasesByProduct = new HashMap<>();
    private Map<String, Long> addCartByProduct = new HashMap<>();

    public WindowSummary() {}

    public long getWindowStart() { return windowStart; }
    public void setWindowStart(long v) { this.windowStart = v; }

    public long getWindowEnd() { return windowEnd; }
    public void setWindowEnd(long v) { this.windowEnd = v; }

    public long getTotalEvents() { return totalEvents; }
    public void setTotalEvents(long v) { this.totalEvents = v; }

    public Map<String, Long> getEventCounts() { return eventCounts; }
    public void setEventCounts(Map<String, Long> v) { this.eventCounts = v; }

    public long getDistinctUsers() { return distinctUsers; }
    public void setDistinctUsers(long v) { this.distinctUsers = v; }

    public Map<String, Long> getPurchasesByCity() { return purchasesByCity; }
    public void setPurchasesByCity(Map<String, Long> v) { this.purchasesByCity = v; }

    public Map<String, Long> getViewsByProduct() { return viewsByProduct; }
    public void setViewsByProduct(Map<String, Long> v) { this.viewsByProduct = v; }

    public Map<String, Long> getPurchasesByProduct() { return purchasesByProduct; }
    public void setPurchasesByProduct(Map<String, Long> v) { this.purchasesByProduct = v; }

    public Map<String, Long> getAddCartByProduct() { return addCartByProduct; }
    public void setAddCartByProduct(Map<String, Long> v) { this.addCartByProduct = v; }
}