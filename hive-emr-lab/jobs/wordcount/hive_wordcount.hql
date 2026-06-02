SET hive.execution.engine=mr;
SET mapreduce.job.reduces=6;

CREATE DATABASE IF NOT EXISTS bigdata_lab;

USE bigdata_lab;

DROP TABLE IF EXISTS wikipedia_corpus;

CREATE EXTERNAL TABLE wikipedia_corpus (
    line STRING
)
STORED AS TEXTFILE
LOCATION '/datasets/wikipedia/raw';

DROP TABLE IF EXISTS wordcount_result;

CREATE TABLE wordcount_result AS
SELECT
    word,
    COUNT(*) AS total
FROM (
    SELECT
        explode(
            split(
                regexp_replace(
                    lower(line),
                    '[^a-z0-9 ]',
                    ' '
                ),
                '\\s+'
            )
        ) AS word
    FROM wikipedia_corpus
) tokens
WHERE word <> ''
GROUP BY word;