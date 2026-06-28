---
name: ua-budget-reallocation-diagnosis
description: 诊断移动应用买量预算迁移与放量优先级，结合 Snowball ROI/CPI/留存/营收与 Google/Meta 投放侧表现，输出 P0/P1/P2 预算动作；适用于是否加预算、降预算、暂停、迁移预算、测试预算的问题。
---

# UA Budget Reallocation Diagnosis

## 目标

把“加预算/降预算/迁移预算”从主观判断变成结构化决策。该 Skill 默认只给建议，不直接执行平台写操作。

## 前置要求

先运行或等价完成 `ads-attribution-data-quality-check`。数据质量为 `blocked` 时，只能输出修复数据建议。

## 输入

- 项目 ID / 项目名。
- 日期范围，默认最近 7 个完整自然日。
- 国家、network、campaign、adgroup/adset 维度数据。
- 项目阈值：优先使用 `grow_base`，没有阈值时使用账户均值做相对基准。

## 判断维度

- ROI0 / ROI3 / ROI7。
- CPI。
- 花费规模与安装数。
- retention_1。
- cohort revenue / cohort profit。
- 国家 eCPM / ARPDAU / IPU。
- 平台预算、状态、learning、最近预算调整。

## 动作规则

| 动作 | 条件 |
|---|---|
| `add_budget` | 成熟样本，ROI0/ROI3 高于基准，CPI 未异常，且有稳定转化 |
| `small_add` | 信号好但 ROI7 预测、样本或上下文仍有不确定性 |
| `maintain` | 表现接近基准，暂不迁移预算 |
| `test_budget` | 低花费但早期信号较好 |
| `reduce_or_reallocate` | 成熟消耗下 ROI 明显弱于基准，且存在更优承接对象 |
| `pause_candidate` | 连续多日成熟消耗低 ROI，且非学习期/非数据问题 |
| `no_action_no_data` | 无数据或数据不可用 |

## 保护规则

- 新 campaign / learning 期不强关停。
- ROI7 是预测时，不能单独驱动强放量。
- CPI 低但 ROI 差，不能放量。
- 低花费高 ROI 只能小预算验证。
- 有平台消耗但 Snowball 无回收时，先查归因。

## 输出格式

```markdown
# 预算迁移诊断

## 账户基准
## 预算承接对象
## 预算回收对象
## P0/P1/P2 动作建议
| 优先级 | 对象 | 当前预算/花费 | 关键指标 | 动作 | 原因 | 置信度 |
## 风险与不能判断
```
