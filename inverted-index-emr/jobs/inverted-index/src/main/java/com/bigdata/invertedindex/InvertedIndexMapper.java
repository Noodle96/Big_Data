package com.bigdata.invertedindex;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;
import java.util.StringTokenizer;

/**
 * Mapper para construir un índice invertido.
 *
 * Entrada:
 *      key   -> offset de línea
 *      value -> línea completa del archivo
 *
 * Salida:
 *      palabra -> documento
 */
public class InvertedIndexMapper
        extends Mapper<LongWritable, Text, Text, Text> {

    /**
     * Palabra emitida.
     */
    private final Text outputKey = new Text();

    /**
     * Nombre del documento emitido.
     */
    private final Text outputValue = new Text();

    @Override
    protected void map(
            LongWritable key,
            Text value,
            Context context
    ) throws IOException, InterruptedException {

        /*
         * Obtener nombre del archivo actual.
         */
        String fileName = context
                .getInputSplit()
                .toString();

        /*
         * Convertir línea a String.
         */
        String line = value.toString().toLowerCase();

        /*
         * Separar palabras.
         */
        StringTokenizer tokenizer = new StringTokenizer(line);

        /*
         * Emitir:
         * palabra -> documento
         */
        while (tokenizer.hasMoreTokens()) {

            String word = tokenizer.nextToken()
                    .replaceAll("[^a-zA-Z0-9]", "");

            /*
             * Ignorar tokens vacíos.
             */
            if (!word.isEmpty()) {

                outputKey.set(word);
                outputValue.set(fileName);

                context.write(outputKey, outputValue);
            }
        }
    }
}