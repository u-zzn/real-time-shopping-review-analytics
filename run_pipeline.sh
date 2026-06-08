#!/usr/bin/env bash
# Real-Time Shopping Review Analytics — 전체 파이프라인 실행 스크립트
#
# 실행 단계:
#   1. 데이터 확인
#   2. HDFS 업로드       (HDP 전용)
#   3. Spark 전처리      (data_preprocessing.py)
#   4. Spark SQL + ML   (spark_analysis.py)
#   5. 시각화            (visualize.py)
#   6. 결과 요약
#
# 실행 방법:
#   로컬      : bash run_pipeline.sh
#   HDP Sandbox: USE_HDFS=1 bash run_pipeline.sh
#   HDP + Python 직접 지정: USE_HDFS=1 PYTHON_BIN=/usr/bin/python3.6 bash run_pipeline.sh

set -euo pipefail

USE_HDFS="${USE_HDFS:-0}"
OUTPUT_DIR="analysis_results"
SAMPLE_PATH="data/sample/shopping_reviews_sample.csv"

# Python 3.6 이상 탐색
find_python() {
    for cmd in "${PYTHON_BIN:-}" python3 python3.6 python36 python; do
        [ -n "$cmd" ] || continue
        if command -v "$cmd" >/dev/null 2>&1; then
            if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3,6) else 1)" 2>/dev/null; then
                echo "$cmd"; return
            fi
        fi
    done
    echo "오류: Python 3.6 이상이 필요합니다." >&2
    echo "HDP 힌트: PYTHON_BIN=/usr/bin/python3.6 bash run_pipeline.sh" >&2
    exit 1
}

PYTHON="$(find_python)"
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"
export PYSPARK_PYTHON="${PYSPARK_PYTHON:-$PYTHON}"
export PYSPARK_DRIVER_PYTHON="${PYSPARK_DRIVER_PYTHON:-$PYTHON}"

divider() { printf '\n%s\n  %s\n%s\n' "$(printf '─%.0s' {1..54})" "$1" "$(printf '─%.0s' {1..54})"; }

divider "Real-Time Shopping Review Analytics Pipeline"
echo "  Python : $PYTHON"
echo "  Mode   : $([ "$USE_HDFS" = "1" ] && echo 'HDP Sandbox (HDFS)' || echo '로컬')"
echo "  Date   : $(date '+%Y-%m-%d %H:%M:%S')"
mkdir -p "$OUTPUT_DIR"

# STEP 1: 데이터 확인
divider "STEP 1: 데이터 확인"
if [ -d "data/raw" ] && ls data/raw/*.csv &>/dev/null 2>&1; then
    RAW_SIZE=$(du -sh data/raw 2>/dev/null | cut -f1)
    PART_CNT=$(ls data/raw/*.csv 2>/dev/null | wc -l | tr -d ' ')
    echo "  원본 데이터 : $RAW_SIZE  ($PART_CNT 파트 파일)"
    INPUT_PATH="data/raw"
else
    echo "  원본 데이터 : 없음 (gitignore 처리) — 샘플 데이터 사용"
    INPUT_PATH="$SAMPLE_PATH"
fi
echo "  샘플 파일   : $SAMPLE_PATH  ($(wc -l < "$SAMPLE_PATH" | tr -d ' ')줄)"

# STEP 2: HDFS 업로드
divider "STEP 2: HDFS 저장"
if [ "$USE_HDFS" = "1" ]; then
    HDFS_URI="$(hdfs getconf -confKey fs.defaultFS)"
    HDFS_URI="${HDFS_URI%/}"
    USER="${USER:-root}"
    HDFS_RAW="${HDFS_URI}/user/${USER}/shopping_reviews/raw"
    HDFS_CLEANED="${HDFS_URI}/user/${USER}/shopping_reviews/cleaned"

    echo "  HDFS URI : $HDFS_URI"
    hdfs dfs -mkdir -p "$HDFS_RAW"

    if [ "$INPUT_PATH" = "data/raw" ]; then
        hdfs dfs -put -f data/raw/*.csv "$HDFS_RAW/"
        echo "  업로드 완료 : data/raw/*.csv → $HDFS_RAW"
    else
        hdfs dfs -put -f "$SAMPLE_PATH" "$HDFS_RAW/"
        echo "  업로드 완료 : $SAMPLE_PATH → $HDFS_RAW"
    fi
    hdfs dfs -ls "$HDFS_RAW" | tail -5
    PREPROCESS_INPUT="$HDFS_RAW"
    PREPROCESS_OUTPUT="$HDFS_CLEANED"
    ANALYSIS_INPUT="$HDFS_CLEANED"
else
    echo "  건너뜀 (로컬 모드)"
    echo "  HDP 실행: USE_HDFS=1 bash run_pipeline.sh"
    PREPROCESS_INPUT="$INPUT_PATH"
    PREPROCESS_OUTPUT="data/cleaned"
    ANALYSIS_INPUT="data/cleaned"
fi

# STEP 3: Spark 전처리
divider "STEP 3: Spark 전처리 (DataFrame)"
if [ "$USE_HDFS" = "1" ] && command -v spark-submit &>/dev/null; then
    # --py-files config.py 로 모든 Spark 워커에서 config.py 사용 가능하게 설정
    spark-submit --py-files config.py data_preprocessing.py \
        --input  "$PREPROCESS_INPUT" \
        --output "$PREPROCESS_OUTPUT"
else
    "$PYTHON" data_preprocessing.py \
        --input  "$PREPROCESS_INPUT" \
        --output "$PREPROCESS_OUTPUT"
fi

# STEP 4: Spark SQL + MLlib 분석
divider "STEP 4: Spark SQL + MLlib 분석"
if [ "$USE_HDFS" = "1" ] && command -v spark-submit &>/dev/null; then
    spark-submit --py-files config.py spark_analysis.py --input "$ANALYSIS_INPUT"
else
    "$PYTHON" spark_analysis.py --input "$ANALYSIS_INPUT"
fi

# STEP 5: 시각화
divider "STEP 5: 시각화 (Matplotlib + Seaborn)"
"$PYTHON" visualize.py

# STEP 6: 결과 요약
divider "STEP 6: 결과 요약"
echo "  CSV 파일:"
ls -lh "$OUTPUT_DIR"/*.csv 2>/dev/null | awk '{printf "    %-50s %s\n", $NF, $5}'
echo ""
echo "  PNG 그래프:"
ls -lh "$OUTPUT_DIR"/*.png 2>/dev/null | awk '{printf "    %-50s %s\n", $NF, $5}'

divider "파이프라인 완료 — 결과 저장 위치: $OUTPUT_DIR/"
