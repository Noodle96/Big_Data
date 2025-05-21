package org.example;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;

import java.io.IOException;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

public class II_Reducer extends MapReduceBase
        implements Reducer<Text, Text, Text, Text> {

    private Text postings = new Text();

    @Override
    public void reduce(Text key, Iterator<Text> values,
                       OutputCollector<Text, Text> output,
                       Reporter reporter) throws IOException {
        Set<String> uniqueDocs = new HashSet<>();
        while (values.hasNext()) {
            uniqueDocs.add(values.next().toString());
        }
        // Construir cadena "doc1,doc2,doc3"
        postings.set(String.join(",", uniqueDocs));
        output.collect(key, postings);
    }
}
