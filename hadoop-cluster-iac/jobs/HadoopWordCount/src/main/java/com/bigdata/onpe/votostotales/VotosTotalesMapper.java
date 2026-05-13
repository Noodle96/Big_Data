package com.bigdata.onpe.votostotales;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class VotosTotalesMapper extends Mapper<LongWritable, Text, Text, IntWritable> {

    private final Text organizacionPolitica = new Text();
    private final IntWritable votos = new IntWritable();

    @Override
    protected void map(
            LongWritable key,
            Text value,
            Context context
    ) throws IOException, InterruptedException {

        String line = value.toString();

        if (line.startsWith("TIPO DE ELECCIÓN")) {
            return;
        }

        String[] columns = line.split("\t");

        if (columns.length < 11) {
            return;
        }

        String organizacionValue = columns[9].trim();
        String votosText = columns[10].trim();

        if (organizacionValue.isEmpty() || votosText.isEmpty()) {
            return;
        }

        int votosValue = (int) Double.parseDouble(votosText);

        organizacionPolitica.set(organizacionValue);
        votos.set(votosValue);

        context.write(organizacionPolitica, votos);
    }
}