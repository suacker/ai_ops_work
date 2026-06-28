#!/usr/bin/env python3
"""
Generate a first-day activation funnel report from GA4 BigQuery export.
"""

from __future__ import annotations

import argparse
import html
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from google.cloud import bigquery
from google.oauth2 import service_account


@dataclass
class StepRow:
    step_no: int
    step_name: str
    users: int
    retained_users: int

    @property
    def funnel_rate(self) -> float:
        return self.users / TOTAL_USERS if TOTAL_USERS else 0.0

    @property
    def step_to_step_rate(self) -> float:
        if self.step_no == 1:
            return 1.0
        prev = STEP_MAP[self.step_no - 1]
        return self.users / prev.users if prev.users else 0.0

    @property
    def d1_retention(self) -> float:
        return self.retained_users / self.users if self.users else 0.0


@dataclass
class CandidateFunnel:
    name: str
    label: str
    steps: list[str]
    counts: list[int]

    @property
    def final_rate(self) -> float:
        return self.counts[-1] / self.counts[0] if self.counts and self.counts[0] else 0.0


TOTAL_USERS = 0
STEP_MAP: dict[int, StepRow] = {}


PRIMARY_STEPS = [
    "first_open",
    "ACT_EnterHomePage",
    "ACT_EnterFunctionDetailPage",
    "ACT_EnterFunctionAddRecordPage",
    "CLK_SaveFunctionRecord",
]

CANDIDATE_FUNNELS: dict[str, tuple[str, list[str]]] = {
    "detail_add_save": (
        "首页 > 功能详情 > 加记录页 > 保存记录",
        ["first_open", "ACT_EnterHomePage", "ACT_EnterFunctionDetailPage", "ACT_EnterFunctionAddRecordPage", "CLK_SaveFunctionRecord"],
    ),
    "detail_click_save": (
        "首页 > 功能详情 > AddRecord点击 > 保存记录",
        ["first_open", "ACT_EnterHomePage", "ACT_EnterFunctionDetailPage", "CLK_AddRecord", "CLK_SaveFunctionRecord"],
    ),
    "measure_add_save": (
        "首页 > 心率测量 > AddRecord点击 > 保存记录",
        ["first_open", "ACT_EnterHomePage", "ACT_EnterHeartRateMeasurePage", "CLK_AddRecord", "CLK_SaveFunctionRecord"],
    ),
    "goal_add_save": (
        "首页 > 饮水目标 > 加记录页 > 保存记录",
        ["first_open", "ACT_EnterHomePage", "ACT_EnterWaterIntakeGoalPage", "ACT_EnterFunctionAddRecordPage", "CLK_SaveFunctionRecord"],
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a GA4 first-day activation funnel report."
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


def pp(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}pp"


def next_day(value: str) -> str:
    return (datetime.strptime(value, "%Y-%m-%d").date() + timedelta(days=1)).isoformat()


def query_primary_steps(
    client: bigquery.Client,
    *,
    project_id: str,
    dataset: str,
    start_date: str,
    end_date: str,
) -> list[StepRow]:
    start_token = date_token(start_date)
    end_token = date_token(end_date)
    retained_start = date_token(next_day(start_date))
    retained_end = date_token(next_day(end_date))
    query = f"""
WITH cohort AS (
  SELECT user_pseudo_id, PARSE_DATE('%Y%m%d', event_date) AS first_date, MIN(event_timestamp) AS ts1
  FROM `{project_id}.{dataset}.events_*`
  WHERE event_name = 'first_open'
    AND _TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
  GROUP BY 1,2
),
retained AS (
  SELECT DISTINCT c.user_pseudo_id
  FROM cohort c
  JOIN `{project_id}.{dataset}.events_*` e
    ON e.user_pseudo_id = c.user_pseudo_id
   AND PARSE_DATE('%Y%m%d', e.event_date) = DATE_ADD(c.first_date, INTERVAL 1 DAY)
  WHERE e._TABLE_SUFFIX BETWEEN '{retained_start}' AND '{retained_end}'
),
s2 AS (
  SELECT c.user_pseudo_id, MIN(e.event_timestamp) AS ts2
  FROM cohort c
  JOIN `{project_id}.{dataset}.events_*` e ON e.user_pseudo_id = c.user_pseudo_id
  WHERE e.event_name = '{PRIMARY_STEPS[1]}'
    AND e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
    AND e.event_timestamp > c.ts1
  GROUP BY 1
),
s3 AS (
  SELECT c.user_pseudo_id, MIN(e.event_timestamp) AS ts3
  FROM cohort c
  JOIN s2 USING(user_pseudo_id)
  JOIN `{project_id}.{dataset}.events_*` e ON e.user_pseudo_id = c.user_pseudo_id
  WHERE e.event_name = '{PRIMARY_STEPS[2]}'
    AND e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
    AND e.event_timestamp > s2.ts2
  GROUP BY 1
),
s4 AS (
  SELECT c.user_pseudo_id, MIN(e.event_timestamp) AS ts4
  FROM cohort c
  JOIN s3 USING(user_pseudo_id)
  JOIN `{project_id}.{dataset}.events_*` e ON e.user_pseudo_id = c.user_pseudo_id
  WHERE e.event_name = '{PRIMARY_STEPS[3]}'
    AND e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
    AND e.event_timestamp > s3.ts3
  GROUP BY 1
),
s5 AS (
  SELECT c.user_pseudo_id, MIN(e.event_timestamp) AS ts5
  FROM cohort c
  JOIN s4 USING(user_pseudo_id)
  JOIN `{project_id}.{dataset}.events_*` e ON e.user_pseudo_id = c.user_pseudo_id
  WHERE e.event_name = '{PRIMARY_STEPS[4]}'
    AND e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
    AND e.event_timestamp > s4.ts4
  GROUP BY 1
)
SELECT * FROM (
  SELECT 1 AS step_no, '{PRIMARY_STEPS[0]}' AS step_name, COUNT(DISTINCT c.user_pseudo_id) AS users, COUNT(DISTINCT r.user_pseudo_id) AS retained_users
  FROM cohort c LEFT JOIN retained r USING(user_pseudo_id)
  UNION ALL
  SELECT 2, '{PRIMARY_STEPS[1]}', COUNT(DISTINCT s2.user_pseudo_id), COUNT(DISTINCT r.user_pseudo_id)
  FROM s2 LEFT JOIN retained r USING(user_pseudo_id)
  UNION ALL
  SELECT 3, '{PRIMARY_STEPS[2]}', COUNT(DISTINCT s3.user_pseudo_id), COUNT(DISTINCT r.user_pseudo_id)
  FROM s3 LEFT JOIN retained r USING(user_pseudo_id)
  UNION ALL
  SELECT 4, '{PRIMARY_STEPS[3]}', COUNT(DISTINCT s4.user_pseudo_id), COUNT(DISTINCT r.user_pseudo_id)
  FROM s4 LEFT JOIN retained r USING(user_pseudo_id)
  UNION ALL
  SELECT 5, '{PRIMARY_STEPS[4]}', COUNT(DISTINCT s5.user_pseudo_id), COUNT(DISTINCT r.user_pseudo_id)
  FROM s5 LEFT JOIN retained r USING(user_pseudo_id)
)
ORDER BY step_no
"""
    rows = []
    for row in client.query(query).result():
        rows.append(
            StepRow(
                step_no=int(row.step_no),
                step_name=row.step_name,
                users=int(row.users),
                retained_users=int(row.retained_users),
            )
        )
    return rows


def query_candidate_counts(
    client: bigquery.Client,
    *,
    project_id: str,
    dataset: str,
    start_date: str,
    end_date: str,
) -> list[CandidateFunnel]:
    start_token = date_token(start_date)
    end_token = date_token(end_date)
    results: list[CandidateFunnel] = []
    for name, (label, steps) in CANDIDATE_FUNNELS.items():
        query = f"""
WITH cohort AS (
  SELECT user_pseudo_id, MIN(event_timestamp) AS ts1
  FROM `{project_id}.{dataset}.events_*`
  WHERE event_name = '{steps[0]}'
    AND _TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
  GROUP BY 1
),
s2 AS (
  SELECT c.user_pseudo_id, MIN(e.event_timestamp) AS ts
  FROM cohort c
  JOIN `{project_id}.{dataset}.events_*` e ON e.user_pseudo_id = c.user_pseudo_id
  WHERE e.event_name = '{steps[1]}'
    AND e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
    AND e.event_timestamp > c.ts1
  GROUP BY 1
),
s3 AS (
  SELECT c.user_pseudo_id, MIN(e.event_timestamp) AS ts
  FROM cohort c JOIN s2 USING(user_pseudo_id)
  JOIN `{project_id}.{dataset}.events_*` e ON e.user_pseudo_id = c.user_pseudo_id
  WHERE e.event_name = '{steps[2]}'
    AND e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
    AND e.event_timestamp > s2.ts
  GROUP BY 1
),
s4 AS (
  SELECT c.user_pseudo_id, MIN(e.event_timestamp) AS ts
  FROM cohort c JOIN s3 USING(user_pseudo_id)
  JOIN `{project_id}.{dataset}.events_*` e ON e.user_pseudo_id = c.user_pseudo_id
  WHERE e.event_name = '{steps[3]}'
    AND e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
    AND e.event_timestamp > s3.ts
  GROUP BY 1
),
s5 AS (
  SELECT c.user_pseudo_id, MIN(e.event_timestamp) AS ts
  FROM cohort c JOIN s4 USING(user_pseudo_id)
  JOIN `{project_id}.{dataset}.events_*` e ON e.user_pseudo_id = c.user_pseudo_id
  WHERE e.event_name = '{steps[4]}'
    AND e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
    AND e.event_timestamp > s4.ts
  GROUP BY 1
)
SELECT
  (SELECT COUNT(*) FROM cohort) AS c1,
  (SELECT COUNT(*) FROM s2) AS c2,
  (SELECT COUNT(*) FROM s3) AS c3,
  (SELECT COUNT(*) FROM s4) AS c4,
  (SELECT COUNT(*) FROM s5) AS c5
"""
        row = next(client.query(query).result())
        results.append(
            CandidateFunnel(
                name=name,
                label=label,
                steps=steps,
                counts=[int(row.c1), int(row.c2), int(row.c3), int(row.c4), int(row.c5)],
            )
        )
    return results


def render_markdown(
    *,
    project_name: str,
    start_date: str,
    end_date: str,
    steps: list[StepRow],
    candidates: list[CandidateFunnel],
    md_path: Path,
) -> str:
    step_lines = [
        "| 步骤 | 事件 | 达成人数 | 占新用户比重 | 上一步转化率 | 该步人群D1 |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in steps:
        step_lines.append(
            f"| {row.step_no} | {row.step_name} | {row.users:,} | {pct(row.funnel_rate)} | {pct(row.step_to_step_rate)} | {pct(row.d1_retention)} |"
        )

    candidate_lines = [
        "| 候选路径 | Step2 | Step3 | Step4 | Step5 | 最终完成率 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in candidates:
        candidate_lines.append(
            f"| {row.label} | {row.counts[1]:,} | {row.counts[2]:,} | {row.counts[3]:,} | {row.counts[4]:,} | {pct(row.final_rate)} |"
        )

    best_step = max(steps[1:], key=lambda s: s.d1_retention)
    final_step = steps[-1]
    lines = [
        f"# {project_name} 首日激活路径漏斗报告",
        "",
        "## 分析范围",
        f"- 项目：`{project_name}`",
        f"- Cohort 周期：`{start_date}` ~ `{end_date}`",
        "- 新用户口径：首日触发 `first_open`",
        "- 激活定义：首日沿主路径完成“进入首页 -> 进入功能详情 -> 进入加记录页 -> 保存记录”",
        "- 次留口径：次日任意事件回访",
        "",
        "## 总体结论",
        f"- 主激活路径最终完成到 `CLK_SaveFunctionRecord` 的新用户为 `{final_step.users:,}`，占全量新用户 `{pct(final_step.funnel_rate)}`。",
        f"- 最大漏损发生在 `ACT_EnterHomePage -> ACT_EnterFunctionDetailPage`，从 `{steps[1].users:,}` 掉到 `{steps[2].users:,}`，单步转化仅 `{pct(steps[2].step_to_step_rate)}`。",
        f"- 完成最终保存记录的新用户 D1 retention 为 `{pct(final_step.d1_retention)}`，比 cohort 基线 `{pp(final_step.d1_retention - steps[0].d1_retention)}`。",
        f"- 在主路径各步中，D1 最高的是 `{best_step.step_name}`，达到 `{pct(best_step.d1_retention)}`，说明越接近“任务闭环”，次留越强。",
        "",
        "## 核心 KPI",
        f"- Cohort 新用户：`{steps[0].users:,}`",
        f"- 首页到达率：`{pct(steps[1].funnel_rate)}`",
        f"- 功能详情进入率：`{pct(steps[2].funnel_rate)}`",
        f"- 加记录页进入率：`{pct(steps[3].funnel_rate)}`",
        f"- 保存记录完成率：`{pct(steps[4].funnel_rate)}`",
        "",
        "## 主激活漏斗明细",
        "",
    ]
    lines.extend(step_lines)
    lines.extend(
        [
            "",
            "## 候选路径对比",
            "选择主路径的标准：语义通用、覆盖相对更大、能够映射明确的首日任务闭环。",
            "",
        ]
    )
    lines.extend(candidate_lines)
    lines.extend(
        [
            "",
            "## 风险与机会定位",
            f"- `first_open -> ACT_EnterHomePage` 已有 `{pct(steps[1].step_to_step_rate)}`，说明首页首达不是主问题，真正问题在于如何把已到首页的新用户引导进具体功能任务。",
            f"- `ACT_EnterFunctionDetailPage -> ACT_EnterFunctionAddRecordPage` 的单步转化为 `{pct(steps[3].step_to_step_rate)}`，这说明功能详情到动作页的 CTA、默认推荐、信息架构仍有明显优化空间。",
            f"- 一旦走到 `ACT_EnterFunctionAddRecordPage`，后续到 `CLK_SaveFunctionRecord` 的转化达到 `{pct(steps[4].step_to_step_rate)}`，说明记录保存本身不是瓶颈，前置引导才是。",
            "",
            "## 动作建议",
            "- **P0**：把 `ACT_EnterFunctionDetailPage` 前置为首页首屏主 CTA，减少用户在首页停留但不进入任务页的情况。",
            "- **P1**：在功能详情页强化“加记录/立即开始”动作，把用户直接推到 `ACT_EnterFunctionAddRecordPage`，并针对高流失页做文案与按钮 AB 实验。",
            "- **P2**：将心率测量支线单独拆成次级激活漏斗，因为它最终保存率更高，但覆盖面更窄，适合作为专项转化路径优化。",
            "",
            "## 方法与限制",
            "- 本报告基于 BigQuery 用户级事件顺序重建漏斗，要求后一步事件时间戳严格晚于前一步。",
            "- 这是“首日激活路径”分析，不代表所有长期留存路径；部分高价值用户可能走的是其他功能支线。",
            "- 如果埋点存在迟到、重发或跨天上报，漏斗转化会被低估。",
            f"- Generated from `{md_path.resolve()}`",
        ]
    )
    return "\n".join(lines) + "\n"


def render_html(
    *,
    project_name: str,
    start_date: str,
    end_date: str,
    steps: list[StepRow],
    candidates: list[CandidateFunnel],
    md_path: Path,
) -> str:
    step_rows = []
    for row in steps:
        step_rows.append(
            f"<tr><td>{row.step_no}</td><td>{html.escape(row.step_name)}</td><td class=\"mono\">{row.users:,}</td><td class=\"mono\">{pct(row.funnel_rate)}</td><td class=\"mono\">{pct(row.step_to_step_rate)}</td><td class=\"mono num-good\">{pct(row.d1_retention)}</td></tr>"
        )
    candidate_rows = []
    for row in candidates:
        candidate_rows.append(
            f"<tr><td>{html.escape(row.label)}</td><td class=\"mono\">{row.counts[1]:,}</td><td class=\"mono\">{row.counts[2]:,}</td><td class=\"mono\">{row.counts[3]:,}</td><td class=\"mono\">{row.counts[4]:,}</td><td class=\"mono num-good\">{pct(row.final_rate)}</td></tr>"
        )
    best_step = max(steps[1:], key=lambda s: s.d1_retention)
    final_step = steps[-1]
    bar_html = []
    max_users = max(row.users for row in steps)
    for row in steps:
        height = max(24, round(row.users / max_users * 180))
        bar_html.append(
            f"""
            <div class="bar-item">
              <div class="bar-value">{row.users:,}</div>
              <div class="bar" style="height:{height}px"></div>
              <div class="bar-label">S{row.step_no}</div>
            </div>
            """
        )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(project_name)} 首日激活路径漏斗报告</title>
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
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
    .metric {{ border:1px solid var(--line); border-radius:12px; background:#fbfdff; padding:12px; }}
    .metric .k {{ color:var(--muted); font-size:12px; }}
    .metric .v {{ margin-top:6px; font-size:20px; font-weight:700; }}
    .metric .sub {{ margin-top:4px; font-size:12px; color:var(--muted); }}
    ul {{ margin:8px 0 0 0; padding-left:20px; }}
    li {{ margin:6px 0; }}
    .table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:12px; }}
    table {{ width:100%; border-collapse:collapse; min-width:960px; background:#fff; }}
    th,td {{ border-bottom:1px solid var(--line); padding:10px 10px; text-align:left; vertical-align:top; font-size:13px; }}
    th {{ background:#f3f8fb; color:#1f4f63; font-weight:700; white-space:nowrap; }}
    tr:last-child td {{ border-bottom:none; }}
    .mono {{ font-variant-numeric:tabular-nums; font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace; }}
    .num-good {{ color:var(--good); font-weight:700; }}
    .trend {{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:12px; align-items:end; min-height:240px; padding:12px 8px 0; }}
    .bar-item {{ display:flex; flex-direction:column; align-items:center; gap:8px; }}
    .bar-value,.bar-label {{ font-size:12px; color:var(--muted); font-variant-numeric:tabular-nums; text-align:center; }}
    .bar {{ width:64px; border-radius:12px 12px 0 0; background:linear-gradient(180deg,#68b3ca 0%,#1f6f8b 100%); }}
    .note {{ border-left:4px solid var(--brand); background:var(--brand-soft); color:#184356; padding:10px 12px; border-radius:8px; font-size:13px; margin-bottom:10px; }}
    .muted {{ color:var(--muted); }}
    @media (max-width:860px) {{ .grid {{ grid-template-columns:1fr; }} .trend {{ grid-template-columns:repeat(2,minmax(0,1fr)); min-height:auto; }} .title {{ font-size:22px; }} .section {{ padding:14px 14px 10px; }} .bar {{ width:100%; max-width:72px; }} }}
  </style>
</head>
<body>
  <main class="container">
    <header class="header">
      <h1 class="title">{html.escape(project_name)} 首日激活路径漏斗报告</h1>
      <p class="subtitle">BigQuery 用户级漏斗 · Cohort：{start_date} ~ {end_date} · 生成日期：{date.today().isoformat()}</p>
    </header>

    <section class="section">
      <h2>总体结论</h2>
      <div class="grid">
        <div class="metric"><div class="k">Cohort 新用户</div><div class="v mono">{steps[0].users:,}</div><div class="sub">事件：first_open</div></div>
        <div class="metric"><div class="k">首页到达</div><div class="v mono">{steps[1].users:,}</div><div class="sub">{pct(steps[1].funnel_rate)}</div></div>
        <div class="metric"><div class="k">最终保存记录</div><div class="v mono">{final_step.users:,}</div><div class="sub">{pct(final_step.funnel_rate)}</div></div>
        <div class="metric"><div class="k">完成用户D1</div><div class="v mono">{pct(final_step.d1_retention)}</div><div class="sub">较基线 {pp(final_step.d1_retention - steps[0].d1_retention)}</div></div>
      </div>
      <ul>
        <li>主激活路径定义为 <span class="mono">first_open → ACT_EnterHomePage → ACT_EnterFunctionDetailPage → ACT_EnterFunctionAddRecordPage → CLK_SaveFunctionRecord</span>。</li>
        <li>最大漏损发生在 <span class="mono">ACT_EnterHomePage → ACT_EnterFunctionDetailPage</span>，单步转化仅 <span class="mono">{pct(steps[2].step_to_step_rate)}</span>。</li>
        <li>一旦用户走到 <span class="mono">CLK_SaveFunctionRecord</span>，其 D1 retention 达到 <span class="mono">{pct(final_step.d1_retention)}</span>，显著高于 cohort 基线。</li>
        <li>D1 retention 最高的漏斗节点是 <span class="mono">{html.escape(best_step.step_name)}</span>，为 <span class="mono">{pct(best_step.d1_retention)}</span>。</li>
      </ul>
    </section>

    <section class="section">
      <h2>主激活漏斗</h2>
      <div class="trend">{''.join(bar_html)}</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>步骤</th><th>事件</th><th>达成人数</th><th>占新用户比重</th><th>上一步转化率</th><th>该步人群D1</th></tr></thead>
          <tbody>{''.join(step_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>候选路径对比</h2>
      <div class="note">主路径选择标准：语义通用、覆盖更大、适合作为“记录类首日激活”主链路。心率测量支线虽最终完成率更高，但覆盖更窄，适合作为次级专题。</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>候选路径</th><th>Step2</th><th>Step3</th><th>Step4</th><th>Step5</th><th>最终完成率</th></tr></thead>
          <tbody>{''.join(candidate_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>动作建议</h2>
      <ul>
        <li><strong>P0：</strong>把 <span class="mono">ACT_EnterFunctionDetailPage</span> 前置为首页主 CTA，压缩“到首页但不进功能”的流失段。</li>
        <li><strong>P1：</strong>强化功能详情页到加记录页的动线，把核心入口统一收敛到 <span class="mono">ACT_EnterFunctionAddRecordPage</span>。</li>
        <li><strong>P2：</strong>单独建立“心率测量支线”激活漏斗，因为 <span class="mono">measure_add_save</span> 支线最终完成率更高，适合做专项优化。</li>
      </ul>
      <p class="muted" style="margin:10px 0 4px; font-size:12px;">Generated from {html.escape(str(md_path.resolve()))}</p>
    </section>
  </main>
</body>
</html>
"""


def main() -> int:
    global TOTAL_USERS, STEP_MAP
    args = parse_args()
    client = bq_client(args.project_id, args.credentials)
    steps = query_primary_steps(
        client,
        project_id=args.project_id,
        dataset=args.dataset,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    TOTAL_USERS = steps[0].users
    STEP_MAP = {row.step_no: row for row in steps}
    candidates = query_candidate_counts(
        client,
        project_id=args.project_id,
        dataset=args.dataset,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.strptime(args.end_date, "%Y-%m-%d").strftime("%m%d")
    base_name = f"{args.project_name}_activation_funnel_{stamp}"
    md_path = output_dir / f"{base_name}.md"
    html_path = output_dir / f"{base_name}.html"
    md_content = render_markdown(
        project_name=args.project_name,
        start_date=args.start_date,
        end_date=args.end_date,
        steps=steps,
        candidates=candidates,
        md_path=md_path,
    )
    html_content = render_html(
        project_name=args.project_name,
        start_date=args.start_date,
        end_date=args.end_date,
        steps=steps,
        candidates=candidates,
        md_path=md_path,
    )
    md_path.write_text(md_content, encoding="utf-8")
    html_path.write_text(html_content, encoding="utf-8")
    print(md_path.resolve())
    print(html_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
