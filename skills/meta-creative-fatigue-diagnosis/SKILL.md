---
name: meta-creative-fatigue-diagnosis
description: 分析 Meta/Facebook/Instagram 广告素材疲劳，基于 Ads Insights、ad/adset/creative 维度和 Snowball 回收数据，判断素材是否需要刷新、复用、停投或扩展变体；适用于 Meta creative fatigue、素材衰退、CTR/CVR/CPA/ROAS 变化分析。
---

# Meta Creative Fatigue Diagnosis

## 目标

识别 Meta 素材是否因为重复曝光、受众耗尽或创意角度单一导致效果衰退，并给出素材刷新与预算动作建议。

## 数据源

- Meta Marketing API / MCP：campaign、adset、ad、creative、insights。
- Snowball MCP：ROI、CPI、留存、ARPDAU、IPU、国家回收。

## 必需字段

- ad_id / creative_id / ad_name。
- spend、impressions、reach、frequency、clicks、ctr、cpc、cpm。
- installs/conversions、cpa/cpi、conversion value、platform ROAS。
- Snowball ROI0/ROI3/ROI7、retention_1。
- 日期序列，至少 3-7 天。

## 疲劳信号

- frequency 上升，同时 CTR 下滑。
- CPM 上升，同时 CVR 或 ROAS 下滑。
- spend 继续增加，但 installs/conversions 不增长。
- 同一 creative 多日高消耗低 ROI。
- 新素材数量不足，账户依赖少数老素材。

## 诊断流程

1. 先按 ad / creative 聚合近 7 天。
2. 对比前半段 vs 后半段趋势。
3. 结合 adset 国家和 Snowball ROI，判断是素材问题还是流量质量问题。
4. 若只有平台指标无 Snowball 回收，输出低置信度。
5. 给素材动作：
   - `keep_scaling`
   - `refresh_hook`
   - `refresh_visual`
   - `make_variants`
   - `reduce_budget`
   - `pause_candidate`

## 输出格式

```markdown
# Meta 素材疲劳诊断

## 总结
## 素材疲劳表
| Creative | Spend | Frequency | CTR趋势 | CVR趋势 | CPI/CPA | Snowball ROI | 状态 | 动作 |
## 素材刷新建议
## 不能判断的数据缺口
```

## 保护规则

- 不能只因 frequency 高就判定疲劳，必须结合 CTR/CVR/CPA/ROI。
- 素材疲劳不等于 adset 质量差；需要拆国家、版位、受众和 Snowball 回收。
- 无 `ads_read` 或 creative 数据时，不输出强素材结论。
