---
name: meta-advantage-app-campaign-diagnosis
description: 分析 Meta Advantage+ App Campaigns / App Promotion 的结构、素材、预算、事件回传和国家表现，结合 Meta Marketing API 与 Snowball ROI 输出优化建议。
---

# Meta Advantage+ App Campaign Diagnosis

## 目标

诊断 Meta 自动化 App campaign 是否具备放量条件，重点检查素材多样性、事件信号、预算学习、国家质量和 Snowball 回收。

## 数据源

- Meta Marketing API：campaign、adset、ad、creative、insights、delivery/status。
- Snowball MCP：ROI、CPI、retention_1、ARPDAU、IPU、国家/campaign 回收。

## 检查项

1. Campaign 状态
   - active / paused / limited / learning。
   - 预算是否频繁变化。
   - optimization goal 是否匹配 App 业务目标。

2. 事件信号
   - install / purchase / ad revenue / value 回传是否稳定。
   - 平台转化与 Snowball DNU/ROI 是否一致。

3. 素材
   - 竖版视频是否足够。
   - UGC/raw 与 polished 是否都有。
   - 素材是否过少导致疲劳。
   - 是否有明显 winning creative 变体。

4. 国家
   - 国家花费与 ROI 是否匹配。
   - 是否需要拆国家或限制低质国家。

5. 动作
   - `keep_broad`
   - `add_creative_variants`
   - `split_country`
   - `small_budget_increase`
   - `reduce_or_reallocate`
   - `data_signal_fix`

## 输出格式

```markdown
# Meta Advantage+ App Campaign 诊断

## Campaign 状态
## 事件回传质量
## 素材多样性
## 国家质量
## 动作建议
```

## 保护规则

- 无 Meta API 数据时，不做 Meta 平台动作。
- 不建议过早限制受众，除非国家或用户质量证据明确。
- 写操作必须另行确认，默认只读分析。
