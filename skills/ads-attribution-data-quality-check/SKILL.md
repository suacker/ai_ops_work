---
name: ads-attribution-data-quality-check
description: 检查广告投放数据归因与口径质量，适用于 Google Ads、Meta Ads、Snowball、MMP、Firebase 等数据源之间的消耗、安装、转化、ROI、国家和 campaign 口径对账；在生成买量动作建议前用于判断数据是否可信。
---

# Ads Attribution Data Quality Check

## 目标

在做预算、素材或生命周期判断前，先确认数据是否可信。该 Skill 的输出不是投放动作，而是数据质量结论、阻断项和可继续分析的范围。

## 输入

- 项目 ID / 项目名。
- 日期范围，默认最近 7 个完整自然日，不含当天。
- 广告平台：Google / Meta / 其他。
- 可选：Snowball campaign、network、country、ad account、campaign/adset/ad ID 映射表。

## 数据源优先级

1. Snowball MCP：ROI、CPI、DNU、留存、广告收入、IAP、国家维度回收。
2. Google Ads / Meta Marketing API：平台消耗、展示、点击、安装/转化、campaign/adset/ad/asset 状态。
3. MMP / Firebase：事件、归因、转化回传和 post-install 行为。

禁止用估算值填补缺失数据。缺失必须标记为 `data_gap`。

## 检查流程

1. 时间窗口
   - 使用绝对日期。
   - 默认不含当天。
   - 标记 Snowball ROI7 / 平台转化是否为预测或延迟数据。

2. 消耗对账
   - 平台 spend vs Snowball cost。
   - 差异 > 5% 标记 `spend_mismatch_warning`。
   - 差异 > 15% 标记 `spend_mismatch_blocker`。

3. 安装/转化对账
   - 平台 installs/conversions vs Snowball DNU/attributed_users。
   - 检查是否存在 SKAN、MMP、Firebase、平台归因窗口差异。

4. 维度映射
   - network 命名是否一致：google / google-play / facebook / meta。
   - campaign 名称或 ID 是否能映射。
   - country 是否使用同一标准。

5. 业务指标可用性
   - ROI0/ROI3/ROI7 是否有效。
   - CPI、retention_1、ARPDAU、IPU 是否有值。
   - `-1` / null / N/A 不能当作 0。

6. 结论分层
   - `ready`：可生成强动作建议。
   - `partial`：只能做低置信度建议。
   - `blocked`：不能做预算或素材结论。

## 输出格式

```markdown
# 数据质量检查

## 结论
- status: ready | partial | blocked
- confidence: high | medium | low

## 对账表
| 来源 | Spend | Installs | Conversions | ROI/ROAS | 备注 |

## 风险
## 可继续分析范围
## 阻断项与修复建议
```

## 规则

- 数据不可信时，必须阻止预算迁移、关停、放量等强建议。
- 平台有消耗但 Snowball 无 ROI 时，优先排查归因/映射，不要直接判定投放差。
- Snowball 无 Facebook 数据时，输出 `inactive_no_data` 或 `data_mapping_gap`，不要生成 Meta 投放动作。
