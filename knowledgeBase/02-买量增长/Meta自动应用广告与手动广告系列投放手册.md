# Meta ASC / 手动 Campaign 买量手册

## 定位

本页用于指导 Facebook / Meta Ads 的 ASC、Advantage+ App Campaign、ABO、CBO、手动 adset 结构诊断和动作建议。Meta 素材和人群信号变化快，所有 scale、maintain、reduce、pause 判断必须结合 Snowball / BI 回收。

## 适用产品

| Project ID | 产品 | 账户 | 当前关注 |
| --- | --- | --- | --- |
| A155 | StepTracker | Step Tracker 01 | 主放量账号、campaign 和素材生命周期 |
| A155 | StepTracker | Step Tracker 02 | 测试或降量账号、素材验证 |

## 账户结构原则

| 结构 | 适用场景 | 优点 | 风险 |
| --- | --- | --- | --- |
| ASC / Advantage+ | 有稳定素材池和足够转化信号，需要自动化扩量 | 系统探索快，操作成本低 | 黑盒、预算可能流向短期高点击低回收人群 |
| CBO | 多 adset 但希望 campaign 级预算自动分配 | 控制预算总量，利于规模 | 弱势 adset 可能拿不到量 |
| ABO | 测试国家、人群、素材或版位 | 对比清晰 | 管理成本高，预算碎片化 |
| Manual broad | 素材驱动、目标国家明确 | 可验证素材真实拉力 | 容易受学习期和频次影响 |
| Manual interest | 需要验证特定人群假设 | 假设明确 | 兴趣包过窄，衰退快 |

## 必看字段

| 来源 | 字段 | 用途 |
| --- | --- | --- |
| Meta Ads | spend、impressions、reach、frequency、clicks、CTR、CPC、CPM、installs/actions、CPA、campaign/adset/ad status | 判断平台获量、频次和成本变化 |
| Creative | creative_id、ad name、video/image、hook、first frame、CTA、language、format | 判断素材可复用元素 |
| Snowball / BI | cost、install、ROI0/3/7、profit、retention、关键事件、广告/IAP 收入 | 决定预算和素材强动作 |

## 诊断流程

1. 先做平台和 Snowball 对账，确认 account、campaign、adset、country 可映射。
2. 看账户层 spend、install、CPI、CTR、CPM、frequency 和 Snowball ROI。
3. 下钻 campaign/adset，判断是结构问题、国家问题、素材问题还是用户质量问题。
4. 只对 active 或高花费对象做素材级复盘，避免一次拉全量历史素材。
5. 素材 ROI 若没有 Snowball creative 级数据，只能写“基于 parent campaign/adgroup 回收质量推断”。
6. 输出动作和复查窗口，不直接执行平台写操作。

## ASC 判断规则

| 信号 | 解释 | 动作 |
| --- | --- | --- |
| Spend 增长且 Snowball ROI 稳定 | 自动化扩量有效 | `small_add` 或 `add_budget` |
| CTR 高但 ROI / 留存弱 | 素材承诺错配或低质流量 | `refresh_creative`，不放量 |
| Frequency 上升且 CTR/CVR 下降 | 素材疲劳 | 补新素材或拆新角度 |
| CPI 低但 profit 弱 | 低价用户不变现 | 检查国家、版位、事件质量 |
| 学习期频繁重启 | 预算或素材变动过密 | `maintain`，延长观察 |

## 手动 Campaign 判断规则

| 场景 | 判断 | 动作 |
| --- | --- | --- |
| 某 adset 回收显著优于其他 adset | 预算分配不均或测试假设成立 | 迁移预算到优质 adset，弱 adset 降量 |
| broad 好于 interest | 素材驱动强，人群限制反而降低质量 | 保留 broad，减少窄兴趣依赖 |
| interest CTR 高 ROI 低 | 人群点击意愿强但转化质量弱 | 暂停扩量，重写素材承诺 |
| 新 adset 样本不足 | 不能判断 | `test_budget`，补 2-3 个完整自然日 |
| 多 adset 同素材同时疲劳 | 素材层问题，不是单一人群问题 | `refresh_creative` |

## 素材决策矩阵

| 平台信号 | Snowball 信号 | 判断 | 动作 |
| --- | --- | --- | --- |
| CTR 高、CPI 低 | ROI / 留存达标 | 高质量 winner 候选 | 扩变体，进入放量候选 |
| CTR 高、CPI 低 | ROI / 留存弱 | 错配或低质流量 | 改 hook / CTA / 落地承诺 |
| CTR 低、CPI 高 | ROI 弱 | 明确 loser 候选 | 停止复用或重做 |
| CTR 一般、CPI 可接受 | ROI 达标 | 可能是稳态素材 | 保持并做轻变体 |
| Spend 低 | 回收不完整 | too early to judge | 继续小预算测试 |

## 预算动作门禁

| 动作 | 必要条件 | 禁止场景 |
| --- | --- | --- |
| `add_budget` | 连续观察窗回收达标，频次和成本未明显恶化，数据质量 ready | 只因 CTR 高或平台 CPA 低 |
| `small_add` | 回收达标但样本、国家或素材稳定性仍需验证 | 数据质量 blocked |
| `maintain` | 回收可接受但边际不清晰 | 无复查计划 |
| `reduce_or_reallocate` | 回收恶化、机会成本高，存在更优对象 | 归因未修复 |
| `pause_candidate` | 连续不达标且刷新素材无效 | 单日波动或样本不足 |

## 输出模板

```text
账户：
Campaign / Adset：
日期范围：YYYY-MM-DD ~ YYYY-MM-DD
结构类型：ASC / CBO / ABO / Manual
数据质量：ready / partial / blocked / inactive_no_data
平台侧信号：
Snowball 回收信号：
素材判断：
动作建议：
复查窗口：
不能判断的范围：
```
