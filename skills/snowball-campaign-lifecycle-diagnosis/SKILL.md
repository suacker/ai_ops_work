---
name: snowball-campaign-lifecycle-diagnosis
description: 基于 Snowball MCP 对单项目买量 Campaign 做生命周期诊断，输出数据质量、投放状态、平台状态、上下文保护、生命周期阶段与今日动作建议。适用于“campaign 生命周期诊断”“买量判断底座”“是否放量/观察/预算迁移”“生成日报前的结构化诊断”等场景。
---

# Snowball Campaign 生命周期诊断

## 目标

把买量判断从报告展示中拆出来，作为可复用诊断层：

`Snowball 数据 -> 数据质量 -> 投放状态 -> 平台状态 -> 上下文保护 -> 生命周期阶段 -> 今日动作建议`

本 Skill 只负责判断，不负责最终日报排版。日报、周报、飞书报告可以复用诊断结果。

## 输入

- `project_id` 或项目名；只有项目名时先用 `mcp__snowball_mcp.get_projects` 解析。
- 日期范围；默认最近 7 个完整自然日，不含当天。若用户指定日期，以用户范围为准。
- 可选过滤：`network_list`、`country_list`、`campaign_list`、`adgroup_list`。
- 可选输出粒度：默认 `network + country + campaign`；需要 Google 局部问题时追加 `adgroup`。

## 数据源

所有定量指标必须来自 `mcp__snowball_mcp`，禁止编造、补全或用本地缓存替代。

主查询：

```text
get_roi_report(
  project_id,
  date_start,
  date_end,
  day_period="daily",
  dimension_list=["date", "network", "country", "campaign"],
  roi_fields=["roi_0", "roi_3", "roi_7"],
  is_forecast=1
)
```

补充查询：

- 按渠道单独查询 Google / Facebook，验证是否有数据。
- 需要国家盈利背景时调用 `get_profit_chart`。
- 需要广告变现归因时调用广告收入相关工具。

## 诊断顺序

### 1. 数据质量

判断是否具备强判断条件：

- 是否有 ROI 数据。
- 是否有有效花费、安装、Campaign 维度。
- ROI7 是否为预测值；预测值只能增强观察，不单独作为强放量依据。
- 是否缺少平台 learning、素材、预算调整、ad/adset 等上下文。
- Snowball 返回 `-1` 时标记为 N/A，不当作 0。

输出字段：

- `data_status`: `ready` / `partial` / `inactive_no_data` / `data_gap_risk`
- `confidence`: `high` / `medium` / `low`
- `limitations`: 数据限制列表

### 2. 投放状态

按 network / country / campaign 聚合：

- `cost`
- `installs` 或 `cpc_install`
- `cpi`
- `roi0`
- `roi3`
- `roi7`
- `cohort_revenue`
- `cohort_profit`

默认以 ROI 报表返回的总计或聚合值为准。若自行聚合，必须说明计算口径。

### 3. 平台状态

按平台分别处理：

- Google 有数据：允许做国家和 Campaign 生命周期判断。
- Facebook/Meta 无数据：标记 `inactive_no_data`，不得生成加预算、降预算、换素材或关停建议。
- Facebook/Meta 有数据但缺 ad/adset/creative：只做 campaign/国家层判断，并说明素材层不可强判断。

### 4. 上下文保护

在输出动作前先降级不可靠判断：

- 新 Campaign / 低花费：只给测试或观察，不强关停。
- 最近几天 ROI 未成熟：ROI7 预测只能作为辅助。
- 缺少平台 learning 状态：不能断言学习期结束。
- 缺少素材和预算调整记录：不能断言素材疲劳或预算调整导致衰退。
- Google adgroup 局部异常不能直接上升为整个 Campaign 衰退，除非 campaign 汇总也同步恶化。

### 5. 生命周期阶段

默认使用账户均值作为相对基准；若用户提供项目专属阈值，优先使用项目阈值。

| 阶段 | 判定 |
|---|---|
| 测试期 | 花费或安装样本偏低，早期 ROI 信号未成熟 |
| 放量验证 | ROI0/ROI3 接近或高于账户均值，但样本、预测或上下文限制仍存在 |
| 放量期 | 消耗有意义，ROI0/ROI3 高于账户均值，ROI7 预测不冲突，且无明显数据缺口 |
| 平稳期 | 有稳定消耗，表现接近账户均值，以维持或渐进预算迁移为主 |
| 衰退候选 | 成熟消耗下 ROI0/ROI3 明显低于账户均值，且连续多日弱于可替代对象 |
| 无数据/不判断 | 渠道或对象无 ROI 数据 |

### 6. 今日动作建议

动作只基于可验证数据：

| 动作 | 使用条件 |
|---|---|
| `add_budget` | 成熟对象，ROI0/ROI3 高于账户均值，CPI 未明显异常 |
| `small_add` | 表现较好但 ROI7 预测、样本量或上下文有不确定性 |
| `maintain` | 表现接近均值，暂不强迁移预算 |
| `test_budget` | 低花费但信号好，适合小预算继续验证 |
| `hard_observe` | 小样本或多项指标偏弱，不做强动作 |
| `reduce_or_reallocate` | 成熟消耗且明显弱于账户均值，同时存在更优承接对象 |
| `no_action_no_data` | 无数据渠道或对象 |

每条建议必须包含：

- 对象：network / country / campaign
- 阶段
- 动作
- 关键指标
- 原因
- 置信度
- 数据限制

## 输出结构

```markdown
# {project_name} Campaign 生命周期诊断

- 项目：{project_id} / {project_name}
- 日期：{date_start} ~ {date_end}
- 数据源：Snowball MCP get_roi_report

## 1. 数据质量
## 2. 平台状态
## 3. 账户基准
## 4. Campaign 生命周期表
## 5. 今日动作建议
## 6. 不能判断与需补充数据
## 7. 可供日报复用的结构化结果
```

## 质量检查

- 日期必须是绝对日期。
- 必须说明数据来自 Snowball MCP。
- ROI/ROAS 展示为百分比。
- Facebook 无数据时必须输出无数据状态，不得补建议。
- ROI7 预测值必须标记。
- 缺少 learning、素材、预算调整、ad/adset 时必须写入限制。
- 诊断结果与展示报告分离，不能把 HTML 样式规则写进诊断层。
