package com.bigdata.invertedindex;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;
import java.util.TreeSet;

/**
 * Reducer para índice invertido.
 *
 * Entrada:
 *      palabra -> [doc1, doc2, doc1, ...]
 *
 * Salida:
 *      palabra -> doc1, doc2, ...
 */
public class InvertedIndexReducer
        extends Reducer<Text, Text, Text, Text> {

    private final Text outputValue = new Text();

    @Override
    protected void reduce(
            Text key,
            Iterable<Text> values,
            Context context
    ) throws IOException, InterruptedException {

        TreeSet<String> documents = new TreeSet<>();

        for (Text value : values) {
            documents.add(value.toString());
        }

        outputValue.set(String.join(", ", documents));
        context.write(key, outputValue);
    }
}