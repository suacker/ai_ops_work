---
name: google-app-campaign-asset-diagnosis
description: 分析 Google App Campaign / Performance Max 的素材资产与 asset group 表现，结合 Google Ads API/MCP 和 Snowball ROI，判断素材覆盖、主题结构、资产表现、放量承接和素材补齐方向。
---

# Google App Campaign Asset Diagnosis

## 目标

诊断 Google App Campaign / PMax 的素材资产是否足够、主题是否清晰、asset group 是否能承接预算，并把 Google Ads 平台表现与 Snowball 回收结果对齐。

## 数据源

- Google Ads API / MCP：campaign、ad group、asset group、asset、asset group asset、metrics、bidding、budget、status。
- Snowball MCP：ROI0/ROI3/ROI7、CPI、retention_1、国家回收、广告变现。

## 分析维度

- campaign / ad group / asset group。
- text、image、video、HTML5、logo。
- impressions、clicks、conversions、cost、conversion value、ROAS。
- asset performance label（如果 API 可用）。
- 国家和 campaign 与 Snowball 映射。

## 诊断流程

1. 检查 campaign 类型、状态、预算、出价策略。
2. 检查素材覆盖：
   - text 是否足够。
   - image / video 是否缺失。
   - 竖版视频是否覆盖。
   - asset group 是否主题清晰。
3. 检查 asset group 表现：
   - 高花费低转化。
   - 低花费高 ROAS。
   - 素材组之间是否互相抢量。
4. 对齐 Snowball：
   - Google Ads 转化好但 Snowball ROI 差，排查转化价值与真实收入。
   - Snowball ROI 好但 Google Ads 花费低，评估小幅放量。

## 输出动作

- `add_assets`
- `split_asset_group`
- `merge_low_signal_group`
- `refresh_video`
- `small_add_budget`
- `maintain`
- `reduce_or_reallocate`
- `data_gap_check`

## 输出格式

```markdown
# Google 素材资产诊断

## Campaign 状态
## Asset Group 体检
| Asset Group | Cost | Conv | Google ROAS | Snowball ROI | 素材覆盖 | 状态 | 动作 |
## 素材补齐建议
## 与 Snowball 回收不一致的问题
```
