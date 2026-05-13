package com.bigdata.onpe.ganadorregion;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class GanadorRegionMapper extends Mapper<LongWritable, Text, Text, Text> {

    private final Text region = new Text();
    private final Text organizacionVotos = new Text();

    @Override
    protected void map(
            LongWritable key,
            Text value,
            Context context
    ) throws IOException, InterruptedException {

        String line = value.toString();

        String[] parts = line.split("\t");

        if (parts.length != 2) {
            return;
        }

        String[] regionOrganizacion = parts[0].split("\\|");

        if (regionOrganizacion.length != 2) {
            return;
        }

        String regionValue = regionOrganizacion[0].trim();
        String organizacionValue = regionOrganizacion[1].trim();
        String votosValue = parts[1].trim();

        region.set(regionValue);
        organizacionVotos.set(organizacionValue + "|" + votosValue);

        context.write(region, organizacionVotos);
    }
}