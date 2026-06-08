"""
Kafka 프로듀서 — 실시간 리뷰 수집 시뮬레이션

CSV 파일을 한 행씩 읽어 각 리뷰를 JSON 메시지로 Kafka 토픽에 전송합니다.
이커머스 플랫폼에서 실시간으로 리뷰가 유입되는 상황을 시뮬레이션합니다.

사전 준비:
  pip install kafka-python
  # Kafka 시작 (HDP Sandbox):
  #   /usr/hdp/current/kafka-broker/bin/kafka-server-start.sh \\
  #       /usr/hdp/current/kafka-broker/config/server.properties &
  # 토픽 생성:
  #   kafka-topics.sh --create --topic shopping-reviews \\
  #       --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

실행 방법:
  python3 src/streaming/kafka_producer.py
  python3 src/streaming/kafka_producer.py --input data/sample/shopping_reviews_sample.csv \\
                                           --delay 0.05
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

# 프로젝트 루트에서 직접 실행 시 config.py 경로 설정
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC


def parse_args():
    parser = argparse.ArgumentParser(description="Kafka 리뷰 스트림 프로듀서")
    parser.add_argument("--input", default="data/sample/shopping_reviews_sample.csv")
    parser.add_argument("--delay", type=float, default=0.1,
                        help="메시지 전송 간격(초), 기본값: 0.1")
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        from kafka import KafkaProducer
    except ImportError:
        print("오류: kafka-python이 설치되어 있지 않습니다. 실행: pip install kafka-python")
        sys.exit(1)

    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
            acks="all",
        )
    except Exception as exc:
        print(f"오류: Kafka 브로커({KAFKA_BOOTSTRAP_SERVERS}) 연결 실패: {exc}")
        print("Kafka가 실행 중인지 확인하거나 KAFKA_SERVERS 환경 변수를 설정하세요.")
        sys.exit(1)

    print(f"토픽 '{KAFKA_TOPIC}'으로 전송 시작 — 입력 파일: {args.input}")
    print(f"브로커: {KAFKA_BOOTSTRAP_SERVERS}  |  전송 간격: {args.delay}초")

    sent = 0
    with open(args.input, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            producer.send(KAFKA_TOPIC, value=dict(row))
            sent += 1
            if sent % 100 == 0:
                print(f"  {sent}건 전송 완료...")
            time.sleep(args.delay)

    producer.flush()
    producer.close()
    print(f"전송 완료. 총 {sent}건을 토픽 '{KAFKA_TOPIC}'에 전송했습니다.")


if __name__ == "__main__":
    main()
