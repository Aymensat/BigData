-- Hive: reddit keyword analysis (OpenCSVSerde handles quoted/multiline bodies)
-- We will create an EXTERNAL table pointed at /user/root/project (where the CSV lives).

-- avoid CLI header in redirected output
set hive.cli.print.header=false;
set hive.resultset.use.unique.column.names=false;

-- If a previous table exists, drop it so schema changes don't get in the way
DROP TABLE IF EXISTS reddit_raw;

CREATE EXTERNAL TABLE reddit_raw (
  subreddit STRING,
  body STRING,
  controversiality INT,
  score INT
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar"     = "\""
)
STORED AS TEXTFILE
LOCATION '/user/root/project'
TBLPROPERTIES ("skip.header.line.count"="1");

-- Main aggregation: same metrics as your MapReduce reducer
SELECT
  subreddit,
  COUNT(*) AS total_mentions,
  ROUND(100.0 * SUM(CASE WHEN controversiality = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_controversial,
  ROUND(100.0 * SUM(CASE WHEN score > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_upvoted,
  ROUND(100.0 * SUM(CASE WHEN score < 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_downvoted
FROM reddit_raw
WHERE lower(body) RLIKE '\\bjew(s|ish)?\\b'
GROUP BY subreddit
ORDER BY total_mentions DESC;
