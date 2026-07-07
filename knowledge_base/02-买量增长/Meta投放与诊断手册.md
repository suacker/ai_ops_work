# Meta 投放与诊断手册

## 1. 定位与适用范围

本页是 Facebook / Meta Ads 出海 App 投放的唯一平台手册，覆盖 Advantage+ App Campaign、ASC、手动 Campaign、CBO / ABO、adset、creative、出价策略、投放节奏、国家、版位、Learning / Learning Limited、素材 fatigue、频次、iOS 归因、日常监测和 Snowball / BI 回收判断。通用的生命周期阶段、数据质量门禁和动作词表见 [[广告系列生命周期诊断模板]] 和 [[动作分级与决策边界]]，本页只展开 Meta 平台特有的判断。

核心原则：

- 本页不是实时报告，不记录未经查询确认的实时结论。每次实际分析必须重新拉取当前日期窗口、当前投放状态、当前素材表现、当前频次和当前 Snowball / BI 回收，禁止用旧经验替代实时数据。
- Meta 素材和人群信号变化快，所有 scale、maintain、reduce、pause 判断必须结合 Snowball / BI 回收，不得只看 CTR、CPI 或平台 ROAS。
- 不编造实时数据。没有查询到的数据写 `数据缺失`，样本不足写 `样本不足/低置信度`，不能把 `-1`、null、N/A 当作 0。
- 本页中标注"行业经验口径"的数值（如放量幅度、事件量门槛、监测阈值）是通用起点，不是公司阈值；正式阈值以 `grow_base/{ProjectID}_{ProjectName}.md` 为准，缺失时结论必须写 `阈值缺失`。

适用产品以 [[买量增长总览]] 的"当前重点产品"表为准（产品注册的源头是 [[产品与项目ID索引模板]]），当前 Meta 渠道主要是 A155 StepTracker（IAA），账户 Step Tracker 01 为主放量账号、Step Tracker 02 为测试/降量账号。

## 2. 账户与 Campaign 结构

### 2.1 结构原则

| 结构 | 适用场景 | 优点 | 风险 |
| --- | --- | --- | --- |
| ASC / Advantage+ | 有稳定素材池和足够转化信号，需要自动化扩量 | 系统探索快，操作成本低 | 黑盒、预算可能流向短期高点击低回收人群 |
| CBO | 多 adset 但希望 campaign 级预算自动分配 | 控制预算总量，利于规模 | 弱势 adset 可能拿不到量 |
| ABO | 测试国家、人群、素材或版位 | 对比清晰 | 管理成本高，预算碎片化 |
| Manual broad | 素材驱动、目标国家明确 | 可验证素材真实拉力 | 容易受学习期和频次影响 |
| Manual interest | 需要验证特定人群假设 | 假设明确 | 兴趣包过窄，衰退快 |

### 2.2 Advantage+ 与手动 Campaign 差异

| 项目 | Advantage+ App Campaign / ASC | 手动 Campaign / CBO / ABO |
| --- | --- | --- |
| 适用场景 | 有稳定素材池、足够事件量，需要自动化扩量 | 需要验证国家、人群、版位、素材或预算假设 |
| 预算分配 | campaign 层预算自动向系统认为机会更好的 adset / 组合分配 | ABO 可固定 adset 预算；CBO 用 campaign budget 自动分配 |
| 可控性 | 控制少，黑盒强 | 控制强，可拆国家、版位、人群和素材实验 |
| 诊断重点 | 看整体回收、国家/版位 mix、素材池新鲜度、频次和边际成本 | 看 adset 间差异、预算迁移、学习期碎片化和实验假设 |
| 常见误判 | 单条 ad CTR 高就加整个 campaign 预算 | 某个 adset 短期好就过早迁移大预算 |
| 推荐动作 | 稳定达标时小幅加预算，优先补充素材变体 | 把预算迁移到高回收 adset / country / creative 组合 |

### 2.3 Andromeda 时代的结构简化

Meta 自 2024 年底起全量升级了广告检索引擎（Andromeda），系统直接读取素材内容做人群匹配，"素材即定向"成为现实。这对账户结构的含义：

| 变化 | 结构含义 | 实操建议 |
| --- | --- | --- |
| 素材内容参与检索匹配 | 人群细分的价值下降，素材多样性的价值上升 | 减少窄兴趣 adset，把精力从拆人群转向拆素材角度 |
| 系统对 adset 碎片化更敏感 | 预算和事件分散会拖慢学习、抬高成本 | 同目标下 adset 收敛到 2-3 个以内（行业经验口径），预算集中 |
| 素材吞吐能力大幅提升 | 系统可以同时探索大量素材 | 放量瓶颈通常在素材供给，不在预算操作（见 9.3 素材供给节奏） |
| 旧的"一素材一 adset"测试结构失效 | 单独隔离素材反而剥夺系统的匹配空间 | 素材测试在同一 adset 内分批投喂，或用专门测试 campaign |

结构迁移原则：已在跑的老结构不要为了"对齐新打法"一次性重建——重建等于全量重进学习期。先在新增预算和新素材上采用收敛结构，老结构按生命周期自然退役。

## 3. 出价策略选择

### 3.1 策略对比

| 策略 | 机制 | 适用阶段 | 设置经验（行业经验口径） | 主要风险 |
| --- | --- | --- | --- | --- |
| Highest volume（lowest cost） | 无成本约束，最大化转化量 | 新 campaign 测试期、信号积累期 | 默认起点，先积累足够优化事件再切换 | 成本随竞价环境漂移，需每日盯 CPI/CPA |
| Cost per result goal（cost cap） | 控制平均成本，兼顾量级 | 放量期主力策略 | 设为目标 CPI/CPA 上浮 10-20%；iOS SKAN 延迟场景再上浮约 20% | 设置过紧会突然掉量；调整过频触发重学习 |
| Bid cap | 硬性限制单次竞价上限 | 竞价环境波动大、需要严格成本控制 | 设为目标成本上浮 20-50% 起步 | 量级受限最明显，容易花不出去 |
| ROAS goal（min ROAS） | 按最低回报优化，偏价值不偏量 | IAP / 混合变现且价值回传稳定后 | 从当前实际 ROAS 的 0.8-0.9 倍起步，逐步上调 | 事件价值样本稀疏时抑制探索 |

### 3.2 进阶路径与调整原则

标准进阶路径：**lowest cost（积累信号）→ cost cap（控成本放量）→ ROAS goal（价值优化，仅在回传可信后）**。

- 切换到 cost cap / ROAS goal 前，确认该 adset 每周优化事件量足够（行业经验口径约 50 个/周；Meta 对 app install / purchase 类目标的门槛更低，以后台学习状态为准）。事件量不足时切进阶策略只会导致学习不稳定。
- 同一观察窗内不连续调整 cost cap / ROAS 目标值；每次调整幅度控制在 10% 以内（行业经验口径），调整后按学习期对待。
- cost cap 达标不等于可以放量：平台成本达标只说明获量效率，放量前必须过 [[动作分级与决策边界]] 的回收门禁（Snowball ROI / profit / 留存）。
- 掉量排查顺序：先查 cap 是否过紧（对比近期实际成本分布），再查素材供给和频次，最后才考虑放开约束。

## 4. 必看字段与实时性要求

### 4.1 平台侧字段

| 层级 | 字段 | 判断用途 |
| --- | --- | --- |
| Account | spend、impressions、reach、frequency、clicks、CTR、CPC、CPM、actions、cost per action | 判断账户整体获量、竞争和流量质量变化 |
| Campaign | objective、campaign type、budget type、budget、bid strategy、status、delivery、spend、results | 判断结构、预算和生命周期阶段 |
| Adset | optimization goal、billing event、attribution setting、country、age、gender、placement、budget、spend limit、learning status | 判断学习期、预算碎片化、国家和版位分配 |
| Ad / Creative | ad_id、creative_id、format、hook、first frame、CTA、language、angle、spend、CTR、CPC、CPM、frequency、actions | 判断 winner / loser、疲劳和承诺错配 |
| Breakdown | country、publisher_platform、platform_position、device_platform、age、gender | 判断低 CPI 是否来自低回收结构 |

### 4.2 Snowball / BI 字段

| 口径 | 字段 | 判断用途 |
| --- | --- | --- |
| 回收 | cost、install、CPI、ROI0、ROI3、ROI7、revenue、profit、payback | 决定预算强动作 |
| 留存 | D1 / D3 / D7 retention | 判断低价用户是否可持续 |
| IAA | ads revenue、eCPM、IPU、ad impressions、ad format、ad scene | 判断广告变现质量 |
| IAP | purchase revenue、payer rate、trial rate、subscribe rate、ARPPU、refund / cancel | 判断付费质量 |
| 用户行为 | onboarding、关键事件、核心功能使用、订阅页曝光、广告触发 | 判断素材承诺与产品行为是否匹配 |

### 4.3 每次分析的实时性要求

| 检查项 | 必须使用当前值 | 禁止做法 |
| --- | --- | --- |
| 日期窗口 | 当前任务对应的最近完整自然日窗口 | 使用旧报告日期或只写"最近几天" |
| 投放状态 | 当前 campaign / adset / ad 状态 | 用历史 active 状态推断当前仍在跑 |
| 预算 | 当前 campaign budget、adset budget、spend limit、最近预算变更 | 用旧预算动作解释当前波动 |
| 学习状态 | 当前 Learning / Learning Limited / Active 状态 | 用上周学习状态判断今天动作 |
| 素材表现 | 当前 ad / creative 的 spend、impression、CTR、CPC、CPM、frequency、actions | 用历史 winner 直接判断当前 winner |
| Snowball 回收 | 当前日期窗口的 ROI0 / ROI3 / ROI7、profit、retention、关键事件 | 只看 Meta 平台指标做预算建议 |
| 归因映射 | 当前 campaign / adset 命名和 Snowball 维度映射 | campaign 改名或新建后继续套旧映射 |

### 4.4 默认日期窗口

| 场景 | 默认窗口 | 说明 |
| --- | --- | --- |
| Campaign 生命周期诊断 | `today-7` ~ `today-1` | 近 7 个完整自然日，不含当天 |
| 素材 fatigue 判断 | `today-14` ~ `today-1`，并拆最近 3 / 7 / 14 天 | 看趋势，不只看单日 |
| 新 campaign / 新 adset 测试 | 至少 2-3 个完整自然日，或达到样本门槛 | 未达到门槛标记 `too early to judge` |
| IAP 回收判断 | 根据产品 payback 周期看 ROI0 / ROI3 / ROI7 / 首购 / 订阅 | 短周期不成熟时降低动作强度 |
| iOS SKAN 场景 | 各窗口整体后移 1-3 天 | postback 延迟 24-72 小时，见第 11 节 |

### 4.5 必须谨慎使用的平台信号

| 字段 | 风险 | 正确处理 |
| --- | --- | --- |
| CTR | 高 CTR 可能是误导性 hook 或低质流量 | 只作为素材吸引力信号，预算动作必须看 Snowball ROI、profit、留存和事件质量 |
| CPI / CPA | 低 CPI 可能来自低价值国家、低质版位或非目标用户 | 结合国家、版位、留存、广告收入、付费收入判断 |
| 平台 ROAS | Meta 平台归因和 Snowball cohort 口径可能不同 | 先做平台与 Snowball 对账，再下结论 |
| 单条 creative 表现 | Meta 通常没有 Snowball creative 级 ROI | 写成"基于所属 campaign/adset 回收质量推断"，不得伪造 creative ROI |
| Learning Limited | 可能是预算不足、事件稀疏、受众过窄或结构碎片化 | 不直接等于 loser，要结合花费、转化量和回收 |
| Frequency | 不同产品、国家、素材形态可接受频次不同 | 结合 CTR/CVR、CPI、ROI 和 reach 变化判断 fatigue |
| 当天数据 | 当天数据未完整，且平台和 Snowball 延迟不同 | 默认排除；若必须看当天，标注低置信度 |

## 5. 新 Campaign 冷启动与放量节奏

本节回答"新计划怎么上、上了几天该干什么、什么时候加预算、加多少"。所有节奏动作仍受 [[动作分级与决策边界]] 的数据质量门禁约束。

### 5.1 上新前检查清单

- [ ] 优化事件已验证回传（MMP / Snowball 可见），事件名与 Snowball 映射一致。
- [ ] campaign / adset 命名符合归因映射规范，新命名已同步 BI（否则上线即 `blocked`）。
- [ ] 素材池就绪：至少 4-6 条不同角度素材（行业经验口径），格式覆盖竖版视频为主。
- [ ] 日预算能支撑学习：预算过低会直接进 Learning Limited（预算 × 转化率能否在 7 天凑够优化事件量，粗算即可）。
- [ ] 产品阈值文件存在（`grow_base/{ProjectID}_{ProjectName}.md`），明确 CPI / ROI0 / 留存的判断线。
- [ ] iOS 计划已与 Android 分开建 campaign（信号类型不同，见第 11 节）。

### 5.2 冷启动节奏表

| 阶段 | 时间 | 该做什么 | 不该做什么 | 判断输出 |
| --- | --- | --- | --- | --- |
| 上线日 D0 | 当天 | 确认正常消耗、无审核拒登、事件回传正常 | 看当天 CPI 下结论 | 仅记录上线状态 |
| 静默观察 | D1-D2 | 每日检查消耗节奏、学习状态、拒登；Snowball 确认 install 映射成功 | 改预算、改定向、换素材（除致命错误：错投国家、事件错配、素材违规） | 无动作，异常才升级 |
| 首次判断 | D3 | 用 2-3 个完整自然日数据做 `test_budget` 复查：CPI 量级、D1 留存首批信号、事件质量 | 加预算（除非数据异常好且 ready） | `test_budget 继续 / 调整 / 停止` |
| 完整窗口判断 | D5-D7 | 用完整窗口过回收门禁：ROI0/ROI3、留存、国家结构 | 因单日波动杀计划 | 进入生命周期判断（第 6 节），输出 `small_add / maintain / reduce_or_reallocate / pause_candidate` |

冷启动期的失败判定必须排除三类干扰：学习期波动、iOS 归因延迟、收入延迟（IAP）。排除前只能 `maintain` 或 `test_budget`，不能 `pause_candidate`。

### 5.3 放量阶梯

| 规则 | 内容 | 原因 |
| --- | --- | --- |
| 单次幅度 | 每次加预算 ≤20%（行业经验口径） | 超过 20% 的预算变更大概率触发重新学习，成本短期飙升 |
| 间隔 | 两次上调之间 ≥2-3 个完整自然日 | 每步都要看到边际回收未劣化再走下一步 |
| 门禁 | 每一步都要 Snowball ROI / profit 复核通过 + 数据质量 `ready` | 平台成本稳定不代表回收稳定 |
| 阶梯示例 | 100 → 120 → 145 → 175 → 210（占位，20% 步长） | 复利式爬坡，约 2 周预算翻倍 |
| 大幅扩量 | 需要跳跃式放量时，新建 campaign 或复制结构承接增量预算，不在原计划上暴力翻倍 | 保护已跑顺的学习成果 |
| 回撤 | 任一步边际回收劣化，回退到上一档并 `maintain`，同时检查素材供给 | 放量失败多数是素材供给跟不上，不是预算错 |

降预算同理：单次降幅也控制在 20% 左右，连续大砍会触发重学习，让"降量观察"变成"杀计划"。

### 5.4 每周投放节奏（团队默认约定，可按产品调整）

| 时间 | 固定动作 |
| --- | --- |
| 每工作日 | 第 14 节的每日监测清单（10-15 分钟/账户） |
| 周一 | 用上一完整 ISO 周数据做周度复盘：生命周期表更新、放量/降量候选、素材 fatigue 扫描 |
| 周二-周三 | 执行本周结构动作：新计划上线、预算阶梯调整、新素材批次入场（大动作尽量集中在周初，给足观察窗） |
| 周四 | 复查周初动作的首批数据；补充下周素材需求给设计侧 |
| 周五 | 只做必要维护，不上新结构、不做大幅预算变更（周末监控薄弱，学习期波动无人兜底） |
| 每周 | 素材供给对齐：确认下周新素材批次数量和角度（见 9.3） |

### 5.5 重大编辑与学习重置成本

以下操作会触发重新学习，做之前先问"值不值得付一次学习期的成本"：

| 操作 | 触发重学习 | 低成本替代 |
| --- | --- | --- |
| 预算单次变更 >20% | 是 | 20% 阶梯分步走 |
| 一次性替换大批素材 | 是 | 每批 2-4 条分批投喂，保留在跑 winner |
| 改优化事件 / 归因设置 | 是，且前后数据不可比 | 新建 campaign 跑新事件，分段分析 |
| 大幅改定向、国家、版位 | 是 | 新增国家用新 adset / campaign 承接 |
| 暂停后重启（长时间） | 可能 | 降到最低预算保温优于反复开关 |

## 6. 生命周期诊断

生命周期通用定义（`testing / scaling / mature / fatigue / pause_candidate` 五阶段）见 [[广告系列生命周期诊断模板]]。注意：`inactive_no_data` 不是生命周期阶段，而是数据质量状态（见 [[动作分级与决策边界]]）——对象无有效投放或 Snowball 无数据时，输出 `no_action_no_data`，不做生命周期判断。

### 6.1 Meta 生命周期判断标准

| 阶段 | Meta 定义 | 可观察信号 | 默认动作 |
| --- | --- | --- | --- |
| testing | 新 campaign、新 adset、新 creative 或新国家测试，算法和回收都未稳定 | spend / install / purchase 样本不足；Learning 中；ROI 信号未成熟 | `test_budget` / `maintain` |
| scaling | 回收达标，且增量预算没有明显拉低用户质量 | spend 增长；CPI / CPA 可控；ROI0 / ROI3 / profit 达标；frequency 未异常 | `small_add` / `add_budget`（按 5.3 阶梯执行） |
| mature | 已稳定运行，量级、成本和回收处在可控范围 | daily spend 稳定；ROI 波动可解释；素材池仍有变体 | `maintain` / `refresh_creative` |
| fatigue | 素材或受众触达效率下降，边际获客质量恶化 | frequency 上升；CTR/CVR 下降；CPI/CPA 上升；Snowball ROI、留存或事件变差 | `refresh_creative` / `reduce_or_reallocate` |
| pause_candidate | 成熟消耗下连续不达标，且排除归因、延迟、学习期和样本问题 | 多日 ROI / profit 不达标；无可用素材修复；存在更优预算承接对象 | 人工确认后再暂停 |

### 6.2 ASC / Advantage+ 判断重点

| 信号 | 判断 | 动作 |
| --- | --- | --- |
| campaign spend 增长，Snowball ROI / profit 不下降 | 自动化扩量有效 | `small_add` 或 `add_budget`，并保持素材补给 |
| CTR 高、CPI 低，但 ROI / 留存弱 | 低质流量或素材承诺错配 | 不放量，拆国家、版位和素材角度 |
| frequency 上升，CTR/CVR 同步下降 | 素材或受众 fatigue | `refresh_creative`，补 hook / first frame / CTA 变体 |
| 国家 mix 向低回收国家倾斜 | 系统短期追低成本，回收质量下降 | 限制或拆出国家，迁移预算到高回收结构 |
| CPI 低但 profit 弱 | 低价用户不变现 | 检查国家、版位、事件质量 |
| 学习状态频繁重启 | 预算或结构改动过密 | `maintain`，暂停大动作，延长观察窗 |

### 6.3 手动 Campaign 判断重点

| 场景 | 判断 | 动作 |
| --- | --- | --- |
| 某 adset 回收显著优于其他 adset | 预算分配不均或测试假设成立 | 迁移预算到优质 adset，弱 adset 降量 |
| broad adset 好于 interest adset | 素材驱动强，兴趣限制降低系统探索 | 保留 broad，减少窄兴趣预算 |
| 某国家 adset CPI 低但 ROI 弱 | 低价国家带来低质量用户 | 降预算或拆出单独验证 |
| interest CTR 高 ROI 低 | 人群点击意愿强但转化质量弱 | 暂停扩量，重写素材承诺 |
| 某 placement CTR 高但留存弱 | 点击诱导或误触风险 | 降低该版位权重，刷新素材承诺 |
| 多 adset 共用素材且同步衰退 | 素材层 fatigue，不是单一人群问题 | 先 `refresh_creative`，不急着改人群 |
| 新 adset Learning Limited 且样本小 | 事件不足或预算碎片化 | 合并结构、提高事件量或降低动作强度；新 adset 样本不足时 `test_budget`，补 2-3 个完整自然日 |

## 7. Learning / Learning Limited

Meta 的投放系统通常需要每个 ad set 在学习期内积累足够优化事件，常见经验口径约为最近一次重大编辑后一周内约 50 个优化事件（app install / purchase 类目标的实际门槛可能更低，以后台学习状态为准）。Learning Limited 表示系统预计难以获得足够优化事件，但它不是自动暂停信号。

| 状态 | 含义 | 诊断动作 |
| --- | --- | --- |
| Learning | 系统仍在探索高效投放方式 | 不用单日 CPI / CPA 做强判断，等待完整观察窗 |
| Learning Limited | 预计优化事件不足，学习难以稳定 | 检查预算、受众规模、优化事件、adset 数量和结构碎片化 |
| Active / Learning Complete | 投放相对稳定 | 可提高生命周期动作置信度，但仍要看 Snowball 回收 |
| Frequent re-learning | 频繁重大编辑导致重新学习 | 降低操作频率，避免每天大改预算、定向或素材组合 |

加速走出学习期的结构手段：预算集中到更少 adset、放宽定向（broad）、上线后 7 天内不做重大编辑、必要时把优化事件上移到量更大的漏斗环节（需同步校验事件质量与回收相关性）。

重大编辑风险清单见 5.5。

## 8. 预算结构与动作门禁

动作词表以 [[动作分级与决策边界]] 为唯一标准。

### 8.1 预算结构诊断

| 预算结构 | 诊断重点 | 动作门禁 |
| --- | --- | --- |
| Campaign budget | 系统是否把预算分配到真实高回收对象 | 加预算前必须确认 Snowball campaign / country 回收稳定 |
| Adset budget | adset 间是否存在明确优劣 | 可做预算迁移，但需防止样本不足 |
| Adset spend limit | 是否阻断系统给优质 adset 放量 | 若优质 adset 受限，可调整限制或迁移预算 |
| Daily budget | 日预算是否足以完成学习 | 预算过低可能导致 Learning Limited |
| Lifetime budget | 观察剩余排期、节奏和短期波动 | 不用单日消耗偏差直接判衰退 |

### 8.2 动作门禁

| 动作 | 必要条件 | 禁止场景 |
| --- | --- | --- |
| `add_budget` | 数据质量 `ready`；成熟消耗；ROI / profit 达标；频次和成本未明显恶化；有素材补给；按 5.3 阶梯执行 | 只因 CTR 高、CPI 低或平台 ROAS 高；单次加幅 >20% |
| `small_add` | 回收达标但样本、ROI7 forecast、国家结构或学习状态仍有不确定性 | Learning 频繁重启且 Snowball 回收未成熟；数据质量 blocked |
| `maintain` | 回收可接受但边际空间不清晰 | 无复查日期 |
| `test_budget` | 新对象或低样本对象有早期正向信号 | 把测试预算当成放量预算 |
| `refresh_creative` | frequency 上升、CTR/CVR 下降、CPI/CPA 上升或回收变差 | 未确认素材层问题就大幅改预算 |
| `reduce_or_reallocate` | 成熟对象连续弱于账户均值，且存在更优承接对象 | 归因或 Snowball 数据 `blocked` |
| `pause_candidate` | 连续不达标，刷新无效，且非数据问题 | 单日波动、样本不足或 Learning 中 |

## 9. 素材 fatigue、频次和 winner / loser

素材测试的通用矩阵和 winner / loser 归档以 [[素材测试复盘模板]] 为准，本节只列 Meta 平台特有的判断信号。

### 9.1 Fatigue 判断

| 信号组合 | 解释 | 动作 |
| --- | --- | --- |
| frequency 上升，CTR 下降，CPI 上升 | 受众看腻或素材吸引力下降 | 补新 hook、first frame、CTA、字幕和节奏变体 |
| frequency 上升，CTR 稳定，但 ROI / 留存下降 | 可能吸引到重复或低质用户 | 拆国家、版位和用户行为，检查承诺错配 |
| CPM 上升，CTR 下降 | 竞争变贵叠加素材效率下降 | 优先刷新素材，再评估预算迁移 |
| CTR 高，CVR / ROI 弱 | 点击强但转化或变现差 | 重新定义卖点，不按 winner 放量 |
| 新素材 spend 低 | 尚未获得分发机会 | 标记 `too early to judge` |

### 9.2 Creative winner / loser 判断

| 类型 | 平台信号 | Snowball / BI 信号 | 判断 |
| --- | --- | --- | --- |
| 高质量 winner | CTR / CVR 可接受，CPI / CPA 达标，frequency 未恶化 | 所属 campaign / adset ROI、profit、留存达标 | 可以做 hook、first frame、CTA、文案、语言、本地化变体 |
| 错配型 winner | CTR 高、CPI 低 | ROI、留存、关键事件或付费弱 | 不放量，重写承诺或更换落地价值 |
| 稳态素材 | CTR 中等，CPI 可接受 | ROI / profit 稳定 | 保留投放，补轻变体防 fatigue |
| loser | CTR 低、CPI 高、spend 有意义 | 回收弱 | 停止复用或重做素材角度 |
| 未成熟素材 | spend / install / purchase 样本不足 | 回收未完整 | 继续测试或降低置信度 |

注意：若 Snowball 没有 creative 级 ROI，报告必须写"creative ROI 基于所属 campaign / adset 回收质量推断"。

### 9.3 素材供给节奏（Andromeda 时代的放量主杠杆）

素材量和多样性已是 Meta 放量的第一杠杆：行业数据显示高频测试新素材的团队（每月 20+ 条）ROAS 显著高于低频团队。预算阶梯（5.3）走得动的前提是素材供给跟得上。

| 节奏项 | 团队默认约定（占位，按产品和设计产能校准） | 说明 |
| --- | --- | --- |
| 新素材供给频率 | 每周一批，每批 2-4 条新角度素材 | 分批投喂，不一次性大批替换（见 5.5） |
| 月度供给量 | 稳定放量产品每月 ≥15-20 条新素材（行业经验口径） | 含 winner 变体和全新角度，比例约 6:4 |
| 多样性维度 | 格式（竖版视频/图片/轮播）、hook 类型、场景、表现形式（真人/UI 录屏/UGC 风/动画）、语言 | 同角度堆量不算多样性 |
| 淘汰节奏 | 每周 fatigue 扫描时下线连续两个完整窗口的 loser | 保留稳态素材兜底，不清空素材池 |
| winner 变体 | 每个确认 winner 至少产出 2-3 个变体（改 hook / first frame / CTA / 语言） | 变体延长 winner 生命周期，防单点依赖 |
| 供给预警 | 素材池中"在跑且未疲劳"素材少于 3 条时，暂停放量动作 | 素材断供时加预算 = 加速疲劳 |

素材测试位置的选择：

| 方式 | 适用 | 注意 |
| --- | --- | --- |
| 直接投入在跑 ASC / 主力 campaign | 素材池稳定、系统已学习成熟 | 每批 2-4 条，观察系统是否给新素材分发机会 |
| 专门测试 campaign（ABO 小预算） | 需要公平对比、主力 campaign 不容有失 | 测试胜出后再进主力结构；测试与放量的成本水平会有差异，以相对排序为准 |

## 10. 国家与版位结构

国家优先级排序和阈值判断用 [[国家放量优先级模板]]，本节只列 Meta 结构信号。

| 结构问题 | 可观察信号 | 判断方式 | 动作 |
| --- | --- | --- | --- |
| 低回收国家吃量 | campaign 总 CPI 下降但 ROI / profit 下降 | 按 country 拆 cost、install、ROI、retention、revenue | 拆国家或限制低回收国家预算 |
| 高价值国家拿不到量 | 高 ROI 国家 spend 低、学习不足 | 看 campaign budget 是否被其他国家吸走 | 单独建测试结构或提高该国家预算机会 |
| 版位误触风险 | 某 placement CTR 高但 CVR / 留存弱 | 按 publisher_platform / platform_position 拆 | 限制或单独验证该版位 |
| 设备结构变化 | Android / iOS、device_platform mix 变化 | 对齐包、系统和变现口径 | 分设备判断 CPI 与回收 |
| 地区语言错配 | CTR 可接受但后续事件弱 | 看素材语言、国家、落地页和产品语言 | 做本地化素材和文案变体 |

## 11. iOS 归因专项：SKAN / AEM / AAK

iOS 投放的信号链路与 Android 完全不同，混在一起会让系统同时优化两种不兼容的信号。本节是 iOS 计划的强制约定。

### 11.1 归因栈速查

| 机制 | 覆盖场景 | 特性 | 对投放的影响 |
| --- | --- | --- | --- |
| SKAdNetwork（SKAN） | app-to-app、未授权 ATT 的用户 | postback 延迟 24-72 小时；conversion value 粗粒度；无用户级数据 | 平台侧数据滞后且模糊，当日/次日数据不可用于判断 |
| AEM（Aggregated Event Measurement） | web-to-app 等链路 | 最多 8 个按优先级排列的事件；聚合 + 噪声 | 事件优先级配置错误会丢关键信号 |
| AdAttributionKit（AAK，iOS 17.4+） | 与 SKAN 并行的新框架 | ATT 授权用户确定性归因，未授权概率归因 | MMP 需同时支持 AAK + SKAN 并行上报 |

### 11.2 iOS 投放强制约定

| 约定 | 原因 |
| --- | --- |
| iOS 与 Android 分开建 campaign，不混投 | Android 是确定性实时信号，iOS 是延迟聚合信号，混合会污染学习 |
| 不用 Ads Manager 数字判断 iOS 效果 | 平台侧 iOS 归因不完整；以 MMP / Snowball cohort 为主口径 |
| iOS 判断窗口整体后移 1-3 天 | SKAN postback 延迟；冷启动首次判断从 D3 推到 D4-D5 |
| iOS 的 cost cap / tCPI 相对目标上浮约 20%（行业经验口径） | 信号延迟导致系统低估转化，出价过低会不起量 |
| MMP 的 SKAN conversion value 映射需定期复查 | 事件映射变化后历史数据不可比，需在报告中标注 |
| 订阅产品 iOS 判断至少看到 trial → 首购信号 | coarse value 下 D0 数据几乎无判断价值 |

### 11.3 iOS 数据质量降级规则

| 场景 | 数据质量 | 允许动作 |
| --- | --- | --- |
| MMP 与 Snowball iOS install 能对齐，SKAN 映射正常 | `ready`（窗口后移后） | 正常动作，复查窗口 +1-3 天 |
| SKAN 映射改动后的过渡期 | `partial` | `maintain` / `test_budget`，标注不可比区间 |
| postback 断流或映射失败 | `blocked` | 仅 `data_gap_check` |

## 12. IAA 与 IAP 的回收判断

| 商业模式 | 主看指标 | Meta 平台信号的作用 | Snowball / BI 门禁 |
| --- | --- | --- | --- |
| IAA | ROI0、ROI3、ads revenue、eCPM、IPU、D1 留存、广告展示场景 | CPI、CTR、frequency 只解释获量质量 | 低 CPI 必须带来足够广告展示和留存，否则不放量 |
| IAP | ROI0、ROI3、ROI7、首购率、订阅率、trial、ARPPU、payback | CPA / purchase actions 可辅助判断 | 平台 purchase 不等于 cohort profit，必须看 Snowball 付费收入和退款 / 取消风险 |
| IAA+IAP | ads revenue + purchase revenue、混合 ROI、关键行为、留存 | 解释流量结构和素材承诺 | 拆广告收入与内购收入，避免总 ROI 掩盖结构恶化 |

IAA 常见误判：

| 误判 | 修正 |
| --- | --- |
| CPI 低就放量 | 还要看 D1 留存、广告展示次数、IPU、eCPM 和 ROI0 |
| CTR 高就判素材 winner | 还要看是否带来广告触发和长期留存 |

IAP 常见误判：

| 误判 | 修正 |
| --- | --- |
| 平台 purchase 多就加预算 | 还要看 Snowball 首购收入、订阅质量、退款和 payback |
| ROI0 低就立刻暂停 | 若产品付费延迟明显，应结合 ROI3 / ROI7 和关键事件 |

## 13. Snowball / BI 对账

完整对账方法和差异判断规则见 [[归因与数据质量检查模板]]，本节为 Meta 侧顺序。

### 13.1 对账顺序

1. 确认 Meta account、campaign、adset、ad 命名和 Snowball network / campaign / adgroup 映射。
2. 对齐日期窗口和时区，默认使用完整自然日。
3. 对齐 spend、install、country、campaign，识别缺失、重复和命名变化。
4. 判断数据质量：`ready / partial / blocked / inactive_no_data`。
5. 只有 `ready` 或 `partial` 可输出预算建议；`blocked` 只输出数据修复建议。

### 13.2 对账表模板

| 对象 | Meta spend | Snowball cost | 差异 | Meta installs / actions | Snowball installs | Snowball ROI0 | Snowball ROI3 | Snowball ROI7 | 数据质量 | 备注 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Campaign A |  |  |  |  |  |  |  |  | ready / partial / blocked |  |

### 13.3 不能下强结论的场景

| 场景 | 输出方式 |
| --- | --- |
| Meta 有 spend，Snowball 无 cost / install | `blocked`，优先修复映射或归因 |
| Snowball 有 ROI，但 campaign / adset 无法映射 | 只能做账户或国家层判断 |
| ROI7 是 forecast | 可辅助判断，不单独作为强放量依据 |
| 当前日数据未完整 | 标注低置信度或排除当前日 |
| 平台和 Snowball 安装差异大 | 先做归因与数据质量检查，不给预算强动作 |
| iOS SKAN 窗口未走完 | 标注延迟区间，判断后移（见 11.2） |

## 14. 日常监测与预警

本节是买量执行者的日常巡检 SOP。目标是在 10-15 分钟内完成一个账户的健康检查，把问题在进入日经营扫读（[[每日经营扫读模板]]）之前就分类清楚。

### 14.1 每日必查清单（每账户 10-15 分钟）

- [ ] 消耗节奏：昨日 spend 与计划偏差是否 >20%（花不出去或超花都要查）。
- [ ] 成本：昨日 CPI / CPA 对比 7 日均值，异动的 campaign 标记待查。
- [ ] 学习状态：是否有 adset 新进入 Learning Limited 或被重置学习。
- [ ] 审核与账户：拒登广告、账户余额 / 支付状态、账户质量分提示。
- [ ] 回收首查：Snowball 前一完整自然日 ROI0 是否有产品级异动。
- [ ] 映射：新上 campaign 是否已在 Snowball 出现且命名映射成功。

### 14.2 预警信号与第一反应

阈值列为行业经验口径占位，正式阈值按产品写入 `grow_base/{ProjectID}_{ProjectName}.md`。

| 信号 | 检测口径 | 预警线（占位） | 第一反应（不是最终动作） |
| --- | --- | --- | --- |
| CPM 突涨 | 单日 CPM 对比 7 日均值 | +30% 且持续 2 天 | 查竞价季节性、受众饱和、素材质量分；不立即动预算 |
| 素材疲劳 | frequency 周环比 + CTR 走势 | frequency 上升且 CTR 连续 3 天下滑 | 进入 9.1 fatigue 判断，准备 `refresh_creative` |
| 素材集中度 | 单条素材 spend 占 campaign 比例 | >50% | 单点依赖风险，优先补该 winner 的变体 |
| 国家 mix 漂移 | 低回收国家 spend 占比周环比 | +10 个百分点 | 按国家拆回收，评估拆分或限制 |
| 学习异常 | Learning Limited 出现 / 频繁重置 | 出现即查 | 查事件量、预算充足度、结构碎片化、近期编辑记录 |
| 对账差异 | Meta installs vs Snowball installs | 差异 >15% 且持续 | `data_gap_check`，修复前预算动作降级 |
| 无效消耗 | 素材/adset 连续消耗但零转化 | 连续 3 个完整自然日 | loser 候选，进入 9.2 判断 |
| 消耗断崖 | 单日 spend 环比 | -40% 且非主动操作 | 查拒登、竞价约束过紧、账户受限 |
| 回收恶化 | 产品级 ROI0 对比 7 日均值 | 连续 2 个完整自然日低于阈值 | 升级到日经营扫读，按 [[广告系列生命周期诊断模板]] 下钻 |

### 14.3 异常分诊顺序

发现异常后按固定顺序分诊，避免上来就调预算：

1. **是数据问题吗**：对账、映射、时区、SKAN 延迟 → 是则 `data_gap_check`，到此为止。
2. **是平台侧问题吗**：拒登、账户受限、学习重置、竞价约束过紧 → 修复平台侧配置，不动策略。
3. **是素材问题吗**：fatigue 信号、集中度、素材池断供 → `refresh_creative` 路径。
4. **是结构问题吗**：国家 / 版位 / adset mix 漂移 → 拆分或迁移路径。
5. **确认是质量/回收问题**：以上排除后，才进入生命周期判断和预算动作（第 6、8 节）。

### 14.4 监测分工与升级

| 层级 | 负责人 | 动作范围 | 升级条件 |
| --- | --- | --- | --- |
| 日常巡检 | 投放执行 | 记录、分诊、素材下线建议、`data_gap_check` 发起 | 涉及预算动作或 P0 信号 |
| 预算动作 | UA 负责人 | 按 [[动作分级与决策边界]] 审批 `add_budget / reduce_or_reallocate / pause_candidate` | 单产品回收连续恶化、需跨团队配合 |
| 经营层 | 日经营扫读 | 跨产品资源决策 | 见 [[经营会议机制]] 升级机制 |

所有预警触发和处理结果记入 [[预算调整记录模板]] 或素材复盘，保证周一复盘可追溯。

## 15. 生命周期表与结论模板

### 15.1 Meta Campaign 生命周期表

| Campaign | 类型 | 预算结构 | 国家 | 当前状态 | Learning 状态 | Spend | Installs | CPI | CTR | CPM | Frequency | ROI0 | ROI3 | ROI7 | Profit | 素材状态 | 生命周期 | 动作 |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Campaign A | Advantage+ App / ASC / Manual | campaign budget / adset budget | US / 混投 | Active | Learning / Learning Limited / Active |  |  |  |  |  |  |  |  | forecast / actual |  | fresh / stable / fatigue | testing / scaling / mature / fatigue / pause_candidate |  |

### 15.2 总体结论

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

### 15.3 候选清单

| 分类 | 对象 | 证据 | 动作 | 置信度 | 复查日期 |
| --- | --- | --- | --- | --- | --- |
| 放量候选 |  |  | `small_add / add_budget` | high / medium / low | YYYY-MM-DD |
| 观察候选 |  |  | `maintain` | high / medium / low | YYYY-MM-DD |
| 降量 / 迁移候选 |  |  | `reduce_or_reallocate` | high / medium / low | YYYY-MM-DD |
| 暂停候选 |  |  | `pause_candidate` | high / medium / low | YYYY-MM-DD |
| 素材刷新候选 |  |  | `refresh_creative` | high / medium / low | YYYY-MM-DD |
| 数据修复候选 |  |  | `data_gap_check` | high / medium / low | YYYY-MM-DD |

## 16. 典型场景

以下仅为写报告时的场景占位，不代表实时数据。

### 16.1 IAA 工具 App - 低 CPI 但广告回收弱

| 项目 | 内容 |
| --- | --- |
| 背景 | Meta ASC 在多国混投中 CPI 下降，但 Snowball ROI0 和广告展示 IPU 同步下降 |
| 初步判断 | 系统可能把预算转向低成本低变现国家或低质量版位 |
| 必查字段 | country spend、publisher_platform、frequency、D1 retention、ad impressions、IPU、eCPM、ROI0 |
| 动作占位 | 拆国家 / 版位结构，低回收国家降预算，高回收国家单独测试，素材承诺改为高意图场景 |

### 16.2 IAP 订阅 App - 平台 purchase 增加但 payback 变慢

| 项目 | 内容 |
| --- | --- |
| 背景 | 手动 Campaign 的 purchase actions 增加，Meta CPA 看似变好，但 Snowball ROI3 / ROI7 和订阅续费不稳定 |
| 初步判断 | 平台归因 purchase 不能直接等同于高质量付费，可能存在 trial 质量或退款风险 |
| 必查字段 | purchase revenue、trial rate、subscribe rate、refund / cancel、ROI3、ROI7、国家 mix、adset 学习状态 |
| 动作占位 | 维持或小幅验证，不做大额放量；检查 trial 到订阅转化和素材承诺 |

### 16.3 IAA+IAP 内容 App - 素材 winner 出现疲劳

| 项目 | 内容 |
| --- | --- |
| 背景 | 历史 winner 素材仍有 spend，但 frequency 上升，CTR 下滑，ROI 和留存走弱 |
| 初步判断 | 素材 fatigue 或受众触达饱和，不能只靠加预算恢复 |
| 必查字段 | creative spend、frequency、CTR、CPC、CPM、CVR、ROI0/3/7、ads revenue、purchase revenue、留存 |
| 动作占位 | 基于 winner 做 hook、first frame、CTA、字幕、语言、本地化变体，并降低旧素材预算权重 |

### 16.4 手动 Campaign - adset 间质量差异大

| 项目 | 内容 |
| --- | --- |
| 背景 | ABO 中某 adset CPI 低但 ROI 弱，另一个 adset CPI 较高但 profit 更好 |
| 初步判断 | 不能按 CPI 分配预算，应按 Snowball 回收和利润迁移预算 |
| 必查字段 | adset spend、install、CPI、ROI0、ROI3、profit、country、placement、retention |
| 动作占位 | 降低低回收 adset，迁移小预算到高 profit adset，并设置 2-3 个完整自然日复查 |

### 16.5 放量期 - 阶梯加预算后边际回收下滑

| 项目 | 内容 |
| --- | --- |
| 背景 | 按 20% 阶梯连续两次加预算后，CPI 可控但 Snowball ROI0 边际下滑，素材池两周未上新 |
| 初步判断 | 素材供给跟不上预算爬坡，系统扩量进入次优人群 |
| 必查字段 | 素材池"在跑未疲劳"数量、frequency 趋势、新素材占 spend 比例、国家 mix、边际 ROI |
| 动作占位 | 回退到上一档预算 `maintain`，先补一批新角度素材，素材恢复分发后再继续爬坡 |

### 16.6 iOS 新计划 - 平台数据延迟导致误判

| 项目 | 内容 |
| --- | --- |
| 背景 | iOS 新计划 D1-D2 平台侧转化极少，团队想直接停 |
| 初步判断 | SKAN postback 延迟 24-72 小时，早期"零转化"可能是延迟不是失败 |
| 必查字段 | MMP SKAN postback 到达情况、conversion value 映射、Snowball iOS install、D4-D5 完整数据 |
| 动作占位 | 判断后移到 D4-D5，期间 `maintain`；确认映射正常后再按冷启动节奏走 |

## 17. 输出检查清单

开始前：

- [ ] 已确认产品、Project ID、Meta account id 和 campaign / adset 命名。
- [ ] 日期范围是绝对日期，默认不含当天；iOS 计划已考虑 SKAN 延迟后移。
- [ ] 已拉取当前投放状态、预算结构、出价策略、Learning 状态、素材表现和频次。
- [ ] 已拉取当前 Snowball / BI 回收，并完成平台与 Snowball 对账。

分析中：

- [ ] `-1`、null、N/A、forecast、当天采样和延迟数据已处理。
- [ ] 已拆国家、campaign、adset、creative、placement 中与问题相关的层级。
- [ ] 没有只用 CTR、CPI、平台 ROAS 或单条素材表现做预算动作。
- [ ] IAA / IAP / IAA+IAP 的回收口径已分别判断。
- [ ] 异常已按 14.3 分诊顺序排除数据、平台、素材、结构问题。

产出前：

- [ ] 放量、观察、降量、暂停、素材刷新和数据修复候选已分开。
- [ ] 每条动作都有对象、证据、置信度和复查日期。
- [ ] 预算动作符合 5.3 放量阶梯（幅度 ≤20%、间隔 ≥2-3 个完整自然日）。
- [ ] 加预算前已确认素材供给状态（9.3），素材断供时不输出放量动作。
- [ ] `blocked` 数据质量没有输出强预算动作。
- [ ] Snowball 无 creative 级 ROI 时，creative 判断已标注为 parent campaign / adset 推断。

## 18. 参考口径

### Meta 官方

| 主题 | 参考 |
| --- | --- |
| Learning phase | [Meta Business Help Center: About the learning phase](https://www.facebook.com/business/help/112167992830700) |
| Learning Limited | [Meta Business Help Center: About Learning Limited](https://www.facebook.com/business/help/269269737396981) |
| Advantage+ campaign budget | [Meta Business Help Center: About Advantage+ campaign budget](https://www.facebook.com/business/help/153514848493595) |
| Campaign budget 与 adset budget | [Meta Business Help Center: About campaign budgets and ad set budgets](https://www.facebook.com/business/help/458847204894307) |
| Creative fatigue | [Meta Business Help Center: About creative fatigue recommendations](https://www.facebook.com/business/help/1346816142327858) |
| Frequency controls | [Meta Business Help Center: About frequency controls for auction](https://www.facebook.com/business/help/422853447344162) |

### 行业参考（2025-2026，观点类，引用时注意时效）

| 主题 | 参考 |
| --- | --- |
| Andromeda 与素材策略 | [Segwise: Meta Andromeda Update Creative Strategy 2026](https://segwise.ai/blog/meta-andromeda-update-creative-strategy-2026)、[TheOptimizer: Creative Testing After Andromeda](https://theoptimizer.io/blog/how-to-test-ad-creatives-on-meta-after-the-andromeda-update-2026-playbook) |
| 预算阶梯与学习期 | [RocketShip HQ: Budget Scaling Rules for Meta App Campaigns](https://www.rocketshiphq.com/meta-budget-scaling-rules-app-campaigns/)、[Modern Marketing Institute: Exit the Learning Phase](https://www.modernmarketinginstitute.com/blog/how-to-exit-the-meta-ads-learning-phase-fast-and-start-scaling-profitably-in-2026) |
| 出价策略 | [TheOptimizer: Cost Cap vs Bid Cap 2026](https://theoptimizer.io/blog/meta-ads-bidding-in-2026-cost-cap-vs-bid-cap-and-when-to-use-each)、[Flighted: Meta Bid Strategies Explained](https://www.flighted.co/blog/meta-ads-bid-strategies-explained-cost-per-result-goal-vs-bid-cap-vs-roas-goal-vs-highest-volume) |
| iOS 归因（SKAN / AEM / AAK） | [AppsFlyer: Meta AEM for iOS](https://support.appsflyer.com/hc/en-us/articles/19228737402129-Meta-Ads-Aggregate-Event-Measurement-AEM-for-iOS)、[Segwise: Meta AEM vs SKAN](https://segwise.ai/blog/meta-aem-vs-skan-2025-ios-attribution)、[RevenueCat: SKAdNetwork Guide for Subscription Apps](https://www.revenuecat.com/blog/growth/skadnetwork-guide-subscription-apps/) |
