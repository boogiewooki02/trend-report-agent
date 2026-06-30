import logging

from agent import TrendReportAgent


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


if __name__ == "__main__":
    path = TrendReportAgent().run()
    print(f"브리핑 생성 완료: {path}")

