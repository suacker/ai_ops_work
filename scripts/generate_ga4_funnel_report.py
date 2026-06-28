#!/usr/bin/env python3
"""
Generate a professional Markdown + HTML funnel report for a GA4 event funnel.
"""

from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

from ga4_new_user_home_conversion import build_client, run_query


@dataclass
class DailyTrendRow:
    date: str
    new_users: int
    converted_users: int
    lost_users: int
    conversion_rate: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a GA4 funnel report with daily trend and HTML output."
    )
    parser.add_argument("--property-id", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--credentials", required=True)
    parser.add_argument("--new-user-event", default="first_open")
    parser.add_argument("--target-event", required=True)
    parser.add_argument("--target-param", action="append", default=[])
    parser.add_argument("--output-dir", default="reports/ga4_funnel")
    return parser.parse_args()


def parse_key_value_pairs(values: Iterable[str]) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for raw in values:
        if "=" not in raw:
            raise ValueError(f"Invalid target param: {raw!r}")
        key, value = raw.split("=", 1)
        pairs[key.strip()] = value.strip()
    return pairs


def iter_dates(start_date: str, end_date: str) -> list[str]:
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    dates: list[str] = []
    current = start
    while current <= end:
        dates.append(current.isoformat())
        current += timedelta(days=1)
    return dates


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def run_daily_trend(
    *,
    property_id: str,
    credentials: str,
    start_date: str,
    end_date: str,
    new_user_event: str,
    target_event: str,
    target_params: dict[str, str],
) -> list[DailyTrendRow]:
    client = build_client(credentials)
    rows: list[DailyTrendRow] = []
    for day in iter_dates(start_date, end_date):
        result = run_query(
            client=client,
            property_id=property_id,
            start_date=day,
            end_date=day,
            new_user_event=new_user_event,
            target_event=target_event,
            target_params=target_params,
            is_open_funnel=False,
        )
        converted = result.converted_users
        new_users = result.new_users
        lost = max(new_users - converted, 0)
        rate = result.conversion_rate or 0.0
        rows.append(
            DailyTrendRow(
                date=day,
                new_users=new_users,
                converted_users=converted,
                lost_users=lost,
                conversion_rate=rate,
            )
        )
    return rows


def build_summary(rows: list[DailyTrendRow]) -> dict[str, object]:
    total_new_users = sum(row.new_users for row in rows)
    total_converted_users = sum(row.converted_users for row in rows)
    total_lost_users = sum(row.lost_users for row in rows)
    overall_rate = total_converted_users / total_new_users if total_new_users else 0.0

    best_day = max(rows, key=lambda row: row.conversion_rate)
    worst_day = min(rows, key=lambda row: row.conversion_rate)
    avg_daily_new_users = total_new_users / len(rows) if rows else 0.0
    avg_daily_converted_users = total_converted_users / len(rows) if rows else 0.0
    last_rate_delta = rows[-1].conversion_rate - rows[0].conversion_rate if len(rows) >= 2 else 0.0

    return {
        "total_new_users": total_new_users,
        "total_converted_users": total_converted_users,
        "total_lost_users": total_lost_users,
        "overall_rate": overall_rate,
        "avg_daily_new_users": avg_daily_new_users,
        "avg_daily_converted_users": avg_daily_converted_users,
        "best_day": best_day,
        "worst_day": worst_day,
        "last_rate_delta": last_rate_delta,
    }


def build_insights(summary: dict[str, object], rows: list[DailyTrendRow]) -> list[str]:
    best_day = summary["best_day"]
    worst_day = summary["worst_day"]
    assert isinstance(best_day, DailyTrendRow)
    assert isinstance(worst_day, DailyTrendRow)
    last_rate_delta = float(summary["last_rate_delta"])
    overall_rate = float(summary["overall_rate"])
    total_lost_users = int(summary["total_lost_users"])

    insights = [
        f"监控期内新用户进入主界面整体转化率为 `{pct(overall_rate)}`，7 日累计有 `{total_lost_users}` 名新用户在主界面前流失。",
        f"最佳单日出现在 `{best_day.date}`，转化率 `{pct(best_day.conversion_rate)}`；最弱单日为 `{worst_day.date}`，转化率 `{pct(worst_day.conversion_rate)}`。",
    ]
    if last_rate_delta >= 0:
        insights.append(
            f"首尾两日对比，转化率提升 `{last_rate_delta * 100:.2f}` 个百分点，近期主界面到达效率呈修复趋势。"
        )
    else:
        insights.append(
            f"首尾两日对比，转化率下滑 `{abs(last_rate_delta) * 100:.2f}` 个百分点，需优先排查首启链路或首页前置拦截。"
        )

    low_days = [row for row in rows if row.conversion_rate < overall_rate]
    if low_days:
        insights.append(
            "低于区间均值的日期有："
            + "、".join(f"`{row.date}`({pct(row.conversion_rate)})" for row in low_days)
            + "。"
        )
    return insights


def build_actions(summary: dict[str, object], rows: list[DailyTrendRow]) -> list[tuple[str, str]]:
    worst_day = summary["worst_day"]
    assert isinstance(worst_day, DailyTrendRow)
    overall_rate = float(summary["overall_rate"])
    actions = [
        (
            "P0",
            f"对 `{worst_day.date}` 前后版本、首启权限弹窗、远端配置和首页加载链路做逐步排查，优先确认 `ACT_EnterHomePage` 是否因崩溃、卡顿或埋点缺失导致转化下探。",
        ),
        (
            "P1",
            f"将新用户进入主界面转化率设为日监控 KPI，建议预警线先设在 `{pct(overall_rate)}` 以下 `3` 个百分点，即 `{(overall_rate - 0.03) * 100:.2f}%`。",
        ),
        (
            "P2",
            "补充首启关键节点事件，如权限弹窗展示/确认、冷启动完成、首页接口成功返回，以便拆解流失到底发生在启动、鉴权还是首页渲染阶段。",
        ),
    ]
    return actions


def render_markdown(
    *,
    project_name: str,
    property_id: str,
    start_date: str,
    end_date: str,
    new_user_event: str,
    target_event: str,
    target_params: dict[str, str],
    summary: dict[str, object],
    rows: list[DailyTrendRow],
    md_path: Path,
) -> str:
    insights = build_insights(summary, rows)
    actions = build_actions(summary, rows)
    params_text = json.dumps(target_params, ensure_ascii=False) if target_params else "无"

    lines = [
        f"# {project_name} 新用户进入主界面漏斗报告",
        "",
        "## 报告范围",
        f"- 项目：`{project_name}`",
        f"- GA4 Property ID：`{property_id}`",
        f"- 统计周期：`{start_date}` ~ `{end_date}`（7 个完整自然日）",
        f"- 漏斗定义：`{new_user_event}` → `{target_event}`",
        f"- 目标事件参数：`{params_text}`",
        f"- 统计口径：闭漏斗，仅统计先发生 `{new_user_event}`、后发生 `{target_event}` 的新用户",
        "",
        "## 总体结论",
    ]
    lines.extend(f"- {item}" for item in insights)
    lines.extend(
        [
            "",
            "## 核心 KPI",
            f"- 7日累计新用户：`{int(summary['total_new_users']):,}`",
            f"- 日均新用户：`{summary['avg_daily_new_users']:.1f}`",
            f"- 7日累计进入主界面用户：`{int(summary['total_converted_users']):,}`",
            f"- 日均进入主界面用户：`{summary['avg_daily_converted_users']:.1f}`",
            f"- 7日累计流失用户：`{int(summary['total_lost_users']):,}`",
            f"- 7日整体转化率：`{pct(float(summary['overall_rate']))}`",
            "",
            "## 每日趋势表",
            "",
            "| 日期 | 新用户数 | 进入主界面用户数 | 流失用户数 | 转化率 |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.date} | {row.new_users} | {row.converted_users} | {row.lost_users} | {pct(row.conversion_rate)} |"
        )

    lines.extend(["", "## 异常与风险定位"])
    worst_day = summary["worst_day"]
    best_day = summary["best_day"]
    assert isinstance(worst_day, DailyTrendRow)
    assert isinstance(best_day, DailyTrendRow)
    lines.extend(
        [
            f"- 低点日期：`{worst_day.date}`，转化率仅 `{pct(worst_day.conversion_rate)}`，较最佳日低 `{(best_day.conversion_rate - worst_day.conversion_rate) * 100:.2f}` 个百分点。",
            f"- 7日流失量最高的日期为 `{max(rows, key=lambda row: row.lost_users).date}`，说明该日首页前链路阻塞最明显。",
            "- 当前只有两步漏斗，能够判断“是否进入主界面”，但还不能精确拆出卡在哪个前置节点；需要补埋点才能继续下钻。",
            "",
            "## 动作建议",
        ]
    )
    for priority, text in actions:
        lines.append(f"- **{priority}**：{text}")

    lines.extend(
        [
            "",
            "## 方法与置信度说明",
            "- 数据来源：GA4 Data API Funnel Report。",
            f"- 新用户口径使用事件 `{new_user_event}`，因此更接近 App 首次打开用户，而不是任意去重安装口径。",
            f"- 主界面到达口径使用事件 `{target_event}`；若该事件存在漏记、延迟上报或多端混用，转化率会被低估。",
            "- 本报告未按平台、版本、国家或流量来源拆分，适合先看总盘趋势，不适合作为版本归因结论的最终依据。",
            f"- Generated from `{md_path}`",
        ]
    )
    return "\n".join(lines) + "\n"


def render_html(
    *,
    project_name: str,
    property_id: str,
    start_date: str,
    end_date: str,
    new_user_event: str,
    target_event: str,
    target_params: dict[str, str],
    summary: dict[str, object],
    rows: list[DailyTrendRow],
    md_path: Path,
) -> str:
    best_day = summary["best_day"]
    worst_day = summary["worst_day"]
    assert isinstance(best_day, DailyTrendRow)
    assert isinstance(worst_day, DailyTrendRow)
    insights = build_insights(summary, rows)
    actions = build_actions(summary, rows)
    max_rate = max((row.conversion_rate for row in rows), default=0.0)
    params_text = json.dumps(target_params, ensure_ascii=False) if target_params else "无"

    trend_bars = []
    for row in rows:
        height = 0 if max_rate == 0 else max(18, round((row.conversion_rate / max_rate) * 160))
        trend_bars.append(
            f"""
            <div class="bar-item">
              <div class="bar-value">{pct(row.conversion_rate)}</div>
              <div class="bar" style="height:{height}px"></div>
              <div class="bar-label">{row.date[5:]}</div>
            </div>
            """
        )

    table_rows = []
    for row in rows:
        css = "num-good" if row.conversion_rate >= float(summary["overall_rate"]) else "num-bad"
        table_rows.append(
            f"<tr><td>{row.date}</td><td class=\"mono\">{row.new_users}</td><td class=\"mono\">{row.converted_users}</td><td class=\"mono\">{row.lost_users}</td><td class=\"mono {css}\">{pct(row.conversion_rate)}</td></tr>"
        )

    action_items = "".join(f"<li><strong>{p}：</strong>{html.escape(text)}</li>" for p, text in actions)
    insight_items = "".join(f"<li>{html.escape(text)}</li>" for text in insights)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(project_name)} 新用户进入主界面漏斗报告</title>
  <style>
    :root {{
      --bg: #f4f6f8;
      --card: #ffffff;
      --ink: #14212b;
      --muted: #5c6b78;
      --line: #d8e0e7;
      --brand: #1f6f8b;
      --brand-soft: #e6f2f7;
      --good: #1f8a5b;
      --warn: #b86d00;
      --bad: #b42318;
      --shadow: 0 8px 24px rgba(16, 24, 40, 0.08);
      --radius: 14px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "SF Pro Text", "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 80% -20%, #d7eef9 0%, transparent 45%),
        radial-gradient(circle at 0% 120%, #e9f7ef 0%, transparent 42%),
        var(--bg);
      line-height: 1.45;
    }}
    .container {{ width: min(1200px, 92vw); margin: 28px auto 40px; }}
    .header {{
      background: linear-gradient(130deg, #10384c 0%, #1f6f8b 58%, #4a9fb4 100%);
      color: #fff;
      border-radius: 18px;
      padding: 24px 26px;
      box-shadow: var(--shadow);
    }}
    .title {{ margin: 0; font-size: 28px; letter-spacing: .2px; }}
    .subtitle {{ margin: 8px 0 0; color: #d8edf5; font-size: 14px; }}
    .section {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      margin-top: 16px;
      padding: 18px 18px 14px;
    }}
    .section h2 {{ margin: 0 0 12px; font-size: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .metric {{ border: 1px solid var(--line); border-radius: 12px; background: #fbfdff; padding: 12px; }}
    .metric .k {{ color: var(--muted); font-size: 12px; }}
    .metric .v {{ margin-top: 6px; font-size: 20px; font-weight: 700; }}
    .metric .sub {{ margin-top: 4px; font-size: 12px; color: var(--muted); }}
    .badge {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 2px 10px;
      font-size: 12px;
      font-weight: 600;
      border: 1px solid transparent;
    }}
    .b-good {{ color: var(--good); background: #eafaf2; border-color: #bfe8d2; }}
    .b-warn {{ color: var(--warn); background: #fff6e8; border-color: #f2d5a2; }}
    .b-bad {{ color: var(--bad); background: #fff0ef; border-color: #f2b8b5; }}
    .num-good {{ color: var(--good); font-weight: 700; }}
    .num-bad {{ color: var(--bad); font-weight: 700; }}
    .table-wrap {{ overflow: auto; border: 1px solid var(--line); border-radius: 12px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 900px; background: #fff; }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 10px 10px;
      text-align: left;
      vertical-align: top;
      font-size: 13px;
    }}
    th {{ background: #f3f8fb; color: #1f4f63; font-weight: 700; white-space: nowrap; }}
    tr:last-child td {{ border-bottom: none; }}
    .mono {{ font-variant-numeric: tabular-nums; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .note {{
      border-left: 4px solid var(--brand);
      background: var(--brand-soft);
      color: #184356;
      padding: 10px 12px;
      border-radius: 8px;
      font-size: 13px;
      margin-bottom: 10px;
    }}
    .muted {{ color: var(--muted); }}
    ul {{ margin: 8px 0 0 0; padding-left: 20px; }}
    li {{ margin: 6px 0; }}
    .trend {{
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 12px;
      align-items: end;
      min-height: 220px;
      padding: 12px 8px 0;
    }}
    .bar-item {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
    }}
    .bar-value {{
      font-size: 12px;
      color: var(--muted);
      font-variant-numeric: tabular-nums;
    }}
    .bar {{
      width: 56px;
      border-radius: 12px 12px 0 0;
      background: linear-gradient(180deg, #68b3ca 0%, #1f6f8b 100%);
      box-shadow: inset 0 -1px 0 rgba(255,255,255,0.24);
    }}
    .bar-label {{
      font-size: 12px;
      color: var(--muted);
      font-variant-numeric: tabular-nums;
    }}
    @media (max-width: 860px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .trend {{ grid-template-columns: repeat(2, minmax(0, 1fr)); min-height: auto; }}
      .title {{ font-size: 22px; }}
      .section {{ padding: 14px 14px 10px; }}
      .bar {{ width: 100%; max-width: 72px; }}
    }}
  </style>
</head>
<body>
  <main class="container">
    <header class="header">
      <h1 class="title">{html.escape(project_name)} 新用户进入主界面漏斗报告</h1>
      <p class="subtitle">GA4 Funnel Report · 统计周期：{start_date} ~ {end_date} · 生成日期：{date.today().isoformat()}</p>
    </header>

    <section class="section">
      <h2>总体结论</h2>
      <div class="grid">
        <div class="metric"><div class="k">7日累计新用户</div><div class="v mono">{int(summary['total_new_users']):,}</div><div class="sub">事件：{html.escape(new_user_event)}</div></div>
        <div class="metric"><div class="k">日均新用户</div><div class="v mono">{summary['avg_daily_new_users']:.1f}</div><div class="sub">用于衡量首启流量规模</div></div>
        <div class="metric"><div class="k">7日累计主界面到达</div><div class="v mono">{int(summary['total_converted_users']):,}</div><div class="sub">事件：{html.escape(target_event)}</div></div>
        <div class="metric"><div class="k">7日整体转化率</div><div class="v mono">{pct(float(summary['overall_rate']))}</div><div class="sub">闭漏斗：首启后进入主界面</div></div>
      </div>
      <ul>{insight_items}</ul>
    </section>

    <section class="section">
      <h2>监控口径</h2>
      <div class="note">GA4 Property ID：<span class="mono">{property_id}</span>；漏斗定义：<span class="mono">{html.escape(new_user_event)} → {html.escape(target_event)}</span>；目标事件参数：<span class="mono">{html.escape(params_text)}</span>。</div>
      <div class="grid">
        <div class="metric"><div class="k">最佳单日</div><div class="v mono">{best_day.date}</div><div class="sub num-good">{pct(best_day.conversion_rate)}</div></div>
        <div class="metric"><div class="k">最弱单日</div><div class="v mono">{worst_day.date}</div><div class="sub num-bad">{pct(worst_day.conversion_rate)}</div></div>
        <div class="metric"><div class="k">累计流失用户</div><div class="v mono">{int(summary['total_lost_users']):,}</div><div class="sub">未进入主界面的新用户</div></div>
        <div class="metric"><div class="k">首尾日变化</div><div class="v mono">{summary['last_rate_delta'] * 100:+.2f}pp</div><div class="sub">用于观察短期修复趋势</div></div>
      </div>
    </section>

    <section class="section">
      <h2>每日转化率趋势</h2>
      <div class="trend">
        {''.join(trend_bars)}
      </div>
    </section>

    <section class="section">
      <h2>每日趋势明细</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>日期</th><th>新用户数</th><th>进入主界面用户数</th><th>流失用户数</th><th>转化率</th></tr>
          </thead>
          <tbody>
            {''.join(table_rows)}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>动作建议</h2>
      <ul>{action_items}</ul>
    </section>

    <section class="section">
      <h2>方法与置信度说明</h2>
      <ul>
        <li>数据直接来自 GA4 Data API Funnel Report，无本地估算或人工补值。</li>
        <li>新用户口径使用 <span class="mono">{html.escape(new_user_event)}</span>，结果反映的是“首次打开后进入主界面”的转化，而非严格安装归因口径。</li>
        <li>若 <span class="mono">{html.escape(target_event)}</span> 存在埋点缺失、延迟、跨端不一致或重命名，报告会低估真实转化率。</li>
        <li>当前未按平台、版本、国家、渠道拆分，因此适合做总盘监控，不适合作为单版本归因的最终结论。</li>
      </ul>
      <p class="muted" style="margin:10px 0 4px; font-size:12px;">Generated from {html.escape(str(md_path))}</p>
    </section>
  </main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    target_params = parse_key_value_pairs(args.target_param)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.strptime(args.end_date, "%Y-%m-%d").strftime("%m%d")
    base_name = f"{args.project_name}_new_user_home_funnel_{stamp}"
    md_path = output_dir / f"{base_name}.md"
    html_path = output_dir / f"{base_name}.html"

    rows = run_daily_trend(
        property_id=args.property_id,
        credentials=args.credentials,
        start_date=args.start_date,
        end_date=args.end_date,
        new_user_event=args.new_user_event,
        target_event=args.target_event,
        target_params=target_params,
    )
    summary = build_summary(rows)
    md_content = render_markdown(
        project_name=args.project_name,
        property_id=args.property_id,
        start_date=args.start_date,
        end_date=args.end_date,
        new_user_event=args.new_user_event,
        target_event=args.target_event,
        target_params=target_params,
        summary=summary,
        rows=rows,
        md_path=md_path.resolve(),
    )
    html_content = render_html(
        project_name=args.project_name,
        property_id=args.property_id,
        start_date=args.start_date,
        end_date=args.end_date,
        new_user_event=args.new_user_event,
        target_event=args.target_event,
        target_params=target_params,
        summary=summary,
        rows=rows,
        md_path=md_path.resolve(),
    )

    md_path.write_text(md_content, encoding="utf-8")
    html_path.write_text(html_content, encoding="utf-8")

    print(md_path.resolve())
    print(html_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
