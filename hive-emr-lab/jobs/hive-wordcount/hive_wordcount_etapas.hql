CREATE DATABASE IF NOT EXISTS bigdata_lab;

USE bigdata_lab;

-- ============================================================
-- ETAPA 1: Tabla externa que apunta al dataset original en HDFS
-- ============================================================

DROP TABLE IF EXISTS wikipedia_corpus;

CREATE EXTERNAL TABLE wikipedia_corpus (
    line STRING
)
STORED AS TEXTFILE
LOCATION '/datasets/wikipedia/raw';


-- ============================================================
-- ETAPA 2: Limpieza del texto
-- Convierte a minúsculas y reemplaza caracteres especiales
-- ============================================================

DROP TABLE IF EXISTS wikipedia_clean_lines;

CREATE TABLE wikipedia_clean_lines AS
SELECT
    regexp_replace(
        lower(line),
        '[^a-z0-9 ]',
        ' '
    ) AS clean_line
FROM wikipedia_corpus;


-- ============================================================
-- ETAPA 3: Tokenización
-- Divide cada línea limpia en palabras individuales
-- ============================================================

DROP TABLE IF EXISTS wikipedia_tokens;

CREATE TABLE wikipedia_tokens AS
SELECT
    explode(split(clean_line, '\\s+')) AS word
FROM wikipedia_clean_lines;


-- ============================================================
-- ETAPA 4: WordCount final
-- Elimina tokens vacíos, agrupa por palabra y cuenta ocurrencias
-- ============================================================

DROP TABLE IF EXISTS wordcount_result;

CREATE TABLE wordcount_result AS
SELECT
    word,
    COUNT(*) AS total
FROM wikipedia_tokens
WHERE word <> ''
GROUP BY word;


-- ============================================================
-- ETAPA 5: Mostrar las 20 palabras más frecuentes
-- ============================================================

-- SELECT
--     word,
--     total
-- FROM wordcount_result
-- ORDER BY total DESC
-- LIMIT 20;

-- SELECT * FROM wikipedia_clean_lines LIMIT 10;
-- SELECT * FROM wikipedia_tokens LIMIT 20;
-- SELECT * FROM wordcount_result ORDER BY total DESC LIMIT 20;

-- SUBIMOS AL S3
-- aws s3 cp \
-- jobs/wordcount/hive_wordcount.hql \
-- s3://bigdata-russell-academy/hql/wordcount/hive_wordcount.hql