package org.bigdata;

import com.google.gson.*;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapred.*;

import java.io.IOException;
import java.util.Map;

public class SceneScoreMapper extends MapReduceBase implements Mapper<LongWritable, Text, Text, IntWritable> {

    private final Gson gson = new Gson();
    private final Text outputKey = new Text();
    private final IntWritable outputValue = new IntWritable();

    public void map(LongWritable key, Text value, OutputCollector<Text, IntWritable> output, Reporter reporter) throws IOException {
        JsonObject json;
        try {
            json = gson.fromJson(value.toString(), JsonObject.class);
        } catch (JsonSyntaxException e) {
            return; // ignorar líneas malformadas
        }

        if (!json.has("scene_id") || !json.has("subclips")) return;

        String sceneId = json.get("scene_id").getAsString();
        JsonArray subclips = json.getAsJsonArray("subclips");

        int totalScore = 0;

        for (JsonElement elem : subclips) {
            JsonObject sub = elem.getAsJsonObject();
            if (!sub.has("textual_tokens")) continue;

            JsonObject tokens = sub.getAsJsonObject("textual_tokens");

            int diversity = tokens.entrySet().size(); // ✅
            int frequency = 0;
            for (Map.Entry<String, JsonElement> entry : tokens.entrySet()) {
                frequency += entry.getValue().getAsInt();  // ✅ suma de frecuencias
            }

            totalScore += diversity + frequency;
        }

        outputKey.set(sceneId);
        outputValue.set(totalScore);
        output.collect(outputKey, outputValue);
    }
}
