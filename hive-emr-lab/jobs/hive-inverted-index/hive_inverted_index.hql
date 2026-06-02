SET hive.execution.engine=mr;
SET mapreduce.job.reduces=6;

CREATE DATABASE IF NOT EXISTS bigdata_lab;
USE bigdata_lab;

DROP TABLE IF EXISTS wikipedia_corpus_inverted;
CREATE EXTERNAL TABLE wikipedia_corpus_inverted (
    line STRING
)
STORED AS TEXTFILE
LOCATION '/datasets/wikipedia/raw';

DROP TABLE IF EXISTS inverted_index_result;
CREATE TABLE inverted_index_result AS
SELECT
    word,
    concat_ws(', ', sort_array(collect_set(document_name))) AS documents
FROM (
    SELECT
        regexp_extract(INPUT__FILE__NAME, '([^/]+)$', 1) AS document_name,
        word
    FROM wikipedia_corpus_inverted
    LATERAL VIEW explode(
        split(
            regexp_replace(
                lower(line),
                '[^a-z0-9 ]',
                ' '
            ),
            '\\s+'
        )
    ) exploded_words AS word
) tokens
WHERE word <> ''
GROUP BY word;