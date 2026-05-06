package com.bigdata.onpe.votoscandidato;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class VotosCandidatoMapper extends Mapper<LongWritable, Text, Text, IntWritable> {

    private final Text candidato = new Text();
    private final IntWritable votos = new IntWritable();

    @Override
    protected void map(
            LongWritable key,
            Text value,
            Context context
    ) throws IOException, InterruptedException {

        String line = value.toString();

        if (line.startsWith("codigo_mesa")) {
            return;
        }

        String[] columns = line.split(",");

        if (columns.length != 3) {
            return;
        }

        String candidatoValue = columns[1].trim();
        int votosValue = Integer.parseInt(columns[2].trim());

        candidato.set(candidatoValue);
        votos.set(votosValue);

        context.write(candidato, votos);
    }
}