from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from config import (
    DATA_AGENT_DB_PATH,
    DATA_AGENT_PATH,
    MACRO_TOP_K,
    NEWS_TOP_K,
    REPORT_TOP_K,
    require_env,
)


class DataAgentClient:
    """Thin adapter around Agent B common functions.

    Agent D should consume Agent B through this adapter instead of reaching into
    Pinecone or SQLite directly.
    """

    def __init__(
        self,
        data_agent_path: Path = DATA_AGENT_PATH,
        db_path: Path = DATA_AGENT_DB_PATH,
    ) -> None:
        self.data_agent_path = Path(data_agent_path)
        self.db_path = Path(db_path)
        if not self.data_agent_path.exists():
            raise RuntimeError(f"Data Agent path not found: {self.data_agent_path}")

        sys.path.insert(0, str(self.data_agent_path))

        from storage.implementations import PineconeVectorDB, UpstageEmbeddingModel
        from storage.sqlite_db import SQLiteDB

        self.relational_db = SQLiteDB(str(self.db_path))
        self.embedding_model = UpstageEmbeddingModel(require_env("UPSTAGE_API_KEY"))
        self.vector_db = PineconeVectorDB(
            api_key=require_env("PINECONE_API_KEY"),
            index_name=require_env("PINECONE_INDEX"),
        )

    def build_trend_context(
        self,
        ticker: str,
        query: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any]:
        from functions.get_macro_data import get_macro_data
        from functions.get_price_data import get_price_data
        from functions.get_report_metadata import get_report_metadata
        from functions.get_target_price_data import get_target_price_data
        from functions.search_documents import search_documents

        report_documents = search_documents(
            query=query,
            ticker=ticker,
            date_from=date_from,
            date_to=date_to,
            document_type="report",
            top_k=REPORT_TOP_K,
            embedding_model=self.embedding_model,
            vector_db=self.vector_db,
        )
        news_documents = search_documents(
            query=query,
            ticker=ticker,
            date_from=date_from,
            date_to=date_to,
            document_type="news",
            top_k=NEWS_TOP_K,
            embedding_model=self.embedding_model,
            vector_db=self.vector_db,
        )
        macro_documents = search_documents(
            query=query,
            ticker="",
            date_from=date_from,
            date_to=date_to,
            document_type="macro_summary",
            top_k=MACRO_TOP_K,
            embedding_model=self.embedding_model,
            vector_db=self.vector_db,
        )

        metadata = get_report_metadata(
            ticker=ticker,
            date_from=date_from,
            date_to=date_to,
            relational_db=self.relational_db,
        )
        target_prices = get_target_price_data(
            ticker=ticker,
            date_from=date_from,
            date_to=date_to,
            relational_db=self.relational_db,
        )

        return {
            "ticker": ticker,
            "query": query,
            "date_from": date_from,
            "date_to": date_to,
            "report_documents": report_documents,
            "news_documents": news_documents,
            "macro_documents": macro_documents,
            "report_metadata": metadata,
            "target_prices": target_prices,
            "price_data": get_price_data(
                ticker=ticker,
                date_from=date_from,
                date_to=date_to,
                relational_db=self.relational_db,
            ),
            "macro_data": get_macro_data(
                date_from=date_from,
                date_to=date_to,
                relational_db=self.relational_db,
            ),
        }
