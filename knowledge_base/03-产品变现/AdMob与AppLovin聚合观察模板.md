# AdMob / AppLovin 聚合、水位与竞价模板

## 适用场景

用于记录和分析 AdMob Mediation、AppLovin MAX 或其他聚合平台的广告位配置、waterfall、水位、bidding source 表现和调整结果。目标是让变现团队能判断：应该调底价、调优先级、开关 bidder、拆广告位、分国家配置，还是保持观察。

本模板只写方法和占位，不包含实时平台数据。

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 产品 | `{Product}` |
| Project ID | `{Project ID}` |
| 平台 | iOS / Android |
| 聚合平台 | AdMob / AppLovin MAX / Other |
| 分析范围 | `{country}` / `{ad_format}` / `{ad_scene}` |
| 日期范围 | `YYYY-MM-DD ~ YYYY-MM-DD` |
| 对比窗口 | `YYYY-MM-DD ~ YYYY-MM-DD` |
| 数据源 | Snowball / AdMob / AppLovin MAX / BI |
| 变更类型 | 新增 bidder / 调整 floor / 拆 ad unit / 关闭 source / 频控调整 |

## 配置快照

| 平台 | 国家 | 广告格式 | 广告场景 | Ad Unit / Mediation Group | Waterfall / Bidding | 主要 Network | Floor / Price Tier | 备注 |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| iOS | US | AppOpen | 启动 |  |  |  |  |  |
| iOS | US | Interstitial | 关键结果页 |  |  |  |  |  |
| Android | US | RewardedVideo | 激励权益 |  |  |  |  |  |

配置记录要求：

- 每次调整前后都要保存配置快照。
- 同一广告格式如果按国家、场景、版本或用户层分组，必须拆行记录。
- Waterfall 与 bidding 混用时，要写明 bidder 是否参与同一次竞价，以及 waterfall line item 的底价。
- 不要只记录广告位 ID；必须记录它服务的产品场景。

## Source 表现表

| Source | 类型 | Requests | Bid Requests | Bid Rate | Fill Rate | Win Rate | Impressions | Show Rate | Revenue | eCPM | 异常 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| AdMob Network | Bidding / Waterfall |  |  |  |  |  |  |  |  |  |  |
| AppLovin | Bidding / Waterfall |  |  |  |  |  |  |  |  |  |  |
| Liftoff Monetize | Bidding / Waterfall |  |  |  |  |  |  |  |  |  |  |
| Meta Audience Network | Bidding / Waterfall |  |  |  |  |  |  |  |  |  |  |

## Waterfall 诊断

| 层级 | Network | Floor / eCPM | Requests | Fill | Impressions | Revenue | 实际 eCPM | 判断 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 |  |  |  |  |  |  |  | 是否吃满高价流量 |
| 2 |  |  |  |  |  |  |  | 是否存在跳层 |
| 3 |  |  |  |  |  |  |  | 是否兜底有效 |

判断规则：

- 高层级 fill 长期很低但请求量高，可能 floor 过高或 source 竞争力不足。
- 高层级 fill 上升但整体 revenue 下降，检查是否挤压了更高 eCPM bidder。
- 低层级兜底 revenue 占比升高，通常说明高价层供给不足、底价过高或用户质量下降。
- 同一 source 在不同层级之间收入迁移，不等于总收入损失；需要计算其他层补偿。

## Bidding 诊断

| Source | Bid Requests | Bid Responses | Bid Rate | Wins | Win Rate | Impressions | Revenue | eCPM | 结论 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
|  |  |  |  |  |  |  |  |  |  |

判断规则：

- Bid rate 下降：优先查隐私授权、SDK adapter、地域覆盖、source 账号状态。
- Win rate 下降：优先查竞争环境、floor、其他 bidder 出价增强、用户质量变化。
- Bid eCPM 高但 impressions 少：可能库存不匹配、超时、展示链路或竞价胜出后加载失败。
- 新 bidder 开启后收入上涨但留存或投诉恶化，要回到广告场景和素材质量检查。

## 水位调整原则

| 场景 | 信号 | 建议动作 | 风险 |
| --- | --- | --- | --- |
| 高 eCPM 国家填充不足 | requests 正常、fill 下降、低层兜底少 | 逐步降低高层 floor 或增加中间层 | eCPM 下滑但 revenue 可能恢复 |
| 高填充低 eCPM | fill 高、impressions 高、revenue 低 | 提高 floor 或限制低价 source | 展示量下降、短期收入波动 |
| Bidder 抢量但收入下降 | 某 bidder win rate 上升、总 eCPM 下降 | 限制 bidder、回看 floor 与竞价优先级 | 可能误杀高潜 source |
| 特定国家 source 崩塌 | 单国家单 source fill/win 异常 | 国家级关闭或替换 source | 需要兜底层保证填充 |
| 新版本展示下降 | requests/fill 正常、show rate 下降 | 优先查客户端加载和展示时机 | 不应先调水位 |

## 调整实验设计

| 项 | 要求 |
| --- | --- |
| 实验对象 | 明确到平台、国家、广告格式、广告场景、ad unit |
| 分流方式 | A/B、灰度国家、灰度版本或小比例 remote config |
| 主指标 | Revenue、ad ARPDAU、eCPM、fill rate、show rate，按问题选择一个主指标 |
| 护栏指标 | 留存、session、crash、ANR、投诉、paywall CVR、purchase rate |
| 最短观察 | 至少覆盖完整自然日；高波动广告位建议覆盖同星期对比 |
| 停止条件 | 净收入下降、护栏恶化、填充断裂、投诉异常 |

## 调整记录

| 时间 | 对象 | 调整前 | 调整后 | 预期 | 实际结果 | 决策 |
| --- | --- | --- | --- | --- | --- | --- |
| `YYYY-MM-DD HH:mm` | `{ad_unit}` |  |  |  |  | 保留 / 回滚 / 扩大 |

## 决策输出

| 结论类型 | 写法模板 |
| --- | --- |
| 维持 | `当前收入提升不足以覆盖护栏风险，保持现有配置，继续观察到 YYYY-MM-DD。` |
| 小流量验证 | `仅在 {country/platform/scene} 灰度 {change}，不扩大到全量，复查 {metric}。` |
| 扩大 | `{metric} 达到成功标准且护栏稳定，扩大到 {scope}。` |
| 回滚 | `{metric} 恶化或影响 {guardrail}，回滚到 {old_config}。` |
| 数据阻塞 | `缺少 {field}，不能判断水位/竞价效果，先补报表或埋点。` |

## 常见错误

- 把 AdMob 付款侧收入变化直接等同于业务收入变化，忽略 AppLovin 或其他 source 补偿。
- 只看聚合平台 eCPM，不拆国家、场景和广告格式。
- 在 show rate 断裂时先调 floor，实际根因可能是客户端展示链路。
- 新 bidder 刚开启就全量放大，没有灰度和护栏。
- 不记录配置快照，导致复盘无法判断收入迁移来自哪次调整。
