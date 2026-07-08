# 买量每日决策SOP与参数表

## 1. 定位

本页把 [[Google_Meta_Campaign生命周期投放优化决策指南]] 落成投手每天可执行的例行流程：每日判断顺序、日报输出规范、投手反馈闭环、分产品×渠道×媒体的阈值参数表和操作时机约定。

- 生命周期阶段和通用框架见 [[广告系列生命周期诊断模板]]。
- 动作词表、保护窗和单主动作的唯一定义见 [[动作分级与决策边界]]。
- 平台机制细节见 [[Google投放与诊断手册]] 和 [[Meta投放与诊断手册]]。

核心纪律：系统/日报先给判断，投手只对分歧拍板；每个对象每天只有一个主动作；保护窗内不做强动作。

> 六步法的完整真实示范见 [[买量决策实战案例_YouDrama与PDFReader]]（IAA 成熟盘 / IAA 衰退盘 / iOS 订阅盘三种场景）。

## 2. 每日决策六步（每账户 10-15 分钟）

| 步骤 | 做什么 | 输出 |
| --- | --- | --- |
| 1 消耗过滤 | 最新完整日无消耗的对象不进入当日判断 | `no_action_no_data` + 无消耗清单计数 |
| 2 保护窗检查 | learning / learning_limited / 重大编辑 / 48h 内降预算 / 72h 内换素材或新建广告（组）/ 刚过审恢复 / 转化滞后 / 异常事件 | 命中则 `maintain` + 预警标记，跳过 3-6 |
| 3 数据质量门禁 | 平台与 Snowball / BI 对账：spend、install、campaign、country、回收字段 | `ready / partial / blocked`；blocked 只给 `data_gap_check` |
| 4 问题层定位 | 前端（CTR、eCPM、素材）还是商业承接（FCPA/CPA、ROI、首付/关键事件人数），还是操作后恢复窗 | problem_layer 标记 |
| 5 阶段判断 | testing / scaling_trial / scaling / mature / fatigue / pause_candidate | business_stage + sub_stage |
| 6 单主动作 | 从 9 个标准动作中选一个，写清触发条件和复查窗口 | action + reason + observe_window |

平台差异要点：

- Google 先看广告组/资产组局部问题（弱广告组换素材、复制优胜广告组），再动 campaign 整盘预算；最早正式复核默认第 6 天，value / lag-heavy 目标更要等成熟窗口。
- Meta 先看素材和审核恢复（素材疲劳先换广告），再动预算；进入放量验证前确认 live creative >= 2 且 top creative 花费占比 <= 75%。

## 3. 每日日报输出规范

每条进入判断的 campaign 至少输出以下字段：

| 字段 | 业务解释 |
| --- | --- |
| delivery_status | 是否真实在投放 |
| platform_status | 是否处于学习、限制、重大编辑重置、转化滞后保护 |
| context_tag | 重大事件、支付异常、风控、产品事故、素材疲劳等 |
| problem_layer | 前端 / 流量库存 / 商业承接 / 操作恢复窗 |
| business_stage | testing / scaling / mature / fatigue / pause_candidate |
| sub_stage | scaling_trial、高弹性放量、放量失败回退、前端疲劳等 |
| action_type | 9 个标准动作之一（见 [[动作分级与决策边界]]） |
| reason_summary | 一句话解释为什么 |
| trigger_reason | 命中的规则条件 |
| observe_window | 下次观察窗口 |
| confidence_level | 高 / 中 / 低置信 |

日报摘要按以下顺序给业务：

1. 今日应加预算 campaign（`small_add` / `add_budget`）。
2. 今日应降预算或止损 campaign（`reduce_or_reallocate` / `pause_candidate`）。
3. 今日需要换素材 / 新建广告组 / 复制重启 campaign（`refresh_creative` / `duplicate_restart`）。
4. 今日继续观察但风险较高 campaign（`maintain` + 预警标记）。
5. 不进入判断的无消耗 / 已停投 campaign 数量。

## 4. 投手反馈与分歧沉淀

每天业务侧对日报建议只反馈两类：认同；不认同并写明实际动作和原因。分歧记录进 [[预算调整记录模板]] 或案例库，重点沉淀四类：

| 分歧类型 | 典型场景 | 沉淀去向 |
| --- | --- | --- |
| 转化滞后误杀 | Google value / lag-heavy campaign 被过早判失败 | 调大该媒体 conversion_cycle 参数 |
| 素材集中度放量失败 | Meta 单素材占比过高，放量后 CPM 涨、CTR 掉 | 收紧 top creative 占比门禁 |
| 异常周误判 | 赛事、节日、大促期间用常规阈值硬判 | 记录异常周放宽比例 |
| 渠道×媒体阈值偏差 | 某分包渠道长期比默认阈值宽/严 | 更新该行参数表 |

## 5. 参数表（按产品 × 渠道 × 媒体维护）

默认阈值只是起点，每产品每渠道单独维护一行；产品级阈值源头在 `grow_base/{ProjectID}_{ProjectName}.md`。Google / value / lag-heavy 类型应比 Meta / 首付类更宽容。

| 参数 | 含义 | 默认起点 |
| --- | --- | --- |
| T_FCPA / T_CPA | 目标获客成本（首付或关键事件口径） | 按产品盈亏模型定 |
| T_ROAS1 / T_ROI1 | 首日回收目标 | 按产品 payback 模型定 |
| CTR_base / eCPM_base / FPR_base | 前端与承接基线 | 取该产品×媒体近 30 天中位数 |
| conversion_cycle | 完整转化周期 | Meta 首付类 1-2 天；Google value 类 3-7 天 |
| 测试期硬止损线 | 见指南 7.1：CTR < 0.6x 基线且 eCPM > 1.3x 基线；或成熟后消耗 >= 1.2x T_FCPA 且 0 首付；或 >= 3 项指标共振失败 | 指南默认值 |
| 放量验证门槛 | FCPA <= 1.25x 目标；ROAS1/ROI1 >= 0.85x 目标；近 2 天转化连续；CTR/eCPM/FPR 至少 2 项接近基线 | 指南默认值 |
| 放量幅度上限 | 普通 +10%-15%，高置信 +15%-20%，高弹性 +20%-30%；每 conversion cycle 最多一次 | 单次 <= 20% 为安全线 |
| 放量失败判据 | 满足任意 2 条：CTR -25%、FCPA +60%、ROAS1 -40%、转化增长 < 预算增长 x 25%、eCPM +35% | 指南默认值 |
| 异常周放宽比例 | 赛事、节日、大促期间阈值放宽 | 10%-20%，按分歧记录校准 |

参数登记表（示例占位）：

| Project ID | 产品 | 渠道/分包 | 媒体 | T_FCPA | T_ROI1 | CTR_base | eCPM_base | conversion_cycle | 放量上限 | 最近校准日期 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| A1XX | 产品A | 渠道X | Google |  |  |  |  | X 天 | +XX% | YYYY-MM-DD |
| A1XX | 产品A | 渠道X | Meta |  |  |  |  | X 天 | +XX% | YYYY-MM-DD |

## 6. 操作时机与每周节奏（团队默认约定）

| 约定 | 原因 |
| --- | --- |
| 加/降预算尽量在预算日重置后的上午做 | 避免午后大幅调整导致当日超投或投放节奏紊乱 |
| 单次预算调整 <= 20%，同一对象每个 conversion cycle 最多调一次 | 降低学习期重置风险，放量效果可归因 |
| 一天只动一个变量：不同时改预算和出价/定向/素材 | 否则波动无法归因，复盘失效 |
| 周四之后不上新结构、不做重大编辑 | 周末流量波动叠加无人盯盘，学习期风险不可控 |
| 复制重启当天不动原 campaign | 保留对照，复制结构视为新 testing |
| 周一复盘上周动作命中率 | 上周每个主动作是否达到预期，分歧写入第 4 节 |

## 7. 常见误判清单

| 误判 | 纠正 |
| --- | --- |
| 用 12-24h 数据强判新 campaign 失败 | 早期只预警；强动作等 1-2 个 conversion cycles |
| 测试期单日 FCPA / CPA 偏高就关停 | 走指南 7.1 硬止损三条件，缺一不强关 |
| CTR 高、CPI 低就放量 | 必须过 Snowball 回收和放量验证门槛，CTR/CPI 不是商业结果 |
| 刚降完预算又因数据难看再降 | 48h 操作恢复窗内不重复同类动作 |
| 周末 / 节日波动当成衰退 | 与上周同期对比，异常周用放宽阈值 |
| iOS 平台数据延迟当成投放恶化 | 先查 SKAN / AEM 延迟和归因质量，见 [[Meta投放与诊断手册]] 第 11 节 |
| 连续多日加预算追量 | 连续两次 >20% 上调是禁止动作；放量后必须等验证窗口 |
| 素材集中度过高时继续放量 | Meta top creative 占比 > 75% 先补素材再谈放量 |
| 对同一对象同日给多个动作 | 单主动作原则；第二天按复查结果再给下一个动作 |
