#!/usr/bin/env python3
"""
Generate a D1 retention correlation report for GA4 BigQuery export.
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
class EventCorrelationRow:
    event_name: str
    users_with_event: int
    retained_with_event: int
    retention_with_event: float
    retention_without_event: float
    uplift_pp: float
    phi: float | None

    @property
    def coverage(self) -> float:
        return self.users_with_event / TOTAL_NEW_USERS if TOTAL_NEW_USERS else 0.0


TOTAL_NEW_USERS = 0
TOTAL_RETAINED_USERS = 0
BASELINE_D1 = 0.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate GA4 event-vs-D1-retention correlation report."
    )
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--credentials", required=True)
    parser.add_argument("--start-date", required=True, help="Cohort start date, YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="Cohort end date, YYYY-MM-DD")
    parser.add_argument("--output-dir", default="reports/ga4_retention")
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


def query_baseline(
    client: bigquery.Client,
    *,
    project_id: str,
    dataset: str,
    start_date: str,
    end_date: str,
) -> tuple[int, int, float]:
    start_token = date_token(start_date)
    end_token = date_token(end_date)
    retained_start = (
        datetime.strptime(start_date, "%Y-%m-%d").date().fromordinal(
            datetime.strptime(start_date, "%Y-%m-%d").date().toordinal() + 1
        )
    ).isoformat()
    retained_end = (
        datetime.strptime(end_date, "%Y-%m-%d").date().fromordinal(
            datetime.strptime(end_date, "%Y-%m-%d").date().toordinal() + 1
        )
    ).isoformat()
    query = f"""
WITH cohort AS (
  SELECT user_pseudo_id, PARSE_DATE('%Y%m%d', event_date) AS first_date
  FROM `{project_id}.{dataset}.events_*`
  WHERE event_name = 'first_open'
    AND _TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
),
retained AS (
  SELECT DISTINCT c.user_pseudo_id
  FROM cohort c
  JOIN `{project_id}.{dataset}.events_*` e
    ON e.user_pseudo_id = c.user_pseudo_id
   AND PARSE_DATE('%Y%m%d', e.event_date) = DATE_ADD(c.first_date, INTERVAL 1 DAY)
  WHERE e._TABLE_SUFFIX BETWEEN '{date_token(retained_start)}' AND '{date_token(retained_end)}'
)
SELECT
  COUNT(DISTINCT c.user_pseudo_id) AS new_users,
  COUNT(DISTINCT r.user_pseudo_id) AS retained_users,
  SAFE_DIVIDE(COUNT(DISTINCT r.user_pseudo_id), COUNT(DISTINCT c.user_pseudo_id)) AS d1
FROM cohort c
LEFT JOIN retained r USING (user_pseudo_id)
"""
    row = next(client.query(query).result())
    return int(row.new_users), int(row.retained_users), float(row.d1)


def query_correlations(
    client: bigquery.Client,
    *,
    project_id: str,
    dataset: str,
    start_date: str,
    end_date: str,
) -> list[EventCorrelationRow]:
    start_token = date_token(start_date)
    end_token = date_token(end_date)
    retained_start = (
        datetime.strptime(start_date, "%Y-%m-%d").date().fromordinal(
            datetime.strptime(start_date, "%Y-%m-%d").date().toordinal() + 1
        )
    ).isoformat()
    retained_end = (
        datetime.strptime(end_date, "%Y-%m-%d").date().fromordinal(
            datetime.strptime(end_date, "%Y-%m-%d").date().toordinal() + 1
        )
    ).isoformat()
    query = f"""
WITH cohort AS (
  SELECT user_pseudo_id, PARSE_DATE('%Y%m%d', event_date) AS first_date
  FROM `{project_id}.{dataset}.events_*`
  WHERE event_name = 'first_open'
    AND _TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
),
retained AS (
  SELECT DISTINCT c.user_pseudo_id
  FROM cohort c
  JOIN `{project_id}.{dataset}.events_*` e
    ON e.user_pseudo_id = c.user_pseudo_id
   AND PARSE_DATE('%Y%m%d', e.event_date) = DATE_ADD(c.first_date, INTERVAL 1 DAY)
  WHERE e._TABLE_SUFFIX BETWEEN '{date_token(retained_start)}' AND '{date_token(retained_end)}'
),
d0_event_flags AS (
  SELECT DISTINCT c.user_pseudo_id, e.event_name
  FROM cohort c
  JOIN `{project_id}.{dataset}.events_*` e
    ON e.user_pseudo_id = c.user_pseudo_id
   AND PARSE_DATE('%Y%m%d', e.event_date) = c.first_date
  WHERE e._TABLE_SUFFIX BETWEEN '{start_token}' AND '{end_token}'
),
base AS (
  SELECT
    f.event_name,
    COUNT(DISTINCT f.user_pseudo_id) AS users_with_event,
    COUNT(DISTINCT IF(r.user_pseudo_id IS NOT NULL, f.user_pseudo_id, NULL)) AS retained_with_event,
    (SELECT COUNT(DISTINCT user_pseudo_id) FROM cohort) AS total_new_users,
    (SELECT COUNT(DISTINCT user_pseudo_id) FROM retained) AS total_retained_users
  FROM d0_event_flags f
  LEFT JOIN retained r USING (user_pseudo_id)
  GROUP BY 1
),
calc AS (
  SELECT
    event_name,
    users_with_event,
    retained_with_event,
    total_new_users - users_with_event AS users_without_event,
    total_retained_users - retained_with_event AS retained_without_event,
    SAFE_DIVIDE(retained_with_event, users_with_event) AS retention_with_event,
    SAFE_DIVIDE(total_retained_users - retained_with_event, total_new_users - users_with_event) AS retention_without_event
  FROM base
)
SELECT
  event_name,
  users_with_event,
  retained_with_event,
  retention_with_event,
  retention_without_event,
  retention_with_event - retention_without_event AS uplift_pp,
  SAFE_DIVIDE(
    retained_with_event * (users_without_event - retained_without_event)
    - (users_with_event - retained_with_event) * retained_without_event,
    SQRT(
      users_with_event * users_without_event *
      (retained_with_event + retained_without_event) *
      ((users_with_event - retained_with_event) + (users_without_event - retained_without_event))
    )
  ) AS phi
FROM calc
WHERE users_with_event >= 100
ORDER BY phi DESC
"""
    rows = []
    for row in client.query(query).result():
        if row.retention_with_event is None or row.retention_without_event is None:
            continue
        rows.append(
            EventCorrelationRow(
                event_name=row.event_name,
                users_with_event=int(row.users_with_event),
                retained_with_event=int(row.retained_with_event),
                retention_with_event=float(row.retention_with_event),
                retention_without_event=float(row.retention_without_event),
                uplift_pp=float(row.uplift_pp),
                phi=float(row.phi) if row.phi is not None else None,
            )
        )
    return rows


def is_actionable(name: str) -> bool:
    return name.startswith("ACT_") or name.startswith("CLK_")


def is_proxy(name: str) -> bool:
    proxy_prefixes = ("push_", "notification_", "th_", "firebase_", "ad_", "ump_", "device_")
    return name.startswith(proxy_prefixes) or name in {
        "app_remove",
        "page_view",
        "screen_view",
        "session_start",
        "user_engagement",
        "track_gclid",
        "track_push_user",
        "Total_Ads_Revenue_001",
    }


def render_table(rows: list[EventCorrelationRow]) -> list[str]:
    lines = [
        "| 事件 | 覆盖新用户 | 触发用户D1 | 未触发用户D1 | 差值 | Phi |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.event_name} | {row.users_with_event:,} ({pct(row.coverage)}) | {pct(row.retention_with_event)} | {pct(row.retention_without_event)} | {pp(row.uplift_pp)} | {row.phi:.4f} |"
        )
    return lines


def render_html_table(rows: list[EventCorrelationRow], negative: bool = False) -> str:
    html_rows = []
    for row in rows:
        diff_class = "num-bad" if negative else "num-good"
        html_rows.append(
            f"<tr><td>{html.escape(row.event_name)}</td><td class=\"mono\">{row.users_with_event:,} ({pct(row.coverage)})</td><td class=\"mono\">{pct(row.retention_with_event)}</td><td class=\"mono\">{pct(row.retention_without_event)}</td><td class=\"mono {diff_class}\">{pp(row.uplift_pp)}</td><td class=\"mono\">{row.phi:.4f}</td></tr>"
        )
    return "".join(html_rows)


def main() -> int:
    global TOTAL_NEW_USERS, TOTAL_RETAINED_USERS, BASELINE_D1
    args = parse_args()
    client = bq_client(args.project_id, args.credentials)
    TOTAL_NEW_USERS, TOTAL_RETAINED_USERS, BASELINE_D1 = query_baseline(
        client,
        project_id=args.project_id,
        dataset=args.dataset,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    rows = query_correlations(
        client,
        project_id=args.project_id,
        dataset=args.dataset,
        start_date=args.start_date,
        end_date=args.end_date,
    )

    positive_actionable = [r for r in rows if is_actionable(r.event_name) and r.uplift_pp > 0][:12]
    negative_actionable = sorted(
        [r for r in rows if is_actionable(r.event_name) and r.uplift_pp < 0],
        key=lambda r: r.phi or 0,
    )[:12]
    proxy_positive = [r for r in rows if is_proxy(r.event_name) and r.uplift_pp > 0][:10]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.strptime(args.end_date, "%Y-%m-%d").strftime("%m%d")
    base_name = f"{args.project_name}_d1_retention_event_correlation_{stamp}"
    md_path = output_dir / f"{base_name}.md"
    html_path = output_dir / f"{base_name}.html"

    insights = [
        f"基线 D1 retention 为 `{pct(BASELINE_D1)}`，样本为 `{TOTAL_NEW_USERS:,}` 个新用户，其中 `{TOTAL_RETAINED_USERS:,}` 在 D1 回访。",
        "正相关事件以功能探索、记录保存、目标设定和测量链路为主，说明用户在首日完成“具体任务闭环”时，次留显著更高。",
        "负相关事件集中在插屏、权限请求、设置页和首页切换，更多像是打断、试探或问题排查信号，不宜直接当成正向激活指标。",
        "Push/通知类事件与 D1 的相关性最高，但它们大概率是用户状态代理变量，不是首选的产品优化抓手。",
    ]

    md_lines = [
        f"# {args.project_name} 新用户事件与次留相关性分析",
        "",
        "## 分析范围",
        f"- 项目：`{args.project_name}`",
        f"- 数据源：`{args.project_id}.{args.dataset}.events_*`",
        f"- Cohort 周期：`{args.start_date}` ~ `{args.end_date}`",
        "- 新用户口径：首日触发 `first_open`",
        "- 次留口径：次日任意事件回访",
        "- 事件口径：仅统计新用户在 `D0` 首日是否触发过该事件",
        "- 相关性指标：`Phi coefficient`，同时展示“触发组 D1 - 未触发组 D1”的 retention 差值",
        "",
        "## 总体结论",
    ]
    md_lines.extend(f"- {item}" for item in insights)
    md_lines.extend(
        [
            "",
            "## 核心 KPI",
            f"- Cohort 新用户数：`{TOTAL_NEW_USERS:,}`",
            f"- D1 回访用户数：`{TOTAL_RETAINED_USERS:,}`",
            f"- 基线 D1 retention：`{pct(BASELINE_D1)}`",
            "",
            "## 优先关注的正相关产品事件",
            "优先级判断标准：覆盖新用户至少约 5%，且触发后 D1 retention 显著高于未触发组。",
            "",
        ]
    )
    md_lines.extend(render_table(positive_actionable))
    md_lines.extend(
        [
            "",
            "## 需要警惕的负相关产品事件",
            "这些事件更像是打断、困惑或无效游走信号，适合拿来做优化排查。",
            "",
        ]
    )
    md_lines.extend(render_table(negative_actionable))
    md_lines.extend(
        [
            "",
            "## 高相关但偏系统代理的事件",
            "这类事件的相关性高，但通常不适合直接作为产品功能优化目标；更适合作为用户分层特征或补充解释变量。",
            "",
        ]
    )
    md_lines.extend(render_table(proxy_positive))
    md_lines.extend(
        [
            "",
            "## 运营与产品建议",
            "- **P0**：围绕“首日任务闭环”补强路径，把 `ACT_EnterFunctionDetailPage`、`ACT_EnterWaterIntakeGoalPage`、`ACT_EnterHeartRateMeasurePage`、`CLK_SaveFunctionRecord` 这类事件前置到新手路径里。",
            "- **P1**：对 `ACT_ShowInterstitial`、`ACT_ShowPermissionRequest`、`ACT_PermissionRequestSuccess` 建立首日分版本监控，优先排查其是否发生在关键任务前，是否对激活路径造成打断。",
            "- **P2**：把用户分成“首日完成记录/设置目标/进入功能详情”和“未完成任务闭环”两组，继续比较 D3、D7 retention 和付费/广告价值，验证这些事件是否真的是长期价值代理。",
            "",
            "## 方法与限制",
            "- 这是相关性分析，不是因果证明；高相关只能说明“同现”，不能直接证明该事件导致了高次留。",
            "- 首日事件可能受到广告、Push、权限请求、技术埋点时序影响，因此系统事件需要单独解读。",
            "- 本次未按平台、版本、国家、渠道拆分；如果要进入执行层，建议下一步按 `platform + app_version` 做二次分析。",
            f"- Generated from `{md_path.resolve()}`",
        ]
    )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    html_content = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(args.project_name)} 新用户事件与次留相关性分析</title>
  <style>
    :root {{
      --bg: #f4f6f8; --card: #ffffff; --ink: #14212b; --muted: #5c6b78; --line: #d8e0e7;
      --brand: #1f6f8b; --brand-soft: #e6f2f7; --good: #1f8a5b; --warn: #b86d00; --bad: #b42318;
      --shadow: 0 8px 24px rgba(16, 24, 40, 0.08); --radius: 14px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: "SF Pro Text", "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
      color: var(--ink);
      background: radial-gradient(circle at 80% -20%, #d7eef9 0%, transparent 45%), radial-gradient(circle at 0% 120%, #e9f7ef 0%, transparent 42%), var(--bg);
      line-height: 1.45;
    }}
    .container {{ width: min(1200px, 92vw); margin: 28px auto 40px; }}
    .header {{ background: linear-gradient(130deg, #10384c 0%, #1f6f8b 58%, #4a9fb4 100%); color: #fff; border-radius: 18px; padding: 24px 26px; box-shadow: var(--shadow); }}
    .title {{ margin: 0; font-size: 28px; letter-spacing: .2px; }}
    .subtitle {{ margin: 8px 0 0; color: #d8edf5; font-size: 14px; }}
    .section {{ background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); box-shadow: var(--shadow); margin-top: 16px; padding: 18px 18px 14px; }}
    .section h2 {{ margin: 0 0 12px; font-size: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .metric {{ border: 1px solid var(--line); border-radius: 12px; background: #fbfdff; padding: 12px; }}
    .metric .k {{ color: var(--muted); font-size: 12px; }}
    .metric .v {{ margin-top: 6px; font-size: 20px; font-weight: 700; }}
    .metric .sub {{ margin-top: 4px; font-size: 12px; color: var(--muted); }}
    ul {{ margin: 8px 0 0 0; padding-left: 20px; }}
    li {{ margin: 6px 0; }}
    .table-wrap {{ overflow: auto; border: 1px solid var(--line); border-radius: 12px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 960px; background: #fff; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 10px 10px; text-align: left; vertical-align: top; font-size: 13px; }}
    th {{ background: #f3f8fb; color: #1f4f63; font-weight: 700; white-space: nowrap; }}
    tr:last-child td {{ border-bottom: none; }}
    .mono {{ font-variant-numeric: tabular-nums; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .num-good {{ color: var(--good); font-weight: 700; }}
    .num-bad {{ color: var(--bad); font-weight: 700; }}
    .note {{ border-left: 4px solid var(--brand); background: var(--brand-soft); color: #184356; padding: 10px 12px; border-radius: 8px; font-size: 13px; margin-bottom: 10px; }}
    .muted {{ color: var(--muted); }}
    @media (max-width: 860px) {{ .grid {{ grid-template-columns: 1fr; }} .title {{ font-size: 22px; }} .section {{ padding: 14px 14px 10px; }} }}
  </style>
</head>
<body>
  <main class="container">
    <header class="header">
      <h1 class="title">{html.escape(args.project_name)} 新用户事件与次留相关性分析</h1>
      <p class="subtitle">BigQuery 用户级事件分析 · Cohort：{args.start_date} ~ {args.end_date} · 生成日期：{date.today().isoformat()}</p>
    </header>

    <section class="section">
      <h2>总体结论</h2>
      <div class="grid">
        <div class="metric"><div class="k">Cohort 新用户数</div><div class="v mono">{TOTAL_NEW_USERS:,}</div><div class="sub">首日事件：first_open</div></div>
        <div class="metric"><div class="k">D1 回访用户数</div><div class="v mono">{TOTAL_RETAINED_USERS:,}</div><div class="sub">次日任意事件回访</div></div>
        <div class="metric"><div class="k">基线 D1 retention</div><div class="v mono">{pct(BASELINE_D1)}</div><div class="sub">全量新用户基线</div></div>
      </div>
      <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in insights)}</ul>
    </section>

    <section class="section">
      <h2>监控口径</h2>
      <div class="note">数据源：<span class="mono">{html.escape(args.project_id)}.{html.escape(args.dataset)}.events_*</span>；仅分析新用户 D0 是否触发某事件，与该用户 D1 是否回访之间的关系。</div>
    </section>

    <section class="section">
      <h2>优先关注的正相关产品事件</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>事件</th><th>覆盖新用户</th><th>触发用户D1</th><th>未触发用户D1</th><th>差值</th><th>Phi</th></tr></thead>
          <tbody>{render_html_table(positive_actionable)}</tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>需要警惕的负相关产品事件</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>事件</th><th>覆盖新用户</th><th>触发用户D1</th><th>未触发用户D1</th><th>差值</th><th>Phi</th></tr></thead>
          <tbody>{render_html_table(negative_actionable, negative=True)}</tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>高相关但偏系统代理的事件</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>事件</th><th>覆盖新用户</th><th>触发用户D1</th><th>未触发用户D1</th><th>差值</th><th>Phi</th></tr></thead>
          <tbody>{render_html_table(proxy_positive)}</tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>运营与产品建议</h2>
      <ul>
        <li><strong>P0：</strong>把“进入功能详情 → 设置目标/开始测量 → 保存记录”的首日任务闭环前置到新手路径和首页推荐位。</li>
        <li><strong>P1：</strong>把插屏、权限请求、首页切换作为首日流失监控对象，重点排查是否在关键任务前发生打断。</li>
        <li><strong>P2：</strong>下一步按 <span class="mono">platform + app_version</span> 继续拆，确认这些相关性是否集中在某个端或某个版本。</li>
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
