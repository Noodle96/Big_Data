package com.bigdata.invertedindex;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;

import java.io.IOException;
import java.util.StringTokenizer;

/**
 * Mapper para construir un índice invertido.
 *
 * Entrada:
 *      key   -> offset de línea dentro del archivo
 *      value -> línea completa del archivo
 *
 * Salida:
 *      palabra -> nombre_documento
 *
 * Ejemplo:
 *      hadoop -> doc1.txt
 */
public class InvertedIndexMapper
        extends Mapper<LongWritable, Text, Text, Text> {

    /**
     * Palabra emitida como clave.
     */
    private final Text outputKey = new Text();

    /**
     * Nombre del documento emitido como valor.
     */
    private final Text outputValue = new Text();

    @Override
    protected void map(
            LongWritable key,
            Text value,
            Context context
    ) throws IOException, InterruptedException {

        /*
         * Obtener el archivo de entrada actual.
         *
         * context.getInputSplit() representa la porción del archivo que
         * este mapper está procesando.
         *
         * Como estamos usando FileInputFormat, podemos convertirlo a FileSplit.
         */
        FileSplit fileSplit = (FileSplit) context.getInputSplit();

        /*
         * Obtener solo el nombre del archivo.
         *
         * Si la ruta completa es:
         *      s3://bucket/input/doc1.txt
         *
         * fileSplit.getPath().getName() devuelve:
         *      doc1.txt
         *
         * Si la ruta HDFS es:
         *      /input/doc1.txt
         *
         * también devuelve:
         *      doc1.txt
         */
        String fileName = fileSplit.getPath().getName();

        /*
         * Convertir la línea actual a minúsculas para normalizar palabras.
         *
         * Así, "Hadoop", "hadoop" y "HADOOP" serán tratados como la misma palabra.
         */
        String line = value.toString().toLowerCase();

        /*
         * Separar la línea en tokens usando espacios en blanco.
         */
        StringTokenizer tokenizer = new StringTokenizer(line);

        /*
         * Recorrer cada palabra de la línea.
         */
        while (tokenizer.hasMoreTokens()) {

            /*
             * Limpiar signos de puntuación u otros caracteres.
             *
             * Ejemplo:
             *      "hadoop," -> "hadoop"
             *      "emr."    -> "emr"
             */
            String word = tokenizer.nextToken()
                    .replaceAll("[^a-zA-Z0-9]", "");

            /*
             * Ignorar tokens vacíos.
             */
            if (!word.isEmpty()) {

                /*
                 * Emitir:
                 *      palabra -> documento
                 */
                outputKey.set(word);
                outputValue.set(fileName);

                context.write(outputKey, outputValue);
            }
        }
    }
}