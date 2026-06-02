package com.bigdata.wordcount;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

/**
 * Mapper para WordCount.
 *
 * Entrada:
 *      key   -> offset de la línea dentro del archivo
 *      value -> línea completa de texto
 *
 * Salida:
 *      palabra -> 1
 */
public class WordCountMapper
        extends Mapper<LongWritable, Text, Text, IntWritable> {

    private static final IntWritable ONE = new IntWritable(1);

    private final Text outputKey = new Text();

    @Override
    protected void map(
            LongWritable key,
            Text value,
            Context context
    ) throws IOException, InterruptedException {

        String line = value.toString().toLowerCase();

        String cleanLine = line.replaceAll("[^a-z0-9 ]", " ");

        String[] words = cleanLine.split("\\s+");

        for (String word : words) {
            if (!word.isEmpty()) {
                outputKey.set(word);
                context.write(outputKey, ONE);
            }
        }
    }
}