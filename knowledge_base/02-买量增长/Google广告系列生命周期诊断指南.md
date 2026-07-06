# Google 广告系列生命周期诊断指南

## 1. 定位

本指南用于把通用的 `广告系列生命周期诊断模板` 扩展为 Google Ads 出海 App 投放的实操诊断文档，覆盖 App Campaign、App Campaign for engagement、tCPA、tROAS、Performance Max、资产组、素材资产、国家扩量、iOS/Android 分平台观察，以及 Snowball / BI 回收对账。

核心原则：

- 每次分析都必须使用当前日期窗口、当前 campaign 状态、当前出价策略、当前预算、当前素材资产表现、当前国家结构和当前 Snowball 回收。
- 历史经验只能作为假设来源，不能替代实时 Google Ads 和 Snowball / BI 数据。
- Google Ads 后台短期转化、平台 ROAS、asset performance label 只能作为平台侧信号；预算动作必须由 Snowball / BI 的真实回收、留存、利润共同确认。
- 不编造实时数据。没有查询到的数据写 `数据缺失`，样本不足写 `样本不足/低置信度`，不能把 `-1`、null、N/A 当作 0。

## 2. 总模板字段采访：哪些可直接用，哪些要改造，哪些要谨慎

### 2.1 可直接沿用的字段

| 总模板字段 | Google Ads 中是否可直接用 | 使用方式 |
| --- | --- | --- |
| 产品 / Project ID | 可直接用 | 先在 [[project_registry]] 或 Snowball 项目列表中确认，不要只用产品俗称。 |
| 渠道 | 可直接用 | 固定写 `Google Ads`，必要时补 `App Campaign / PMax / ACE`。 |
| 账户 | 可直接用 | 写 Google Ads customer id、MCC 层级、账户名称。 |
| 日期范围 | 可直接用 | 使用绝对日期，例如 `2026-06-28 ~ 2026-07-04`，默认不含当天。 |
| 商业模式 | 可直接用 | `IAA / IAP / IAA+IAP`，后续回收字段随商业模式变化。 |
| 数据质量 | 可直接用 | `ready / partial / blocked / inactive_no_data`，决定是否允许给预算动作。 |
| 回收口径 | 可直接用 | `ROI0 / ROI3 / ROI7 / profit / payback`，ROI7 forecast 必须标注。 |
| 生命周期状态 | 可直接用 | 保留 `testing / scaling / mature / fatigue / pause_candidate`，Google 场景补充 `learning` 判断。 |
| P0/P1/P2 动作 | 可直接用 | 预算、素材、国家动作必须符合 [[action_rules]]。 |

### 2.2 需要改成 Google 特有字段的内容

| 总模板字段 | Google Ads 改造字段 | 说明 |
| --- | --- | --- |
| Campaign 类型 | advertising channel type / subtype | 区分 `App Campaign`、`App Campaign for engagement`、`Performance Max`，不要只写 App。 |
| 子层级 | ad group / asset group / asset | App Campaign 常见分析层级是 campaign、ad group、asset；PMax 重点是 asset group、asset group asset。 |
| 素材字段 | asset type、asset performance label、policy status、approval status | Google 的素材不是 Meta ad creative 结构，不能直接套 ad/adset 口径。 |
| 出价策略 | bid strategy type、target CPA、target ROAS、maximize conversions/value | 生命周期判断必须结合当前出价策略和最近是否改过 target。 |
| 转化目标 | conversion action、primary/secondary、conversion value、import source | 先确认 Google 优化目标是否仍代表真实高质量用户。 |
| 国家结构 | campaign location、country spend、country ROI、country retention | Google 自动化投放容易让预算向低 CPI 但低质量国家漂移。 |
| 平台 ROAS | Google conversion value / cost | 只能代表 Google 归因价值，必须和 Snowball cohort revenue 对账。 |
| 学习状态 | learning / limited / eligible / serving health | 预算、出价、目标事件、素材大改后需要额外观察学习期。 |

### 2.3 必须谨慎使用的内容

| 字段或信号 | 风险 | 正确处理 |
| --- | --- | --- |
| Google Ads conversions | 可能包含延迟、重复、窗口差异或低质量事件 | 与 Snowball install、关键事件、收入对账后再判断。 |
| Google Ads ROAS | 可能受价值回传、事件配置和归因窗口影响 | 不单独作为放量依据，必须看 Snowball ROI/profit。 |
| asset performance label | 是平台相对信号，不等于真实 ROI | 用于素材迭代线索，不直接决定加预算。 |
| 低 CPI | 可能是低质国家、低质库存或事件承诺错配 | 同看 D1/D3 留存、关键事件、广告展示、付费率。 |
| 短期 ROI0 | IAP 和订阅可能收入延迟，IAA 也会受 eCPM 波动影响 | 按商业模式看 ROI3/ROI7、payback 和利润。 |
| PMax 自动化分配 | 流量和资产归因更黑盒 | 更重视 asset group 主题、国家结构和 Snowball 回收。 |
| 历史 winner 素材 | 可能已经疲劳或换量失效 | 每次重新拉当前资产表现和 parent campaign 回收。 |

## 3. Google Ads 生命周期定义

| 状态 | Google Ads 判断标准 | Snowball / BI 判断标准 | 主要风险 | 默认动作 |
| --- | --- | --- | --- | --- |
| testing | 新 campaign、新国家、新目标事件或新素材组，预算和转化样本未达观察门槛 | ROI / 留存 / 关键事件尚未完整 | 过早判定 winner / loser | `test_budget` / `maintain` |
| learning | 最近发生预算、target CPA / target ROAS、转化目标、国家、资产组大改，系统分配仍在重新稳定 | cohort 数据未完整，边际质量不可确认 | 频繁改动导致学习反复重启 | `maintain` / `observe` |
| scaling | 消耗和转化增长，CPA/ROAS 可接受，国家和资产组结构健康 | ROI、profit、留存达标或边际可接受 | 加预算后向低质国家或低质资产倾斜 | `small_add` / `add_budget` |
| mature | 消耗、CPA、ROI、留存稳定，预算已经进入常规承接 | 多个完整窗口回收稳定 | 素材疲劳、国家结构固化、增长停滞 | `maintain` / `refresh_creative` |
| fatigue | CTR/CVR 下降、CPC/CPM/CPA 上升、资产标签变弱或展示集中到老素材 | ROI、留存、关键事件或利润下滑 | 继续烧预算但用户质量下降 | `refresh_creative` / `reduce_or_reallocate` |
| pause_candidate | 连续多个完整窗口不达标，且不是归因延迟、事件配置或学习期扰动 | ROI/profit 连续不达标，留存或收入质量明显弱 | 误停仍有恢复机会的 campaign | 人工复核后 `pause_candidate` |

注意：`learning` 不是总模板中的独立最终状态，而是 Google 自动化投放必须附加标记。最终输出可写成 `testing + learning`、`scaling + learning_risk`、`mature` 等组合。

## 4. 每次诊断必须重新拉取的实时输入

| 输入类别 | 当前字段 | 用途 |
| --- | --- | --- |
| Campaign 基础 | status、serving status、advertising channel type、campaign subtype、start/end date | 判断是否真的在投、是否受限、是否处于 App / PMax / ACE。 |
| 预算 | daily budget、budget status、最近预算调整记录 | 判断是否 budget limited、是否大幅调整后进入学习扰动。 |
| 出价 | bidding strategy、target CPA、target ROAS、maximize conversions/value | 判断当前算法目标和业务目标是否一致。 |
| 转化 | conversion actions、primary/secondary、conversion value、attribution settings | 判断平台优化事件是否可靠。 |
| 平台表现 | cost、impressions、clicks、CTR、CPC、CPM、conversions、CPA、conversion value、Google ROAS | 判断获量效率、平台侧趋势和流量价格。 |
| 资产表现 | asset group、asset type、asset text/name、performance label、approval/policy status | 判断素材覆盖、主题结构、疲劳和审核问题。 |
| 国家表现 | country、cost、conversions、CPA、Google ROAS、Snowball ROI/retention/profit | 判断国家 mix 是否拖累或支撑扩量。 |
| Snowball 回收 | install、cost、revenue、ROI0/3/7、profit、retention、关键事件、IAA/IAP 收入拆分 | 决定最终预算动作。 |

默认日期窗口：

| 场景 | 建议窗口 | 说明 |
| --- | --- | --- |
| 生命周期初判 | 近 7 个完整自然日 | 不含当天，适合 campaign / 国家 / 预算动作。 |
| 学习期观察 | 最近一次大改后到昨天 | 必须标注大改日期。 |
| 素材疲劳 | 近 14-30 个完整自然日 | 看 CTR/CVR/CPA 和素材标签趋势。 |
| IAP / 订阅回收 | 近 7 天投放 + ROI7/更长 payback | 不要只看 ROI0。 |
| IAA 回收 | 近 7 天投放 + ROI0/ROI3 + eCPM/IPU | 留存和广告展示机会必须同看。 |

## 5. Google Ads 可观察信号

| 信号层 | 关键字段 | 代表问题 | 常见动作 |
| --- | --- | --- | --- |
| 流量价格 | CPM、CPC、CTR | 竞价变贵、素材吸引力下降、受众变窄 | 补素材、换 hook、拆国家、谨慎加预算。 |
| 转化效率 | CVR、CPA、cost_per_conversion | 落地页 / 商店页 / 事件质量 / 国家 mix 问题 | 查 store listing、目标事件、国家结构。 |
| 价值效率 | conversion value、Google ROAS、value/cost | 平台价值回传是否支撑出价 | 和 Snowball cohort revenue 对账。 |
| 资产覆盖 | text/image/video/logo/HTML5 数量和审核状态 | 素材不足导致系统自动生成或分发受限 | `add_assets` / `refresh_video`。 |
| 资产质量 | asset performance label、花费集中度、转化集中度 | winner、疲劳、主题混杂、低质承接 | 保留 winner 变体，拆分或合并 asset group。 |
| 国家结构 | country spend、CPA、ROI、retention | 低价低质国家吃预算或高质国家未吃量 | 国家拆分、预算迁移、排除/单独测试。 |
| 后端质量 | ROI、profit、retention、关键事件、广告展示、付费率 | 平台转化与真实商业价值不一致 | 不放量，先做数据和事件质量检查。 |

## 6. App Campaign 与 Performance Max 差异

| 维度 | App Campaign | Performance Max |
| --- | --- | --- |
| 主要目标 | App installs、in-app actions、engagement、value | 跨 Google 库存按目标最大化转化或转化价值，App 业务需确认是否适配当前账户和目标。 |
| 常见优化 | tCPI、tCPA、tROAS、maximize conversions/value | Smart Bidding，常见为 maximize conversions/value，可带 target CPA / target ROAS。 |
| 核心结构 | campaign、ad group、asset、conversion action | campaign、asset group、asset group asset、audience signal、final URL/素材主题。 |
| 素材组织 | 多类型 app assets，系统自动组合分发 | 按 asset group 主题组织标题、描述、图片、视频、logo 等。 |
| 诊断难点 | 安装/事件质量和素材资产贡献不完全透明 | 流量更黑盒，asset group 和库存分配更需要后端回收校验。 |
| 放量判断 | 看目标事件质量、国家 ROI、素材供给 | 看 asset group 主题是否清晰、国家结构是否健康、Snowball 回收是否承接。 |
| 不建议 | 只因 tCPA 达标就加预算 | 只因 PMax Google ROAS 高就加预算。 |

## 7. 测试期与学习期判断

### 7.1 testing 的最低判断项

| 检查项 | 问题 | 结论写法 |
| --- | --- | --- |
| 是否达到最低 spend / install / conversion 样本 | 样本不足会让 CPA/ROAS 抖动 | `样本不足，仅保留测试预算`。 |
| 是否跨完整自然日 | 当天数据可能延迟或采样 | `不含当天，使用完整自然日判断`。 |
| 是否有足够素材资产 | 素材不足会限制系统探索 | `先补素材，再判断放量`。 |
| 是否有可解释的国家结构 | 混合国家会掩盖低质流量 | `需拆国家 ROI 和留存`。 |
| 是否对齐 Snowball install / revenue | 平台转化好不等于真实回收好 | `Snowball 未确认前不放量`。 |

### 7.2 learning 的触发项

| 触发项 | 影响 | 建议观察 |
| --- | --- | --- |
| 日预算大幅调整 | 系统重新分配流量，CPA/ROI 可能短期波动 | 至少观察 2-3 个完整自然日，IAP 看更长回收。 |
| target CPA / target ROAS 调整 | 改变竞价约束和可触达库存 | 避免连续多次大幅调整。 |
| primary conversion action 变更 | 学习目标改变，历史表现不可直接比较 | 新旧事件分段分析。 |
| 新增/删除国家 | 国家 mix 改变，整体 CPA/ROI 失真 | 按国家拆分 before/after。 |
| 大量替换素材或 asset group | 创意探索重新分配 | 看 asset label、CTR/CVR 和 parent ROI。 |

## 8. 资产组与素材资产诊断

### 8.1 Asset Group 体检表

| Asset Group | 主题 | 国家/语言 | Cost | Conv | Google ROAS | Snowball ROI | 素材覆盖 | 风险 | 动作 |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| 占位 | 例如：新手引导 / 订阅权益 / 工具场景 | 占位 | 占位 | 占位 | 占位 | 占位 | text/image/video/logo | 占位 | `add_assets / split_asset_group / maintain` |

### 8.2 素材资产判断

| 资产类型 | 必看字段 | 常见问题 | 动作 |
| --- | --- | --- | --- |
| Video | 展示、点击、转化、CTR、CVR、资产标签、视频方向 | 缺竖版、前 3 秒弱、老 winner 疲劳 | `refresh_video`，做 hook / first frame / CTA / 语言变体。 |
| Image | CTR、CPC、展示份额、审核状态 | UI 不清、承诺过强、场景不匹配 | 补核心卖点、真实界面、国家语言版本。 |
| Text | 标题、短描述、长描述、转化贡献 | 关键词意图泛、夸大承诺、与商店页不一致 | 保留高意图表达，删除误导承诺。 |
| Logo / Brand | 审核状态、覆盖状态 | 品牌信任弱、审核受限 | 补标准尺寸和清晰品牌资产。 |
| HTML5 / playable | 互动率、转化、后端质量 | 高互动低回收、玩法承诺错配 | 只在 Snowball 质量通过后扩量。 |

素材结论必须写清楚：

- `Google Ads asset label 仅表示平台相对表现，不代表素材真实 ROI`。
- `creative ROI 基于所属 campaign / asset group / 国家回收推断`。
- fresh low-spend 新素材写 `too early to judge`，不要提前判 winner/loser。

## 9. 国家放量诊断

| 国家状态 | Google Ads 信号 | Snowball / BI 信号 | 动作 |
| --- | --- | --- | --- |
| 可放量国家 | cost 增长后 CPA 稳定，转化量可持续 | ROI/profit/留存达标，IAA 或 IAP 收入质量稳定 | `small_add`，优先小幅预算或单独 campaign 承接。 |
| 观察国家 | CPA 可接受但样本不足或 ROI 延迟 | ROI 未完整，留存/事件未明显异常 | `maintain`，补样本后复查。 |
| 高风险国家 | 低 CPI 但转化价值弱，或消耗快速扩大 | ROI/profit 不达标，留存或广告展示/付费弱 | `reduce_or_reallocate`，必要时拆出或排除。 |
| 数据阻塞国家 | 平台和 Snowball cost/install 对不上 | 数据质量 `partial / blocked` | 不做预算动作，先 `data_gap_check`。 |

国家扩量注意事项：

- 高 eCPM / 高付费国家和低价长尾国家不要长期混在同一预算池里判断。
- iOS 和 Android 要分开观察，尤其是 IAP、订阅、SKAN / 隐私延迟影响明显时。
- 低 CPI 国家若 D1 留存、广告展示机会、付费率弱，不是放量机会。

## 10. 预算调整规则

| 场景 | 必须满足 | 建议动作 | 禁止动作 |
| --- | --- | --- | --- |
| 小幅加预算 | Snowball ROI/profit 达标，国家结构健康，学习期已稳定 | `small_add`，记录复查日期 | 一次性大幅加预算且不设复查。 |
| 加大预算 | 多个完整窗口达标，边际回收未劣化，素材储备足够 | `add_budget`，同步看素材供给 | 只因 Google CPA 降低就加预算。 |
| 维持 | 平台和后端信号基本稳定，无明显增量空间 | `maintain` | 为了追求规模频繁改 target。 |
| 降预算/迁移 | 某国家、asset group 或 campaign 拖累回收 | `reduce_or_reallocate` | 数据质量 blocked 时直接降预算。 |
| 暂停候选 | 连续不达标且排除归因、事件、学习期、收入延迟问题 | `pause_candidate`，需人工确认 | 自动执行暂停。 |

预算动作必须注明：

- 当前预算。
- 最近一次预算调整日期。
- 是否处于 learning。
- 复查窗口。
- Snowball 回收是否支持。

## 11. tCPA / tROAS 调整规则

| 出价策略 | 适用阶段 | 看什么 | 调整建议 | 风险 |
| --- | --- | --- | --- | --- |
| tCPI | 冷启动、安装量测试 | install、CPI、D1 留存、关键事件 | 只用于验证基础量和国家质量 | 容易买到低质安装。 |
| tCPA | 关键事件稳定后 | CPA、event-to-revenue 相关性、ROI3/ROI7 | 目标事件质量可靠时再放量 | CPA 达标但真实收入弱。 |
| tROAS | IAP 或混合变现价值回传稳定后 | Google ROAS、Snowball ROI/profit、收入延迟 | 以真实 payback 和利润决定 target | 样本稀疏会抑制探索。 |
| Maximize conversions | 测试新目标或放开探索 | 转化量、CPA、后端质量 | 配合预算上限和完整观察窗 | 可能追低质量转化。 |
| Maximize conversion value | 价值回传较可信时 | value/cost、收入源拆分、ROI | 与 tROAS 分阶段测试 | 回传价值偏差会误导出价。 |

调整原则：

- 不在同一观察窗内连续大幅调整 target CPA / target ROAS。
- target CPA 降得过紧可能导致量级下降，target ROAS 设得过高可能抑制探索。
- tROAS 不能只看 Google Ads conversion value，必须看 Snowball cohort revenue 和利润。
- IAA 项目通常更依赖广告收入、留存、展示机会，不要用不稳定价值回传直接重压 tROAS。

## 12. IAA、IAP、IAA+IAP 的回收判断

| 商业模式 | 核心回收字段 | Google Ads 侧重点 | Snowball / BI 侧重点 | 常见误判 |
| --- | --- | --- | --- | --- |
| IAA | ROI0/3、ads revenue、eCPM、IPU、D1/D3 留存 | install、CPA、国家、素材吸引力 | 广告展示机会、留存、广告格式收入 | 低 CPI 但低留存，广告收入撑不起来。 |
| IAP | ROI3/7、payer rate、first purchase rate、ARPPU、subscription trial | 高质量事件、conversion value、tROAS | 付费率、首购成本、订阅回收、利润 | ROI0 弱就过早停，忽略收入延迟。 |
| IAA+IAP | 总 ROI、广告收入、IAP 收入、利润、payback | value-based bidding 与事件质量 | 分收入源看边际质量 | 广告活跃掩盖付费质量下滑，或反过来。 |

输出结论时必须写：

- 当前使用哪个收入源做主判断。
- ROI7 是否 forecast。
- IAP 是否存在回收延迟。
- IAA 是否检查 eCPM、IPU、留存和广告展示机会。

## 13. Snowball / BI 对账流程

| 步骤 | 对账项 | 判断 |
| --- | --- | --- |
| 1 | Google Ads cost vs Snowball cost | 金额口径、时区、税费、账户映射是否一致。 |
| 2 | Google conversions vs Snowball installs / events | 转化事件、归因窗口、延迟、重复是否一致。 |
| 3 | Google conversion value vs Snowball revenue | 价值回传是否覆盖 IAA/IAP，是否漏回传或延迟。 |
| 4 | Campaign / country 映射 | campaign 名称、国家、平台、包名是否能对上。 |
| 5 | ROI / profit | 是否达到阈值，是否受 forecast、样本不足或当天数据影响。 |
| 6 | 数据质量分级 | `ready` 才能给强预算动作；`partial` 降级建议；`blocked` 只给修复动作。 |

数据质量动作：

| 数据质量 | 可给动作 | 不可给动作 |
| --- | --- | --- |
| ready | `small_add / add_budget / maintain / reduce_or_reallocate / refresh_creative` | 仍需人工确认暂停。 |
| partial | `maintain / observe / refresh_creative / data_gap_check` | 不给强放量或强暂停。 |
| blocked | `data_gap_check` | 不给预算、暂停、放量结论。 |
| inactive_no_data | `no_action_no_data` | 不做投放判断。 |

## 14. Google 生命周期诊断输出模板

### 14.1 基本信息

| 项目 | 内容 |
| --- | --- |
| 产品 | 占位 |
| Project ID | 占位 |
| 平台 | Android / iOS / both |
| Google Ads 账户 | 占位 |
| Campaign 类型 | App Campaign / App Engagement / PMax |
| Campaign / Asset Group | 占位 |
| 日期范围 | YYYY-MM-DD ~ YYYY-MM-DD |
| 最近一次预算/出价/目标事件调整 | YYYY-MM-DD，动作占位 |
| 商业模式 | IAA / IAP / IAA+IAP |
| 当前出价策略 | tCPI / tCPA / tROAS / Max Conv / Max Value |
| 数据质量 | ready / partial / blocked / inactive_no_data |
| 回收口径 | ROI0 / ROI3 / ROI7 forecast / profit / payback |

### 14.2 Campaign 生命周期表

| Campaign | 类型 | 平台 | 国家 | 当前状态 | 出价策略 | Spend | Conv/Installs | CPA/CPI | Google ROAS | Snowball ROI0 | Snowball ROI3 | Snowball ROI7 | Profit | 生命周期 | 动作 |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 占位 | App / PMax | Android / iOS | 占位 | enabled / paused / limited | 占位 | 占位 | 占位 | 占位 | 占位 | 占位 | 占位 | 占位 | 占位 | testing / scaling / mature / fatigue / pause_candidate | 占位 |

### 14.3 国家下钻表

| 国家 | Spend | Installs | CPI | Google Conv | Google ROAS | Snowball ROI | D1 留存 | IAA 收入 | IAP 收入 | 状态 | 动作 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 占位 | 占位 | 占位 | 占位 | 占位 | 占位 | 占位 | 占位 | 占位 | 占位 | 占位 | 占位 |

### 14.4 资产组 / 素材表

| Asset Group / Asset | 类型 | 主题 | 审核状态 | Cost | Impr | CTR | Conv | CPA | Asset Label | Parent Snowball ROI | 判断 | 动作 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |
| 占位 | video / image / text / logo | 占位 | approved / limited / disapproved | 占位 | 占位 | 占位 | 占位 | 占位 | best / good / low / learning | 占位 | 占位 | 占位 |

### 14.5 诊断结论

- 放量候选：
- 观察候选：
- 降量/迁移预算候选：
- 暂停候选：
- 素材刷新候选：
- 国家拆分候选：
- 出价策略调整候选：
- 数据修复候选：

### 14.6 下一步动作

| 优先级 | 动作 | 对象 | 触发条件 | 执行限制 | 复查日期 |
| --- | --- | --- | --- | --- | --- |
| P0 / P1 / P2 | `small_add / add_budget / maintain / reduce_or_reallocate / refresh_creative / add_assets / data_gap_check` | Campaign / country / asset group / asset | 占位 | 需 Snowball ready / 需人工确认 / 只读建议 | YYYY-MM-DD |

## 15. 真实出海 App 案例场景占位

以下是写报告时可复用的案例结构，不代表当前实时数据。

### 15.1 IAA 工具类 App：低 CPI 但回收弱

| 场景 | 占位内容 |
| --- | --- |
| 产品 | 例如 PDF / Scanner / Cleaner / Weather 工具类 App |
| 现象 | Google Ads tCPI / tCPA 达标，安装增长，但 Snowball ROI0/3 不达标。 |
| 可能原因 | 低价国家占比上升、D1 留存弱、广告展示机会不足、素材承诺与真实功能错配。 |
| 需要查询 | country spend、CPI、D1 retention、IPU、ads revenue、asset group spend。 |
| 结论模板 | `平台侧 CPA 达标但 Snowball 回收弱，暂不放量；优先拆国家和检查素材承诺。` |

### 15.2 IAP / 订阅 App：ROI0 弱但 ROI7 可能恢复

| 场景 | 占位内容 |
| --- | --- |
| 产品 | 例如 AI 工具、翻译、编辑、订阅型效率 App |
| 现象 | 初期 ROI0 弱，Google tROAS 波动，Snowball ROI7 或 payback 需要更长观察。 |
| 可能原因 | 试用期、首购延迟、订阅转化延迟、价值回传稀疏。 |
| 需要查询 | first purchase rate、trial start、payer rate、ROI3/7、subscription revenue、target ROAS 调整记录。 |
| 结论模板 | `不基于 ROI0 直接暂停；在数据质量 ready 前维持预算或小幅调整 target。` |

### 15.3 IAA+IAP 混合变现：广告收入掩盖付费质量

| 场景 | 占位内容 |
| --- | --- |
| 产品 | 例如内容、阅读、天气、工具混合变现 App |
| 现象 | 总 ROI 接近达标，但 IAP 收入下滑或付费率下降。 |
| 可能原因 | 新增用户偏广告活跃但低付费，人群结构变化。 |
| 需要查询 | ads revenue、IAP revenue、payer rate、IPU、国家 mix、campaign / asset group。 |
| 结论模板 | `总 ROI 可观察，但不建议强放量；需拆收入源和国家后确认边际质量。` |

### 15.4 PMax 资产组扩量：Google ROAS 高但 Snowball 未确认

| 场景 | 占位内容 |
| --- | --- |
| 产品 | 任意有 PMax 结构的出海 App |
| 现象 | 某 asset group Google ROAS 高、平台转化多，但 Snowball campaign / 国家回收未同步提升。 |
| 可能原因 | conversion value 回传偏差、归因窗口差异、低质库存、跨国家 mix。 |
| 需要查询 | asset group cost、conversion value、country Snowball ROI、campaign mapping、conversion action。 |
| 结论模板 | `asset group 是素材迭代候选，不是预算放量依据；需等 Snowball ready 后复判。` |

### 15.5 iOS / Android 分平台差异

| 场景 | 占位内容 |
| --- | --- |
| 产品 | 同产品双平台投放 |
| 现象 | Android 量级稳定，iOS 平台 ROAS 或 Snowball 回收延迟更明显。 |
| 可能原因 | SKAN / 隐私延迟、订阅回收周期、平台转化回传差异。 |
| 需要查询 | platform、campaign subtype、ROI0/3/7、payback、first purchase rate、国家结构。 |
| 结论模板 | `Android 和 iOS 分开判断生命周期，不合并给预算动作。` |

## 16. 总模板建议反向引用本指南的内容

建议在总模板中增加或引用以下 Google 专属内容：

| 建议引用位置 | 引用内容 | 原因 |
| --- | --- | --- |
| `诊断输入` | 增加 `出价策略 / conversion action / asset group / asset performance label / campaign serving status` | Google 自动化投放的生命周期无法只靠 spend、ROI、素材 CTR 判断。 |
| `生命周期定义` | 增加 `learning` 作为附加标记 | App Campaign / PMax 在预算、出价、目标事件、素材大改后会重新学习。 |
| `Campaign 表` | 增加 `出价策略、Google ROAS、Snowball ROI、平台、当前状态` | 区分平台信号和后端真实回收。 |
| `注意事项` | 增加 `asset performance label 不等于真实 ROI` | 避免把 Google 素材标签当预算依据。 |
| `下一步` | 增加 `tCPA/tROAS 调整、asset group 拆分/合并、add_assets` | Google Ads 的实操动作不只有加/降预算和刷新素材。 |
| `数据质量` | 增加 `Google Ads 与 Snowball 对账状态` | 对账不通过时不能给强预算动作。 |

## 17. 参考资料

- [Google Ads Help: About Performance Max campaigns](https://support.google.com/google-ads/answer/10724817)
- [Google Ads Help: Choose a bid strategy for your App campaign](https://support.google.com/google-ads/answer/12073727)
- [Google Ads Help: About Target CPA bidding](https://support.google.com/google-ads/answer/6268632)
- [Google Ads Help: About Target ROAS bidding](https://support.google.com/google-ads/answer/6268637)
- [Google Ads API: Performance Max asset groups](https://developers.google.com/google-ads/api/performance-max/asset-groups)
- [Google Ads API: Performance Max campaign reporting](https://developers.google.com/google-ads/api/performance-max/campaign-reporting)
