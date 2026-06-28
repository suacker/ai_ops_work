# 多项目买量作战日报

## 报告范围
- 日期范围：`2026-06-11` ~ `2026-06-17`
- 生成时间：`2026-06-18T17:28:48+08:00`
- 模式：`read_only`（只读建议，不执行平台写操作）

## 组合结论
StepTracker 当前应保 Google、小幅控 Meta 低质计划；Weather&News 为高消耗 Google US 单 campaign，长期利润口径仍为正，但 ROI0、CPI、次留均未达 grow_base US 阈值，优先控价与补齐 Google Ads CLI 对账。

## 核心 KPI
| 指标 | 数值 |
|---|---:|
| 项目数 | 2 |
| Snowball总花费 | $19,437.93 |
| Snowball买量安装 | 25,905 |
| 组合CPI | $0.7504 |
| StepTracker ROI0 | 36.34% |
| Weather&News ROI0 | 47.53% |

## 项目排行与数据质量
| 项目 | 数据状态 | 置信度 | Spend | Installs | CPI | ROI0 | ROI3 | ROI7 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| A155 StepTracker | ready | high | $3,198.55 | 2076 | $1.5464 | 36.34% | 45.88% | 46.61% |
| A151 Weather&News | partial | medium | $16,239.38 | 23829 | $0.6822 | 47.53% | 59.88% | 64.41% |

## 平台状态
| 项目 | Google | Facebook/Meta | TikTok |
|---|---|---|---|
| A155_StepTracker | ready | ready | inactive_no_data |
| A151_Weather&News | partial | inactive_no_data | inactive_no_data |

## P0/P1/P2 动作建议
| 优先级 | 对象 | 动作 | 置信度 | 原因 | 反馈状态 | 复盘日期 |
|---|---|---|---|---|---|---|
| P0 | Google / US-3.0-251231 | small_add | medium | Google 是当前唯一较强承接盘，ROI0/ROI3 优于 Facebook；但 ROI7/ROI14 仍有预测限制，建议只做小幅验证，不做激进放量。 | pending | 2026-06-19 |
| P0 | Facebook / US-IAA-260612 与 US-IAA-260616 | reduce_or_reallocate | high | 这两条计划平台 CTR 不差，但 CPI 和 Snowball ROI 明显弱，应把预算优先回收给 Google 或 Meta 01 中更稳的健康走路素材方向。 | pending | 2026-06-19 |
| P1 | Facebook / Step Tracker 02 | data_gap_check | medium | 账号 02 CTR 高但 CPM/CPI 高，需要继续拆 publisher_platform、placement 和 ad 层，确认是否 Audience Network 或低质版位拉高点击。 | pending | 2026-06-19 |
| P1 | Facebook / 260601 winner 素材系 | refresh_creative | medium | 历史 winner 当前仍有安装效率，但 Snowball ROI 已不突出；继续围绕 Lose Weight by Walking、步数、卡路里、心率/血压、免费 tracker 做变体，而不是直接扩大旧素材。 | pending | 2026-06-20 |
| P2 | Facebook / FB-US-ABO-IAA-VO-Targeted-Earn-260610 | maintain | medium | 该计划 ROI3 好于 260601 但仍不够强，适合维持观察与素材学习，不适合作为放量主承接。 | pending | 2026-06-19 |
| P1 | Google / US-3.0-251028 | reduce_or_reallocate | medium | 当前 CPI $0.6822 高于 grow_base US 上限 $0.4886，ROI0 47.53% 低于 53.59% 阈值；建议人工复核后先控价或回收高成本流量，而不是继续加预算。 | pending | 2026-06-19 |
| P1 | Google Ads CLI / A151 account mapping | data_gap_check | medium | 需要补齐 Google Ads CLI 账号、campaign/ad group/asset 只读数据，验证 Snowball 成本、安装与平台侧状态是否一致，再决定具体预算迁移动作。 | pending | 2026-06-19 |
| P2 | Weather&News / US 素材与投放结构 | refresh_creative | low | 次留约 16.94% 低于 20.13% 基准，说明当前素材/流量承接质量不足；但未接入素材级平台数据，先作为素材刷新方向，不作为强素材淘汰结论。 | pending | 2026-06-20 |
| P2 | Facebook/Meta / Weather&News | no_action_no_data | high | 本地没有 A151 Meta 账号映射，且 Snowball 当前窗口未显示 Facebook 买量主链路；不生成 Meta 平台动作。 | pending | 2026-06-19 |

## 风险与数据缺口
### A155_StepTracker
- 未执行任何 Meta/Google 写操作，本报告只提供动作建议。
- Snowball ROI7/ROI14 多为预测或 N/A，强动作主要依据 ROI0/ROI3、CPI、成本对账和平台安装效率。
- 本轮未重新下钻全量 ad/creative 明细，素材层结论继承历史 winner 方向并结合 campaign 表现。
### A151_Weather&News
- 未执行任何 Google/Meta/TikTok 写操作，本报告只提供只读动作建议。
- Weather&News 本轮只有 Snowball 数据，没有 Google Ads CLI 素材、预算、出价、状态和账户层对账。
- A151 买量集中在 US 单 campaign，当前不能输出同项目内跨 campaign 预算迁移优先级。
- ROI7 多数仍为预测值，不能作为单独强放量依据。

## Source Refs
- A155_StepTracker：Snowball MCP list_projects(project_name=StepTracker)；Snowball MCP view_roi_report(A155, 2026-06-11~2026-06-17, network/campaign)；Snowball MCP view_profit_report(A155, 2026-06-11~2026-06-17, country)；Meta Ads CLI insights get, act_959455393396016, 2026-06-11~2026-06-17；Meta Ads CLI insights get, act_1302740031791808, 2026-06-11~2026-06-17；config/ad_account_registry.md
- A151_Weather&News：Snowball MCP list_projects(project_name=Weather, use_cache=false)；Snowball MCP view_roi_report(A151, 2026-06-11~2026-06-17, network)；Snowball MCP view_roi_report(A151, 2026-06-11~2026-06-17, country)；Snowball MCP view_roi_report(A151, 2026-06-11~2026-06-17, google campaign)；Snowball MCP view_profit_report(A151, 2026-06-11~2026-06-17, country)；grow_base/A151_Weather_News.md；config/ad_account_registry.md

> Generated from `reports/ops_daily/data/2026-06-17_diagnostics.json`
