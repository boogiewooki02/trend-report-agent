from __future__ import annotations

import os

from openai import OpenAI

from config import require_env
from prompts import SYSTEM_PROMPT, build_user_prompt
from schemas import CompanyEvidence


class ReportGenerator:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=require_env("UPSTAGE_API_KEY"),
            base_url="https://api.upstage.ai/v1",
        )
        self.model = os.getenv("TREND_REPORT_LLM_MODEL", "solar-pro3")

    def generate(self, evidence: list[CompanyEvidence]) -> str:
        evidence_text, sources = self._format_evidence(evidence)
        as_of_date = evidence[0].as_of_date.isoformat() if evidence else ""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(as_of_date, evidence_text),
                },
            ],
            temperature=0.2,
        )
        body = response.choices[0].message.content or ""
        header = self._build_status_header(evidence)
        return (
            f"# 증권사 리포트 데일리 브리핑\n\n"
            f"기준일: {as_of_date}\n\n"
            f"{header}\n\n{body.rstrip()}\n\n"
            f"## 참고 리포트\n\n" + "\n".join(sources) + "\n"
        )

    @staticmethod
    def _build_status_header(evidence: list[CompanyEvidence]) -> str:
        lines = ["## 자료 현황"]
        for item in evidence:
            if item.has_new_report:
                status = "최근 1일 신규 리포트 있음"
            elif item.is_fallback:
                status = (
                    f"신규 리포트 없음 · 최근 {item.lookback_days}일 자료 사용"
                    f" · 최신 발행일 {item.latest_report_date}"
                )
            else:
                status = "최근 30일 리포트 없음"
            lines.append(f"- **{item.company.name}**: {status}")
        return "\n".join(lines)

    def _format_evidence(
        self, evidence: list[CompanyEvidence]
    ) -> tuple[str, list[str]]:
        blocks: list[str] = []
        sources: list[str] = []
        source_records: dict[str, dict[str, object]] = {}
        source_no = 0

        for item in evidence:
            if item.lookback_days is None:
                blocks.append(f"### {item.company.name}\n자료 상태: 최근 30일 리포트 없음")
                continue

            status = "최근 1일 신규 리포트" if item.has_new_report else (
                f"최근 1일 신규 리포트 없음, 최근 {item.lookback_days}일 자료로 보완"
            )
            lines = [f"### {item.company.name}", f"자료 상태: {status}"]

            for chunk in item.chunks:
                source_no += 1
                label = f"S{source_no}"
                lines.append(
                    f"[{label}] 발행일={chunk.published_at} | 제목={chunk.title} | "
                    f"발행기관={chunk.author_org or chunk.source}\n{chunk.content[:1200]}"
                )
                record = source_records.setdefault(
                    chunk.report_id,
                    {"labels": [], "chunk": chunk},
                )
                record["labels"].append(label)
            blocks.append("\n\n".join(lines))

        for record in source_records.values():
            chunk = record["chunk"]
            labels = ", ".join(record["labels"])
            link = f"[{chunk.title}]({chunk.url})" if chunk.url else chunk.title
            sources.append(
                f"- [{labels}] {link} — {chunk.author_org or chunk.source}, "
                f"{chunk.published_at}"
            )

        return "\n\n".join(blocks), sources
