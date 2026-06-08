# Dataset Documentation

## Overview

| Item | Value |
|---|---|
| Source | Amazon Multilingual Product Reviews (Kaggle) |
| Total rows | ~1,200,000 |
| Total size | ~335 MB (24 part files) |
| Languages | German, English, Spanish, French, Japanese, Chinese |
| Rating range | 1 – 5 stars |

## Schema

| Column | Type | Description |
|---|---|---|
| `review_id` | string | Unique review identifier |
| `product_id` | string | Product identifier |
| `category` | string | Product category (e.g. `home`, `wireless`, `book`) |
| `rating` | int | Star rating 1–5 |
| `review_text` | string | Full review body |
| `review_title` | string | Review headline |
| `review_date` | date | Review submission date (YYYY-MM-DD) |
| `user_id` | string | Reviewer identifier |
| `language` | string | ISO 639-1 language code |

## Directory Structure

```
data/
├── sample/
│   └── shopping_reviews_sample.csv   ← 1,000 rows, committed to GitHub
│                                       (stratified: 200 rows per rating 1–5)
├── raw/                               ← 335 MB, 24 part files, GITIGNORED
│   ├── reviews_part_001.csv
│   ├── reviews_part_002.csv
│   └── ...  (reviews_part_024.csv)
└── original/                          ← Source CSVs before cleaning, GITIGNORED
```

## How to Regenerate Raw Data

Download the source CSV from Kaggle, then run:

```bash
python3 src/ingest/collect_reviews.py \
    --input <path-to-source.csv> \
    --raw-output data/raw \
    --sample-output data/sample/shopping_reviews_sample.csv \
    --part-size 50000
```

`collect_reviews.py` cleans and standardizes column names, removes
duplicates and null-critical rows, and splits output into 50,000-row
part files.

## GitHub Policy

- `data/raw/` and `data/original/` are excluded via `.gitignore`.
- Only `data/sample/shopping_reviews_sample.csv` (1,000 rows) is committed.
- `analysis_results/` CSV and PNG files are committed as submission evidence.
