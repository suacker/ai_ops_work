# StepTracker 买量作战日报

## 报告范围
- 日期范围：`2026-06-11` ~ `2026-06-17`
- 生成时间：`2026-06-18T13:10:00+08:00`
- 模式：`read_only`（只读建议，不执行平台写操作）

## 组合结论
StepTracker 近 7 天 Google 回收明显优于 Facebook；Facebook 平台消耗与 Snowball 成本基本对齐，但 ROI0/ROI3 偏弱，应先控 Meta 低质承接、保留 Google 小幅验证空间，并继续围绕健康走路类素材做变体。

## 核心 KPI
| 指标 | 数值 |
|---|---:|
| Snowball总花费 | $3,198.55 |
| Snowball买量安装 | 2,076 |
| 总体CPI | $1.5464 |
| 总体ROI0 | 36.34% |
| Google ROI3 | 60.04% |
| Facebook ROI3 | 29.63% |

## 项目排行与数据质量
| 项目 | 数据状态 | 置信度 | Spend | Installs | CPI | ROI0 | ROI3 | ROI7 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| A155 StepTracker | ready | high | $3,198.55 | 2076 | $1.5464 | 36.34% | 45.88% | 46.61% |

## 平台状态
| 项目 | Google | Facebook/Meta | TikTok |
|---|---|---|---|
| A155_StepTracker | ready | ready | inactive_no_data |

## P0/P1/P2 动作建议
| 优先级 | 对象 | 动作 | 置信度 | 原因 | 反馈状态 | 复盘日期 |
|---|---|---|---|---|---|---|
| P0 | Google / US-3.0-251231 | small_add | medium | Google 是当前唯一较强承接盘，ROI0/ROI3 优于 Facebook；但 ROI7/ROI14 仍有预测限制，建议只做小幅验证，不做激进放量。 | pending | 2026-06-19 |
| P0 | Facebook / US-IAA-260612 与 US-IAA-260616 | reduce_or_reallocate | high | 这两条计划平台 CTR 不差，但 CPI 和 Snowball ROI 明显弱，应把预算优先回收给 Google 或 Meta 01 中更稳的健康走路素材方向。 | pending | 2026-06-19 |
| P1 | Facebook / Step Tracker 02 | data_gap_check | medium | 账号 02 CTR 高但 CPM/CPI 高，需要继续拆 publisher_platform、placement 和 ad 层，确认是否 Audience Network 或低质版位拉高点击。 | pending | 2026-06-19 |
| P1 | Facebook / 260601 winner 素材系 | refresh_creative | medium | 历史 winner 当前仍有安装效率，但 Snowball ROI 已不突出；继续围绕 Lose Weight by Walking、步数、卡路里、心率/血压、免费 tracker 做变体，而不是直接扩大旧素材。 | pending | 2026-06-20 |
| P2 | Facebook / FB-US-ABO-IAA-VO-Targeted-Earn-260610 | maintain | medium | 该计划 ROI3 好于 260601 但仍不够强，适合维持观察与素材学习，不适合作为放量主承接。 | pending | 2026-06-19 |

## 风险与数据缺口
### A155_StepTracker
- 未执行任何 Meta/Google 写操作，本报告只提供动作建议。
- Snowball ROI7/ROI14 多为预测或 N/A，强动作主要依据 ROI0/ROI3、CPI、成本对账和平台安装效率。
- 本轮未重新下钻全量 ad/creative 明细，素材层结论继承历史 winner 方向并结合 campaign 表现。

## Source Refs
- A155_StepTracker：Snowball MCP list_projects(project_name=StepTracker)；Snowball MCP view_roi_report(A155, 2026-06-11~2026-06-17, network/campaign)；Snowball MCP view_profit_report(A155, 2026-06-11~2026-06-17, country)；Meta Ads CLI insights get, act_959455393396016, 2026-06-11~2026-06-17；Meta Ads CLI insights get, act_1302740031791808, 2026-06-11~2026-06-17；config/ad_account_registry.md

> Generated from `reports/ops_daily/steptracker/data/2026-06-17_diagnostics.json`
