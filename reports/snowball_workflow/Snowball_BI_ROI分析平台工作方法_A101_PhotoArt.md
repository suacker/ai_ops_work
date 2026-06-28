# Snowball BI 数据分析平台工作方法：ROI 报表

## 适用范围

- 平台：`https://snowball.thinkyeah.com`
- 项目：`A101 PhotoArt`
- 项目类型：Android App
- 包名：`photoeditor.photocollage.ai.editor.photoart`
- 主要用途：通过 Snowball BI 页面与 `snowball_mcp` 数据接口，分析 ROI、成本、回收周期、国家/渠道/Campaign 质量。

## 本次浏览器复现记录

| 步骤 | 操作 | 记录 |
| --- | --- | --- |
| 1 | 使用持久化浏览器 profile 打开 Chrome | `--user-data-dir=/Users/suacker/dev/DataAnalysis/BI/.chrome-profile` |
| 2 | 访问 ROI 自然增长报表 | `https://snowball.thinkyeah.com/bi/A101/overview/roi?tab=natural_growth_roi&from=2025-11-10&to=2026-05-08&day_period=monthly` |
| 3 | 确认项目 | `A101 PhotoArt` |
| 4 | 确认报表页签 | `tab=natural_growth_roi`，即自然增长 ROI |
| 5 | 确认日期范围 | `2025-11-10` ~ `2026-05-08` |
| 6 | 确认时间粒度 | `day_period=monthly`，即按月聚合 |
| 7 | 点击页面右侧蓝色 `查询` 按钮 | 查询后页面出现 `累计ROAS` 图表与 `ROI报表` 表格 |
| 8 | 记录查询后截图 | `/Users/suacker/dev/DataAnalysis/BI/output/playwright/snowball_roi_monthly_a101_20260508_after_query.png` |
| 9 | 使用 Snowball MCP 校验数据 | `get_roi_report(project_id="A101", day_period="monthly", dimension_list=["date"])` |

## ROI 页面 URL 参数说明

示例 URL：

```text
https://snowball.thinkyeah.com/bi/A101/overview/roi?tab=natural_growth_roi&from=2025-11-10&to=2026-05-08&day_period=monthly
```

| 参数 | 含义 | 示例 | 分析影响 |
| --- | --- | --- | --- |
| `A101` | 项目 ID | `A101` | 决定查询哪个产品 |
| `tab` | ROI 报表页签 | `natural_growth_roi` | 决定报表口径，本文为自然增长 ROI |
| `from` | 开始日期 | `2025-11-10` | 决定 cohort 起始范围 |
| `to` | 结束日期 | `2026-05-08` | 决定 cohort 结束范围 |
| `day_period` | 聚合粒度 | `monthly` | 决定按天、周、月等维度展示 |

常用粒度：

| 页面参数 | MCP 参数 | 用途 |
| --- | --- | --- |
| `daily` | `day_period="daily"` | 近几天监控、异常定位 |
| `weekly` | `day_period="weekly"` | 周报、投放节奏对比 |
| `monthly` | `day_period="monthly"` | 月度 cohort 回收与长期 ROI 分析 |

## 页面操作方法

### 1. 进入项目 ROI 报表

推荐直接使用 URL 进入，避免页面菜单路径变化影响效率：

```text
https://snowball.thinkyeah.com/bi/{project_id}/overview/roi
```

例如：

```text
https://snowball.thinkyeah.com/bi/A101/overview/roi
```

进入后确认三件事：

- 项目 ID 是否正确：`A101`
- 项目名称是否正确：`PhotoArt`
- 当前报表页签是否符合分析任务：例如 `natural_growth_roi`

### 2. 设置日期范围

日期范围要和分析目标一致：

| 任务 | 推荐范围 | 示例 |
| --- | --- | --- |
| 近 5 天监控 | 最近 5 个完整自然日，不含今天 | `2026-05-03 ~ 2026-05-07` |
| 月度累计 ROI | 覆盖多个完整月份 | `2025-11-10 ~ 2026-05-08` |
| 回本周期分析 | 至少覆盖 ROI90 或 ROI180 所需成熟期 | 近 6 个月以上 |

注意：当天数据通常不完整，日常监控默认不含今天。

### 3. 选择时间粒度

按月看累计 ROI 时，选择 `monthly`。页面中每一行通常代表一个月 cohort，例如：

- `2025-12-01` 表示 2025 年 12 月 cohort
- `2026-01-01` 表示 2026 年 1 月 cohort

### 4. 读取核心字段

设置完筛选条件后，必须点击页面右侧蓝色 `查询` 按钮。只有结果区域从“点击 查询，查看分析数据”切换为图表和 `ROI报表` 表格后，才可以开始分析。

ROI 报表必须优先读取以下字段：

| 字段 | 含义 | 判断方式 |
| --- | --- | --- |
| `costs / total_cost` | 花费 | 判断规模和预算压力 |
| `cpc_install` | 买量安装 | 判断样本量 |
| `cpi` | 单安装成本 | 判断买量成本 |
| `cohort_revenue` | cohort 收入 | 判断累计回收金额 |
| `cohort_profit` | cohort 利润 | 正数表示已盈利 |
| `roas` | 当前累计 ROAS | 衡量整体回收 |
| `roi0` | 首日 ROI | 早期质量信号 |
| `roi7 / roi14 / roi30` | 短中期 ROI | 判断回收爬坡速度 |
| `roi60 / roi90 / roi180` | 长周期 ROI | 判断最终能否回本 |

## Snowball MCP 对应取数方法

浏览器页面用于操作和核对，正式分析结论必须以 `snowball_mcp` 返回数据为准。

### 月度自然增长 ROI

```text
get_roi_report(
  project_id="A101",
  date_start="2025-11-10",
  date_end="2026-05-08",
  day_period="monthly",
  dimension_list=["date"],
  roi_fields=["roi0","roi1","roi3","roi7","roi14","roi30","roi60","roi90","roi180"],
  is_forecast=1
)
```

### 按国家拆解

用于判断哪个国家贡献了回本或亏损：

```text
get_roi_report(
  project_id="A101",
  date_start="YYYY-MM-DD",
  date_end="YYYY-MM-DD",
  day_period="daily/monthly",
  dimension_list=["date","country"],
  roi_fields=["roi0","roi7","roi30","roi60","roi90"],
  is_forecast=1
)
```

### 按买量计划拆解

用于定位 campaign 质量：

```text
get_roi_report(
  project_id="A101",
  date_start="YYYY-MM-DD",
  date_end="YYYY-MM-DD",
  day_period="daily",
  dimension_list=["date","campaign"],
  roi_fields=["roi0","roi1","roi3","roi7","roi14"],
  is_forecast=1
)
```

### 按广告组拆解

用于排查素材包、受众包、广告组学习状态：

```text
get_roi_report(
  project_id="A101",
  date_start="YYYY-MM-DD",
  date_end="YYYY-MM-DD",
  day_period="daily",
  dimension_list=["date","campaign","adgroup"],
  roi_fields=["roi0","roi1","roi3","roi7","roi14"],
  is_forecast=1
)
```

## 累计 ROI 分析框架

### 1. 先看是否回本

判断顺序：

1. `cohort_profit > 0`：已产生正利润。
2. `ROAS >= 100%`：当前累计回收已超过花费。
3. `ROI90 >= 100%`：90 天窗口已回本。
4. `ROI180 >= 100%`：长期预测或成熟窗口可能回本。

注意：带 `is_forecast=true` 的 ROI 只能作为参考，不能作为最终结论。

### 2. 再看回收速度

常用分层：

| 类型 | 典型表现 | 判断 |
| --- | --- | --- |
| 快速回收 | ROI7 或 ROI14 已接近 100% | 可积极放量 |
| 中期回收 | ROI30/ROI60 接近 100%，ROI90 回本 | 可控量放大 |
| 慢速回收 | ROI90 未回本，但 ROI180 预测回本 | 谨慎观察 |
| 无法回收 | ROI90/ROI180 都低于 100% | 需要降量或换流量结构 |

### 3. 拆解成本与质量

不要只看 CPI。必须同时看：

- CPI 是否下降
- ROI0 是否同步改善
- ROI30/ROI60/ROI90 是否能跟上
- cohort_profit 是否转正

典型误区：CPI 下降但 ROI90 下降，说明买到了更便宜但低质量的流量。

## 示例：2025 年 12 月 cohort

| 指标 | 数值 |
| --- | ---: |
| 花费 | `$19,143.91` |
| 买量安装 | `32,829` |
| CPI | `$0.5830` |
| Cohort Revenue | `$20,657.30` |
| Cohort Profit | `$1,513.39` |
| ROAS | `107.91%` |
| ROI0 | `37.72%` |
| ROI30 | `89.51%` |
| ROI60 | `97.54%` |
| ROI90 | `102.53%` |
| ROI180 | `111.51%`，预测值 |

结论：2025 年 12 月已经在 ROI90 回本，cohort_profit 为正。虽然 CPI 较高，但长期回收质量较好。

## 示例：2026 年 1 月 cohort

| 指标 | 数值 |
| --- | ---: |
| 花费 | `$28,749.72` |
| 买量安装 | `105,270` |
| CPI | `$0.2730` |
| Cohort Revenue | `$26,002.08` |
| Cohort Profit | `-$2,747.64` |
| ROAS | `90.44%` |
| ROI0 | `37.89%` |
| ROI30 | `76.39%` |
| ROI60 | `83.65%` |
| ROI90 | `88.06%` |
| ROI180 | `120.63%`，预测值 |

结论：2026 年 1 月 CPI 比 12 月明显降低，但成熟窗口 ROI90 仍未回本。该月属于“低成本但回收不足”，需要拆国家、渠道和 campaign 判断低价流量是否拉低 LTV。

## 标准分析输出模板

每次从 Snowball BI 分析 ROI 后，建议按以下结构输出：

```text
1. 报告范围
   - 项目
   - 日期范围
   - 时间粒度
   - 报表页签
   - 数据源

2. 核心 KPI
   - 花费
   - 日均/月均花费
   - 安装
   - CPI
   - cohort_revenue
   - cohort_profit
   - ROAS

3. 累计 ROI 曲线
   - ROI0
   - ROI1
   - ROI3
   - ROI7
   - ROI14
   - ROI30
   - ROI60
   - ROI90
   - ROI180

4. 结论
   - 是否回本
   - 回本发生在哪个周期
   - 成本变化
   - 回收质量变化

5. 异常定位
   - 国家
   - 渠道
   - campaign
   - adgroup

6. 动作建议
   - P0：立即执行
   - P1：24-48 小时
   - P2：本周跟进

7. 方法与置信度
   - 是否有预测值
   - 样本量是否足够
   - 是否需要补充维度
```

## 质量检查清单

- [ ] 页面项目 ID 与 MCP `project_id` 一致。
- [ ] 页面日期范围与 MCP `date_start/date_end` 一致。
- [ ] 页面时间粒度与 MCP `day_period` 一致。
- [ ] 设置筛选条件后已经点击页面右侧蓝色 `查询` 按钮。
- [ ] 页面结果区已出现图表和 `ROI报表` 表格，而不是空状态提示。
- [ ] ROI 展示为百分比，不展示为小数。
- [ ] CPI 展示为美元，保留 4 位小数用于精确判断。
- [ ] ROI 结论区分真实值和预测值。
- [ ] 不用单一 CPI 判断投放质量。
- [ ] 不用低样本计划做强结论。
- [ ] 关键结论必须能下钻到国家、渠道或 campaign。

## 工作方法总结

Snowball BI 页面适合做交互式定位和口径确认，Snowball MCP 适合做可复现的数据分析。实际工作中建议采用“双轨流程”：

1. 浏览器打开页面，确认项目、日期、粒度、页签。
2. 记录 URL 参数，转写为 MCP 查询参数。
3. 用 MCP 获取结构化数据。
4. 按 ROI 周期判断是否回本。
5. 对异常月份继续下钻国家、渠道、campaign、adgroup。
6. 输出 Markdown 报告，必要时生成 HTML 可视化。

这样可以避免只依赖页面截图，也可以保证后续复盘和报告生成时口径一致。
