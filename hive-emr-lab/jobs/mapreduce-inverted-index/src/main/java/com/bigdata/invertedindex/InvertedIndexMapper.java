package com.bigdata.invertedindex;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;

import java.io.IOException;

/**
 * Mapper para índice invertido.
 *
 * Entrada:
 *      key   -> offset de línea
 *      value -> línea de texto
 *
 * Salida:
 *      palabra -> documento
 */
public class InvertedIndexMapper
        extends Mapper<LongWritable, Text, Text, Text> {

    private final Text outputKey = new Text();
    private final Text outputValue = new Text();

    @Override
    protected void map(
            LongWritable key,
            Text value,
            Context context
    ) throws IOException, InterruptedException {

        FileSplit fileSplit = (FileSplit) context.getInputSplit();
        String documentName = fileSplit.getPath().getName();

        String line = value.toString().toLowerCase();
        String cleanLine = line.replaceAll("[^a-z0-9 ]", " ");

        String[] words = cleanLine.split("\\s+");

        for (String word : words) {
            if (!word.isEmpty()) {
                outputKey.set(word);
                outputValue.set(documentName);
                context.write(outputKey, outputValue);
            }
        }
    }
}