package org.bigdata;

import org.apache.hadoop.io.*;
import org.apache.hadoop.mapred.*;

import java.io.IOException;
import java.util.*;

public class SceneReducer extends MapReduceBase implements Reducer<Text, Text, Text, Text> {

    public void reduce(Text key, Iterator<Text> values, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
        Set<String> postings = new HashSet<>();
        while (values.hasNext()) {
            postings.add(values.next().toString());
        }

        List<String> sorted = new ArrayList<>(postings);
        Collections.sort(sorted);

        output.collect(key, new Text(String.join(", ", sorted)));
    }
}