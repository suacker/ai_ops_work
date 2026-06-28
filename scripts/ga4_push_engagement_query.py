#!/usr/bin/env python3
"""
Query Firebase push engagement metrics from a linked GA4 property.

This script queries push-related Analytics events such as:
- notification_open
- notification_receive
- notification_dismiss
- notification_foreground

It uses the Google Analytics Data API and returns aggregated results.

Prerequisites:
1. Firebase project is linked to a GA4 property.
2. Firebase Analytics is enabled in the app.
3. Google Analytics Data API v1 is enabled in Google Cloud.
4. The service account has at least Viewer access to the GA4 property.

Install:
    pip install google-analytics-data google-auth

Examples:
    python scripts/ga4_push_engagement_query.py \
      --property-id 123456789 \
      --start-date 2026-04-20 \
      --end-date 2026-04-26 \
      --event-name notification_open

    python scripts/ga4_push_engagement_query.py \
      --property-id 123456789 \
      --start-date 2026-04-20 \
      --end-date 2026-04-26 \
      --event-name notification_receive \
      --platform Android \
      --daily \
      --json

    python scripts/ga4_push_engagement_query.py \
      --property-id 123456789 \
      --start-date 2026-04-20 \
      --end-date 2026-04-26 \
      --compare-open-rate \
      --platform iOS
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from typing import Optional

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
SUPPORTED_EVENTS = {
    "notification_open",
    "notification_receive",
    "notification_dismiss",
    "notification_foreground",
}


@dataclass
class PushEventRow:
    event_name: str
    date: Optional[str]
    platform: Optional[str]
    stream_id: Optional[str]
    event_count: int
    total_users: int
    event_count_per_user: float


@dataclass
class PushOpenRateRow:
    date: Optional[str]
    platform: Optional[str]
    stream_id: Optional[str]
    notification_receive_count: int
    notification_open_count: int
    open_rate_pct: Optional[float]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query Firebase push engagement data from a linked GA4 property."
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
        "--event-name",
        default="notification_open",
        help=(
            "Push event name to query. Supported: "
            "notification_open, notification_receive, "
            "notification_dismiss, notification_foreground"
        ),
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
    parser.add_argument(
        "--compare-open-rate",
        action="store_true",
        help=(
            "Query both notification_receive and notification_open, "
            "then compute open rate = open / receive."
        ),
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
    event_name: str,
    platform: Optional[str],
    stream_id: Optional[str],
) -> FilterExpression:
    expressions: list[FilterExpression] = [
        FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(
                    value=event_name,
                    match_type=Filter.StringFilter.MatchType.EXACT,
                ),
            )
        )
    ]

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

    if len(expressions) == 1:
        return expressions[0]

    return FilterExpression(
        and_group=FilterExpression.FilterExpressionList(expressions=expressions)
    )


def build_dimensions(
    daily: bool,
    platform: Optional[str],
    stream_id: Optional[str],
) -> list[Dimension]:
    dimensions: list[Dimension] = []

    if daily:
        dimensions.append(Dimension(name="date"))
    if platform:
        dimensions.append(Dimension(name="platform"))
    if stream_id:
        dimensions.append(Dimension(name="streamId"))

    return dimensions


def run_event_query(
    client: BetaAnalyticsDataClient,
    property_id: str,
    start_date: str,
    end_date: str,
    event_name: str,
    platform: Optional[str],
    stream_id: Optional[str],
    daily: bool,
) -> list[PushEventRow]:
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=build_dimensions(daily=daily, platform=platform, stream_id=stream_id),
        metrics=[
            Metric(name="eventCount"),
            Metric(name="totalUsers"),
            Metric(name="eventCountPerUser"),
        ],
        dimension_filter=build_dimension_filter(
            event_name=event_name,
            platform=platform,
            stream_id=stream_id,
        ),
        keep_empty_rows=True,
    )

    response = client.run_report(request)
    rows: list[PushEventRow] = []

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

        rows.append(
            PushEventRow(
                event_name=event_name,
                date=date_value,
                platform=platform_value,
                stream_id=stream_id_value,
                event_count=int(metric_values[0]),
                total_users=int(metric_values[1]),
                event_count_per_user=round(float(metric_values[2]), 4),
            )
        )

    return rows


def merge_open_rate(
    receive_rows: list[PushEventRow],
    open_rows: list[PushEventRow],
) -> list[PushOpenRateRow]:
    receive_map = {
        (row.date, row.platform, row.stream_id): row
        for row in receive_rows
    }
    open_map = {
        (row.date, row.platform, row.stream_id): row
        for row in open_rows
    }

    keys = sorted(set(receive_map) | set(open_map))
    result: list[PushOpenRateRow] = []

    for key in keys:
        receive_count = receive_map.get(key).event_count if key in receive_map else 0
        open_count = open_map.get(key).event_count if key in open_map else 0
        open_rate_pct = None
        if receive_count > 0:
            open_rate_pct = round(open_count / receive_count * 100, 2)

        result.append(
            PushOpenRateRow(
                date=key[0],
                platform=key[1],
                stream_id=key[2],
                notification_receive_count=receive_count,
                notification_open_count=open_count,
                open_rate_pct=open_rate_pct,
            )
        )

    return result


def format_event_rows(rows: list[PushEventRow]) -> str:
    if not rows:
        return "No data returned."

    headers = [
        "event_name",
        "date",
        "platform",
        "stream_id",
        "event_count",
        "total_users",
        "event_count_per_user",
    ]

    raw_rows = [
        [
            row.event_name,
            row.date or "-",
            row.platform or "-",
            row.stream_id or "-",
            str(row.event_count),
            str(row.total_users),
            f"{row.event_count_per_user:.4f}",
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


def format_open_rate_rows(rows: list[PushOpenRateRow]) -> str:
    if not rows:
        return "No data returned."

    headers = [
        "date",
        "platform",
        "stream_id",
        "notification_receive_count",
        "notification_open_count",
        "open_rate_pct",
    ]

    raw_rows = [
        [
            row.date or "-",
            row.platform or "-",
            row.stream_id or "-",
            str(row.notification_receive_count),
            str(row.notification_open_count),
            f"{row.open_rate_pct:.2f}%" if row.open_rate_pct is not None else "N/A",
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

    if args.event_name not in SUPPORTED_EVENTS:
        print(
            "Unsupported --event-name. Supported values: "
            + ", ".join(sorted(SUPPORTED_EVENTS)),
            file=sys.stderr,
        )
        return 2

    try:
        client = build_client(args.credentials)

        if args.compare_open_rate:
            receive_rows = run_event_query(
                client=client,
                property_id=args.property_id,
                start_date=args.start_date,
                end_date=args.end_date,
                event_name="notification_receive",
                platform=args.platform,
                stream_id=args.stream_id,
                daily=args.daily,
            )
            open_rows = run_event_query(
                client=client,
                property_id=args.property_id,
                start_date=args.start_date,
                end_date=args.end_date,
                event_name="notification_open",
                platform=args.platform,
                stream_id=args.stream_id,
                daily=args.daily,
            )
            rows = merge_open_rate(receive_rows, open_rows)
            if args.json:
                print(json.dumps([asdict(row) for row in rows], ensure_ascii=False, indent=2))
            else:
                print(format_open_rate_rows(rows))
            return 0

        rows = run_event_query(
            client=client,
            property_id=args.property_id,
            start_date=args.start_date,
            end_date=args.end_date,
            event_name=args.event_name,
            platform=args.platform,
            stream_id=args.stream_id,
            daily=args.daily,
        )
    except Exception as exc:  # pragma: no cover
        print(f"Query failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps([asdict(row) for row in rows], ensure_ascii=False, indent=2))
    else:
        print(format_event_rows(rows))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
