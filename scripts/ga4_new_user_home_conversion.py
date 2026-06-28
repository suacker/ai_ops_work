#!/usr/bin/env python3
"""
Query "new user -> home screen" conversion with the GA4 Funnel API.

This script is intended for Firebase / GA4 app properties where:
- step 1 is a new-user event such as `first_open`
- step 2 is a "entered main screen" event such as:
  - `screen_view` with `firebase_screen=Home`
  - a custom event like `home_show`

Prerequisites:
1. Google Analytics Data API is enabled in Google Cloud.
2. The service account has at least Viewer access to the GA4 property.
3. Python package `google-analytics-data` is installed.

Examples:
    python scripts/ga4_new_user_home_conversion.py \
      --property-id 509028946 \
      --start-date 2026-04-25 \
      --end-date 2026-05-01 \
      --credentials firebase_service_account/steptrack_firebase_service_account.json \
      --new-user-event first_open \
      --target-event screen_view \
      --target-param firebase_screen=Home

    python scripts/ga4_new_user_home_conversion.py \
      --property-id 509028946 \
      --start-date 2026-04-25 \
      --end-date 2026-05-01 \
      --credentials firebase_service_account/steptrack_firebase_service_account.json \
      --target-event home_show \
      --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from typing import Iterable, Optional

from google.analytics.data_v1alpha import AlphaAnalyticsDataClient
from google.analytics.data_v1alpha.types import (
    DateRange,
    Funnel,
    FunnelEventFilter,
    FunnelFilterExpression,
    FunnelFilterExpressionList,
    FunnelParameterFilter,
    FunnelParameterFilterExpression,
    FunnelParameterFilterExpressionList,
    FunnelStep,
    RunFunnelReportRequest,
    StringFilter,
)
from google.oauth2 import service_account


SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


@dataclass
class FunnelStepSummary:
    step_name: str
    active_users: int
    completion_rate: Optional[float]
    abandonments: Optional[int]
    abandonment_rate: Optional[float]


@dataclass
class ConversionResult:
    property_id: str
    start_date: str
    end_date: str
    new_user_event: str
    target_event: str
    target_params: dict[str, str]
    is_open_funnel: bool
    new_users: int
    converted_users: int
    conversion_rate: Optional[float]
    steps: list[FunnelStepSummary]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query GA4 new-user to home-screen conversion rate with a funnel report."
    )
    parser.add_argument("--property-id", required=True, help="GA4 property ID.")
    parser.add_argument("--start-date", required=True, help="Start date, e.g. 2026-04-25.")
    parser.add_argument("--end-date", required=True, help="End date, e.g. 2026-05-01.")
    parser.add_argument(
        "--credentials",
        help="Path to a Google service account JSON key. Defaults to GOOGLE_APPLICATION_CREDENTIALS.",
    )
    parser.add_argument(
        "--new-user-event",
        default="first_open",
        help="New-user event name. Default: first_open.",
    )
    parser.add_argument(
        "--target-event",
        required=True,
        help="Target event name for entering the main screen, e.g. screen_view or home_show.",
    )
    parser.add_argument(
        "--target-param",
        action="append",
        default=[],
        help=(
            "Optional event parameter filter in KEY=VALUE form. "
            "Repeat this flag for multiple filters."
        ),
    )
    parser.add_argument(
        "--open-funnel",
        action="store_true",
        help="Use an open funnel. Default is a closed funnel.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of a text summary.",
    )
    return parser.parse_args()


def build_client(credentials_path: Optional[str]) -> AlphaAnalyticsDataClient:
    if credentials_path:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        return AlphaAnalyticsDataClient(credentials=credentials)

    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path:
        credentials = service_account.Credentials.from_service_account_file(
            env_path, scopes=SCOPES
        )
        return AlphaAnalyticsDataClient(credentials=credentials)

    raise RuntimeError(
        "Missing credentials. Use --credentials /path/to/key.json or set "
        "GOOGLE_APPLICATION_CREDENTIALS."
    )


def parse_key_value_pairs(values: Iterable[str]) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for raw in values:
        if "=" not in raw:
            raise ValueError(
                f"Invalid --target-param value {raw!r}. Expected KEY=VALUE."
            )
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Invalid --target-param value {raw!r}. Empty key.")
        pairs[key] = value
    return pairs


def make_event_filter_expression(
    event_name: str, event_params: Optional[dict[str, str]] = None
) -> FunnelFilterExpression:
    parameter_filter_expression: Optional[FunnelParameterFilterExpression] = None

    if event_params:
        parameter_expressions = [
            FunnelParameterFilterExpression(
                funnel_parameter_filter=FunnelParameterFilter(
                    event_parameter_name=key,
                    string_filter=StringFilter(
                        match_type=StringFilter.MatchType.EXACT,
                        value=value,
                        case_sensitive=False,
                    ),
                )
            )
            for key, value in event_params.items()
        ]

        if len(parameter_expressions) == 1:
            parameter_filter_expression = parameter_expressions[0]
        else:
            parameter_filter_expression = FunnelParameterFilterExpression(
                and_group=FunnelParameterFilterExpressionList(
                    expressions=parameter_expressions
                )
            )

    return FunnelFilterExpression(
        funnel_event_filter=FunnelEventFilter(
            event_name=event_name,
            funnel_parameter_filter_expression=parameter_filter_expression,
        )
    )


def build_request(
    property_id: str,
    start_date: str,
    end_date: str,
    new_user_event: str,
    target_event: str,
    target_params: dict[str, str],
    is_open_funnel: bool,
) -> RunFunnelReportRequest:
    return RunFunnelReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        funnel=Funnel(
            is_open_funnel=is_open_funnel,
            steps=[
                FunnelStep(
                    name="New users",
                    filter_expression=make_event_filter_expression(new_user_event),
                ),
                FunnelStep(
                    name="Entered main screen",
                    filter_expression=make_event_filter_expression(
                        target_event, target_params
                    ),
                ),
            ],
        ),
    )


def header_indexes(sub_report) -> tuple[dict[str, int], dict[str, int]]:
    dimension_indexes = {
        header.name: idx for idx, header in enumerate(sub_report.dimension_headers)
    }
    metric_indexes = {
        header.name: idx for idx, header in enumerate(sub_report.metric_headers)
    }
    return dimension_indexes, metric_indexes


def parse_optional_float(value: str) -> Optional[float]:
    if value == "":
        return None
    return float(value)


def parse_optional_int(value: str) -> Optional[int]:
    if value == "":
        return None
    return int(value)


def parse_funnel_steps(response) -> list[FunnelStepSummary]:
    sub_report = response.funnel_table
    dimension_indexes, _ = header_indexes(sub_report)
    steps: list[FunnelStepSummary] = []

    step_name_idx = dimension_indexes.get("funnelStepName")
    if step_name_idx is None:
        step_name_idx = dimension_indexes.get("funnelStep")

    metric_names = [header.name for header in sub_report.metric_headers]
    metric_names = metric_names[: len(sub_report.rows[0].metric_values)] if sub_report.rows else metric_names

    active_users_idx = metric_names.index("activeUsers")
    completion_rate_idx = (
        metric_names.index("funnelStepCompletionRate")
        if "funnelStepCompletionRate" in metric_names
        else None
    )
    abandonments_idx = (
        metric_names.index("funnelStepAbandonments")
        if "funnelStepAbandonments" in metric_names
        else None
    )
    abandonment_rate_idx = (
        metric_names.index("funnelStepAbandonmentRate")
        if "funnelStepAbandonmentRate" in metric_names
        else None
    )

    for row in sub_report.rows:
        step_name = row.dimension_values[step_name_idx].value if step_name_idx is not None else ""
        steps.append(
            FunnelStepSummary(
                step_name=step_name,
                active_users=int(row.metric_values[active_users_idx].value),
                completion_rate=(
                    parse_optional_float(row.metric_values[completion_rate_idx].value)
                    if completion_rate_idx is not None
                    else None
                ),
                abandonments=(
                    parse_optional_int(row.metric_values[abandonments_idx].value)
                    if abandonments_idx is not None
                    else None
                ),
                abandonment_rate=(
                    parse_optional_float(row.metric_values[abandonment_rate_idx].value)
                    if abandonment_rate_idx is not None
                    else None
                ),
            )
        )
    return steps


def run_query(
    client: AlphaAnalyticsDataClient,
    property_id: str,
    start_date: str,
    end_date: str,
    new_user_event: str,
    target_event: str,
    target_params: dict[str, str],
    is_open_funnel: bool,
) -> ConversionResult:
    response = client.run_funnel_report(
        build_request(
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            new_user_event=new_user_event,
            target_event=target_event,
            target_params=target_params,
            is_open_funnel=is_open_funnel,
        )
    )
    steps = parse_funnel_steps(response)

    new_users = steps[0].active_users if steps else 0
    converted_users = steps[1].active_users if len(steps) > 1 else 0
    conversion_rate = None
    if new_users:
        conversion_rate = converted_users / new_users

    return ConversionResult(
        property_id=property_id,
        start_date=start_date,
        end_date=end_date,
        new_user_event=new_user_event,
        target_event=target_event,
        target_params=target_params,
        is_open_funnel=is_open_funnel,
        new_users=new_users,
        converted_users=converted_users,
        conversion_rate=conversion_rate,
        steps=steps,
    )


def print_text(result: ConversionResult) -> None:
    print(f"Property ID: {result.property_id}")
    print(f"Date range: {result.start_date} ~ {result.end_date}")
    print(f"New user event: {result.new_user_event}")
    print(f"Target event: {result.target_event}")
    print(f"Target params: {json.dumps(result.target_params, ensure_ascii=False)}")
    print(f"Open funnel: {'yes' if result.is_open_funnel else 'no'}")
    print()
    print(f"New users: {result.new_users}")
    print(f"Converted users: {result.converted_users}")
    if result.conversion_rate is None:
        print("Conversion rate: N/A")
    else:
        print(f"Conversion rate: {result.conversion_rate * 100:.2f}%")
    print()
    print("Funnel steps:")
    for step in result.steps:
        parts = [f"- {step.step_name}: active_users={step.active_users}"]
        if step.completion_rate is not None:
            parts.append(f"completion_rate={step.completion_rate * 100:.2f}%")
        if step.abandonments is not None:
            parts.append(f"abandonments={step.abandonments}")
        if step.abandonment_rate is not None:
            parts.append(f"abandonment_rate={step.abandonment_rate * 100:.2f}%")
        print(", ".join(parts))


def main() -> int:
    args = parse_args()
    try:
        target_params = parse_key_value_pairs(args.target_param)
        client = build_client(args.credentials)
        result = run_query(
            client=client,
            property_id=args.property_id,
            start_date=args.start_date,
            end_date=args.end_date,
            new_user_event=args.new_user_event,
            target_event=args.target_event,
            target_params=target_params,
            is_open_funnel=args.open_funnel,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
