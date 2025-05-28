package org.bigdata;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapred.*;

public class SceneRunner {
    public static void main(String[] args) throws Exception {
        JobConf conf = new JobConf(SceneRunner.class);
        conf.setJobName("SceneInvertedIndex");

        conf.setMapperClass(SceneMapper.class);
        conf.setReducerClass(SceneReducer.class);

        conf.setOutputKeyClass(Text.class);
        conf.setOutputValueClass(Text.class);

        conf.setInputFormat(TextInputFormat.class);
        conf.setOutputFormat(TextOutputFormat.class);

        FileInputFormat.setInputPaths(conf, new Path(args[0]));
        FileOutputFormat.setOutputPath(conf, new Path(args[1]));

        JobClient.runJob(conf);
    }
}
