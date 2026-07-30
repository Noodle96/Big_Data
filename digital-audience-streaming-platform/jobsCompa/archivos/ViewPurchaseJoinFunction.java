
package pe.unsa.processing;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.api.common.functions.JoinFunction;
import pe.unsa.model.Event;

import java.util.LinkedHashMap;
import java.util.Map;

public class ViewPurchaseJoinFunction implements JoinFunction<Event, Event, String> {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    @Override
    public String join(Event viewed, Event purchased) throws Exception {
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("tipo", "producto_relacionado_vista_compra");
        out.put("product", viewed.getProduct());
        out.put("viewed_by", viewed.getUser_id());
        out.put("purchased_by", purchased.getUser_id());
        return MAPPER.writeValueAsString(out);
    }
}