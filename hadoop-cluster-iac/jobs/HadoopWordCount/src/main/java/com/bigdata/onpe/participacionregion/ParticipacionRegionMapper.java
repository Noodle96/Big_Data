package com.bigdata.onpe.participacionregion;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class ParticipacionRegionMapper extends Mapper<LongWritable, Text, Text, Text> {

    private final Text region = new Text();
    private final Text electoresVotos = new Text();

    @Override
    protected void map(
            LongWritable key,
            Text value,
            Context context
    ) throws IOException, InterruptedException {

        String line = value.toString();

        if (line.startsWith("REGIÓN / CONTINENTE")) {
            return;
        }

        String[] columns = line.split("\t");

        if (columns.length < 4) {
            return;
        }

        String regionValue = columns[0].trim();
        String electoresText = columns[2].trim();
        String votosText = columns[3].trim();

        if (regionValue.isEmpty() || electoresText.isEmpty() || votosText.isEmpty()) {
            return;
        }

        int electores = (int) Double.parseDouble(electoresText);
        int votos = (int) Double.parseDouble(votosText);

        region.set(regionValue);
        electoresVotos.set(electores + "|" + votos);

        context.write(region, electoresVotos);
    }
}