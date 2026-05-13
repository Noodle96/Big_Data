package com.bigdata.onpe.participacionregion;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

public class ParticipacionRegionReducer extends Reducer<Text, Text, Text, Text> {

    private final Text resultado = new Text();

    @Override
    protected void reduce(
            Text key,
            Iterable<Text> values,
            Context context
    ) throws IOException, InterruptedException {

        long totalElectores = 0L;
        long totalVotos = 0L;

        for (Text value : values) {
            String[] parts = value.toString().split("\\|");

            if (parts.length != 2) {
                continue;
            }

            long electores = Long.parseLong(parts[0].trim());
            long votos = Long.parseLong(parts[1].trim());

            totalElectores += electores;
            totalVotos += votos;
        }

        double participacion = 0.0;

        if (totalElectores > 0) {
            participacion = (double) totalVotos / (double) totalElectores;
        }

        resultado.set(totalVotos + "|" + totalElectores + "|" + participacion);

        context.write(key, resultado);
    }
}