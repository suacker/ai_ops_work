# 使用 Snowball MCP 分析广告变现项目ROI

## 🧑‍💻 User

使用 snowball mcp ， 参照一下的 IAA 产品的 买量推广分析方法， 分析 Weather&News 项目的 买量ROI 打正的产品数值指标阈值和核心指标。

请参照以下分析方法：

推算产品的买量 ROI 打正的指标阈值和核心指标
 对于产品的买量阈值和核心指标分析，需要按产品的类型分别分析，分 IAA （广告变现）和 IAP （内购变现） 两种产品类型。
 - IAA （广告变现）产品分析方法
 对 IAA 产品变现型产品 ROI 目标需要核对产品的 ROI 日期时长，结合历史数据，对项目核对项目的 ROI 打正目标，几种常见的项目类型：
 - 对于留存较好的产品 （如 次留大于20%， 14日留存大于 4%， 30日 留存大于 3%，如果 ROI 45 天 能出现 ROI 45 天 100% 结果，则 我们可以参照 ROI 45 天 出现100% 的 买量日期。取 15天历史记录，取平均值 ROI 0 的数值，作为买量计划的最低阈值， 核心指标： 次留 >= 20%。
 - 对于留存较差的产品 （如 次留小于10%， 14日留存在 3% 左右， 30日 留存在 1.5% 左右，如果 ROI 21 天 能出现 90 % 结果，则 我们可以参照 ROI 21天 出现90% 的 买量日期。取 15天历史记录，取平均值 ROI 0 的数值，作为买量计划的最低阈值, 核心指标以 ROI 打正时 次留。

---
## 🤖 Assistant

下面给出针对 Weather&News 项目，基于 Snowball MCP 的可执行分析方法、需要从 MCP 提取的指标、计算步骤、以及按不同留存情况给出的买量 ROI 打正（break-even）数值阈值建议与核心指标。方法参照你提供的 IAA 产品分析逻辑（按留存好/差分别选取 ROI 时间窗口、用 15 天历史取平均等），并补充如何在 Snowball MCP 上落地执行与检验的细节。

一、总体思路（公式与概念）
- 定义：
 - LTV_X = 从安装日起到第 X 天的累计人均广告收益（ARP U 累计），单位同广告收入（RMB 或 USD）。
 - CPI_max(X) = LTV_X * (目标 ROI 放缩系数)。若目标“打正”即 ROI = 0，则 CPI_max = LTV_X；若希望正 ROI （例如 +10%），则 CPI_max = LTV_X * (1 + 0.10)。
- ROI 判定：当投放渠道的平均 CPI ≤ CPI_max(X) 时，投放在 X 天窗口内可认为达到或超过打正目标。
- 选择 X（ROI 时间窗口）原则：按产品留存质量决定：
 - 留存较好 → 选择较长窗口（如 45 天）；
 - 留存较差 → 选择较短窗口（如 21 天）；
 - 参照样例使用 15 天历史取平均 CPI_max 为买量最低阈值（即在历史 15 天 cohort 上计算的 CPI_max 平均值）。

二、需要在 Snowball MCP 抽取与校验的核心数据字段（必取）
从 Snowball MCP 获取按安装 cohort 的日粒度数据（分渠道/创意/国家/设备维度）：
- installs（安装数，按日期 cohort）
- retention: D1（次留）、D3、D7、D14、D21、D30（如可得）
- daily_active_users / DAU（用于校验）
- ad_impressions_per_user（或总 impressions / installs）
- ad_revenue_by_day（按 cohort 的日收入）
- cumulative_ad_revenue_by_day（用于算 LTV_X）
- eCPM（按渠道/国家/日期）
- cost（campaign level cost）与 CPI（如果 Snowball 有 Cost 数据，或与采购平台对齐）
- country / channel / creative 标签（用于分层）

三、计算步骤（在 Snowball MCP 上落地）
1. 确定 ROI 时间窗口 X：
 - 若 D1 >=20% 且 D14>=4% 且 D30>=3% → 选择 X = 45（或 30~45）；
 - 若 D1 <10% 且 D14≈3% 且 D30≈1.5% → 选择 X = 21（或 21~30）。
 - 对 Weather&News 建议初步假设为“留存中等偏好”：D1 建议关注 18~25%，D14 4~6%，D30 2~3%。可并行计算 X=21 和 X=45 两条曲线供决策。
2. 根据最近 15 天的安装 cohort，计算每 cohort 的 LTV_X（累计 ad revenue 到第 X 天 人均）：
 - 对每个 cohort：LTV_X = sum_{day=0..X} ad_revenue_day / installs_cohort
3. 计算 CPI_max(cohort) = LTV_X（或加上所需正 ROI 比例）。
4. 对 15 天内的 CPI_max 求平均和标准差，得到“历史平均 CPI_max”与波动区间（用于定价基线）。
5. 将当前 / 计划要投放的渠道预估 CPI 与 CPI_max 比较：
 - 若渠道 CPI ≤ 平均 CPI_max → 可投放（可视为打正）；
 - 若 CPI 接近 CPI_max（比如在 -10% 到 +10%）→ 建议小规模投放并密切监控；
 - 若 CPI 明显高于 CPI_max → 不开或优化素材/落地页。
6. 监控指标：投放后至少按日更新 cohort 的实际 LTV_X 与 retention，若实际 LTV 跌破预期，及时调整出价/暂停。

四、Weather&News 的具体阈值与推荐（按留存两类场景给出数值阈值范围）
说明：以下阈值以“百分比阈值”与“指标公式”为主，因为具体 CPI/货币阈值需基于你们 MCP 的实际收入数据计算。下面同时给出示例数值计算流程示例（用假设的 ARPU 值展示如何算 CPI_max）。

A. 留存较好（目标使用 X = 45）
- 核心阈值：
 - 次留（D1）≥ 20%（核心判断指标）
 - D14 ≥ 4%
 - D30 ≥ 3%
 - eCPM 稳定且 >= 项目历史平均（用于保证 LTV 能持续）
- 行动阈值：
 - 从最近 15 日各 cohort 计算 LTV_45，取平均 μ_LTV45 与标准差 σ。
 - 买量 CPI 最低阈值（保守） = μ_LTV45 * 0.9（留 10% 安全边际）
 - 买量 CPI 推荐上线（进攻） = μ_LTV45（目标打正）
 - 若希望 +10% ROI → CPI_target = μ_LTV45 * 1.1
- 核心监控指标：D1、D7、D14、D30、LTV_7/14/30/45、eCPM、impressions_per_user、fill rate。

B. 留存较差（目标使用 X = 21）
- 核心阈值：
 - 次留（D1）≈ 8%–12%（若低于 8% 则需产品优化）
 - D14 ≈ 2.5%–3.5%
 - D30 ≈ 1%–1.8%
 - 当 ROI 21 天能出现 90% 的样本时，可以 21 天 LTV 为参考
- 行动阈值：
 - 从最近 15 日 cohort 计算 LTV_21，取平均 μ_LTV21。
 - 买量 CPI 最低阈值 = μ_LTV21 * 0.9（安全边际）
 - 若要稳妥打正：CPI ≤ μ_LTV21
 - 若 CPI 高于 μ_LTV21，则需缩减出价或优化素材/人群
- 核心监控指标：D1（作为打正时的核心指标）、LTV_7/14/21、eCPM、impressions_per_user。

五、示例计算（假设示范，说明如何把数据套入公式）
- 假设从 Snowball MCP 得到某 cohort：
 - installs = 10,000
 - cumulative ad revenue 到 day21 = ¥2,500 → LTV_21 = 2,500 / 10,000 = ¥0.25
 - 则 CPI_max(21, ROI=0) = ¥0.25
 - 若你想要 10% 正 ROI → CPI_target = ¥0.275
- 用 15 天 cohort 求 μ_LTV21 = ¥0.24，σ = ¥0.03：
 - 保守 CPI 阈值 = ¥0.24 * 0.9 = ¥0.216
 - 推荐 CPI 阈值 = ¥0.24

六、Snowball MCP 上的落地实现建议（操作步骤）
1. 建 cohort 报表：按安装日分 cohort，计算 installs、D1/D7/D14/D21/D30 retention、daily ad revenue、cumulative ad revenue。
2. 导出最近 15 天的 cohort 数据，计算 LTV_X（X=21、45）。
3. 对投放渠道（campaign）拉取实际 cost 与 installs，计算实际 CPI 并与 CPI_max 比较（若 Snowball 无 cost，需与广告平台对账导入 cost）。
4. 做分层分析：按 country/channel/creative/OS 分别计算 LTV_X 与 D1，找高 LTV、高 D1 的组合优先放量。
5. 实时监控：建立 Dashboard（D1、D7、LTV_7/14/21/45、CPI vs CPI_max 曲线），对超过阈值的渠道自动告警（比如 CPI 超过 CPI_max 的 10%）。

七、决策建议（投放策略）
- 如果项目当前 D1 ≥ 20%，建议将 ROI 窗口设为 45 天，用 LTV_45 做 CPI 定价，并用 15 天历史均值做保守阈值；
- 如果 D1 在 10% 左右或更低，优先做产品/用户体验优化，再用 21 天窗口做短期投放测试，CPI 目标更低；
- 优先把投放预算投向那些同时满足“D1 高 + LTV_X 高 + eCPM 稳定” 的渠道/国家/素材；
- 对接 Snowball 的实时数据与广告平台 cost，做到当日 CPI 超阈或 LTV 异常下降时，自动降低投放或暂停。

八、核心指标汇总（方便直接落地监控）
- 必看：D1（次留）、LTV_21、LTV_45、CPI（实际）、CPI_max（目标）、eCPM、impressions_per_user、fill rate、installs（分渠道）。
- 次要：D7、D14、D30、ARPU_D1/D7/D14、DAU 留存曲线、ROI 时间窗的累计 ROI 曲线。

九、交付物建议（给数据/BI 团队）
- 一个由 Snowball MCP 自动更新的 CSV/表格，字段包括：install_date, channel, country, installs, D1, D7, D14, D21, D30, cumulative_revenue_day7/14/21/45, LTV_7/14/21/45, campaign_cost, CPI, CPI_max_21, CPI_max_45。
- 一个 Dashboard：展示近 15 日 μ_LTV21、μ_LTV45、CPI_vs_CPI_max 折线和超阈告警。

十、注意事项
- IAA 收益易受 eCPM 波动与广告生态影响（季节、政策），建议定期（每周）复算 μ_LTVX；
- 若有重大素材/落地页改动，应做新的 A/B cohort 来重新校准 LTV；
- 不同国家 eCPM 差异大，CPI_max 需按国家分设阈值。

如果你愿意，我可以：
- 基于你提供的 Snowball MCP 原始导出（cohort 表：install_date、installs、每日 ad_revenue）帮你计算出真实的 LTV_21、LTV_45、以及基于 15 天历史的 CPI 阈值和推荐出价区间；
- 或者我可以给出一个标准化的 Excel 模板（带公式），便于你直接把 Snowball 的数据粘进来得到 CPI_max 与推荐阈值。

你想先把 MCP 的近 15 天 cohort 导出给我，还是我先把 Excel 模板发给你？

---
## 🧑‍💻 User

请使用 snowball mcp 工具直接查询

---
## 🤖 Assistant

我无法直接在你的 Snowball MCP 帐号里远程登录并执行查询。但我可以立即给出：1）在 Snowball MCP 上一步步可执行的精确查询/报表设置（含字段、过滤器、时间窗、分组维度、导出格式）；2）一个标准导出模板（CSV 字段头）以及如何把导出的文件发给我，我帮你完成 LTV、CPI_max、15 天均值与阈值计算并给出投放建议。下面是具体可直接在 Snowball MCP 上执行的操作说明与示例查询（按你之前要求的 IAA 分析逻辑）。

1) 建议的时间窗口与 cohort 范围
- 安装 cohort 时间：取最近 45 日的 install_date（用于计算 LTV_21 与 LTV_45，同时保留最近 15 个 install cohort 用于取平均阈值）。
- 导出频率：按 “install_date”（安装日 cohort）分组，最近至少 45 天；用于取最近 15 天做平均阈值时要确保至少有 15 个 install_date cohort。

2) 必要维度与指标（在报表/查询中必须包含的字段）
- 维度（Group by）：install_date, channel (或 campaign), country, os (可选), creative (可选)
- 指标（Metrics）：
 - installs（安装数）
 - retention: D1, D3, D7, D14, D21, D30（次留及各日留存率）
 - daily_ad_revenue_day0, daily_ad_revenue_day1, ..., daily_ad_revenue_day45（或直接 daily_ad_revenue 按 day_offset）
 - cumulative_ad_revenue_day7/14/21/45（若 MCP 能直接给累计值）
 - impressions（按 cohort 的总 impressions）
 - eCPM（按 cohort）
 - fill_rate（如有）
 - campaign_cost（若 Snowball 可同步 cost；否则需把广告平台的 cost/installs 导入/对齐）
 - installs_by_campaign（若 cost 在广告平台，需要 campaign 层级 installs/cost）

3) 如果 Snowball 支持 SQL 查询（示例 SQL 思路）
- 若 MCP 提供按 day_offset 的 daily_ad_revenue 表结构，可用类似的 SQL（示例为逻辑示范，字段名按你的 MCP 实际字段替换）：

SELECT
install_date,
channel,
country,
SUM(installs) AS installs,
SUM(CASE WHEN day_offset = 0 THEN ad_revenue ELSE 0 END) AS revenue_d0,
SUM(CASE WHEN day_offset = 1 THEN ad_revenue ELSE 0 END) AS revenue_d1,
...
SUM(CASE WHEN day_offset <= 21 THEN ad_revenue ELSE 0 END) / SUM(installs) AS LTV_21,
SUM(CASE WHEN day_offset <= 45 THEN ad_revenue ELSE 0 END) / SUM(installs) AS LTV_45,
MAX(d1_retention) AS D1,
MAX(d7_retention) AS D7,
MAX(d14_retention) AS D14,
MAX(d21_retention) AS D21,
MAX(d30_retention) AS D30,
SUM(impressions) AS impressions,
AVG(ecpm) AS ecpm
FROM your_cohort_table
WHERE install_date BETWEEN date_sub(current_date, interval 45 day) AND current_date
GROUP BY install_date, channel, country
ORDER BY install_date DESC;

注意：把上面示例的字段名（day_offset, ad_revenue, installs, d1_retention 等）替换为 Snowball MCP 的实际字段名。

4) 在 MCP UI 的操作步骤（若你使用 UI 报表）
- 新建 Cohort 报表：
 - 按 install_date 分组
 - 选择维度 channel、country、OS
 - 指标添加 installs、D1/D7/D14/D21/D30、daily ad revenue（0~45 day）或 cumulative revenue 到 day21/day45、impressions、ecpm
 - 时间范围：最近 45 日 install cohorts
 - 导出格式：CSV (UTF-8)
- 导出后请确保每一行代表一个 install_date + channel + country 的 cohort，且包括 installs 与各 day 的 revenue（或累计 LTV_21/LTV_45 列）。

5) 导出文件的字段模板（把这个 CSV 导出并发给我以便我直接计算）
- 建议 CSV 列头（严格按此格式方便我自动化处理）：
install_date,channel,country,os,installs,d1_retention,d3_retention,d7_retention,d14_retention,d21_retention,d30_retention,impressions,ecpm,fill_rate,cost,cost_installs,daily_revenue_d0,daily_revenue_d1,...,daily_revenue_d45
- 如果 MCP 已直接给 cumulative LTV 列，可用：
install_date,channel,country,installs,d1_retention,d7_retention,d14_retention,d21_retention,d30_retention,impressions,ecpm,fill_rate,cost,cost_installs,LTV_7,LTV_14,LTV_21,LTV_45

说明：
- cost 与 cost_installs：若 Snowball 没有 campaign cost，请你从广告平台导出 campaign 的 cost 与 installs（同时间段、同渠道/国家粒度）并把 cost & cost_installs 合并到同一表里（或单独上传）。
- daily_revenue_dX：若 MCP 仅提供按日分表，导出时请包含 0~45 的 daily_revenue 列，或至少累计 LTV_21 与 LTV_45 两列。

6) 我会基于你导出的文件为你完成的计算（交付内容）
一旦你把 CSV 上传/发给我（或粘贴文件），我会：
- 对最近 15 个 install_date cohort（按你指定的渠道/国家聚合或总体）计算 LTV_21 和 LTV_45；
- 计算 μ_LTV21、σ_LTV21、μ_LTV45、σ_LTV45（15 天均值与标准差）；
- 生成 CPI_max（ROI=0）阈值：CPI_max_21 = μ_LTV21；CPI_max_45 = μ_LTV45；
- 给出保守阈值（μ * 0.9）、进攻阈值（μ）与+10% ROI 的目标出价；
- 按 channel/country/creative 分层输出哪些组合满足“可投放/可小量测试/不可投放”；
- 输出一个包含每个 cohort：installs、D1、LTV_21、LTV_45、CPI（若提供 cost）、是否达标 的表格与建议。

7) 现在我能帮你的两种方式（请选择其一）
- 方案 A（推荐）：按照我上面给的 CSV 字段模板，在 Snowball MCP 导出最近 45 天的 cohort CSV（含 cost 若可），并把 CSV 上传到此对话（或提供下载链接）。我会基于该数据做完整计算并返回阈值与分渠道建议。
- 方案 B：你希望我直接给出在 Snowball MCP 控制台可复制粘贴的查询脚本 / UI 报表配置（我已经在上面给出），你自己执行后把结果贴上来让我分析。

告诉我你选择哪种方式，或者直接把 Snowball MCP 导出的 CSV 上传（或粘贴前几行示例），我马上开始计算并返回 Weather&News 项目的买量 ROI 打正阈值与核心指标。

---
## 🧑‍💻 User

请使用 SnowBall MCP

---
## 🤖 Assistant

抱歉，我无法直接登录或在你的 Snowball MCP 帐号里执行查询。但我可以立刻给出可在 Snowball MCP 控制台“直接复制/执行”的完整操作步骤、精确查询（SQL/报表配置）、导出字段模板、及后续自动化计算（LTV_21/LTV_45、15 天均值、CPI_max、保守/进攻阈值）的脚本。你按下面步骤在 MCP 运行并导出结果后，把 CSV 发给我，我会帮你算出 Weather&News 的最终阈值与分渠道建议；如果需要，我也可以给出 Dashboard/告警设置示例。

一、在 Snowball MCP 上要做的总体任务
- 按 install_date 建立 cohort（最近 45 天），计算每个 cohort 到 day21 与 day45 的累计广告收益（LTV_21、LTV_45），以及留存（D1/D7/D14/D21/D30）。
- 用最近 15 个 install_date cohort 的 LTV_21 / LTV_45 求平均 μ 与标准差 σ，得出 CPI_max（ROI=0）与保守/进攻阈值。
- 将投放渠道的实际 CPI（cost/installs）与 CPI_max 对比，决定可投/小量/暂停。

二、MCP UI 报表配置（一步步）
1) 时间区间：install_date 选择最近 45 天（确保包含最近 15 个 install cohort 用于均值）。
2) 分组（Group by）：install_date, channel (或 campaign), country, os（按需）
3) 指标（Metrics）必选：
 - installs（安装数）
 - retention: D1, D7, D14, D21, D30
 - daily_ad_revenue/day_offset（0~45）或直接 cumulative_ad_revenue_day21、cumulative_ad_revenue_day45（若 MCP 支持）
 - impressions, eCPM, fill_rate（如有）
 - campaign_cost（若 MCP 内部有 cost 同步；否则后续合并）
4) 输出格式：CSV (UTF-8)

三、若 MCP 支持 SQL 查询，请复制并替换字段名后执行（示例 SQL，按你 MCP 字段名改）
注意：把 table_name 与字段名替换为你 MCP 的实际名称。

示例 SQL（逻辑示范）：
SELECT
install_date,
channel,
country,
SUM(installs) AS installs,
MAX(d1_retention) AS d1,
MAX(d7_retention) AS d7,
MAX(d14_retention) AS d14,
MAX(d21_retention) AS d21,
MAX(d30_retention) AS d30,
SUM(CASE WHEN day_offset <= 21 THEN ad_revenue ELSE 0 END) / NULLIF(SUM(installs),0) AS LTV_21,
SUM(CASE WHEN day_offset <= 45 THEN ad_revenue ELSE 0 END) / NULLIF(SUM(installs),0) AS LTV_45,
SUM(impressions) AS impressions,
AVG(ecpm) AS avg_ecpm,
SUM(cost) AS cost, -- 若有cost
CASE WHEN SUM(cost) > 0 THEN SUM(cost) / NULLIF(SUM(installs),0) ELSE NULL END AS CPI
FROM your_cohort_table
WHERE install_date BETWEEN DATE_SUB(CURRENT_DATE, INTERVAL 45 DAY) AND CURRENT_DATE
GROUP BY install_date, channel, country
ORDER BY install_date DESC, channel, country;

四、导出 CSV 字段模板（请按此格式导出，便于我直接处理）
CSV 列头建议：
install_date,channel,country,os,installs,d1_retention,d7_retention,d14_retention,d21_retention,d30_retention,impressions,avg_ecpm,fill_rate,cost,cpi,LTV_7,LTV_14,LTV_21,LTV_45

说明：
- 若没有 LTV_7/14/21/45，请导出 day_offset 的 daily_revenue_d0..daily_revenue_d45 列，我将按行累加计算 LTV。
- 若 MCP 无 cost，请同时导出广告平台的 campaign cost & installs（按相同维度：install_date/channel/country）并在同一表中合并或单独提供 CSV。

五、如何把广告平台 cost 与 MCP 数据对齐
- 在广告平台导出：date, campaign/channel, country, installs, cost
- 把两表按 (install_date, channel, country) 左连接，计算 CPI = cost / installs（对应 MCP 的 installs）
- 若存在时间差（点击->安装延迟），请按 install_date 来对齐（通常以 SDK 上报的 install_date 为准）。

六、导出后我会为你完成的计算（你发 CSV 后我会执行）
- 选择最近 15 个 install_date cohort（可按总体或按 channel/country 分组）：
 - 计算 μ_LTV21、σ_LTV21 与 μ_LTV45、σ_LTV45
 - CPI_max_21 = μ_LTV21（ROI=0），CPI_max_45 = μ_LTV45
 - 保守阈值 = μ * 0.9（留 10% 安全边际）
 - 进攻阈值 = μ（目标打正）
 - +10% ROI 目标 = μ * 1.1
- 输出分渠道表（每行：install_date, channel, country, installs, D1, LTV_21, LTV_45, CPI, status），status 为：可放量 / 小量测试 / 暂停（基于 CPI 与 CPI_max 比较）

七、我给你的自动化脚本（本地/线上运行，处理你导出的 CSV）
下面给出 Python（pandas）脚本片段，你可在本地直接运行，或把 CSV 发给我让我跑。替换 input.csv 为你导出的文件名。

Python 示例（用于计算 μ/σ、阈值与分渠道判定）：
# 示例伪代码（请在有 Python 环境下运行）
import pandas as pd
df = pd.read_csv('input.csv', parse_dates=['install_date'])
# 只取最近 45 天并按 install_date 排序
df = df.sort_values('install_date', ascending=False)
# 取最近 15 个 install_date cohort 的汇总（可按 channel/country 分组）
recent_dates = df['install_date'].drop_duplicates().head(15)
df15 = df[df['install_date'].isin(recent_dates)]
# 按总体计算 LTV 均值与阈值
mu_ltv21 = df15['LTV_21'].mean()
sigma_ltv21 = df15['LTV_21'].std()
cpi_max_21 = mu_ltv21
cpi_conservative_21 = mu_ltv21 * 0.9
cpi_aggressive_21 = mu_ltv21 * 1.1
print('LTV21 mean', mu_ltv21, 'std', sigma_ltv21)
print('CPI_max_21', cpi_max_21, 'conservative', cpi_conservative_21, 'target+10%', cpi_aggressive_21)
# 分渠道判定
def status(row):
 if pd.isna(row['cpi']): return 'no_cost'
 if row['cpi'] <= cpi_conservative_21: return 'go'
 if row['cpi'] <= cpi_max_21 * 1.1: return 'test_small'
 return 'stop'
df['status'] = df.apply(status, axis=1)
df.to_csv('output_with_status.csv', index=False)

八、若你现在就想要快速结果（两种快速方式）
- 方式 A（我推荐）：按我上面的 CSV 模板在 Snowball MCP 导出数据并上传到此对话（或提供下载链接）。我会替你计算并直接返回阈值/分渠道建议与可下载表格。
- 方式 B：你希望我给出更详细的 UI 报表截图步骤、告警规则（例如 CPI 超过 CPI_max 10% 即告警）和 Dashboard 配置，我会把完整步骤和示例告警规则列出（可直接在 MCP 或监控系统中配置）。

九、注意事项（快速提示）
- IAA LTV 受 eCPM 波动影响，要按 country/channel 单独计算 CPI_max；
- 若 D1 < 10% 建议先做产品优化再重启大规模买量；
- 若你要立刻投放，先做小量测试（CPI ≤ 保守阈值）并观察首周 LTV 与留存。

现在请任选其一：
1) 直接在 Snowball MCP 导出最近 45 天 cohort（按我给的 CSV 列头），然后把 CSV 上传到对话中；我会立刻计算并返回 Weather&News 的 CPI_max_21/CPI_max_45、保守/进攻阈值和按 channel 的投放建议。
2) 如果你需要我给出更精确的 SQL（针对你 MCP 的具体字段名），把你 MCP 表的字段清单发给我，我会把 SQL 语句精确化，你直接复制运行即可。

你选哪个？或者现在就把导出的 CSV 上传。
