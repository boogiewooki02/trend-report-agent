from __future__ import annotations

import json
from pathlib import Path

from config import BASE_DIR, DEFAULT_TICKERS, SEARCH_QUERY, SUPPORTED_COMPANIES, today_kst
from data_agent_client import DataAgentClient
from report_generator import ReportGenerator
from schemas import TrendReportRequest, TrendReportResult


class TrendReportAgent:
    def __init__(
        self,
        data_client: DataAgentClient | None = None,
        generator: ReportGenerator | None = None,
    ) -> None:
        self.data_client = data_client
        self.retriever = None
        self.generator = generator or ReportGenerator()

    def run(self) -> Path:
        from pinecone_retriever import ReportRetriever

        as_of_date = today_kst()
        retriever = self.retriever or ReportRetriever()
        evidence = [
            retriever.retrieve(company, as_of_date)
            for company in [SUPPORTED_COMPANIES[ticker] for ticker in DEFAULT_TICKERS]
        ]
        report = self.generator.generate(evidence)

        output_dir = BASE_DIR / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"daily_briefing_{as_of_date.isoformat()}.md"
        output_path.write_text(report, encoding="utf-8")
        return output_path

    def run_trend_report(self, request: TrendReportRequest) -> TrendReportResult:
        client = self.data_client or DataAgentClient()
        as_of_date = request.as_of_date or today_kst().isoformat()
        query = request.query or f"{request.company} {request.sector} {SEARCH_QUERY}"

        context = client.build_trend_context(
            ticker=request.ticker,
            query=query,
            date_from=request.date_from,
            date_to=request.date_to,
        )
        evidence = self._build_evidence(context)
        cards = self.generator.generate_cards(request, context)
        self._patch_target_price_summary(cards, context)

        return TrendReportResult(
            ticker=request.ticker,
            company=request.company,
            as_of_date=as_of_date,
            cards=cards,
            evidence=evidence,
            data_status=self._build_data_status(context),
            raw_context=context,
        )

    def save_json(self, result: TrendReportResult) -> Path:
        output_dir = BASE_DIR / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"trend_report_{result.ticker}_{result.as_of_date}.json"
        output_path.write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output_path

    @staticmethod
    def _build_evidence(context: dict) -> list[dict]:
        evidence: list[dict] = []
        source_no = 0
        for key in ("report_documents", "news_documents", "macro_documents"):
            for item in context.get(key, {}).get("results", []):
                source_no += 1
                evidence.append({
                    "evidence_id": f"S{source_no}",
                    "chunk_id": item.get("chunk_id", ""),
                    "report_id": item.get("report_id", ""),
                    "ticker": item.get("ticker", ""),
                    "company": item.get("company", ""),
                    "document_type": item.get("document_type", ""),
                    "report_type": item.get("report_type"),
                    "title": item.get("title", ""),
                    "source": item.get("source", ""),
                    "author_org": item.get("author_org", ""),
                    "date": item.get("date", ""),
                    "page_start": item.get("page_start"),
                    "page_end": item.get("page_end"),
                    "score": item.get("score", 0.0),
                    "url": item.get("url", ""),
                    "content_preview": item.get("content", "")[:240],
                })
        return evidence

    @staticmethod
    def _build_data_status(context: dict) -> dict:
        return {
            "report_chunks": len(context.get("report_documents", {}).get("results", [])),
            "news_chunks": len(context.get("news_documents", {}).get("results", [])),
            "macro_summary_chunks": len(context.get("macro_documents", {}).get("results", [])),
            "report_metadata_count": context.get("report_metadata", {}).get("count", 0),
            "target_price_count": context.get("target_prices", {}).get("summary", {}).get("count", 0),
        }

    @staticmethod
    def _patch_target_price_summary(cards: dict, context: dict) -> None:
        target_summary = context.get("target_prices", {}).get("summary", {})
        target_card = cards.setdefault("target_price_trend", {})
        for key in ("avg_target_price", "min_target_price", "max_target_price"):
            if target_card.get(key) in (None, ""):
                target_card[key] = target_summary.get(key)

