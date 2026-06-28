# StepTrack 首日激活路径漏斗报告

## 分析范围
- 项目：`StepTrack`
- Cohort 周期：`2026-04-02` ~ `2026-04-30`
- 新用户口径：首日触发 `first_open`
- 激活定义：首日沿主路径完成“进入首页 -> 进入功能详情 -> 进入加记录页 -> 保存记录”
- 次留口径：次日任意事件回访

## 总体结论
- 主激活路径最终完成到 `CLK_SaveFunctionRecord` 的新用户为 `544`，占全量新用户 `4.82%`。
- 最大漏损发生在 `ACT_EnterHomePage -> ACT_EnterFunctionDetailPage`，从 `8,687` 掉到 `2,361`，单步转化仅 `27.18%`。
- 完成最终保存记录的新用户 D1 retention 为 `86.40%`，比 cohort 基线 `+29.53pp`。
- 在主路径各步中，D1 最高的是 `CLK_SaveFunctionRecord`，达到 `86.40%`，说明越接近“任务闭环”，次留越强。

## 核心 KPI
- Cohort 新用户：`11,293`
- 首页到达率：`76.92%`
- 功能详情进入率：`20.91%`
- 加记录页进入率：`6.62%`
- 保存记录完成率：`4.82%`

## 主激活漏斗明细

| 步骤 | 事件 | 达成人数 | 占新用户比重 | 上一步转化率 | 该步人群D1 |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | first_open | 11,293 | 100.00% | 100.00% | 56.87% |
| 2 | ACT_EnterHomePage | 8,687 | 76.92% | 76.92% | 59.16% |
| 3 | ACT_EnterFunctionDetailPage | 2,361 | 20.91% | 27.18% | 79.80% |
| 4 | ACT_EnterFunctionAddRecordPage | 748 | 6.62% | 31.68% | 83.42% |
| 5 | CLK_SaveFunctionRecord | 544 | 4.82% | 72.73% | 86.40% |

## 候选路径对比
选择主路径的标准：语义通用、覆盖相对更大、能够映射明确的首日任务闭环。

| 候选路径 | Step2 | Step3 | Step4 | Step5 | 最终完成率 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 首页 > 功能详情 > 加记录页 > 保存记录 | 8,687 | 2,361 | 748 | 544 | 4.82% |
| 首页 > 功能详情 > AddRecord点击 > 保存记录 | 8,687 | 2,361 | 783 | 542 | 4.80% |
| 首页 > 心率测量 > AddRecord点击 > 保存记录 | 8,687 | 899 | 690 | 583 | 5.16% |
| 首页 > 饮水目标 > 加记录页 > 保存记录 | 8,687 | 1,605 | 344 | 254 | 2.25% |

## 风险与机会定位
- `first_open -> ACT_EnterHomePage` 已有 `76.92%`，说明首页首达不是主问题，真正问题在于如何把已到首页的新用户引导进具体功能任务。
- `ACT_EnterFunctionDetailPage -> ACT_EnterFunctionAddRecordPage` 的单步转化为 `31.68%`，这说明功能详情到动作页的 CTA、默认推荐、信息架构仍有明显优化空间。
- 一旦走到 `ACT_EnterFunctionAddRecordPage`，后续到 `CLK_SaveFunctionRecord` 的转化达到 `72.73%`，说明记录保存本身不是瓶颈，前置引导才是。

## 动作建议
- **P0**：把 `ACT_EnterFunctionDetailPage` 前置为首页首屏主 CTA，减少用户在首页停留但不进入任务页的情况。
- **P1**：在功能详情页强化“加记录/立即开始”动作，把用户直接推到 `ACT_EnterFunctionAddRecordPage`，并针对高流失页做文案与按钮 AB 实验。
- **P2**：将心率测量支线单独拆成次级激活漏斗，因为它最终保存率更高，但覆盖面更窄，适合作为专项转化路径优化。

## 方法与限制
- 本报告基于 BigQuery 用户级事件顺序重建漏斗，要求后一步事件时间戳严格晚于前一步。
- 这是“首日激活路径”分析，不代表所有长期留存路径；部分高价值用户可能走的是其他功能支线。
- 如果埋点存在迟到、重发或跨天上报，漏斗转化会被低估。
- Generated from `/Users/suacker/dev/DataAnalysis/BI/reports/ga4_activation/StepTrack_activation_funnel_0430.md`
