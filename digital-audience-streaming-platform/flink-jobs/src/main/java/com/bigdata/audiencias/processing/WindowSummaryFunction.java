package com.bigdata.audiencias.processing;

import com.bigdata.audiencias.model.Event;
import com.bigdata.audiencias.model.WindowSummary;
import org.apache.flink.streaming.api.functions.windowing.ProcessAllWindowFunction;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Adaptado de jobsCompa/ (pe.unsa.processing.WindowSummaryFunction), sin
 * cambios de lógica -- solo paquete y referencias a las clases de modelo
 * movidas a com.bigdata.audiencias.model.
 */
public class WindowSummaryFunction extends ProcessAllWindowFunction<Event, WindowSummary, TimeWindow> {

    @Override
    public void process(Context context, Iterable<Event> elements, Collector<WindowSummary> out) {
        WindowSummary summary = new WindowSummary();
        summary.setWindowStart(context.window().getStart());
        summary.setWindowEnd(context.window().getEnd());

        Map<String, Long> eventCounts = new HashMap<>();
        Map<String, Long> purchasesByCity = new HashMap<>();
        Map<String, Long> viewsByProduct = new HashMap<>();
        Map<String, Long> purchasesByProduct = new HashMap<>();
        Map<String, Long> addCartByProduct = new HashMap<>();
        Set<String> users = new HashSet<>();
        long total = 0;

        for (Event e : elements) {
            total++;
            users.add(e.getUser_id());
            eventCounts.merge(e.getEvent(), 1L, Long::sum);

            switch (e.getEvent()) {
                case "PURCHASE":
                    purchasesByCity.merge(e.getCity(), 1L, Long::sum);
                    purchasesByProduct.merge(e.getProduct(), 1L, Long::sum);
                    break;
                case "VIEW_PRODUCT":
                    viewsByProduct.merge(e.getProduct(), 1L, Long::sum);
                    break;
                case "ADD_CART":
                    addCartByProduct.merge(e.getProduct(), 1L, Long::sum);
                    break;
                default:
                    break;
            }
        }

        summary.setTotalEvents(total);
        summary.setEventCounts(eventCounts);
        summary.setDistinctUsers(users.size());
        summary.setPurchasesByCity(purchasesByCity);
        summary.setViewsByProduct(viewsByProduct);
        summary.setPurchasesByProduct(purchasesByProduct);
        summary.setAddCartByProduct(addCartByProduct);

        out.collect(summary);
    }
}
