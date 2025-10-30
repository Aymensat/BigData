# Big Data Analysis Project (Hadoop & Spark)

This is the source code for my university Big Data project.  
The goal was to analyze 1 million Reddit comments using MapReduce,  
Hive, Pig, and Spark.

## How to Run This Project

All code, data, and dependencies are pre-installed in a  
portable Docker image available on Docker Hub.

**1. Pull and run the image:**

```bash
docker pull aymensatouri/hadoop-project:v999
docker run -it --privileged --name hadoop-single \
 -p 50070:50070 -p 8088:8088 -p 8080:8080 \
 aymensatouri/hadoop-project:v999 bash
```
