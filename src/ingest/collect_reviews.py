import argparse
import math
import os

import pandas as pd


REQUIRED_COLUMNS = [
    "review_id",
    "product_id",
    "reviewer_id",
    "stars",
    "review_body",
    "review_title",
    "language",
    "product_category",
]


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    df = df[REQUIRED_COLUMNS].copy()

    # 컬럼명 표준화
    df = df.rename(
        columns={
            "reviewer_id": "user_id",
            "stars": "rating",
            "review_body": "review_text",
            "product_category": "category",
        }
    )

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["review_id", "product_id", "user_id", "rating", "review_text", "category"])
    df = df.drop_duplicates(subset=["user_id", "product_id", "review_text"])

    df["rating"] = df["rating"].astype(int)
    df["review_text"] = df["review_text"].astype(str)
    df["review_title"] = df["review_title"].fillna("").astype(str)

    # 원본 데이터에 날짜 컬럼이 없어서, 수집일 기준 컬럼 생성
    df["review_date"] = "2026-06-01"

    return df[
        [
            "review_id",
            "product_id",
            "category",
            "rating",
            "review_text",
            "review_title",
            "review_date",
            "user_id",
            "language",
        ]
    ]


def split_and_save(df: pd.DataFrame, output_dir: str, part_size: int) -> int:
    os.makedirs(output_dir, exist_ok=True)

    total_parts = math.ceil(len(df) / part_size)

    for i in range(total_parts):
        start = i * part_size
        end = start + part_size
        part = df.iloc[start:end]

        output_path = os.path.join(output_dir, f"reviews_part_{i + 1:03d}.csv")
        part.to_csv(output_path, index=False)

    return total_parts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--raw-output", default="data/raw")
    parser.add_argument("--sample-output", default="data/sample/shopping_reviews_sample.csv")
    parser.add_argument("--part-size", type=int, default=50000)
    args = parser.parse_args()

    os.makedirs(args.raw_output, exist_ok=True)
    os.makedirs(os.path.dirname(args.sample_output), exist_ok=True)

    df = pd.read_csv(args.input)
    cleaned_df = clean_reviews(df)

    total_parts = split_and_save(cleaned_df, args.raw_output, args.part_size)
    cleaned_df.head(1000).to_csv(args.sample_output, index=False)

    print("데이터 수집 완료.")
    print(f"입력 파일: {args.input}")
    print(f"총 행 수: {len(cleaned_df)}")
    print(f"파트 수: {total_parts}")
    print(f"Raw 저장 경로: {args.raw_output}")
    print(f"샘플 저장 경로: {args.sample_output}")


if __name__ == "__main__":
    main()
