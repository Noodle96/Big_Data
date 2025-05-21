package org.example;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reporter;
import org.apache.hadoop.mapred.FileSplit;

import java.io.IOException;
import java.util.StringTokenizer;

public class II_Mapper extends MapReduceBase
        implements Mapper<LongWritable, Text, Text, Text> {

    private Text word = new Text();
    private Text docId = new Text();

    @Override
    public void map(LongWritable key,
                    Text value,
                    OutputCollector<Text, Text> output,
                    Reporter reporter) throws IOException {

        // 1. Incrementar contador de líneas leídas
        reporter.incrCounter("DEBUG", "LINES_READ", 1);

        // 2. Obtener nombre del archivo actual
        FileSplit split = (FileSplit) reporter.getInputSplit();
        String filename = split.getPath().getName();
        docId.set(filename);

        // 3. Tokenizar la línea y emitir palabra → docId
        String line = value.toString();
        StringTokenizer st = new StringTokenizer(line);
        while (st.hasMoreTokens()) {
            String raw = st.nextToken().replaceAll("\\W+", "").toLowerCase();
            if (raw.isEmpty()) continue;
            word.set(raw);
            output.collect(word, docId);
            // opcional: contar palabras emitidas
            reporter.incrCounter("DEBUG", "EMITIDOS", 1);
        }
    }
}
