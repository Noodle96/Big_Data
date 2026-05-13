package com.bigdata.onpe.ganadorregion;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

public class GanadorRegionReducer extends Reducer<Text, Text, Text, Text> {

    private final Text resultado = new Text();

    @Override
    protected void reduce(
            Text key,
            Iterable<Text> values,
            Context context
    ) throws IOException, InterruptedException {

        String ganador = "";
        int maxVotos = -1;

        for (Text value : values) {

            String[] parts = value.toString().split("\\|");

            if (parts.length != 2) {
                continue;
            }

            String organizacion = parts[0].trim();
            int votos = Integer.parseInt(parts[1].trim());

            if (votos > maxVotos) {
                maxVotos = votos;
                ganador = organizacion;
            }
        }

        resultado.set(ganador + "|" + maxVotos);

        context.write(key, resultado);
    }
}