package com.bigdata.onpe.votosprovincia;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class VotosProvinciaMapper extends Mapper<LongWritable, Text, Text, IntWritable> {

    private final Text provinciaOrganizacion = new Text();
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

        String region = columns[2].trim();
        String provincia = columns[3].trim();
        String organizacionPolitica = columns[9].trim();
        String votosText = columns[10].trim();

        if (region.isEmpty() || provincia.isEmpty() || organizacionPolitica.isEmpty() || votosText.isEmpty()) {
            return;
        }

        int votosValue = (int) Double.parseDouble(votosText);

        provinciaOrganizacion.set(region + "|" + provincia + "|" + organizacionPolitica);
        votos.set(votosValue);

        context.write(provinciaOrganizacion, votos);
    }
}