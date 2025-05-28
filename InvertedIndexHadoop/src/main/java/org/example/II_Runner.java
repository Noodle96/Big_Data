package org.example;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.*;
import org.apache.hadoop.fs.Path;
import java.io.IOException;

public class II_Runner {
    public static void main(String[] args) throws IOException {
        JobConf conf = new JobConf(II_Runner.class);
        conf.setJobName("InvertedIndex");

        conf.setOutputKeyClass(Text.class);
        conf.setOutputValueClass(Text.class);

        conf.setMapperClass(II_Mapper.class);
        // No usamos combiner porque queremos la lista completa de docIDs
        conf.setReducerClass(II_Reducer.class);

        conf.setInputFormat(TextInputFormat.class);
        conf.setOutputFormat(TextOutputFormat.class);

        FileInputFormat.setInputPaths(conf, new Path(args[0]));   // carpeta con archivos "docID\ttexto"
        FileOutputFormat.setOutputPath(conf, new Path(args[1])); // carpeta de salida

        JobClient.runJob(conf);
    }
}

// maven clean
// maven install
