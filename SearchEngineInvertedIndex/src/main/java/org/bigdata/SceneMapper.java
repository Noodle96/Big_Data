package org.bigdata;

import org.apache.hadoop.io.*;
import org.apache.hadoop.mapred.*;
import com.google.gson.*;
import java.io.IOException;
import java.util.Map;

public class SceneMapper extends MapReduceBase implements Mapper<LongWritable, Text, Text, Text> {

    private static final Gson gson = new Gson();
    private final Text outputKey = new Text();
    private final Text outputValue = new Text();

    public void map(LongWritable key, Text value, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
        JsonObject json;
        try {
            json = gson.fromJson(value.toString(), JsonObject.class);
        } catch (JsonSyntaxException e) {
            return; // ignorar líneas malformadas
        }

        if (!json.has("scene_id") || !json.has("subclips")) return;

        String sceneId = json.get("scene_id").getAsString();
        JsonArray subclips = json.getAsJsonArray("subclips");

        for (JsonElement scElem : subclips) {
            JsonObject sc = scElem.getAsJsonObject();
            if (!sc.has("clip_id") || !sc.has("textual_tokens")) continue;

            String clipId = sc.get("clip_id").getAsString();
            JsonObject tokens = sc.getAsJsonObject("textual_tokens");

            for (Map.Entry<String, JsonElement> entry : tokens.entrySet()) {
                String token = entry.getKey().toLowerCase();
                int freq = entry.getValue().getAsInt();

                outputKey.set(token);
                outputValue.set(sceneId + "|" + clipId + ":" + freq);
                output.collect(outputKey, outputValue);
            }
        }
    }
}