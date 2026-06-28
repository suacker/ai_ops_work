#!/usr/bin/env python3
"""
Query Firebase app crash metrics from a linked GA4 property.

This script uses the Google Analytics Data API to query:
- crashFreeUsersRate
- crashAffectedUsers
- totalUsers

It can return either:
- a summary for the whole date range
- a daily time series grouped by date

Prerequisites:
1. Firebase project is linked to a GA4 property.
2. Firebase Crashlytics is enabled.
3. Google Analytics Data API is enabled in Google Cloud.
4. The service account has at least Viewer access to the GA4 property.

Install:
    pip install google-analytics-data google-auth

Examples:
    python scripts/ga4_crash_rate_query.py \
      --property-id 123456789 \
      --start-date 2026-04-20 \
      --end-date 2026-04-26 \
      --platform Android

    python scripts/ga4_crash_rate_query.py \
      --property-id 123456789 \
      --start-date 2026-04-20 \
      --end-date 2026-04-26 \
      --platform iOS \
      --daily \
      --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from typing import Iterable, Optional

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Filter,
    FilterExpression,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account


SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


@dataclass
class CrashRateRow:
    date: Optional[str]
    platform: Optional[str]
    stream_id: Optional[str]
    crash_free_users_rate: float
    crash_free_users_rate_pct: float
    crash_rate: float
    crash_rate_pct: float
    crash_affected_users: int
    total_users: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query Firebase app crash rate from a linked GA4 property."
    )
    parser.add_argument(
        "--property-id",
        required=True,
        help="GA4 property ID, for example: 123456789",
    )
    parser.add_argument(
        "--start-date",
        required=True,
        help="Start date, for example: 2026-04-20 or 7daysAgo",
    )
    parser.add_argument(
        "--end-date",
        required=True,
        help="End date, for example: 2026-04-26 or yesterday",
    )
    parser.add_argument(
        "--platform",
        help="Optional platform filter, usually Android / iOS / web",
    )
    parser.add_argument(
        "--stream-id",
        help="Optional GA4 streamId filter. Recommended if one property contains multiple apps.",
    )
    parser.add_argument(
        "--credentials",
        help=(
            "Path to Google service account JSON key. "
            "If omitted, GOOGLE_APPLICATION_CREDENTIALS is used."
        ),
    )
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Group results by date.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of a text table.",
    )
    return parser.parse_args()


def build_client(credentials_path: Optional[str]) -> BetaAnalyticsDataClient:
    if credentials_path:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        return BetaAnalyticsDataClient(credentials=credentials)

    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path:
        credentials = service_account.Credentials.from_service_account_file(
            env_path, scopes=SCOPES
        )
        return BetaAnalyticsDataClient(credentials=credentials)

    raise RuntimeError(
        "Missing credentials. Use --credentials /path/to/key.json "
        "or set GOOGLE_APPLICATION_CREDENTIALS."
    )


def build_dimension_filter(
    platform: Optional[str], stream_id: Optional[str]
) -> Optional[FilterExpression]:
    expressions: list[FilterExpression] = []

    if platform:
        expressions.append(
            FilterExpression(
                filter=Filter(
                    field_name="platform",
                    string_filter=Filter.StringFilter(
                        value=platform,
                        match_type=Filter.StringFilter.MatchType.EXACT,
                    ),
                )
            )
        )

    if stream_id:
        expressions.append(
            FilterExpression(
                filter=Filter(
                    field_name="streamId",
                    string_filter=Filter.StringFilter(
                        value=stream_id,
                        match_type=Filter.StringFilter.MatchType.EXACT,
                    ),
                )
            )
        )

    if not expressions:
        return None

    if len(expressions) == 1:
        return expressions[0]

    return FilterExpression(
        and_group=FilterExpression.FilterExpressionList(expressions=expressions)
    )


def run_query(
    client: BetaAnalyticsDataClient,
    property_id: str,
    start_date: str,
    end_date: str,
    platform: Optional[str] = None,
    stream_id: Optional[str] = None,
    daily: bool = False,
) -> list[CrashRateRow]:
    dimensions: list[Dimension] = []

    if daily:
        dimensions.append(Dimension(name="date"))
    if platform:
        dimensions.append(Dimension(name="platform"))
    if stream_id:
        dimensions.append(Dimension(name="streamId"))

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=dimensions,
        metrics=[
            Metric(name="crashFreeUsersRate"),
            Metric(name="crashAffectedUsers"),
            Metric(name="totalUsers"),
        ],
        dimension_filter=build_dimension_filter(platform=platform, stream_id=stream_id),
        keep_empty_rows=True,
    )

    response = client.run_report(request)
    rows: list[CrashRateRow] = []

    for row in response.rows:
        dimension_values = [value.value for value in row.dimension_values]
        metric_values = [value.value for value in row.metric_values]

        index = 0
        date_value: Optional[str] = None
        platform_value: Optional[str] = None
        stream_id_value: Optional[str] = None

        if daily:
            date_value = dimension_values[index]
            index += 1
        if platform:
            platform_value = dimension_values[index]
            index += 1
        if stream_id:
            stream_id_value = dimension_values[index]

        crash_free_users_rate = float(metric_values[0])
        crash_rate = 1.0 - crash_free_users_rate

        rows.append(
            CrashRateRow(
                date=date_value,
                platform=platform_value,
                stream_id=stream_id_value,
                crash_free_users_rate=round(crash_free_users_rate, 6),
                crash_free_users_rate_pct=round(crash_free_users_rate * 100, 2),
                crash_rate=round(crash_rate, 6),
                crash_rate_pct=round(crash_rate * 100, 2),
                crash_affected_users=int(metric_values[1]),
                total_users=int(metric_values[2]),
            )
        )

    return rows


def to_json(rows: Iterable[CrashRateRow]) -> str:
    return json.dumps([asdict(row) for row in rows], ensure_ascii=False, indent=2)


def format_table(rows: list[CrashRateRow]) -> str:
    if not rows:
        return "No data returned."

    headers = [
        "date",
        "platform",
        "stream_id",
        "crash_free_users_rate_pct",
        "crash_rate_pct",
        "crash_affected_users",
        "total_users",
    ]

    raw_rows = [
        [
            row.date or "-",
            row.platform or "-",
            row.stream_id or "-",
            f"{row.crash_free_users_rate_pct:.2f}%",
            f"{row.crash_rate_pct:.2f}%",
            str(row.crash_affected_users),
            str(row.total_users),
        ]
        for row in rows
    ]

    widths = [
        max(len(header), *(len(record[i]) for record in raw_rows))
        for i, header in enumerate(headers)
    ]

    def fmt_line(values: list[str]) -> str:
        return " | ".join(value.ljust(widths[i]) for i, value in enumerate(values))

    parts = [
        fmt_line(headers),
        "-+-".join("-" * width for width in widths),
    ]
    parts.extend(fmt_line(record) for record in raw_rows)
    return "\n".join(parts)


def main() -> int:
    args = parse_args()

    try:
        client = build_client(args.credentials)
        rows = run_query(
            client=client,
            property_id=args.property_id,
            start_date=args.start_date,
            end_date=args.end_date,
            platform=args.platform,
            stream_id=args.stream_id,
            daily=args.daily,
        )
    except Exception as exc:  # pragma: no cover
        print(f"Query failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(to_json(rows))
    else:
        print(format_table(rows))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
