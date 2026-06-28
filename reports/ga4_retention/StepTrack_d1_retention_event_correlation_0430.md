# StepTrack 新用户事件与次留相关性分析

## 分析范围
- 项目：`StepTrack`
- 数据源：`steptracker-cfbd0.analytics_509028946.events_*`
- Cohort 周期：`2026-04-02` ~ `2026-04-30`
- 新用户口径：首日触发 `first_open`
- 次留口径：次日任意事件回访
- 事件口径：仅统计新用户在 `D0` 首日是否触发过该事件
- 相关性指标：`Phi coefficient`，同时展示“触发组 D1 - 未触发组 D1”的 retention 差值

## 总体结论
- 基线 D1 retention 为 `56.87%`，样本为 `11,293` 个新用户，其中 `6,422` 在 D1 回访。
- 正相关事件以功能探索、记录保存、目标设定和测量链路为主，说明用户在首日完成“具体任务闭环”时，次留显著更高。
- 负相关事件集中在插屏、权限请求、设置页和首页切换，更多像是打断、试探或问题排查信号，不宜直接当成正向激活指标。
- Push/通知类事件与 D1 的相关性最高，但它们大概率是用户状态代理变量，不是首选的产品优化抓手。

## 核心 KPI
- Cohort 新用户数：`11,293`
- D1 回访用户数：`6,422`
- 基线 D1 retention：`56.87%`

## 优先关注的正相关产品事件
优先级判断标准：覆盖新用户至少约 5%，且触发后 D1 retention 显著高于未触发组。

| 事件 | 覆盖新用户 | 触发用户D1 | 未触发用户D1 | 差值 | Phi |
| --- | ---: | ---: | ---: | ---: | ---: |
| ACT_ShowLockscreenCard | 419 (3.71%) | 77.09% | 56.09% | +21.00pp | 0.0801 |
| ACT_EnterFunctionDetailPage | 1,319 (11.68%) | 64.06% | 55.92% | +8.15pp | 0.0528 |
| CLK_HydratePageAction | 372 (3.29%) | 70.97% | 56.39% | +14.58pp | 0.0525 |
| ACT_EnterWaterIntakeGoalPage | 711 (6.30%) | 66.53% | 56.22% | +10.31pp | 0.0506 |
| CLK_SaveFunctionRecord | 471 (4.17%) | 68.79% | 56.35% | +12.44pp | 0.0502 |
| ACT_EnterStepPage | 144 (1.28%) | 76.39% | 56.61% | +19.77pp | 0.0448 |
| CLK_FunctionDetailPageAction | 468 (4.14%) | 67.52% | 56.41% | +11.11pp | 0.0447 |
| CLK_LockscreenCardButton | 137 (1.21%) | 76.64% | 56.62% | +20.02pp | 0.0442 |
| ACT_EnterFunctionAddRecordPage | 620 (5.49%) | 65.65% | 56.36% | +9.29pp | 0.0427 |
| ACT_AllowFullscreenPermission | 163 (1.44%) | 74.23% | 56.61% | +17.62pp | 0.0424 |
| ACT_EnterHeartRateMeasurePage | 617 (5.46%) | 65.32% | 56.38% | +8.94pp | 0.0410 |
| CLK_MeasureHeartRateGuidePage | 617 (5.46%) | 65.32% | 56.38% | +8.94pp | 0.0410 |

## 需要警惕的负相关产品事件
这些事件更像是打断、困惑或无效游走信号，适合拿来做优化排查。

| 事件 | 覆盖新用户 | 触发用户D1 | 未触发用户D1 | 差值 | Phi |
| --- | ---: | ---: | ---: | ---: | ---: |
| ACT_ShowInterstitial | 9,823 (86.98%) | 55.84% | 63.74% | -7.90pp | -0.0537 |
| ACT_PermissionRequestSuccess | 7,929 (70.21%) | 55.32% | 60.52% | -5.21pp | -0.0481 |
| ACT_ShowPermissionRequest | 8,080 (71.55%) | 55.73% | 59.73% | -4.00pp | -0.0364 |
| ACT_EnterHomePage | 8,018 (71.00%) | 55.81% | 59.45% | -3.64pp | -0.0333 |
| ACT_InterstitialDone | 8,658 (76.67%) | 56.12% | 59.32% | -3.20pp | -0.0273 |
| CLK_ChangeHomepageTab | 2,204 (19.52%) | 54.13% | 57.53% | -3.40pp | -0.0272 |
| CLK_PauseCountSteps | 295 (2.61%) | 48.81% | 57.08% | -8.27pp | -0.0266 |
| ACT_EnterSettingPage | 737 (6.53%) | 52.24% | 57.19% | -4.95pp | -0.0247 |
| CLK_SelectExercise | 1,613 (14.28%) | 54.93% | 57.19% | -2.26pp | -0.0160 |
| CLK_StartExercise | 1,246 (11.03%) | 55.30% | 57.06% | -1.76pp | -0.0112 |
| CLK_SavePersonalInfo | 220 (1.95%) | 53.18% | 56.94% | -3.76pp | -0.0105 |
| CLK_Setting | 347 (3.07%) | 54.18% | 56.95% | -2.77pp | -0.0097 |

## 高相关但偏系统代理的事件
这类事件的相关性高，但通常不适合直接作为产品功能优化目标；更适合作为用户分层特征或补充解释变量。

| 事件 | 覆盖新用户 | 触发用户D1 | 未触发用户D1 | 差值 | Phi |
| --- | ---: | ---: | ---: | ---: | ---: |
| push_custom_receive | 7,512 (66.52%) | 74.40% | 22.03% | +52.37pp | 0.4990 |
| notification_receive | 7,559 (66.94%) | 73.98% | 22.23% | +51.75pp | 0.4916 |
| push_displayed | 8,862 (78.47%) | 69.50% | 10.82% | +58.68pp | 0.4870 |
| push_received | 8,916 (78.95%) | 69.13% | 10.85% | +58.28pp | 0.4797 |
| device_boot | 1,360 (12.04%) | 78.46% | 53.91% | +24.54pp | 0.1613 |
| notification_dismiss | 1,074 (9.51%) | 78.21% | 54.62% | +23.59pp | 0.1397 |
| push_opened | 1,541 (13.65%) | 66.13% | 55.40% | +10.72pp | 0.0743 |
| track_gclid | 10,676 (94.54%) | 57.49% | 46.03% | +11.46pp | 0.0526 |
| th_oobe_done | 741 (6.56%) | 66.53% | 56.19% | +10.34pp | 0.0517 |
| notification_foreground | 180 (1.59%) | 74.44% | 56.58% | +17.86pp | 0.0452 |

## 运营与产品建议
- **P0**：围绕“首日任务闭环”补强路径，把 `ACT_EnterFunctionDetailPage`、`ACT_EnterWaterIntakeGoalPage`、`ACT_EnterHeartRateMeasurePage`、`CLK_SaveFunctionRecord` 这类事件前置到新手路径里。
- **P1**：对 `ACT_ShowInterstitial`、`ACT_ShowPermissionRequest`、`ACT_PermissionRequestSuccess` 建立首日分版本监控，优先排查其是否发生在关键任务前，是否对激活路径造成打断。
- **P2**：把用户分成“首日完成记录/设置目标/进入功能详情”和“未完成任务闭环”两组，继续比较 D3、D7 retention 和付费/广告价值，验证这些事件是否真的是长期价值代理。

## 方法与限制
- 这是相关性分析，不是因果证明；高相关只能说明“同现”，不能直接证明该事件导致了高次留。
- 首日事件可能受到广告、Push、权限请求、技术埋点时序影响，因此系统事件需要单独解读。
- 本次未按平台、版本、国家、渠道拆分；如果要进入执行层，建议下一步按 `platform + app_version` 做二次分析。
- Generated from `/Users/suacker/dev/DataAnalysis/BI/reports/ga4_retention/StepTrack_d1_retention_event_correlation_0430.md`
