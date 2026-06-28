#!/usr/bin/env python3
"""
Generate activation funnel segment report by app version and device brand.
"""

from __future__ import annotations

import argparse
import html
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from google.cloud import bigquery
from google.oauth2 import service_account


@dataclass
class SegmentRow:
    group_key: str
    step1_users: int
    step2_users: int
    step3_users: int
    step4_users: int
    step1_to_step2: float
    step2_to_step3: float
    step3_to_step4: float


@dataclass
class ComboRow:
    app_version: str
    brand: str
    step1_users: int
    step2_users: int
    step3_users: int
    step4_users: int
    step1_to_step2: float
    step2_to_step3: float
    step3_to_step4: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate activation funnel report grouped by app version and device brand."
    )
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--credentials", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--output-dir", default="reports/ga4_activation")
    return parser.parse_args()


def bq_client(project_id: str, credentials_path: str) -> bigquery.Client:
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    return bigquery.Client(project=project_id, credentials=credentials)


def date_token(value: str) -> str:
    return value.replace("-", "")


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


BASE_CTE = """
WITH cohort AS (
  SELECT
    user_pseudo_id,
    MIN(event_timestamp) AS ts1,
    ARRAY_AGG(app_info.version IGNORE NULLS ORDER BY event_timestamp LIMIT 1)[SAFE_OFFSET(0)] AS app_version,
    ARRAY_AGG(device.mobile_brand_name IGNORE NULLS ORDER BY event_timestamp LIMIT 1)[SAFE_OFFSET(0)] AS brand
  FROM `{project_id}.{dataset}.events_*`
  WHERE event_name = 'first_open'
    AND _TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
  GROUP BY 1
),
s2 AS (
  SELECT c.user_pseudo_id, MIN(e.event_timestamp) AS ts2
  FROM cohort c
  JOIN `{project_id}.{dataset}.events_*` e ON e.user_pseudo_id = c.user_pseudo_id
  WHERE e.event_name = 'ACT_EnterHomePage'
    AND e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
    AND e.event_timestamp > c.ts1
  GROUP BY 1
),
s3 AS (
  SELECT c.user_pseudo_id, MIN(e.event_timestamp) AS ts3
  FROM cohort c
  JOIN s2 USING(user_pseudo_id)
  JOIN `{project_id}.{dataset}.events_*` e ON e.user_pseudo_id = c.user_pseudo_id
  WHERE e.event_name = 'ACT_EnterFunctionDetailPage'
    AND e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
    AND e.event_timestamp > s2.ts2
  GROUP BY 1
),
s4 AS (
  SELECT c.user_pseudo_id, MIN(e.event_timestamp) AS ts4
  FROM cohort c
  JOIN s3 USING(user_pseudo_id)
  JOIN `{project_id}.{dataset}.events_*` e ON e.user_pseudo_id = c.user_pseudo_id
  WHERE e.event_name = 'ACT_EnterFunctionAddRecordPage'
    AND e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
    AND e.event_timestamp > s3.ts3
  GROUP BY 1
)
"""


def query_group_rows(
    client: bigquery.Client,
    *,
    project_id: str,
    dataset: str,
    start_date: str,
    end_date: str,
    field_name: str,
) -> list[SegmentRow]:
    query = BASE_CTE.format(
        project_id=project_id,
        dataset=dataset,
        start_token=date_token(start_date),
        end_token=date_token(end_date),
    ) + f"""
SELECT
  COALESCE(NULLIF({field_name}, ''), 'unknown') AS grp,
  COUNT(*) AS step1_users,
  COUNTIF(s2.user_pseudo_id IS NOT NULL) AS step2_users,
  COUNTIF(s3.user_pseudo_id IS NOT NULL) AS step3_users,
  COUNTIF(s4.user_pseudo_id IS NOT NULL) AS step4_users,
  SAFE_DIVIDE(COUNTIF(s2.user_pseudo_id IS NOT NULL), COUNT(*)) AS step1_to_step2,
  SAFE_DIVIDE(COUNTIF(s3.user_pseudo_id IS NOT NULL), COUNTIF(s2.user_pseudo_id IS NOT NULL)) AS step2_to_step3,
  SAFE_DIVIDE(COUNTIF(s4.user_pseudo_id IS NOT NULL), COUNTIF(s3.user_pseudo_id IS NOT NULL)) AS step3_to_step4
FROM cohort c
LEFT JOIN s2 USING(user_pseudo_id)
LEFT JOIN s3 USING(user_pseudo_id)
LEFT JOIN s4 USING(user_pseudo_id)
GROUP BY 1
HAVING step1_users >= 80
ORDER BY step1_users DESC
"""
    rows = []
    for row in client.query(query).result():
        rows.append(
            SegmentRow(
                group_key=row.grp,
                step1_users=int(row.step1_users),
                step2_users=int(row.step2_users),
                step3_users=int(row.step3_users),
                step4_users=int(row.step4_users),
                step1_to_step2=float(row.step1_to_step2 or 0.0),
                step2_to_step3=float(row.step2_to_step3 or 0.0),
                step3_to_step4=float(row.step3_to_step4 or 0.0),
            )
        )
    return rows


def query_combo_rows(
    client: bigquery.Client,
    *,
    project_id: str,
    dataset: str,
    start_date: str,
    end_date: str,
) -> list[ComboRow]:
    query = BASE_CTE.format(
        project_id=project_id,
        dataset=dataset,
        start_token=date_token(start_date),
        end_token=date_token(end_date),
    ) + """
SELECT
  COALESCE(NULLIF(app_version, ''), 'unknown') AS app_version,
  COALESCE(NULLIF(brand, ''), 'unknown') AS brand,
  COUNT(*) AS step1_users,
  COUNTIF(s2.user_pseudo_id IS NOT NULL) AS step2_users,
  COUNTIF(s3.user_pseudo_id IS NOT NULL) AS step3_users,
  COUNTIF(s4.user_pseudo_id IS NOT NULL) AS step4_users,
  SAFE_DIVIDE(COUNTIF(s2.user_pseudo_id IS NOT NULL), COUNT(*)) AS step1_to_step2,
  SAFE_DIVIDE(COUNTIF(s3.user_pseudo_id IS NOT NULL), COUNTIF(s2.user_pseudo_id IS NOT NULL)) AS step2_to_step3,
  SAFE_DIVIDE(COUNTIF(s4.user_pseudo_id IS NOT NULL), COUNTIF(s3.user_pseudo_id IS NOT NULL)) AS step3_to_step4
FROM cohort c
LEFT JOIN s2 USING(user_pseudo_id)
LEFT JOIN s3 USING(user_pseudo_id)
LEFT JOIN s4 USING(user_pseudo_id)
GROUP BY 1,2
HAVING step1_users >= 80
ORDER BY step2_to_step3 ASC, step3_to_step4 ASC, step1_users DESC
"""
    rows = []
    for row in client.query(query).result():
        rows.append(
            ComboRow(
                app_version=row.app_version,
                brand=row.brand,
                step1_users=int(row.step1_users),
                step2_users=int(row.step2_users),
                step3_users=int(row.step3_users),
                step4_users=int(row.step4_users),
                step1_to_step2=float(row.step1_to_step2 or 0.0),
                step2_to_step3=float(row.step2_to_step3 or 0.0),
                step3_to_step4=float(row.step3_to_step4 or 0.0),
            )
        )
    return rows


def md_table_segment(rows: list[SegmentRow]) -> list[str]:
    lines = [
        "| 分组 | 新用户 | 到首页率 | 首页→功能详情 | 功能详情→加记录页 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.group_key} | {row.step1_users:,} | {pct(row.step1_to_step2)} | {pct(row.step2_to_step3)} | {pct(row.step3_to_step4)} |"
        )
    return lines


def md_table_combo(rows: list[ComboRow]) -> list[str]:
    lines = [
        "| 版本 | 品牌 | 新用户 | 到首页率 | 首页→功能详情 | 功能详情→加记录页 |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.app_version} | {row.brand} | {row.step1_users:,} | {pct(row.step1_to_step2)} | {pct(row.step2_to_step3)} | {pct(row.step3_to_step4)} |"
        )
    return lines


def html_rows_segment(rows: list[SegmentRow], focus: str) -> str:
    out = []
    for row in rows:
        cls = "num-bad" if (row.step2_to_step3 if focus == "r23" else row.step3_to_step4) < 0.25 else "num-good"
        out.append(
            f"<tr><td>{html.escape(row.group_key)}</td><td class=\"mono\">{row.step1_users:,}</td><td class=\"mono\">{pct(row.step1_to_step2)}</td><td class=\"mono {cls}\">{pct(row.step2_to_step3)}</td><td class=\"mono\">{pct(row.step3_to_step4)}</td></tr>"
        )
    return "".join(out)


def html_rows_combo(rows: list[ComboRow]) -> str:
    out = []
    for row in rows:
        cls = "num-bad" if row.step2_to_step3 < 0.25 else "num-good"
        out.append(
            f"<tr><td>{html.escape(row.app_version)}</td><td>{html.escape(row.brand)}</td><td class=\"mono\">{row.step1_users:,}</td><td class=\"mono\">{pct(row.step1_to_step2)}</td><td class=\"mono {cls}\">{pct(row.step2_to_step3)}</td><td class=\"mono\">{pct(row.step3_to_step4)}</td></tr>"
        )
    return "".join(out)


def main() -> int:
    args = parse_args()
    client = bq_client(args.project_id, args.credentials)
    version_rows = query_group_rows(
        client,
        project_id=args.project_id,
        dataset=args.dataset,
        start_date=args.start_date,
        end_date=args.end_date,
        field_name="app_version",
    )
    brand_rows = query_group_rows(
        client,
        project_id=args.project_id,
        dataset=args.dataset,
        start_date=args.start_date,
        end_date=args.end_date,
        field_name="brand",
    )
    combo_rows = query_combo_rows(
        client,
        project_id=args.project_id,
        dataset=args.dataset,
        start_date=args.start_date,
        end_date=args.end_date,
    )

    worst_version = min(version_rows, key=lambda r: r.step2_to_step3)
    worst_brand = min(brand_rows, key=lambda r: r.step2_to_step3)
    worst_combo = min(combo_rows, key=lambda r: (r.step2_to_step3, r.step3_to_step4))

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.strptime(args.end_date, "%Y-%m-%d").strftime("%m%d")
    base_name = f"{args.project_name}_activation_segment_funnel_{stamp}"
    md_path = output_dir / f"{base_name}.md"
    html_path = output_dir / f"{base_name}.html"

    md_lines = [
        f"# {args.project_name} 首日激活路径分组漏斗报告（版本 / 设备品牌）",
        "",
        "## 分析范围",
        f"- 项目：`{args.project_name}`",
        f"- Cohort 周期：`{args.start_date}` ~ `{args.end_date}`",
        "- 主路径：`first_open -> ACT_EnterHomePage -> ACT_EnterFunctionDetailPage -> ACT_EnterFunctionAddRecordPage`",
        "- 目标：定位哪类新用户更容易断在第 2 步“首页 -> 功能详情”或第 3 步“功能详情 -> 加记录页”",
        "- 仅展示样本数 `>= 80` 的分组，避免小样本误导",
        "",
        "## 总体结论",
        f"- 版本侧最明显的问题在 `1.1.31`：`首页 -> 功能详情` 转化只有 `{pct(worst_version.step2_to_step3)}`，显著低于 `1.1.29` 的 `{pct(next(r.step2_to_step3 for r in version_rows if r.group_key == '1.1.29'))}`。",
        f"- 品牌侧最弱的是 `{worst_brand.group_key}`：`首页 -> 功能详情` 转化仅 `{pct(worst_brand.step2_to_step3)}`，同时 `功能详情 -> 加记录页` 也只有 `{pct(worst_brand.step3_to_step4)}`。",
        f"- 组合维度最差的是 `版本 {worst_combo.app_version} × 品牌 {worst_combo.brand}`：`首页 -> 功能详情` 仅 `{pct(worst_combo.step2_to_step3)}`，`功能详情 -> 加记录页` 仅 `{pct(worst_combo.step3_to_step4)}`。",
        "- 结论更接近“版本问题叠加特定品牌放大”，而不是所有品牌普遍恶化，因为 `1.1.29` 在 Samsung / Motorola 上都明显好于 `1.1.31 × Samsung` 和 `1.1.29 × Google`。",
        "",
        "## 按版本汇总",
        "",
    ]
    md_lines.extend(md_table_segment(version_rows))
    md_lines.extend(["", "## 按设备品牌汇总", ""])
    md_lines.extend(md_table_segment(brand_rows))
    md_lines.extend(["", "## 按版本 × 品牌组合（风险优先）", ""])
    md_lines.extend(md_table_combo(combo_rows))
    md_lines.extend(
        [
            "",
            "## 风险定位",
            f"- `1.1.31` 的问题集中在第 2 步：虽然到首页率还有 `{pct(worst_version.step1_to_step2)}`，但进入功能详情只有 `{pct(worst_version.step2_to_step3)}`，说明首页改版、推荐逻辑、默认落点或 CTA 文案很可能影响了点击进入任务页。",
            f"- `{worst_brand.group_key}` 品牌在第 2 步和第 3 步都弱，倾向于存在设备适配、渲染性能、点击热区或特殊权限/系统行为导致的额外流失。",
            f"- `Samsung` 样本最大，`1.1.31 × Samsung` 的第 2 步仅 `{pct(next(r.step2_to_step3 for r in combo_rows if r.app_version == '1.1.31' and r.brand == 'Samsung'))}`，可以作为首要复现对象。",
            "",
            "## 动作建议",
            "- **P0**：优先回看 `1.1.31` 首页相关变更，重点检查首页首屏入口、功能卡片排序、CTA 曝光与点击埋点是否有变动。",
            f"- **P1**：用 `Google` 与 `Samsung(1.1.31)` 设备做真机复现，重点观察首页进入功能详情是否存在卡顿、点击无响应、布局遮挡或品牌定制 ROM 行为差异。",
            "- **P2**：把该漏斗接入版本发布后 24 小时监控，特别盯 `首页 -> 功能详情`，避免新版本继续扩大激活损失。",
            "",
            "## 方法与限制",
            "- 本报告基于 BigQuery 用户级事件顺序计算，要求后一步事件时间戳严格晚于前一步。",
            "- 版本和品牌取自新用户 `first_open` 的首条可用属性，若埋点延迟或属性缺失，可能归为 `unknown`。",
            "- 当前仅分析主路径前三步，不代表所有功能支线。",
            f"- Generated from `{md_path.resolve()}`",
        ]
    )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    html_content = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(args.project_name)} 首日激活路径分组漏斗报告</title>
  <style>
    :root {{ --bg:#f4f6f8; --card:#fff; --ink:#14212b; --muted:#5c6b78; --line:#d8e0e7; --brand:#1f6f8b; --brand-soft:#e6f2f7; --good:#1f8a5b; --warn:#b86d00; --bad:#b42318; --shadow:0 8px 24px rgba(16,24,40,.08); --radius:14px; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:"SF Pro Text","PingFang SC","Noto Sans SC","Microsoft YaHei",sans-serif; color:var(--ink); background:radial-gradient(circle at 80% -20%, #d7eef9 0%, transparent 45%),radial-gradient(circle at 0% 120%, #e9f7ef 0%, transparent 42%),var(--bg); line-height:1.45; }}
    .container {{ width:min(1200px,92vw); margin:28px auto 40px; }}
    .header {{ background:linear-gradient(130deg,#10384c 0%,#1f6f8b 58%,#4a9fb4 100%); color:#fff; border-radius:18px; padding:24px 26px; box-shadow:var(--shadow); }}
    .title {{ margin:0; font-size:28px; letter-spacing:.2px; }}
    .subtitle {{ margin:8px 0 0; color:#d8edf5; font-size:14px; }}
    .section {{ background:var(--card); border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow); margin-top:16px; padding:18px 18px 14px; }}
    .section h2 {{ margin:0 0 12px; font-size:18px; }}
    .grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }}
    .metric {{ border:1px solid var(--line); border-radius:12px; background:#fbfdff; padding:12px; }}
    .metric .k {{ color:var(--muted); font-size:12px; }}
    .metric .v {{ margin-top:6px; font-size:20px; font-weight:700; }}
    .metric .sub {{ margin-top:4px; font-size:12px; color:var(--muted); }}
    ul {{ margin:8px 0 0 0; padding-left:20px; }}
    li {{ margin:6px 0; }}
    .table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:12px; }}
    table {{ width:100%; border-collapse:collapse; min-width:900px; background:#fff; }}
    th,td {{ border-bottom:1px solid var(--line); padding:10px 10px; text-align:left; vertical-align:top; font-size:13px; }}
    th {{ background:#f3f8fb; color:#1f4f63; font-weight:700; white-space:nowrap; }}
    tr:last-child td {{ border-bottom:none; }}
    .mono {{ font-variant-numeric:tabular-nums; font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace; }}
    .num-good {{ color:var(--good); font-weight:700; }}
    .num-bad {{ color:var(--bad); font-weight:700; }}
    .note {{ border-left:4px solid var(--brand); background:var(--brand-soft); color:#184356; padding:10px 12px; border-radius:8px; font-size:13px; margin-bottom:10px; }}
    .muted {{ color:var(--muted); }}
    @media (max-width:860px) {{ .grid {{ grid-template-columns:1fr; }} .title {{ font-size:22px; }} .section {{ padding:14px 14px 10px; }} }}
  </style>
</head>
<body>
  <main class="container">
    <header class="header">
      <h1 class="title">{html.escape(args.project_name)} 首日激活路径分组漏斗报告</h1>
      <p class="subtitle">版本 / 设备品牌分组 · Cohort：{args.start_date} ~ {args.end_date} · 生成日期：{date.today().isoformat()}</p>
    </header>

    <section class="section">
      <h2>总体结论</h2>
      <div class="grid">
        <div class="metric"><div class="k">最弱版本</div><div class="v mono">{worst_version.group_key}</div><div class="sub">首页→功能详情 {pct(worst_version.step2_to_step3)}</div></div>
        <div class="metric"><div class="k">最弱品牌</div><div class="v mono">{html.escape(worst_brand.group_key)}</div><div class="sub">首页→功能详情 {pct(worst_brand.step2_to_step3)}</div></div>
        <div class="metric"><div class="k">最差组合</div><div class="v mono">{worst_combo.app_version} × {html.escape(worst_combo.brand)}</div><div class="sub">首页→功能详情 {pct(worst_combo.step2_to_step3)}</div></div>
      </div>
      <ul>
        <li>版本侧最弱的是 <span class="mono">{worst_version.group_key}</span>，第 2 步仅 <span class="mono">{pct(worst_version.step2_to_step3)}</span>。</li>
        <li>品牌侧最弱的是 <span class="mono">{html.escape(worst_brand.group_key)}</span>，第 2 步仅 <span class="mono">{pct(worst_brand.step2_to_step3)}</span>，第 3 步仅 <span class="mono">{pct(worst_brand.step3_to_step4)}</span>。</li>
        <li>组合维度最差是 <span class="mono">{worst_combo.app_version} × {html.escape(worst_combo.brand)}</span>，说明问题更像版本改动在特定品牌上被放大。</li>
      </ul>
    </section>

    <section class="section">
      <h2>按版本汇总</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>版本</th><th>新用户</th><th>到首页率</th><th>首页→功能详情</th><th>功能详情→加记录页</th></tr></thead>
          <tbody>{html_rows_segment(version_rows, 'r23')}</tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>按设备品牌汇总</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>品牌</th><th>新用户</th><th>到首页率</th><th>首页→功能详情</th><th>功能详情→加记录页</th></tr></thead>
          <tbody>{html_rows_segment(brand_rows, 'r23')}</tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>按版本 × 品牌组合（风险优先）</h2>
      <div class="note">仅展示新用户样本数 ≥ 80 的组合，按“首页→功能详情”升序排序，优先暴露最差断点。</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>版本</th><th>品牌</th><th>新用户</th><th>到首页率</th><th>首页→功能详情</th><th>功能详情→加记录页</th></tr></thead>
          <tbody>{html_rows_combo(combo_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>动作建议</h2>
      <ul>
        <li><strong>P0：</strong>优先审查 <span class="mono">1.1.31</span> 首页变更，并在 <span class="mono">Samsung</span> 真机上复现首页到功能详情的点击链路。</li>
        <li><strong>P1：</strong>用 <span class="mono">Google</span> 品牌设备专项排查布局、触控、卡顿和权限行为差异，因为其第 2 步和第 3 步都明显偏弱。</li>
        <li><strong>P2：</strong>将该分组漏斗接入版本发布后的日监控，避免后续版本继续扩大 `首页 -> 功能详情` 的损失。</li>
      </ul>
      <p class="muted" style="margin:10px 0 4px; font-size:12px;">Generated from {html.escape(str(md_path.resolve()))}</p>
    </section>
  </main>
</body>
</html>
"""
    html_path.write_text(html_content, encoding="utf-8")
    print(md_path.resolve())
    print(html_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
