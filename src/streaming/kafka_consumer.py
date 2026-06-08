"""
Kafka 컨슈머 — 실시간 리뷰 집계

Kafka 토픽에서 리뷰 메시지를 읽어 카테고리별 리뷰 수와
평균 평점을 실시간으로 집계합니다. 실시간 대시보드를 시뮬레이션합니다.

실행 방법:
  python3 src/streaming/kafka_consumer.py
  python3 src/streaming/kafka_consumer.py --timeout 30
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

# 프로젝트 루트에서 직접 실행 시 config.py 경로 설정
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Kafka 리뷰 스트림 컨슈머")
    parser.add_argument("--timeout", type=int, default=10,
                        help="새 메시지가 없을 때 종료 대기 시간(초), 기본값: 10")
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        from kafka import KafkaConsumer
    except ImportError:
        print("오류: kafka-python이 설치되어 있지 않습니다. 실행: pip install kafka-python")
        sys.exit(1)

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        consumer_timeout_ms=args.timeout * 1000,
    )

    print(f"토픽 '{KAFKA_TOPIC}' 수신 시작 (타임아웃: {args.timeout}초)...")

    category_counts = defaultdict(int)
    rating_sums = defaultdict(float)
    total = 0

    for message in consumer:
        review = message.value
        cat = review.get("category", "unknown")
        try:
            rating = float(review.get("rating", 0))
        except (ValueError, TypeError):
            rating = 0.0

        category_counts[cat] += 1
        rating_sums[cat] += rating
        total += 1

        if total % 100 == 0:
            print(f"  {total}건 수신 완료...")

    consumer.close()

    print(f"\n총 수신 리뷰: {total}건")
    if total == 0:
        print("수신된 메시지가 없습니다. 프로듀서가 실행 중인지 확인하세요.")
        return

    print("\n상위 5개 카테고리:")
    for cat, cnt in sorted(category_counts.items(), key=lambda x: -x[1])[:5]:
        avg_r = rating_sums[cat] / cnt
        print(f"  {cat:<30} 리뷰 수={cnt:>4}  평균 평점={avg_r:.2f}")


if __name__ == "__main__":
    main()
