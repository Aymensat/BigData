#!/usr/bin/env python3
"""
PySpark job to analyze Reddit comments, replicating the MapReduce/Hive/Pig logic.

This job uses the DataFrame API, which is the correct way to handle
complex, multi-line CSV files in Spark (equivalent to Hive's OpenCSVSerde).
The logic maps to MapReduce as follows:
1.  read.csv() + filter() + withColumn() == 'Map' phase
2.  groupBy()                          == 'Shuffle' phase
3.  agg() + withColumn()               == 'Reduce' phase
"""

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, when, lit, sum, count, round
from pyspark.sql.types import StructType, StructField, StringType

def main():
    spark = SparkSession.builder \
        .appName("Reddit Keyword Analysis (Spark)") \
        .getOrCreate()

    # Define paths
    input_path = "/user/root/project/reddit_comments.csv"
    output_path = "/user/root/spark_keyword_analysis"

    # Define schema to avoid inferring, which can be slow and error-prone
    # We read controversiality and score as String, then cast manually
    # to replicate the 'safe_int' logic from the mapper.
    schema = StructType([
        StructField("subreddit", StringType(), True),
        StructField("body", StringType(), True),
        StructField("controversiality", StringType(), True),
        StructField("score", StringType(), True)
    ])

    # 1. LOAD (Part of Map)
    # Use multiLine=True to correctly parse quoted fields with newlines,
    # a problem you identified in the MapReduce 'gotchas'.
    df = spark.read.csv(
        input_path,
        header=True,
        schema=schema,
        quote='"',
        escape='"',
        multiLine=True
    )

    # 2. FILTER (Map logic)
    # Regex for keyword matching (case-insensitive)
    keyword_regex = r'\b(jew|jews|jewish)\b'

    filtered_df = df.filter(col("body").isNotNull()) \
                    .filter(lower(col("body")).rlike(keyword_regex))

    # 3. TRANSFORM (Map logic)
    # Create the intermediate metrics, equivalent to the mapper's output.
    # We cast to 'int' and fill non-numeric values (which become null) with 0.
    metrics_df = filtered_df.withColumn("cont_int", col("controversiality").cast("int")) \
                            .withColumn("score_int", col("score").cast("int")) \
                            .fillna(0, subset=["cont_int", "score_int"])

    metrics_df = metrics_df.withColumn("is_controversial", (col("cont_int") == 1).cast("int")) \
                           .withColumn("is_upvoted", (col("score_int") > 0).cast("int")) \
                           .withColumn("is_downvoted", (col("score_int") < 0).cast("int")) \
                           .withColumn("total", lit(1))

    # 4. GROUP (Shuffle) & 5. AGGREGATE (Reduce logic)
    # This is the reduceByKey step, summing the metrics per subreddit.
    agg_df = metrics_df.groupBy("subreddit") \
                       .agg(
                           sum("total").alias("total_mentions"),
                           sum("is_controversial").alias("sum_contro"),
                           sum("is_upvoted").alias("sum_up"),
                           sum("is_downvoted").alias("sum_down")
                       )

    # 6. CALCULATE PERCENTAGES (Reduce logic)
    # This is the final step from your reducer.py, calculating percentages.
    final_df = agg_df.withColumn(
        "pct_controversial",
        when(col("total_mentions") > 0, round((col("sum_contro") / col("total_mentions")) * 100.0, 1))
        .otherwise(0.0)
    ).withColumn(
        "pct_upvoted",
        when(col("total_mentions") > 0, round((col("sum_up") / col("total_mentions")) * 100.0, 1))
        .otherwise(0.0)
    ).withColumn(
        "pct_downvoted",
        when(col("total_mentions") > 0, round((col("sum_down") / col("total_mentions")) * 100.0, 1))
        .otherwise(0.0)
    )

    # 7. FORMAT & ORDER
    # Select final columns and order by total_mentions descending.
    output_df = final_df.select(
        "subreddit",
        "total_mentions",
        "pct_controversial",
        "pct_upvoted",
        "pct_downvoted"
    ).orderBy(col("total_mentions").desc())

    # 8. SAVE (Output)
    # Save as TSV. Coalesce(1) creates a single 'part-00000' file,
    # just like your MapReduce job.
    output_df.coalesce(1).write.csv(
        output_path,
        sep="\t",
        header=False,
        mode="overwrite"
    )

    print(f"Spark job complete. Results saved to HDFS: {output_path}")

if __name__ == "__main__":
    main()
