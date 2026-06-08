"""
쇼핑 리뷰 데이터 Spark DataFrame 기반 전처리 스크립트

원본 CSV 파일을 읽어 컬럼을 정제·변환하고, 아래 파생 변수를 추가합니다:
  - sentiment       : Positive / Neutral / Negative (평점 기반)
  - sentiment_binary: 1 = Positive (rating >= 4), 0 = Negative (rating <= 2)
  - review_length   : review_text 글자 수

결과는 CSV 형식으로 --output 경로에 저장됩니다 (로컬 또는 HDFS).

실행 방법:
  로컬 : python3 data_preprocessing.py
          python3 data_preprocessing.py --input data/raw --output data/cleaned
  HDP  : spark-submit data_preprocessing.py \\
              --input  hdfs:///user/$USER/shopping_reviews/raw \\
              --output hdfs:///user/$USER/shopping_reviews/cleaned
"""

import argparse
import glob as _glob

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType

from config import SAMPLE_PATH


def parse_args():
    parser = argparse.ArgumentParser(description="쇼핑 리뷰 Spark 전처리 스크립트")
    parser.add_argument("--input", default="data/raw",
                        help="원본 CSV 파일 디렉토리 (또는 단일 CSV 경로)")
    parser.add_argument("--output", default="data/cleaned",
                        help="정제된 CSV 저장 경로")
    return parser.parse_args()


def resolve_input_path(spark, path):
    """Spark가 읽을 수 있는 glob 패턴을 반환합니다. 로컬 및 HDFS 경로 모두 지원합니다."""
    if path.endswith(".csv"):
        return path

    # HDFS 경로 감지
    if path.startswith("hdfs://") or path.startswith("hdfs:"):
        return f"{path.rstrip('/')}/*.csv"

    # 로컬: 실제 파일 존재 여부 확인
    matched = _glob.glob(f"{path}/*.csv")
    if matched:
        return f"{path}/*.csv"

    # 파일 없으면 샘플 데이터로 대체
    print(f"'{path}'에서 CSV 파일을 찾을 수 없어 샘플 데이터를 사용합니다: {SAMPLE_PATH}")
    return SAMPLE_PATH


def main():
    args = parse_args()

    spark = (
        SparkSession.builder
        .appName("ShoppingReviewPreprocessing")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    input_path = resolve_input_path(spark, args.input)
    print(f"\n데이터 로드 경로: {input_path}")

    df = (
        spark.read
        .option("header", "true")
        .option("multiLine", "true")
        .option("escape", '"')
        .csv(input_path)
    )

    # 타입 변환
    df = df.withColumn("rating", F.col("rating").cast(IntegerType()))

    # 품질 필터링 (결측치 제거, 평점 범위 검증, 중복 제거)
    df = df.dropna(subset=["review_id", "rating", "category", "review_text"])
    df = df.filter(F.col("rating").between(1, 5))
    df = df.dropDuplicates(["review_id"])

    # 파생 변수 생성
    df = df.withColumn("review_length", F.length(F.col("review_text")))

    df = df.withColumn(
        "sentiment",
        F.when(F.col("rating") >= 4, "Positive")
         .when(F.col("rating") <= 2, "Negative")
         .otherwise("Neutral"),
    )

    df = df.withColumn(
        "sentiment_binary",
        F.when(F.col("rating") >= 4, 1)
         .when(F.col("rating") <= 2, 0)
         .otherwise(None)
         .cast(IntegerType()),
    )

    total = df.count()
    print(f"전처리 완료: {total:,}건\n")

    print("전처리 후 평점 분포:")
    df.groupBy("rating").count().orderBy("rating").show()

    print("언어별 리뷰 수:")
    df.groupBy("language").count().orderBy(F.col("count").desc()).show()

    # 저장
    (
        df.coalesce(1)
        .write
        .mode("overwrite")
        .option("header", "true")
        .csv(args.output)
    )
    print(f"정제된 데이터 저장 완료: {args.output}")
    spark.stop()


if __name__ == "__main__":
    main()
