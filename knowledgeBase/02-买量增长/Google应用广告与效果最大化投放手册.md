# Google App Campaign / PMax 买量手册

## 定位

本页用于指导 Google App Campaign、App Campaign for engagement、PMax 等自动化投放结构的规划、诊断和动作建议。Google 的平台优化信号很强，但预算动作必须以 Snowball / BI 的 install cohort 回收、留存和利润为主口径。

## 适用产品

| Project ID | 产品 | 商业模式 | 当前关注 |
| --- | --- | --- | --- |
| A151 | Weather&News | IAA + IAP | Google US 集中买量、混合变现回收 |
| A124 | MessagePro | IAA | 国家阈值、广告变现回收 |
| A115 | PDF_Reader | IAA | 国家阈值、漏斗和回收 |

## Campaign 结构原则

| 结构问题 | 推荐做法 | 不推荐做法 |
| --- | --- | --- |
| 目标拆分 | 按优化目标拆 campaign，如 install、in-app action、ROAS | 一个 campaign 同时承载多个互相冲突目标 |
| 国家拆分 | 核心国家单独建组或单独 campaign，长尾国家谨慎合并 | 把高 eCPM 国家和低质量国家混在一起放量 |
| 预算稳定 | 学习期保持预算相对稳定，小幅迭代 | 频繁大幅调预算导致学习重启 |
| 资产组 | 按卖点、用户意图、语言或国家组织 asset group | 把所有素材堆在同一组里无法复盘 |
| 信号 | 使用真实高质量事件，如关键行为、付费、广告价值 | 只优化安装且不看后续质量 |

## 必看字段

| 来源 | 字段 | 用途 |
| --- | --- | --- |
| Google Ads | spend、impressions、clicks、CTR、CPC、CPM、conversions、cost_per_conversion、conversion_value、asset_group、asset performance label | 判断平台侧获量效率和资产分配 |
| Snowball / BI | cost、install、revenue、roi_0、roi_3、roi_7、profit、retention、关键事件、广告收入、IAP 收入 | 判断真实回收和用户质量 |
| 配置 | conversion action、国家、语言、预算、bid strategy、target ROAS / target CPA | 判断优化目标是否和业务目标一致 |

## 目标选择

| 目标 | 适用场景 | 主要风险 | Snowball 校验 |
| --- | --- | --- | --- |
| Install volume | 新项目、新国家、冷启动 | 低价低质安装 | D1 留存、关键事件、ROI0 |
| In-app action | 已有足够事件量，关键行为能代表质量 | 事件被刷或与变现弱相关 | 事件到收入的相关性、ROI3/7 |
| tCPA | CPA 稳定且目标事件质量可靠 | CPA 达标但后端回收弱 | CPA、ROI、profit 同看 |
| tROAS | IAP 或混合变现收入回传稳定 | 收入延迟和样本稀疏 | ROI7、付费率、广告收入拆分 |
| PMax | 需要跨库存扩量且素材资产丰富 | 流量黑盒、资产归因不透明 | campaign / asset group 级回收 |

## Google 诊断流程

1. 先确认 conversion action 是否仍代表高质量用户。
2. 对账 Google spend / conversions 与 Snowball cost / install。
3. 按国家拆 ROI、CPI、留存、广告收入、IAP 收入。
4. 按 campaign / asset group 看预算是否流向低质国家或低质素材组合。
5. 看素材资产标签，但只作为素材迭代线索，不作为预算最终依据。
6. 输出 `add_budget / small_add / maintain / reduce_or_reallocate / refresh_creative / data_gap_check`。

## 预算动作规则

| 场景 | 信号 | 动作 |
| --- | --- | --- |
| 回收稳定达标且国家结构健康 | ROI、profit、留存达标，成本增长后未明显劣化 | `small_add`，成熟后 `add_budget` |
| 平台 CPA 达标但 Snowball ROI 弱 | 低 CPI、低 CPA，但留存或收入弱 | 不放量，查事件质量和人群错配 |
| 某国家拖累整体 | 总体可接受，但低质国家消耗扩大 | 拆国家或迁移预算 |
| 资产疲劳 | CTR/CVR 下降、CPI 上升、资产标签走弱 | `refresh_creative`，先补素材再加预算 |
| 数据不齐 | conversion、cost、install 或 revenue 对不上 | `data_gap_check` |

## 资产测试矩阵

| 资产类型 | 测试变量 | 判断字段 | 迭代动作 |
| --- | --- | --- | --- |
| Video | 前 3 秒、场景、人物、字幕、CTA | CTR、CVR、CPI、parent ROI | 保留胜出 hook，做多国家语言版本 |
| Image | 主视觉、利益点、UI 露出、社证 | CTR、CPC、CPI | 扩展同卖点不同构图 |
| Text | 标题、短描述、长描述 | CTR、CVR、搜索意图匹配 | 保留高意图词，避免夸大承诺 |
| Store listing | 图标、截图、首屏文案 | CVR、install quality | 与素材承诺保持一致 |

## 混合变现特别检查

| 商业模式 | 必查字段 | 决策重点 |
| --- | --- | --- |
| IAA | ads revenue、eCPM、IPU、D1/D3 留存 | 用户是否产生广告展示机会 |
| IAP | first purchase rate、payer rate、ARPPU、subscription trial | 低成本用户是否有付费意愿 |
| IAA + IAP | 广告收入、付费收入、总 ROI、分收入源利润 | 不要让广告高活跃掩盖付费质量下滑 |

## 输出模板

```text
Campaign：
目标类型：
日期范围：YYYY-MM-DD ~ YYYY-MM-DD
数据质量：ready / partial / blocked / inactive_no_data
主要问题：
Snowball 回收判断：
Google 平台侧判断：
国家/资产组问题：
建议动作：
复查窗口：YYYY-MM-DD ~ YYYY-MM-DD
不能判断的范围：
```
