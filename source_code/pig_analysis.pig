/*
 * Pig script to analyze Reddit comments (STREAMING Version)
 *
 * Final version: Removes the failing CACHE directive.
 * We rely on 'python3' being in the default PATH on the nodes,
 * which was proven by the successful Hadoop Streaming job.
 */

-- 1. Define the streaming command.
DEFINE CMD `python3 mapper.py`
    SHIP('/code/mapper.py');

-- 2. Load the raw data as single-column lines.
A = LOAD '/user/root/project/reddit_comments.csv' USING PigStorage() AS (line:chararray);

-- 3. STREAM the data through our Python mapper.
B = STREAM A THROUGH CMD AS (
    subreddit:chararray,
    is_controversial:int,
    is_upvoted:int,
    is_downvoted:int,
    total:int);

-- 4. Group by subreddit
C = GROUP B BY subreddit;

-- 5. Aggregate the counts for each subreddit
D = FOREACH C GENERATE
    group AS subreddit,
    SUM(B.total) AS total_mentions,
    SUM(B.is_controversial) AS sum_contro,
    SUM(B.is_upvoted) AS sum_up,
    SUM(B.is_downvoted) AS sum_down;

-- 6. Calculate final percentages
E = FOREACH D GENERATE
    subreddit,
    total_mentions,
    (total_mentions > 0 ? (double)sum_contro * 100.0 / (double)total_mentions : 0.0) AS pct_controversial,
    (total_mentions > 0 ? (double)sum_up * 100.0 / (double)total_mentions : 0.0) AS pct_up,
    (total_mentions > 0 ? (double)sum_down * 100.0 / (double)total_mentions : 0.0) AS pct_down;

-- 7. Order by total mentions (descending)
F = ORDER E BY total_mentions DESC;

-- 8. Store the results in HDFS
STORE F INTO '/user/root/pig_keyword_analysis' USING PigStorage('\t');
