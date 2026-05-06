package com.bigdata.onpe.votoscandidato;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

public class VotosCandidatoReducer extends Reducer<Text, IntWritable, Text, IntWritable> {

    private final IntWritable totalVotos = new IntWritable();

    @Override
    protected void reduce(
            Text key,
            Iterable<IntWritable> values,
            Context context
    ) throws IOException, InterruptedException {

        int sum = 0;

        for (IntWritable value : values) {
            sum += value.get();
        }

        totalVotos.set(sum);
        context.write(key, totalVotos);
    }
}