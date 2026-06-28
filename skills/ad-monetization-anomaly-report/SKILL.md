---
name: ad-monetization-anomaly-report
description: Use when analyzing a mobile app's ad monetization anomaly, ad revenue drop, eCPM/IPU change, ad format trend, ad scene issue, or SnowBall MCP IAA diagnosis report.
---

# 广告变现异常诊断报告

## 目标

对指定 SnowBall 项目生成广告变现异常诊断，重点判断：

- 收入变化是否由用户新增/活跃变化解释。
- 广告格式级 `eCPM` / `IPU` 是否存在明显下滑。
- 主要转折日期是哪一天。
- 异常应优先回查哪些广告格式、广告场景和后台配置。

默认产出双格式文件：

- `reports/ad_monetization/{project_id}_{ProjectName}_ads_anomaly_{date_start}_{date_end}.md`
- `reports/ad_monetization/{project_id}_{ProjectName}_ads_anomaly_{date_start}_{date_end}.html`

## 输入与日期

必需输入：

- 项目名或 `project_id`。若只给项目名，先用 `snowball_mcp.get_projects` 解析项目。

默认日期：

- 主分析窗口：近 30 个完整自然日，`today-30` ~ `today-1`。
- 扩展观察窗口：近 60 个完整自然日，`today-60` ~ `today-1`。
- 不含当天，避免实时回传不完整。

报告必须写明绝对日期范围。

## SnowBall 查询

所有定量结论只能来自 SnowBall MCP；缺失、`-1`、样本过小必须标为“数据缺失/低置信度”，禁止补数。

### 1) 项目确认

```text
get_projects(project_name=项目名, use_cache=false)
```

记录 `project_id`、项目名、平台、包名。

### 2) 主窗口总览

```text
get_est_ads_revenue_chart_data(
  project_id,
  date_start=主窗口开始,
  date_end=主窗口结束,
  day_period="daily",
  dimension_list=["date"],
  indexes=["ads_revenue","impressions","ecpm","dau","dnu","ipu","ctr"]
)
```

计算：

- 近 30 日总广告收入、日均广告收入、展示数、加权 eCPM、平均 IPU、平均 CTR。
- 首 7 日、前 7 日、最近 7 日均值。
- DNU、DAU、广告收入、eCPM、IPU 的 `最近 7 日 vs 前 7 日` 与 `最近 7 日 vs 首 7 日`。

### 3) 扩展窗口广告格式趋势

```text
get_est_ads_revenue_chart_data(
  project_id,
  date_start=扩展窗口开始,
  date_end=扩展窗口结束,
  day_period="daily",
  dimension_list=["date","ad_unit_format"],
  indexes=["ipu","ecpm","ads_revenue","impressions","dnu","dau"]
)
```

对每个广告格式计算：

- 主窗口收入、收入占比、展示数、加权 eCPM。
- 最近 7 日收入/eCPM/IPU vs 前 7 日。
- 60 日转折点。

重点格式优先级：

1. `Interstitial`
2. `AppOpen`
3. `Banner`
4. `Native`
5. 其他有量格式

### 4) 广告场景

先用表格接口发现高贡献场景：

```text
get_est_ads_revenue_table_data(
  project_id,
  date_start=主窗口开始,
  date_end=主窗口结束,
  dimension_list=["scene"]
)
```

再选择收入贡献最高、且覆盖 `I_` / `O_` / `B_` / `N_` 的代表场景，用图表接口拉日趋势：

```text
get_est_ads_revenue_chart_data(
  project_id,
  date_start=主窗口开始,
  date_end=主窗口结束,
  day_period="daily",
  dimension_list=["date","scene"],
  indexes=["ads_revenue","impressions","ecpm","ipu","dnu_ads_revenue","dnu_impressions_rate","ctr"],
  scene_list=[高贡献场景列表]
)
```

若场景表过大，优先筛选：

- 收入最高的 `I_` 插屏场景。
- 收入最高的 `O_` AppOpen 场景。
- 有量的 `B_` Banner 场景。
- 有量的 `N_` Native 场景。

## 转折点算法

对扩展窗口中每个广告格式、每个指标（`IPU`、`eCPM`）执行：

1. 对每一天 `d`，把 `d` 作为新窗口第一天。
2. 计算 `d` 前 7 日均值 `before_avg`。
3. 计算 `d` 起后 7 日均值 `after_avg`。
4. 计算变化：`after_avg / before_avg - 1`。
5. 找下降最大的日期；若下降超过 `15%` 且后续低位持续，判定为明显转折。

解释规则：

- `IPU` 先降：优先查广告触发、展示机会、频控、场景策略、SDK 展示调用。
- `eCPM` 后降：优先查 AdMob / Waterfall / bidding / 价格规则 / 变现平台需求 / 无效流量。
- 收入不明显下降但 eCPM 降：标记为“观察/中风险”，不要夸大成收入塌陷。

## 报告判断框架

先回答 5 个问题：

1. 新增用户是否解释收入变化？
2. 收入是否明显异常？
3. 主要问题是 eCPM、IPU、展示数，还是 CTR？
4. 哪个广告格式贡献最大且变化最大？
5. 转折点是哪一天，应该回查哪个操作窗口？

常用阈值：

- 最近 7 日收入变化超过 `20%`：高风险。
- 最近 7 日 eCPM 或 IPU 变化超过 `15%`：需定位。
- 收入占比低于 `3%` 的格式/场景：默认低优先级，除非用户特别要求。

## HTML 视觉规范

HTML 采用卡片式报告，不套用 grow-monitor 通用模板：

- 浅蓝背景。
- 大标题 + 右上“数据口径”卡片。
- 第一屏双栏：左侧核心结论，右侧广告格式收入贡献条形图。
- “核心广告格式”双列卡片：每张卡包含收入、最近 7 日 eCPM、最近 7 日 IPU。
- “60 日格式级 IPU / eCPM”转折点表。
- “重点场景定位”场景卡片。
- “最终建议”排序卡片。
- HTML 页脚：`Generated from {md 绝对路径}`。

HTML 与 Markdown 数值必须一致。

## 输出结构

Markdown：

1. 标题、项目、日期、数据源。
2. 先给结论：5 行以内表格。
3. 用户新增 vs 广告收入。
4. 60 日格式级 IPU / eCPM 转折点。
5. 广告格式诊断。
6. 广告场景诊断。
7. P0/P1/P2 动作建议。
8. 数据限制。

HTML：

- 使用同一组数值。
- 主视觉用卡片和排序，不把大表格放在首屏。
- 可包含较少的日级明细，但不能删除关键判断依据。

## 质量检查

发布前必须检查：

- 项目 ID、项目名、平台、包名是否来自 SnowBall。
- 主窗口和扩展窗口日期是否都是完整自然日且不含当天。
- MD/HTML 核心数值是否一致。
- 收入、eCPM、ARPDAU 用美元格式；CTR、占比、变化率用百分比；IPU 保留 2 位。
- `-1`、缺失、样本过小是否标记为“数据缺失/低置信度”。
- 结论是否区分 SnowBall 趋势事实和 AdMob 后台事实。
- HTML 页脚是否指向 Markdown 绝对路径。
- 用浏览器或 headless Chrome 渲染截图，确认报告可视布局正常。

## 手动协助边界

以下内容不能由 SnowBall 趋势直接断言，只能写为“需 AdMob 后台复核”：

- 当天实时收入、实时填充。
- AdMob 政策中心报错。
- 账户级无效流量核减。
- 具体 Mediation Group 的实时 Waterfall 出价和填充表现。
