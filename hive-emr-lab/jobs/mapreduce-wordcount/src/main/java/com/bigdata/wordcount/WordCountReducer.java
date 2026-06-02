package com.bigdata.wordcount;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

/**
 * Reducer para WordCount.
 *
 * Entrada:
 *      palabra -> [1, 1, 1, ...]
 *
 * Salida:
 *      palabra -> total
 */
public class WordCountReducer
        extends Reducer<Text, IntWritable, Text, IntWritable> {

    private final IntWritable outputValue = new IntWritable();

    @Override
    protected void reduce(
            Text key,
            Iterable<IntWritable> values,
            Context context
    ) throws IOException, InterruptedException {

        int total = 0;

        for (IntWritable value : values) {
            total += value.get();
        }

        outputValue.set(total);
        context.write(key, outputValue);
    }
}