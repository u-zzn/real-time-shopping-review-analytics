import os

DATA_DIR = "data"
RAW_DIR = f"{DATA_DIR}/raw"
CLEANED_DIR = f"{DATA_DIR}/cleaned"
SAMPLE_PATH = f"{DATA_DIR}/sample/shopping_reviews_sample.csv"
OUTPUT_DIR = "analysis_results"

_user = os.environ.get("USER") or os.environ.get("USERNAME") or "root"
HDFS_BASE = f"/user/{_user}/shopping_reviews"
HDFS_RAW_DIR = f"{HDFS_BASE}/raw"
HDFS_CLEANED_DIR = f"{HDFS_BASE}/cleaned"

SCHEMA_COLUMNS = [
    "review_id", "product_id", "category", "rating",
    "review_text", "review_title", "review_date", "user_id", "language",
]

ML_LABEL = "sentiment_binary"
ML_FEATURES = ["cat_idx", "lang_idx", "review_length"]
ML_FEATURE_LABELS = {
    "cat_idx": "Category",
    "lang_idx": "Language",
    "review_length": "Review Length",
}

KAFKA_TOPIC = "shopping-reviews"
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_SERVERS", "localhost:9092")
