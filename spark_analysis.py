"""
쇼핑 리뷰 분석 — Spark SQL + Spark MLlib

7가지 SQL 분석 질문과 로지스틱 회귀 모델을 실행합니다.
결과(CSV)는 analysis_results/ 폴더에 저장됩니다.

실행 방법:
  로컬 : python3 spark_analysis.py
          python3 spark_analysis.py --input data/cleaned
  HDP  : spark-submit spark_analysis.py \\
              --input hdfs:///user/$USER/shopping_reviews/cleaned
"""

import argparse
import glob as _glob
import math
import os
from pathlib import Path

from config import OUTPUT_DIR, SAMPLE_PATH

Path(OUTPUT_DIR).mkdir(exist_ok=True)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None,
                        help="정제된 CSV 디렉토리 경로 (또는 단일 CSV). "
                             "미지정 시 data/cleaned → 없으면 샘플 데이터 사용.")
    return parser.parse_args()


def resolve_input(path):
    if path:
        if path.startswith("hdfs"):
            return f"{path.rstrip('/')}/*.csv"
        if path.endswith(".csv"):
            return path
        matched = _glob.glob(f"{path}/*.csv")
        return f"{path}/*.csv" if matched else SAMPLE_PATH

    cleaned_files = _glob.glob("data/cleaned/*.csv")
    if cleaned_files:
        return "data/cleaned/*.csv"
    return SAMPLE_PATH


def run_sql_analyses(spark, df):
    df.createOrReplaceTempView("reviews")
    total = df.count()
    print(f"총 리뷰 수: {total:,}건\n")

    queries = [
        ("analysis_rating_distribution", "[Q1] 평점 분포", """
            SELECT rating, COUNT(*) AS review_count
            FROM reviews
            GROUP BY rating
            ORDER BY rating
        """),
        ("analysis_category_distribution", "[Q2] 리뷰 수 상위 10개 카테고리", """
            SELECT category, COUNT(*) AS review_count
            FROM reviews
            GROUP BY category
            ORDER BY review_count DESC
            LIMIT 10
        """),
        ("analysis_avg_rating_by_category", "[Q3] 카테고리별 평균 평점", """
            SELECT
                category,
                ROUND(AVG(CAST(rating AS DOUBLE)), 2) AS avg_rating,
                COUNT(*) AS review_count
            FROM reviews
            GROUP BY category
            HAVING COUNT(*) >= 5
            ORDER BY avg_rating DESC
        """),
        ("analysis_sentiment_distribution", "[Q4] 감성 분포 (긍정/중립/부정)", """
            SELECT
                CASE
                    WHEN rating >= 4 THEN 'Positive'
                    WHEN rating <= 2 THEN 'Negative'
                    ELSE 'Neutral'
                END AS sentiment,
                COUNT(*) AS review_count
            FROM reviews
            GROUP BY
                CASE
                    WHEN rating >= 4 THEN 'Positive'
                    WHEN rating <= 2 THEN 'Negative'
                    ELSE 'Neutral'
                END
            ORDER BY review_count DESC
        """),
        ("analysis_language_distribution", "[Q5] 언어별 리뷰 수", """
            SELECT language, COUNT(*) AS review_count
            FROM reviews
            WHERE language RLIKE '^[a-z]{2}$'
            GROUP BY language
            ORDER BY review_count DESC
        """),
        ("analysis_negative_rate_by_category", "[Q6] 카테고리별 부정 리뷰 비율 (상위 10개)", """
            SELECT
                category,
                COUNT(*) AS total_reviews,
                SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) AS negative_count,
                ROUND(
                    SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1
                ) AS negative_rate_pct
            FROM reviews
            GROUP BY category
            HAVING COUNT(*) >= 5
            ORDER BY total_reviews DESC
            LIMIT 10
        """),
        ("analysis_category_language_heatmap", "[Q7] 카테고리 × 언어 교차 분석 (평균 평점)", """
            SELECT
                category,
                language,
                ROUND(AVG(CAST(rating AS DOUBLE)), 2) AS avg_rating,
                COUNT(*) AS review_count
            FROM reviews
            WHERE language RLIKE '^[a-z]{2}$'
            GROUP BY category, language
            HAVING COUNT(*) >= 3
            ORDER BY category, language
        """),
    ]

    for csv_name, label, sql in queries:
        print(label)
        result = spark.sql(sql)
        result.show()
        result.toPandas().to_csv(f"{OUTPUT_DIR}/{csv_name}.csv", index=False)


def run_ml(spark, df):
    """
    로지스틱 회귀 모델: review_length, category, language로 긍정/부정 감성 예측.

    중립 리뷰(rating=3)는 이진 분류에서 제외합니다.
    파이프라인: StringIndexer × 2 → VectorAssembler → LogisticRegression
    """
    from pyspark.ml import Pipeline
    from pyspark.ml.classification import LogisticRegression
    from pyspark.ml.evaluation import BinaryClassificationEvaluator
    from pyspark.ml.feature import StringIndexer, VectorAssembler
    from pyspark.sql import functions as F

    print("[ML] 로지스틱 회귀 — 감성 예측 모델")

    ml_df = (
        df.filter(F.col("rating") != 3)
        .withColumn("label", F.when(F.col("rating") >= 4, 1.0).otherwise(0.0))
        .withColumn("review_length",
                    F.length(F.col("review_text")).cast("double"))
        .dropna(subset=["label", "review_length", "category", "language"])
    )

    total = ml_df.count()
    if total < 50:
        print(f"  학습 데이터 부족 ({total}건) — ML 분석을 건너뜁니다.")
        return

    print(f"  학습 데이터: {total:,}건")

    cat_idx = StringIndexer(inputCol="category", outputCol="cat_idx",
                            handleInvalid="keep")
    lang_idx = StringIndexer(inputCol="language", outputCol="lang_idx",
                             handleInvalid="keep")
    assembler = VectorAssembler(
        inputCols=["cat_idx", "lang_idx", "review_length"],
        outputCol="features",
        handleInvalid="skip",
    )
    lr = LogisticRegression(
        featuresCol="features", labelCol="label",
        maxIter=20, regParam=0.01,
    )

    pipeline = Pipeline(stages=[cat_idx, lang_idx, assembler, lr])
    train_df, test_df = ml_df.randomSplit([0.8, 0.2], seed=42)
    model = pipeline.fit(train_df)
    predictions = model.transform(test_df)

    evaluator = BinaryClassificationEvaluator(
        labelCol="label", metricName="areaUnderROC"
    )
    auc = evaluator.evaluate(predictions)
    test_count = predictions.count()
    correct = predictions.filter(F.col("prediction") == F.col("label")).count()
    accuracy = correct / test_count if test_count else 0.0

    print(f"  AUC     : {auc:.4f}")
    print(f"  정확도  : {accuracy:.4f}")

    import pandas as pd
    metrics = pd.DataFrame([
        {"metric": "training_rows", "value": total},
        {"metric": "test_rows",     "value": test_count},
        {"metric": "auc",           "value": round(auc, 4)},
        {"metric": "accuracy",      "value": round(accuracy, 4)},
    ])
    metrics.to_csv(f"{OUTPUT_DIR}/analysis_model_metrics.csv", index=False)

    lr_model = model.stages[-1]
    feature_names = ["Category (Index)", "Language (Index)", "Review Length"]
    coef_df = pd.DataFrame({
        "feature":     feature_names,
        "coefficient": list(lr_model.coefficients),
        "odds_ratio":  [math.exp(c) for c in lr_model.coefficients],
    }).sort_values("coefficient", ascending=False)
    coef_df.to_csv(f"{OUTPUT_DIR}/analysis_model_coefficients.csv", index=False)
    print("  저장 완료: analysis_model_metrics.csv, analysis_model_coefficients.csv")


def main():
    args = parse_args()
    data_path = resolve_input(args.input)

    try:
        from pyspark.sql import SparkSession
        from pyspark.sql import functions as F

        spark = (
            SparkSession.builder
            .appName("ShoppingReviewAnalysis")
            .getOrCreate()
        )
        spark.sparkContext.setLogLevel("WARN")

        print(f"\n데이터 경로: {data_path}")
        df = (
            spark.read
            .option("header", "true")
            .option("inferSchema", "true")
            .option("multiLine", "true")
            .option("escape", '"')
            .csv(data_path)
        )
        df = (
            df.dropna(subset=["review_id", "rating", "category"])
            .withColumn("rating", F.col("rating").cast("int"))
        )

        run_sql_analyses(spark, df)
        run_ml(spark, df)
        spark.stop()

    except ModuleNotFoundError:
        # pyspark 미설치 시 pandas로 SQL 분석만 수행 (ML 제외)
        import pandas as pd

        print(f"\n[pandas 대체 실행] pyspark 없음 — SQL 분석만 수행합니다.")
        print(f"데이터 경로: {data_path if not data_path.endswith('*.csv') else SAMPLE_PATH}")

        src = SAMPLE_PATH if data_path.endswith("*.csv") else data_path
        df = pd.read_csv(src).dropna(subset=["review_id", "rating", "category"])
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").astype("Int64")
        df["sentiment"] = df["rating"].apply(
            lambda r: "Positive" if r >= 4 else ("Negative" if r <= 2 else "Neutral")
        )
        df["review_length"] = df["review_text"].astype(str).str.len()
        print(f"총 {len(df):,}건 로드 완료\n")

        pd.Series(df["rating"].value_counts().sort_index()).rename_axis("rating").reset_index(
            name="review_count").to_csv(f"{OUTPUT_DIR}/analysis_rating_distribution.csv", index=False)

        df["category"].value_counts().head(10).rename_axis("category").reset_index(
            name="review_count").to_csv(f"{OUTPUT_DIR}/analysis_category_distribution.csv", index=False)

        (df.groupby("category")["rating"]
           .agg(avg_rating="mean", review_count="count")
           .query("review_count >= 5")
           .assign(avg_rating=lambda x: x["avg_rating"].round(2))
           .sort_values("avg_rating", ascending=False)
           .reset_index()
           .to_csv(f"{OUTPUT_DIR}/analysis_avg_rating_by_category.csv", index=False))

        df["sentiment"].value_counts().rename_axis("sentiment").reset_index(
            name="review_count").to_csv(f"{OUTPUT_DIR}/analysis_sentiment_distribution.csv", index=False)

        df["language"].value_counts().rename_axis("language").reset_index(
            name="review_count").to_csv(f"{OUTPUT_DIR}/analysis_language_distribution.csv", index=False)

        grp = df.groupby("category").agg(
            total_reviews=("rating", "count"),
            negative_count=("sentiment", lambda x: (x == "Negative").sum()),
        ).reset_index().query("total_reviews >= 5")
        grp["negative_rate_pct"] = (grp["negative_count"] / grp["total_reviews"] * 100).round(1)
        (grp.sort_values("total_reviews", ascending=False)
            .head(10)
            .to_csv(f"{OUTPUT_DIR}/analysis_negative_rate_by_category.csv", index=False))

        (df.groupby(["category", "language"])["rating"]
           .agg(avg_rating="mean", review_count="count")
           .reset_index()
           .query("review_count >= 3")
           .assign(avg_rating=lambda x: x["avg_rating"].round(2))
           .to_csv(f"{OUTPUT_DIR}/analysis_category_language_heatmap.csv", index=False))

        print("SQL 분석 결과 저장 완료 (ML은 pyspark 설치 후 실행 가능).")
        print("pyspark 설치: pip install pyspark")

    print(f"\n모든 결과가 {OUTPUT_DIR}/에 저장되었습니다.")


if __name__ == "__main__":
    main()
