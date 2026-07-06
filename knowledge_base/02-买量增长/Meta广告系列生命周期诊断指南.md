# Meta 广告系列生命周期诊断指南

## 定位

本页用于把通用 `Campaign 生命周期诊断模板` 扩展为 Meta / Facebook Ads 出海 App 投放场景的实操指南，覆盖 Advantage+ App Campaign、ASC、手动 Campaign、CBO / ABO、ad set、creative、国家、版位、Learning / Learning Limited、素材 fatigue、频次和 Snowball / BI 回收判断。

本页不是实时报告，不记录未经查询确认的实时结论。每次实际分析必须重新拉取当前日期窗口、当前投放状态、当前素材表现、当前频次和当前 Snowball / BI 回收，禁止用旧经验替代实时数据。

## 0. 总模板采访与改造结论

### 0.1 可直接复用的字段

| 总模板字段 | Meta 是否可直接用 | 使用说明 |
| --- | --- | --- |
| 产品、Project ID、渠道、账户 | 可直接用 | 账户要写 Meta ad account 名称和 account id。 |
| 日期范围 | 可直接用 | 必须写绝对日期，例如 `2026-06-20 ~ 2026-06-26`，默认不含当天。 |
| 商业模式 | 可直接用 | IAA、IAP、IAA+IAP 的回收判断不同，必须在报告开头声明。 |
| 数据质量 | 可直接用 | 继续使用 `ready / partial / blocked / inactive_no_data`。 |
| 回收口径 | 可直接用 | 继续使用 ROI0 / ROI3 / ROI7 / profit / payback，但 ROI7 forecast 必须标注。 |
| 生命周期状态 | 可直接用 | `testing / scaling / mature / fatigue / pause_candidate` 仍适用。 |
| 默认动作 | 可直接用 | `test_budget / maintain / small_add / add_budget / refresh_creative / reduce_or_reallocate / pause_candidate` 仍适用。 |
| 诊断结论与下一步 | 可直接用 | 输出 P0/P1/P2、对象、触发条件、负责人、复查日期。 |

### 0.2 需要改成 Meta 特有字段的部分

| 总模板字段 | Meta 专用扩展 | 为什么要改 |
| --- | --- | --- |
| Campaign 类型 | Advantage+ App Campaign / ASC / Manual / CBO / ABO | Meta 的预算分配和学习机制会直接影响判断。 |
| 子层级 | adset、ad、creative、placement、publisher platform | Meta 的 adset 和 creative 决策比 Google asset group 更细。 |
| 素材字段 | creative_id、ad_id、hook、first frame、CTA、format、language、angle、winner 来源 | Meta 素材疲劳和承诺错配常是 lifecycle 转折点。 |
| 学习状态 | Learning、Learning Limited、Active、Limited、Rejected、Paused | 学习状态会影响短期成本和预算动作置信度。 |
| 预算结构 | campaign budget、adset budget、adset spend limit、daily / lifetime budget | Advantage+ campaign budget 和 adset budget 的决策逻辑不同。 |
| 频次字段 | reach、impressions、frequency、unique CTR、CTR、CVR | fatigue 判断必须结合 reach 和 frequency，不能只看 CTR。 |
| 国家和版位结构 | country、region、publisher_platform、platform_position、device_platform | 混投中低 CPI 可能来自低回收国家或版位。 |
| 事件动作 | app_install、purchase、subscribe、trial、ad_impression、关键行为事件 | IAP 和 IAA 的优化事件与 Snowball 回收口径必须对齐。 |

### 0.3 必须谨慎使用的字段

| 字段 | 风险 | 正确处理 |
| --- | --- | --- |
| CTR | 高 CTR 可能是误导性 hook 或低质流量 | 只作为素材吸引力信号，预算动作必须看 Snowball ROI、profit、留存和事件质量。 |
| CPI / CPA | 低 CPI 可能来自低价值国家、低质版位或非目标用户 | 结合国家、版位、留存、广告收入、付费收入判断。 |
| 平台 ROAS | Meta 平台归因和 Snowball cohort 口径可能不同 | 先做平台与 Snowball 对账，再下结论。 |
| 单条 creative 表现 | Meta 通常没有 Snowball creative 级 ROI | 写成“基于所属 campaign/adset 回收质量推断”，不得伪造 creative ROI。 |
| Learning Limited | 可能是预算不足、事件稀疏、受众过窄或结构碎片化 | 不直接等于 loser，要结合花费、转化量和回收。 |
| Frequency | 不同产品、国家、素材形态可接受频次不同 | 结合 CTR/CVR、CPI、ROI 和 reach 变化判断 fatigue。 |
| 当天数据 | 当天数据未完整，且平台和 Snowball 延迟不同 | 默认排除；若必须看当天，标注低置信度。 |

## 1. 每次分析的实时性要求

| 检查项 | 必须使用当前值 | 禁止做法 |
| --- | --- | --- |
| 日期窗口 | 当前任务对应的最近完整自然日窗口 | 使用旧报告日期或只写“最近几天”。 |
| 投放状态 | 当前 campaign / adset / ad 状态 | 用历史 active 状态推断当前仍在跑。 |
| 预算 | 当前 campaign budget、adset budget、spend limit、最近预算变更 | 用旧预算动作解释当前波动。 |
| 学习状态 | 当前 Learning / Learning Limited / Active 状态 | 用上周学习状态判断今天动作。 |
| 素材表现 | 当前 ad / creative 的 spend、impression、CTR、CPC、CPM、frequency、actions | 用历史 winner 直接判断当前 winner。 |
| Snowball 回收 | 当前日期窗口的 ROI0 / ROI3 / ROI7、profit、retention、关键事件 | 只看 Meta 平台指标做预算建议。 |
| 归因映射 | 当前 campaign / adset 命名和 Snowball 维度映射 | campaign 改名或新建后继续套旧映射。 |

默认日期窗口：

| 场景 | 默认窗口 | 说明 |
| --- | --- | --- |
| Campaign 生命周期诊断 | `today-7` ~ `today-1` | 近 7 个完整自然日，不含当天。 |
| 素材 fatigue 判断 | `today-14` ~ `today-1`，并拆最近 3 / 7 / 14 天 | 看趋势，不只看单日。 |
| 新 campaign / 新 adset 测试 | 至少 2-3 个完整自然日，或达到样本门槛 | 未达到门槛标记 `too early to judge`。 |
| IAP 回收判断 | 根据产品 payback 周期看 ROI0 / ROI3 / ROI7 / 首购 / 订阅 | 短周期不成熟时降低动作强度。 |

## 2. 生命周期定义

| 阶段 | Meta 定义 | 可观察信号 | 默认动作 |
| --- | --- | --- | --- |
| testing | 新 campaign、新 adset、新 creative 或新国家测试，算法和回收都未稳定 | spend / install / purchase 样本不足；Learning 中；ROI 信号未成熟 | `test_budget` / `maintain` |
| scaling | 回收达标，且增量预算没有明显拉低用户质量 | spend 增长；CPI / CPA 可控；ROI0 / ROI3 / profit 达标；frequency 未异常 | `small_add` / `add_budget` |
| mature | 已稳定运行，量级、成本和回收处在可控范围 | daily spend 稳定；ROI 波动可解释；素材池仍有变体 | `maintain` / `refresh_creative` |
| fatigue | 素材或受众触达效率下降，边际获客质量恶化 | frequency 上升；CTR/CVR 下降；CPI/CPA 上升；Snowball ROI、留存或事件变差 | `refresh_creative` / `reduce_or_reallocate` |
| pause_candidate | 成熟消耗下连续不达标，且排除归因、延迟、学习期和样本问题 | 多日 ROI / profit 不达标；无可用素材修复；存在更优预算承接对象 | 人工确认后再暂停 |
| inactive_no_data | 对象无有效投放或 Snowball 无数据 | spend、install、ROI 缺失 | `no_action_no_data` |

## 3. Meta 可观察信号

### 3.1 平台侧字段

| 层级 | 字段 | 判断用途 |
| --- | --- | --- |
| Account | spend、impressions、reach、frequency、clicks、CTR、CPC、CPM、actions、cost per action | 判断账户整体获量、竞争和流量质量变化。 |
| Campaign | objective、campaign type、budget type、budget、bid strategy、status、delivery、spend、results | 判断结构、预算和生命周期阶段。 |
| Adset | optimization goal、billing event、attribution setting、country、age、gender、placement、budget、spend limit、learning status | 判断学习期、预算碎片化、国家和版位分配。 |
| Ad / Creative | ad_id、creative_id、format、hook、first frame、CTA、language、angle、spend、CTR、CPC、CPM、frequency、actions | 判断 winner / loser、疲劳和承诺错配。 |
| Breakdown | country、publisher_platform、platform_position、device_platform、age、gender | 判断低 CPI 是否来自低回收结构。 |

### 3.2 Snowball / BI 字段

| 口径 | 字段 | 判断用途 |
| --- | --- | --- |
| 回收 | cost、install、CPI、ROI0、ROI3、ROI7、revenue、profit、payback | 决定预算强动作。 |
| 留存 | D1 / D3 / D7 retention | 判断低价用户是否可持续。 |
| IAA | ads revenue、eCPM、IPU、ad impressions、ad format、ad scene | 判断广告变现质量。 |
| IAP | purchase revenue、payer rate、trial rate、subscribe rate、ARPPU、refund / cancel | 判断付费质量。 |
| 用户行为 | onboarding、关键事件、核心功能使用、订阅页曝光、广告触发 | 判断素材承诺与产品行为是否匹配。 |

## 4. Advantage+ 与手动 Campaign 差异

| 项目 | Advantage+ App Campaign / ASC | 手动 Campaign / CBO / ABO |
| --- | --- | --- |
| 适用场景 | 有稳定素材池、足够事件量，需要自动化扩量 | 需要验证国家、人群、版位、素材或预算假设 |
| 预算分配 | campaign 层预算自动向系统认为机会更好的 adset / 组合分配 | ABO 可固定 adset 预算；CBO 用 campaign budget 自动分配 |
| 可控性 | 控制少，黑盒强 | 控制强，可拆国家、版位、人群和素材实验 |
| 诊断重点 | 看整体回收、国家/版位 mix、素材池新鲜度、频次和边际成本 | 看 adset 间差异、预算迁移、学习期碎片化和实验假设 |
| 常见误判 | 单条 ad CTR 高就加整个 campaign 预算 | 某个 adset 短期好就过早迁移大预算 |
| 推荐动作 | 稳定达标时小幅加预算，优先补充素材变体 | 把预算迁移到高回收 adset / country / creative 组合 |

### 4.1 Advantage+ / ASC 判断重点

| 信号 | 判断 | 动作 |
| --- | --- | --- |
| campaign spend 增长，Snowball ROI / profit 不下降 | 自动化扩量有效 | `small_add` 或 `add_budget`，并保持素材补给。 |
| CTR 高、CPI 低，但 ROI / 留存弱 | 低质流量或素材承诺错配 | 不放量，拆国家、版位和素材角度。 |
| frequency 上升，CTR/CVR 同步下降 | 素材或受众 fatigue | `refresh_creative`，补 hook / first frame / CTA 变体。 |
| 国家 mix 向低回收国家倾斜 | 系统短期追低成本，回收质量下降 | 限制或拆出国家，迁移预算到高回收结构。 |
| 学习状态频繁重启 | 预算或结构改动过密 | 暂停大动作，延长观察窗。 |

### 4.2 手动 Campaign 判断重点

| 场景 | 判断 | 动作 |
| --- | --- | --- |
| broad adset 好于 interest adset | 素材驱动强，兴趣限制降低系统探索 | 保留 broad，减少窄兴趣预算。 |
| 某国家 adset CPI 低但 ROI 弱 | 低价国家带来低质量用户 | 降预算或拆出单独验证。 |
| 某 placement CTR 高但留存弱 | 点击诱导或误触风险 | 降低该版位权重，刷新素材承诺。 |
| 多 adset 共用素材且同步衰退 | 素材层 fatigue | 先刷新素材，不急着改人群。 |
| 新 adset Learning Limited 且样本小 | 事件不足或预算碎片化 | 合并结构、提高事件量或降低动作强度。 |

## 5. Learning / Learning Limited

Meta 的投放系统通常需要每个 ad set 在学习期内积累足够优化事件，常见经验口径约为最近一次重大编辑后一周内约 50 个优化事件。Learning Limited 表示系统预计难以获得足够优化事件，但它不是自动暂停信号。

| 状态 | 含义 | 诊断动作 |
| --- | --- | --- |
| Learning | 系统仍在探索高效投放方式 | 不用单日 CPI / CPA 做强判断，等待完整观察窗。 |
| Learning Limited | 预计优化事件不足，学习难以稳定 | 检查预算、受众规模、优化事件、adset 数量和结构碎片化。 |
| Active / Learning Complete | 投放相对稳定 | 可提高生命周期动作置信度，但仍要看 Snowball 回收。 |
| Frequent re-learning | 频繁重大编辑导致重新学习 | 降低操作频率，避免每天大改预算、定向或素材组合。 |

重大编辑风险：

| 变更 | 影响 |
| --- | --- |
| 大幅调整预算 | 可能触发重新学习，短期成本波动加大。 |
| 改优化事件或归因设置 | 前后数据不可直接简单比较。 |
| 大幅改定向、国家、版位 | 流量池变化，需重新观察。 |
| 批量暂停 / 新增 ad 或 adset | 影响素材池和预算分配。 |

## 6. 预算结构与动作门禁

| 预算结构 | 诊断重点 | 动作门禁 |
| --- | --- | --- |
| Campaign budget | 系统是否把预算分配到真实高回收对象 | 加预算前必须确认 Snowball campaign / country 回收稳定。 |
| Adset budget | adset 间是否存在明确优劣 | 可做预算迁移，但需防止样本不足。 |
| Adset spend limit | 是否阻断系统给优质 adset 放量 | 若优质 adset 受限，可调整限制或迁移预算。 |
| Daily budget | 日预算是否足以完成学习 | 预算过低可能导致 Learning Limited。 |
| Lifetime budget | 观察剩余排期、节奏和短期波动 | 不用单日消耗偏差直接判衰退。 |

动作分级：

| 动作 | 必要条件 | 禁止场景 |
| --- | --- | --- |
| `add_budget` | 数据质量 `ready`；成熟消耗；ROI / profit 达标；频次和成本未明显恶化；有素材补给 | 只因 CTR 高、CPI 低或平台 ROAS 高。 |
| `small_add` | 回收达标但样本、ROI7 forecast、国家结构或学习状态仍有不确定性 | Learning 频繁重启且 Snowball 回收未成熟。 |
| `maintain` | 回收可接受但边际空间不清晰 | 无复查日期。 |
| `test_budget` | 新对象或低样本对象有早期正向信号 | 把测试预算当成放量预算。 |
| `refresh_creative` | frequency 上升、CTR/CVR 下降、CPI/CPA 上升或回收变差 | 未确认素材层问题就大幅改预算。 |
| `reduce_or_reallocate` | 成熟对象连续弱于账户均值，且存在更优承接对象 | 归因或 Snowball 数据 `blocked`。 |
| `pause_candidate` | 连续不达标，刷新无效，且非数据问题 | 单日波动、样本不足或 Learning 中。 |

## 7. 素材 fatigue、频次和 winner / loser

### 7.1 Fatigue 判断

| 信号组合 | 解释 | 动作 |
| --- | --- | --- |
| frequency 上升，CTR 下降，CPI 上升 | 受众看腻或素材吸引力下降 | 补新 hook、first frame、CTA、字幕和节奏变体。 |
| frequency 上升，CTR 稳定，但 ROI / 留存下降 | 可能吸引到重复或低质用户 | 拆国家、版位和用户行为，检查承诺错配。 |
| CPM 上升，CTR 下降 | 竞争变贵叠加素材效率下降 | 优先刷新素材，再评估预算迁移。 |
| CTR 高，CVR / ROI 弱 | 点击强但转化或变现差 | 重新定义卖点，不按 winner 放量。 |
| 新素材 spend 低 | 尚未获得分发机会 | 标记 `too early to judge`。 |

### 7.2 Creative winner / loser 判断

| 类型 | 平台信号 | Snowball / BI 信号 | 判断 |
| --- | --- | --- | --- |
| 高质量 winner | CTR / CVR 可接受，CPI / CPA 达标，frequency 未恶化 | 所属 campaign / adset ROI、profit、留存达标 | 可以做 hook、first frame、CTA、文案、语言、本地化变体。 |
| 错配型 winner | CTR 高、CPI 低 | ROI、留存、关键事件或付费弱 | 不放量，重写承诺或更换落地价值。 |
| 稳态素材 | CTR 中等，CPI 可接受 | ROI / profit 稳定 | 保留投放，补轻变体防 fatigue。 |
| loser | CTR 低、CPI 高、spend 有意义 | 回收弱 | 停止复用或重做素材角度。 |
| 未成熟素材 | spend / install / purchase 样本不足 | 回收未完整 | 继续测试或降低置信度。 |

注意：若 Snowball 没有 creative 级 ROI，报告必须写“creative ROI 基于所属 campaign / adset 回收质量推断”。

## 8. 国家与版位结构

| 结构问题 | 可观察信号 | 判断方式 | 动作 |
| --- | --- | --- | --- |
| 低回收国家吃量 | campaign 总 CPI 下降但 ROI / profit 下降 | 按 country 拆 cost、install、ROI、retention、revenue | 拆国家或限制低回收国家预算。 |
| 高价值国家拿不到量 | 高 ROI 国家 spend 低、学习不足 | 看 campaign budget 是否被其他国家吸走 | 单独建测试结构或提高该国家预算机会。 |
| 版位误触风险 | 某 placement CTR 高但 CVR / 留存弱 | 按 publisher_platform / platform_position 拆 | 限制或单独验证该版位。 |
| 设备结构变化 | Android / iOS、device_platform mix 变化 | 对齐包、系统和变现口径 | 分设备判断 CPI 与回收。 |
| 地区语言错配 | CTR 可接受但后续事件弱 | 看素材语言、国家、落地页和产品语言 | 做本地化素材和文案变体。 |

## 9. IAA 与 IAP 的回收判断

| 商业模式 | 主看指标 | Meta 平台信号的作用 | Snowball / BI 门禁 |
| --- | --- | --- | --- |
| IAA | ROI0、ROI3、ads revenue、eCPM、IPU、D1 留存、广告展示场景 | CPI、CTR、frequency 只解释获量质量 | 低 CPI 必须带来足够广告展示和留存，否则不放量。 |
| IAP | ROI0、ROI3、ROI7、首购率、订阅率、trial、ARPPU、payback | CPA / purchase actions 可辅助判断 | 平台 purchase 不等于 cohort profit，必须看 Snowball 付费收入和退款 / 取消风险。 |
| IAA+IAP | ads revenue + purchase revenue、混合 ROI、关键行为、留存 | 解释流量结构和素材承诺 | 拆广告收入与内购收入，避免总 ROI 掩盖结构恶化。 |

IAA 常见误判：

| 误判 | 修正 |
| --- | --- |
| CPI 低就放量 | 还要看 D1 留存、广告展示次数、IPU、eCPM 和 ROI0。 |
| CTR 高就判素材 winner | 还要看是否带来广告触发和长期留存。 |

IAP 常见误判：

| 误判 | 修正 |
| --- | --- |
| 平台 purchase 多就加预算 | 还要看 Snowball 首购收入、订阅质量、退款和 payback。 |
| ROI0 低就立刻暂停 | 若产品付费延迟明显，应结合 ROI3 / ROI7 和关键事件。 |

## 10. Snowball / BI 对账

### 10.1 对账顺序

1. 确认 Meta account、campaign、adset、ad 命名和 Snowball network / campaign / adgroup 映射。
2. 对齐日期窗口和时区，默认使用完整自然日。
3. 对齐 spend、install、country、campaign，识别缺失、重复和命名变化。
4. 判断数据质量：`ready / partial / blocked / inactive_no_data`。
5. 只有 `ready` 或 `partial` 可输出预算建议；`blocked` 只输出数据修复建议。

### 10.2 对账表模板

| 对象 | Meta spend | Snowball cost | 差异 | Meta installs / actions | Snowball installs | Snowball ROI0 | Snowball ROI3 | Snowball ROI7 | 数据质量 | 备注 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Campaign A |  |  |  |  |  |  |  |  | ready / partial / blocked |  |

### 10.3 不能下强结论的场景

| 场景 | 输出方式 |
| --- | --- |
| Meta 有 spend，Snowball 无 cost / install | `blocked`，优先修复映射或归因。 |
| Snowball 有 ROI，但 campaign / adset 无法映射 | 只能做账户或国家层判断。 |
| ROI7 是 forecast | 可辅助判断，不单独作为强放量依据。 |
| 当前日数据未完整 | 标注低置信度或排除当前日。 |
| 平台和 Snowball 安装差异大 | 先做归因与数据质量检查，不给预算强动作。 |

## 11. Meta Campaign 生命周期表模板

| Campaign | 类型 | 预算结构 | 国家 | 当前状态 | Learning 状态 | Spend | Installs | CPI | CTR | CPM | Frequency | ROI0 | ROI3 | ROI7 | Profit | 素材状态 | 生命周期 | 动作 |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Campaign A | Advantage+ App / ASC / Manual | campaign budget / adset budget | US / 混投 | Active | Learning / Learning Limited / Active |  |  |  |  |  |  |  |  | forecast / actual |  | fresh / stable / fatigue | testing / scaling / mature / fatigue / pause_candidate |  |

## 12. 诊断结论模板

### 12.1 总体结论

- 项目：`{Project ID} / {Product}`
- 账户：`{Meta ad account name} / {account id}`
- 日期：`YYYY-MM-DD ~ YYYY-MM-DD`
- 商业模式：`IAA / IAP / IAA+IAP`
- 数据源：Meta Ads 当前投放数据 + Snowball / BI 当前回收数据
- 数据质量：`ready / partial / blocked / inactive_no_data`

5 行内结论：

1. `{Campaign / account 当前处于什么生命周期阶段}`。
2. `{核心证据：spend / CPI / frequency / ROI / profit / retention}`。
3. `{主要风险：learning、fatigue、国家 mix、版位、归因或回收延迟}`。
4. `{今日动作：add_budget / small_add / maintain / refresh_creative / reduce_or_reallocate / pause_candidate}`。
5. `{复查窗口：下一个完整自然日或 2-3 个完整自然日}`。

### 12.2 候选清单

| 分类 | 对象 | 证据 | 动作 | 置信度 | 复查日期 |
| --- | --- | --- | --- | --- | --- |
| 放量候选 |  |  | `small_add / add_budget` | high / medium / low | YYYY-MM-DD |
| 观察候选 |  |  | `maintain / hard_observe` | high / medium / low | YYYY-MM-DD |
| 降量 / 迁移候选 |  |  | `reduce_or_reallocate` | high / medium / low | YYYY-MM-DD |
| 暂停候选 |  |  | `pause_candidate` | high / medium / low | YYYY-MM-DD |
| 素材刷新候选 |  |  | `refresh_creative` | high / medium / low | YYYY-MM-DD |
| 数据修复候选 |  |  | `data_gap_check` | high / medium / low | YYYY-MM-DD |

## 13. 真实出海 App 案例场景占位

以下仅为写报告时的场景占位，不代表实时数据。

### 13.1 IAA 工具 App - 低 CPI 但广告回收弱

| 项目 | 内容 |
| --- | --- |
| 背景 | Meta ASC 在多国混投中 CPI 下降，但 Snowball ROI0 和广告展示 IPU 同步下降。 |
| 初步判断 | 系统可能把预算转向低成本低变现国家或低质量版位。 |
| 必查字段 | country spend、publisher_platform、frequency、D1 retention、ad impressions、IPU、eCPM、ROI0。 |
| 动作占位 | 拆国家 / 版位结构，低回收国家降预算，高回收国家单独测试，素材承诺改为高意图场景。 |

### 13.2 IAP 订阅 App - 平台 purchase 增加但 payback 变慢

| 项目 | 内容 |
| --- | --- |
| 背景 | 手动 Campaign 的 purchase actions 增加，Meta CPA 看似变好，但 Snowball ROI3 / ROI7 和订阅续费不稳定。 |
| 初步判断 | 平台归因 purchase 不能直接等同于高质量付费，可能存在 trial 质量或退款风险。 |
| 必查字段 | purchase revenue、trial rate、subscribe rate、refund / cancel、ROI3、ROI7、国家 mix、adset 学习状态。 |
| 动作占位 | 维持或小幅验证，不做大额放量；检查 trial 到订阅转化和素材承诺。 |

### 13.3 IAA+IAP 内容 App - 素材 winner 出现疲劳

| 项目 | 内容 |
| --- | --- |
| 背景 | 历史 winner 素材仍有 spend，但 frequency 上升，CTR 下滑，ROI 和留存走弱。 |
| 初步判断 | 素材 fatigue 或受众触达饱和，不能只靠加预算恢复。 |
| 必查字段 | creative spend、frequency、CTR、CPC、CPM、CVR、ROI0/3/7、ads revenue、purchase revenue、留存。 |
| 动作占位 | 基于 winner 做 hook、first frame、CTA、字幕、语言、本地化变体，并降低旧素材预算权重。 |

### 13.4 手动 Campaign - adset 间质量差异大

| 项目 | 内容 |
| --- | --- |
| 背景 | ABO 中某 adset CPI 低但 ROI 弱，另一个 adset CPI 较高但 profit 更好。 |
| 初步判断 | 不能按 CPI 分配预算，应按 Snowball 回收和利润迁移预算。 |
| 必查字段 | adset spend、install、CPI、ROI0、ROI3、profit、country、placement、retention。 |
| 动作占位 | 降低低回收 adset，迁移小预算到高 profit adset，并设置 2-3 个完整自然日复查。 |

## 14. 输出检查清单

开始前：

- [ ] 已确认产品、Project ID、Meta account id 和 campaign / adset 命名。
- [ ] 日期范围是绝对日期，默认不含当天。
- [ ] 已拉取当前投放状态、预算结构、Learning 状态、素材表现和频次。
- [ ] 已拉取当前 Snowball / BI 回收，并完成平台与 Snowball 对账。

分析中：

- [ ] `-1`、null、N/A、forecast、当天采样和延迟数据已处理。
- [ ] 已拆国家、campaign、adset、creative、placement 中与问题相关的层级。
- [ ] 没有只用 CTR、CPI、平台 ROAS 或单条素材表现做预算动作。
- [ ] IAA / IAP / IAA+IAP 的回收口径已分别判断。

产出前：

- [ ] 放量、观察、降量、暂停、素材刷新和数据修复候选已分开。
- [ ] 每条动作都有对象、证据、置信度和复查日期。
- [ ] `blocked` 数据质量没有输出强预算动作。
- [ ] Snowball 无 creative 级 ROI 时，creative 判断已标注为 parent campaign / adset 推断。

## 15. 参考口径

| 主题 | 参考 |
| --- | --- |
| Learning phase | [Meta Business Help Center: About the learning phase](https://www.facebook.com/business/help/112167992830700) |
| Learning Limited | [Meta Business Help Center: About Learning Limited](https://www.facebook.com/business/help/269269737396981) |
| Advantage+ campaign budget | [Meta Business Help Center: About Advantage+ campaign budget](https://www.facebook.com/business/help/153514848493595) |
| Campaign budget 与 adset budget | [Meta Business Help Center: About campaign budgets and ad set budgets](https://www.facebook.com/business/help/458847204894307) |
| Creative fatigue | [Meta Business Help Center: About creative fatigue recommendations](https://www.facebook.com/business/help/1346816142327858) |
| Frequency controls | [Meta Business Help Center: About frequency controls for auction](https://www.facebook.com/business/help/422853447344162) |
