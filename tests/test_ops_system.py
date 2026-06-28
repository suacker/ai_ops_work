from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from ops_system.data_model import validate_diagnostics
from ops_system.report_renderer import render_html, render_markdown
from ops_system.rules_engine import (
    ACTIONS,
    DATA_QUALITY_STATUSES,
    WriteActionError,
    ensure_read_only_action,
)


def sample_diagnostics() -> dict:
    return {
        "report": {
            "title": "多项目买量作战日报",
            "date_start": "2026-06-11",
            "date_end": "2026-06-17",
            "generated_at": "2026-06-18T10:00:00+08:00",
            "mode": "read_only",
        },
        "portfolio_summary": {
            "conclusion": "MessagePro 可小幅扩量，StepTracker 需要继续核对 Meta 回收。",
            "kpis": [
                {"label": "项目数", "value": "3"},
                {"label": "P0 动作", "value": "1"},
            ],
        },
        "projects": [
            {
                "project": {
                    "project_id": "A124",
                    "project_name": "MessagePro",
                    "monetization_type": "IAA",
                    "priority_countries": ["US", "GB"],
                },
                "platform_status": {
                    "google": "ready",
                    "facebook": "inactive_no_data",
                    "tiktok": "inactive_no_data",
                },
                "data_quality": {
                    "status": "ready",
                    "confidence": "high",
                    "limitations": ["Meta 当前窗口无 ROI 数据"],
                },
                "metrics": {
                    "spend": 11057.44,
                    "installs": 7768,
                    "cpi": 1.4934,
                    "roi0": 0.3552,
                    "roi3": 0.5181,
                    "roi7": None,
                },
                "diagnostics": [
                    {
                        "scope": "google / US / US-3.0-250114",
                        "status": "scale_candidate",
                        "reason": "ROI0 与 ROI3 高于账户基准，但 ROI7 为预测或缺失。",
                    }
                ],
                "recommended_actions": [
                    {
                        "priority": "P0",
                        "object": "google / US / US-3.0-250114",
                        "action": "small_add",
                        "confidence": "medium",
                        "reason": "成熟消耗下回收优于账户基准，建议小幅加预算验证。",
                        "review_date": "2026-06-19",
                        "feedback_status": "pending",
                    }
                ],
                "limitations": ["缺少 Google learning 状态"],
                "source_refs": [
                    "Snowball MCP get_roi_report",
                    "grow_base/A124_MessagePro.md",
                ],
            },
            {
                "project": {
                    "project_id": "A155",
                    "project_name": "StepTracker",
                    "monetization_type": "IAA",
                    "priority_countries": ["US"],
                },
                "platform_status": {
                    "facebook": "partial",
                    "google": "ready",
                    "tiktok": "inactive_no_data",
                },
                "data_quality": {
                    "status": "partial",
                    "confidence": "medium",
                    "limitations": ["Meta spend 与 Snowball cost 需要对账"],
                },
                "metrics": {
                    "spend": 3158.46,
                    "installs": 2155,
                    "cpi": 1.65,
                    "roi0": 0.261,
                    "roi3": 0.403,
                    "roi7": 1.635,
                },
                "diagnostics": [
                    {
                        "scope": "facebook",
                        "status": "data_gap_check",
                        "reason": "平台与 Snowball 回收口径不完全一致。",
                    }
                ],
                "recommended_actions": [
                    {
                        "priority": "P1",
                        "object": "facebook / account mapping",
                        "action": "data_gap_check",
                        "confidence": "medium",
                        "reason": "先核对归因窗口、时区和成本导入。",
                        "review_date": "2026-06-19",
                        "feedback_status": "pending",
                    }
                ],
                "limitations": ["Meta creative 数据未接入本次样例"],
                "source_refs": ["Meta Ads CLI", "Snowball MCP get_roi_report"],
            },
        ],
    }


def test_action_taxonomy_contains_only_read_only_suggestions() -> None:
    assert "small_add" in ACTIONS
    assert "no_action_no_data" in ACTIONS
    assert "set_budget" not in ACTIONS
    assert "create_ad" not in ACTIONS
    assert DATA_QUALITY_STATUSES == {"ready", "partial", "blocked", "inactive_no_data"}
    ensure_read_only_action("small_add")
    with pytest.raises(WriteActionError):
        ensure_read_only_action("set_budget")


def test_validate_diagnostics_accepts_complete_report() -> None:
    diagnostics = sample_diagnostics()
    errors = validate_diagnostics(diagnostics)
    assert errors == []


def test_validate_diagnostics_rejects_unknown_action_and_status() -> None:
    diagnostics = sample_diagnostics()
    diagnostics["projects"][0]["data_quality"]["status"] = "made_up"
    diagnostics["projects"][0]["recommended_actions"][0]["action"] = "set_budget"
    errors = validate_diagnostics(diagnostics)
    assert any("data_quality.status" in error for error in errors)
    assert any("recommended_actions[0].action" in error for error in errors)


def test_markdown_and_html_render_from_same_diagnostics() -> None:
    diagnostics = sample_diagnostics()
    md = render_markdown(diagnostics, source_path=Path("reports/ops_daily/data/sample.json"))
    html = render_html(diagnostics, source_path=Path("reports/ops_daily/data/sample.json"))
    assert "# 多项目买量作战日报" in md
    assert "MessagePro 可小幅扩量" in md
    assert "| P0 | google / US / US-3.0-250114 | small_add | medium |" in md
    assert "Generated from reports/ops_daily/data/sample.json" in html
    assert "MessagePro 可小幅扩量" in html
    assert "small_add" in html
    assert "class=\"hero\"" in html
    assert "class=\"kpi-grid\"" in html
    assert "class=\"action-card priority-p0\"" in html
    assert "<table" in html
    assert "table-line" not in html


def test_cli_render_writes_json_markdown_html_and_feedback(tmp_path: Path) -> None:
    input_path = tmp_path / "diagnostics.json"
    output_dir = tmp_path / "ops_daily"
    input_path.write_text(json.dumps(sample_diagnostics(), ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ops_system",
            "render",
            "--input",
            str(input_path),
            "--output-dir",
            str(output_dir),
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert (output_dir / "2026-06-17_multi_project_ads_ops.md").exists()
    assert (output_dir / "2026-06-17_multi_project_ads_ops.html").exists()
    assert (output_dir / "data" / "2026-06-17_diagnostics.json").exists()
    feedback_path = output_dir / "feedback" / "2026-06-17_feedback.md"
    assert feedback_path.exists()
    assert "feedback_status: pending" in feedback_path.read_text(encoding="utf-8")


def test_cli_validate_blocks_invalid_report(tmp_path: Path) -> None:
    input_path = tmp_path / "invalid.json"
    diagnostics = sample_diagnostics()
    diagnostics["projects"][0]["recommended_actions"][0]["action"] = "create_ad"
    input_path.write_text(json.dumps(diagnostics, ensure_ascii=False), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "ops_system", "validate", "--input", str(input_path)],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "recommended_actions[0].action" in result.stderr
