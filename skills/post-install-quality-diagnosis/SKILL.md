---
name: post-install-quality-diagnosis
description: 分析买量用户安装后的质量，结合 Snowball 事件、漏斗、留存、ARPDAU、IPU、广告格式和国家/渠道/campaign 维度，判断用户质量、广告入口触发、变现行为和投放质量问题。
---

# Post-install Quality Diagnosis

## 目标

回答“买来的用户是不是好用户”。用于解释 ROI 变化、IPU 异常、留存下降、广告变现下降、Facebook/Google 用户质量差异。

## 数据源

- Snowball ROI / profit / ads revenue。
- Snowball event / funnel / retention。
- Google/Meta campaign/adset/country 数据。

## 分析流程

1. 先看总体质量：
   - retention_1。
   - ARPDAU。
   - IPU。
   - ROI0/ROI3。
2. 拆渠道：
   - Google vs Facebook vs 其他。
3. 拆国家和 campaign/adset。
4. 拆广告格式：
   - RewardedVideo。
   - Interstitial。
   - AppOpen。
   - Banner / Native。
5. 拆关键事件漏斗：
   - first_open。
   - onboarding。
   - paywall / ad entry。
   - core action。
6. 判断原因：
   - 用户质量差。
   - 广告入口触发少。
   - 填充/展示问题。
   - 版本或配置问题。
   - 归因/数据问题。

## 输出格式

```markdown
# 安装后用户质量诊断

## 总结
## 渠道质量对比
## 国家/Campaign 下钻
## 广告格式与关键入口
## 归因判断
## 投放与产品动作建议
```

## 规则

- IPU = impressions / DAU；必须拆 DAU、impressions、requests、fill_rate、imp_rate、eCPM。
- ROI 差不一定是买量差，可能是广告入口或产品路径问题。
- 当前日数据未沉淀时必须标注低置信度。
