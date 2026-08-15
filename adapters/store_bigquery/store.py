"""BigQuery TimeSeriesPort — load jobs for write (immediately queryable).

Streaming inserts buffer rows for seconds; load jobs complete before return so
reads do not flake. SDK import stays in this adapter (F55).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from core.config import AnalyticsSettings, LLMSettings
from core.tracking.models import Recommendation
from core.valuation.models import ValuationSnapshot


def _dec(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _opt_dec(value: Any) -> Decimal | None:
    if value is None:
        return None
    return _dec(value)


def _snapshot_row(snapshot: ValuationSnapshot) -> dict[str, Any]:
    return {
        "portfolio_id": snapshot.portfolio_id,
        "as_of": snapshot.as_of.isoformat(),
        "market_value": str(snapshot.market_value),
        "cash": str(snapshot.cash) if snapshot.cash is not None else None,
        "cost_basis": str(snapshot.cost_basis) if snapshot.cost_basis is not None else None,
        "twr": str(snapshot.twr) if snapshot.twr is not None else None,
        "mwr": str(snapshot.mwr) if snapshot.mwr is not None else None,
        "currency": snapshot.currency,
        "source": snapshot.source,
        "created_at": snapshot.created_at.isoformat(),
        "schema_version": snapshot.schema_version,
    }


def _rec_row(rec: Recommendation) -> dict[str, Any]:
    return {
        "rec_id": rec.rec_id,
        "user_id": rec.user_id,
        "portfolio_id": rec.portfolio_id,
        "ticker": rec.ticker,
        "market": rec.market,
        "action": rec.action,
        "rating": rec.rating,
        "price_at_issue": str(rec.price_at_issue),
        "price_as_of": rec.price_as_of.isoformat(),
        "currency": rec.currency,
        "issued_at": rec.issued_at.isoformat(),
        "note_ref": rec.note_ref,
        "model_attribution": rec.model_attribution,
        "schema_version": rec.schema_version,
    }


def _snapshot_from_row(row: Any) -> ValuationSnapshot:
    return ValuationSnapshot(
        portfolio_id=str(row["portfolio_id"]),
        as_of=row["as_of"],
        market_value=_dec(row["market_value"]),
        cash=_opt_dec(row["cash"]),
        cost_basis=_opt_dec(row["cost_basis"]),
        twr=_opt_dec(row["twr"]),
        mwr=_opt_dec(row["mwr"]),
        currency=str(row["currency"]),
        source=str(row["source"]),
        created_at=row["created_at"],
        schema_version=int(row["schema_version"]),
    )


def _rec_from_row(row: Any) -> Recommendation:
    portfolio_id = row["portfolio_id"]
    return Recommendation(
        rec_id=str(row["rec_id"]),
        user_id=str(row["user_id"]),
        portfolio_id=str(portfolio_id) if portfolio_id is not None else None,
        ticker=str(row["ticker"]),
        market=str(row["market"]),
        action=str(row["action"]),
        rating=str(row["rating"]),
        price_at_issue=_dec(row["price_at_issue"]),
        price_as_of=row["price_as_of"],
        currency=str(row["currency"]),
        issued_at=row["issued_at"],
        note_ref=str(row["note_ref"]) if row["note_ref"] is not None else None,
        model_attribution=(
            str(row["model_attribution"]) if row["model_attribution"] is not None else None
        ),
        schema_version=int(row["schema_version"]),
    )


class BigQueryTimeSeriesStore:
    """TimeSeriesPort backed by BigQuery load jobs + parameterized queries."""

    def __init__(
        self,
        *,
        project: str | None = None,
        dataset: str | None = None,
        location: str | None = None,
        client: Any | None = None,
    ) -> None:
        analytics = AnalyticsSettings()
        llm = LLMSettings()
        self._project = project or llm.gcp_project
        self._dataset = dataset or analytics.bq_dataset
        self._location = location or analytics.bq_location
        self._client = client

    def _bq(self) -> Any:
        if self._client is not None:
            return self._client
        from google.cloud import bigquery

        self._client = bigquery.Client(project=self._project, location=self._location)
        return self._client

    def _table(self, name: str) -> str:
        return f"{self._project}.{self._dataset}.{name}"

    def _append_rows(self, table: str, rows: list[dict[str, Any]]) -> None:
        from google.cloud import bigquery

        client = self._bq()
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
        job = client.load_table_from_json(rows, table, job_config=job_config)
        job.result()

    async def write_valuation_snapshot(self, snapshot: ValuationSnapshot) -> None:
        self._append_rows(self._table("valuation_snapshots"), [_snapshot_row(snapshot)])

    async def query_valuation_history(
        self,
        portfolio_id: str,
        since: datetime,
        until: datetime,
    ) -> list[ValuationSnapshot]:
        from google.cloud import bigquery

        sql = (
            f"SELECT * FROM `{self._table('valuation_snapshots')}` "
            "WHERE portfolio_id = @portfolio_id "
            "AND as_of >= @since AND as_of <= @until "
            "ORDER BY as_of ASC"
        )
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("portfolio_id", "STRING", portfolio_id),
                bigquery.ScalarQueryParameter("since", "TIMESTAMP", since),
                bigquery.ScalarQueryParameter("until", "TIMESTAMP", until),
            ]
        )
        rows = self._bq().query(sql, job_config=job_config).result()
        return [_snapshot_from_row(row) for row in rows]

    async def latest_valuation(self, portfolio_id: str) -> ValuationSnapshot | None:
        from google.cloud import bigquery

        sql = (
            f"SELECT * FROM `{self._table('valuation_snapshots')}` "
            "WHERE portfolio_id = @portfolio_id "
            "ORDER BY as_of DESC LIMIT 1"
        )
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("portfolio_id", "STRING", portfolio_id),
            ]
        )
        rows = list(self._bq().query(sql, job_config=job_config).result())
        if not rows:
            return None
        return _snapshot_from_row(rows[0])

    async def write_recommendation(self, rec: Recommendation) -> None:
        self._append_rows(self._table("recommendations"), [_rec_row(rec)])

    async def query_recommendations(
        self,
        user_id: str | None = None,
        ticker: str | None = None,
        since: datetime | None = None,
    ) -> list[Recommendation]:
        from google.cloud import bigquery

        clauses: list[str] = ["1 = 1"]
        params: list[Any] = []
        if user_id is not None:
            clauses.append("user_id = @user_id")
            params.append(bigquery.ScalarQueryParameter("user_id", "STRING", user_id))
        if ticker is not None:
            clauses.append("ticker = @ticker")
            params.append(bigquery.ScalarQueryParameter("ticker", "STRING", ticker))
        if since is not None:
            clauses.append("issued_at >= @since")
            params.append(bigquery.ScalarQueryParameter("since", "TIMESTAMP", since))
        sql = (
            f"SELECT * FROM `{self._table('recommendations')}` "
            f"WHERE {' AND '.join(clauses)} "
            "ORDER BY issued_at ASC"
        )
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        rows = self._bq().query(sql, job_config=job_config).result()
        return [_rec_from_row(row) for row in rows]
