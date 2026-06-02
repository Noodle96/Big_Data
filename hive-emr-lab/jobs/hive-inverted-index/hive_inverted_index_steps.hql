SET hive.execution.engine=mr;
SET mapreduce.job.reduces=6;

CREATE DATABASE IF NOT EXISTS bigdata_lab;

USE bigdata_lab;

-- ============================================================
-- ETAPA 1: Tabla externa sobre el corpus Wikipedia en HDFS
-- ============================================================

DROP TABLE IF EXISTS wikipedia_corpus_inverted;

CREATE EXTERNAL TABLE wikipedia_corpus_inverted (
    line STRING
)
STORED AS TEXTFILE
LOCATION '/datasets/wikipedia/raw';


-- ============================================================
-- ETAPA 2: Asociar cada línea con el archivo/documento origen
-- INPUT__FILE__NAME permite obtener la ruta HDFS del archivo
-- ============================================================

DROP TABLE IF EXISTS wikipedia_lines_with_document;

CREATE TABLE wikipedia_lines_with_document AS
SELECT
    regexp_extract(INPUT__FILE__NAME, '([^/]+)$', 1) AS document_name,
    line
FROM wikipedia_corpus_inverted;


-- ============================================================
-- ETAPA 3: Limpiar texto
-- Convierte a minúsculas y reemplaza caracteres especiales
-- ============================================================

DROP TABLE IF EXISTS wikipedia_clean_lines_inverted;

CREATE TABLE wikipedia_clean_lines_inverted AS
SELECT
    document_name,
    regexp_replace(
        lower(line),
        '[^a-z0-9 ]',
        ' '
    ) AS clean_line
FROM wikipedia_lines_with_document;


-- ============================================================
-- ETAPA 4: Tokenización
-- Divide cada línea limpia en palabras individuales
-- ============================================================

DROP TABLE IF EXISTS wikipedia_tokens_inverted;

CREATE TABLE wikipedia_tokens_inverted AS
SELECT
    document_name,
    word
FROM wikipedia_clean_lines_inverted
LATERAL VIEW explode(split(clean_line, '\\s+')) exploded_words AS word
WHERE word <> '';


-- ============================================================
-- ETAPA 5: Índice invertido
-- Agrupa por palabra y construye la lista de documentos
-- ============================================================

DROP TABLE IF EXISTS inverted_index_result;

CREATE TABLE inverted_index_result AS
SELECT
    word,
    concat_ws(', ', sort_array(collect_set(document_name))) AS documents
FROM wikipedia_tokens_inverted
GROUP BY word;


-- ============================================================
-- Consultas opcionales de inspección
-- No ejecutar para medir tiempo oficial
-- ============================================================

-- SELECT * FROM wikipedia_lines_with_document LIMIT 10;
-- SELECT * FROM wikipedia_clean_lines_inverted LIMIT 10;
-- SELECT * FROM wikipedia_tokens_inverted LIMIT 20;
-- SELECT * FROM inverted_index_result ORDER BY word LIMIT 20;