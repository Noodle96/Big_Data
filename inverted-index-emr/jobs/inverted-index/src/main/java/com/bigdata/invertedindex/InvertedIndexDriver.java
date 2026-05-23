package com.bigdata.invertedindex;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
 * Driver principal del job MapReduce para construir un índice invertido.
 *
 * Uso:
 *      hadoop jar inverted-index.jar <input_path> <output_path>
 */
public class InvertedIndexDriver {

    public static void main(String[] args) throws Exception {

        if (args.length != 2) {
            System.err.println("Uso: hadoop jar inverted-index.jar <input_path> <output_path>");
            System.exit(1);
        }

        Configuration configuration = new Configuration();

        Job job = Job.getInstance(configuration, "Inverted Index");

        job.setJarByClass(InvertedIndexDriver.class);

        job.setMapperClass(InvertedIndexMapper.class);
        job.setReducerClass(InvertedIndexReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        boolean success = job.waitForCompletion(true);

        System.exit(success ? 0 : 1);
    }
}