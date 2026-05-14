# genre-movie-analytics-platform
Distributed big data analytics platform using Hadoop, Spark, Hive, Kafka, and Flink

<div align="center">

# 🎬 Genre-based Movie Preference Analytics Platform

### Distributed Big Data Analytics using Hadoop Ecosystem

<br>

[![Hadoop](https://img.shields.io/badge/Hadoop-BigData-yellow?style=for-the-badge&logo=apachehadoop)]
[![Spark](https://img.shields.io/badge/Apache-Spark-orange?style=for-the-badge&logo=apachespark)]
[![Kafka](https://img.shields.io/badge/Apache-Kafka-black?style=for-the-badge&logo=apachekafka)]
[![Hive](https://img.shields.io/badge/Apache-Hive-FDEE21?style=for-the-badge&logo=apachehive)]
[![Pig](https://img.shields.io/badge/Apache-Pig-blue?style=for-the-badge)]
[![Flink](https://img.shields.io/badge/Apache-Flink-E6526F?style=for-the-badge&logo=apacheflink)]
[![GCP](https://img.shields.io/badge/Google-Cloud-4285F4?style=for-the-badge&logo=googlecloud)]

<br>

### 2026 Big Data Programming Final Project

</div>

---

# 📌 Project Overview

본 프로젝트는 Hadoop Ecosystem 기반의  
분산 빅데이터 분석 플랫폼을 구축하고,

MovieLens 데이터를 활용하여 사용자들의 영화 장르 선호 패턴과  
평점 행동 데이터를 분석하는 프로젝트입니다.

단순 영화 순위 분석이 아닌,

- 사용자 선호 장르 분석
- 장르별 평점 패턴 분석
- 사용자 행동 기반 데이터 분석
- 실시간 스트리밍 데이터 처리 구조 설계

를 목표로 하며,

Hadoop, HDFS, Pig, Hive, Spark, Kafka, Flink를 활용하여  
대규모 데이터 처리 파이프라인을 구현합니다.

---

# 🎯 Project Goals

## 주요 목표

- Hadoop 기반 분산 저장 환경 구축
- 대규모 영화 데이터 분석
- 장르 기반 사용자 선호도 분석
- Hive/Pig 기반 데이터 처리
- Spark 기반 분산 처리 학습
- Kafka 기반 실시간 스트리밍 구조 설계
- Spark Streaming/Flink 기반 실시간 분석 구조 설계

---

# 🧠 Problem Definition

OTT 플랫폼과 영화 서비스에서는  
수많은 사용자 행동 데이터가 지속적으로 생성됩니다.

본 프로젝트에서는 다음과 같은 문제를 해결하고자 합니다.

---

## 1️⃣ 어떤 영화 장르가 가장 선호되는가?

사용자 평점 데이터를 기반으로:

- 가장 많이 평가된 장르
- 평균 평점이 높은 장르
- 사용자 선호 장르 패턴

을 분석합니다.

---

## 2️⃣ 사용자들은 어떤 방식으로 평점을 남기는가?

사용자 행동 데이터를 기반으로:

- 사용자별 평균 평점
- 활발한 사용자 분석
- 평점 분포 분석

을 수행합니다.

---

## 3️⃣ 대규모 데이터를 어떻게 효율적으로 처리할 수 있는가?

분산 처리 환경에서:

- Batch Processing
- Distributed Processing
- Streaming Processing

구조를 설계하고 분석합니다.

---

# 📂 Dataset

## 🎥 MovieLens Dataset

본 프로젝트는 GroupLens Research에서 제공하는  
MovieLens Dataset을 사용합니다.

### Dataset Information

| Item | Description |
|---|---|
| Dataset | MovieLens Latest Small |
| Source | https://grouplens.org/datasets/movielens/ |
| Format | CSV |
| Domain | Movie Rating Data |

---

## Dataset Structure

| File | Description |
|---|---|
| movies.csv | 영화 메타데이터 |
| ratings.csv | 사용자 평점 데이터 |
| tags.csv | 사용자 태그 정보 |
| links.csv | 외부 영화 사이트 연결 정보 |

---

# 🏗️ System Architecture

```text
                         ┌────────────────────┐
                         │  MovieLens Dataset │
                         └─────────┬──────────┘
                                   │
                                   ▼

                    ┌────────────────────────────┐
                    │            HDFS            │
                    │ Distributed File System    │
                    └─────────┬──────────────────┘
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
          ▼                   ▼                    ▼

 ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
 │      Pig       │  │      Hive      │  │   MapReduce    │
 │ Data Flow Proc │  │ SQL Analytics  │  │ Batch Analysis │
 └────────────────┘  └────────────────┘  └────────────────┘

                              │
                              ▼

                    ┌────────────────────────────┐
                    │        Apache Spark        │
                    │ Distributed Processing     │
                    └─────────┬──────────────────┘
                              │

               ┌──────────────┴──────────────┐
               │                             │
               ▼                             ▼

      ┌────────────────┐          ┌────────────────┐
      │     Kafka      │          │ Spark Streaming│
      │ Event Streaming│          │ Real-time Proc │
      └────────────────┘          └────────────────┘

                              │
                              ▼

                    ┌────────────────────────────┐
                    │            Flink           │
                    │ Real-time Analytics Engine │
                    └────────────────────────────┘
```

---

# ⚙️ Technology Stack

# ☁️ Cloud Environment

| Technology | Purpose |
|---|---|
| GCP | Cloud Infrastructure |
| Ubuntu | Linux Environment |
| Docker | Container Environment |

---

# 🗄️ Big Data Ecosystem

| Technology | Purpose |
|---|---|
| Hadoop | Distributed Computing |
| HDFS | Distributed Storage |
| MapReduce | Batch Processing |
| Pig | Data Flow Processing |
| Hive | SQL-based Analytics |
| Spark | Distributed Processing |
| Kafka | Real-time Streaming |
| Spark Streaming | Streaming Analytics |
| Flink | Real-time Data Processing |

---

# 🔄 Data Processing Pipeline

## 1️⃣ Data Collection

MovieLens 데이터를 수집합니다.

```bash
wget https://files.grouplens.org/datasets/movielens/ml-latest-small.zip
unzip ml-latest-small.zip
```

---

## 2️⃣ Upload to HDFS

수집한 데이터를 HDFS에 저장합니다.

```bash
hadoop fs -mkdir ml-latest-small
hadoop fs -copyFromLocal * ml-latest-small
```

---

## 3️⃣ Pig-based Data Processing

Pig Latin을 사용하여 장르 및 평점 데이터를 처리합니다.

### Example Processing

- 장르별 평점 집계
- 사용자 행동 분석
- 평점 분포 분석

```pig
grouped = GROUP ratings BY movieId;

rating_stats = FOREACH grouped GENERATE
group AS movieId,
AVG(ratings.rating) AS avg_rating,
COUNT(ratings.rating) AS rating_count;
```

---

## 4️⃣ Hive-based Analytics

Hive SQL을 사용하여 데이터 분석을 수행합니다.

```sql
SELECT genres,
AVG(r.rating) AS avg_rating,
COUNT(*) AS rating_count
FROM movies m
JOIN ratings r
ON m.movieid = r.movieid
GROUP BY genres
ORDER BY avg_rating DESC;
```

---

## 5️⃣ Spark Distributed Processing

Spark를 사용하여 대규모 데이터를 병렬 처리합니다.

### 주요 목적

- In-memory Processing
- Distributed Computing
- Parallel Data Analysis

---

## 6️⃣ Kafka Streaming Architecture

Kafka를 활용하여 실시간 데이터 스트리밍 구조를 설계합니다.

### Example Scenario

- 사용자 평점 이벤트 수집
- 실시간 데이터 전달
- Streaming Pipeline 구성

---

## 7️⃣ Spark Streaming & Flink

실시간 데이터 처리 및 분석 구조를 구현합니다.

### 주요 기능

- Real-time Event Processing
- Stream Analytics
- Low-latency Distributed Processing

---

# 📊 Expected Results

본 프로젝트를 통해 다음과 같은 분석 결과를 기대합니다.

---

## 🎬 Genre Preference Analysis

- 가장 인기 있는 영화 장르
- 장르별 평균 평점
- 장르별 사용자 선호도

---

## 👤 User Behavior Analysis

- 활발한 사용자 분석
- 사용자 평점 패턴 분석
- 사용자 활동 분포 분석

---

## ⚡ Distributed Processing Experience

- Hadoop 기반 분산 처리 경험
- Spark 기반 병렬 처리 경험
- Streaming 기반 실시간 분석 구조 이해

---

# 📁 Project Structure

```text
genre-movie-analytics-platform/
│
├── data/
│   ├── movies.csv
│   ├── ratings.csv
│   ├── tags.csv
│   └── links.csv
│
├── hdfs/
│
├── pig/
│   └── genre_analysis.pig
│
├── hive/
│   └── genre_analysis.sql
│
├── spark/
│   └── spark_analysis.py
│
├── kafka/
│   ├── producer.py
│   └── consumer.py
│
├── streaming/
│   └── spark_streaming.py
│
├── flink/
│   └── flink_analysis.py
│
├── results/
│
└── README.md
```

---

# 🚀 Future Improvements

## 향후 확장 계획

- 머신러닝 기반 추천 시스템
- 실시간 사용자 추천 시스템
- Spark MLlib 기반 분석
- Dashboard 시각화
- 대규모 클러스터 확장
- 사용자 맞춤형 추천 시스템

---

# 📚 References

- https://hadoop.apache.org/
- https://spark.apache.org/
- https://kafka.apache.org/
- https://flink.apache.org/
- https://hive.apache.org/
- https://pig.apache.org/
- https://cloud.google.com/
- https://grouplens.org/datasets/movielens/

---

# 👨‍💻 Author

| Name | University | Major |
|---|---|---|
| Yu Jin Jung | Myongji University | Data Science |

---

<div align="center">

## ⭐ Big Data Programming Final Project ⭐

Distributed Processing · Big Data Analytics · Streaming Architecture

</div>
