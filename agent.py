from __future__ import annotations

from pathlib import Path

from config import BASE_DIR, PORTFOLIO, today_kst
from pinecone_retriever import ReportRetriever
from report_generator import ReportGenerator


class TrendReportAgent:
    def __init__(self) -> None:
        self.retriever = ReportRetriever()
        self.generator = ReportGenerator()

    def run(self) -> Path:
        as_of_date = today_kst()
        evidence = [
            self.retriever.retrieve(company, as_of_date)
            for company in PORTFOLIO
        ]
        report = self.generator.generate(evidence)

        output_dir = BASE_DIR / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"daily_briefing_{as_of_date.isoformat()}.md"
        output_path.write_text(report, encoding="utf-8")
        return output_path

