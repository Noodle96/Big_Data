package org.bigdata;

import java.io.IOException;

import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class AverageTemperatureMapper
        extends Mapper<LongWritable, Text, Text, DoubleWritable> {

    private final Text city = new Text();
    private final DoubleWritable temp = new DoubleWritable();

    @Override
    protected void map(LongWritable key, Text value, Context context)
            throws IOException, InterruptedException {
        // valor de entrada: "2025-05-23,Lima,22.5"
        String[] parts = value.toString().split(",");
        if (parts.length == 3) {
            city.set(parts[1]);
            try {
                double t = Double.parseDouble(parts[2]);
                temp.set(t);
                context.write(city, temp);
            } catch (NumberFormatException e) {
                // línea malformada: omitir
            }
        }
    }
}


