package org.bigdata;

import java.io.IOException;

import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

public class AverageTemperatureReducer
        extends Reducer<Text, DoubleWritable, Text, DoubleWritable> {

    private final DoubleWritable result = new DoubleWritable();

    @Override
    protected void reduce(Text key, Iterable<DoubleWritable> values, Context context)
            throws IOException, InterruptedException {
        double sum = 0.0;
        long count = 0;
        for (DoubleWritable val : values) {
            sum += val.get();
            count++;
        }
        if (count > 0) {
            result.set(sum / count);
            context.write(key, result);
        }
    }
}
