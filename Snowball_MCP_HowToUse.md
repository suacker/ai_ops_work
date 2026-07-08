# Snowball MCP 使用方法

# SnowBall MCP 介绍

Snowball MCP 用于  AI Agent 工具连接公司 SnowBall 数据，从 Snowball 系统读取项目各项数据，目前支持 项目信息，买量计划ROI 报告、项目营收、广告变现、用户数据、内购报告等数据，基本支持 BI 网页集成数据报告。SnowBall MCP 支持目前所有的 AI Agent 工具，Claude Code, Codex, Cursor , OpenClaw 或者 Hermes Agent ，飞书智能体等。

# MCP 配置

**配置信息**

1. 类型选择：streamableHttp

2. MCP URL：https://snowball\-ai\-api\.thinkyeah\.com/mcp

3. 添加认证：复制自己的Token，填入MCP 客户端的 header 配置里，Authorization=xxxxxxxxxxxxxxxxxx



**MCP 配置过程如下 （以Codex 为例）**

1. 在 Codex 设置中 MCP 设置

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YjAzMzUxNTc0NGM0OTNlZmIwMzY2MTgwY2U3OGE1MmZfYWJmODllZjRkZTE0MjE2ZjFhZDlmNzNhNzc1ZTBjZGVfSUQ6NzY0MTU4Nzc0MjAzNjA1MzE3Ml8xNzgzNDcyMjE2OjE3ODM1NTg2MTZfVjM)

2. 添加 MCP 服务器

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YzU5MjBhOTczNDdlNTQxYjJlYTVjNmVhZDk0NmIwM2FfM2Y0Mjg1YzU2NTZjZTg0OTI5OGJmNjczYWY3ZDgyM2VfSUQ6NzY0MTU5MDM2OTg0Mjc0NDI1Ml8xNzgzNDcyMjE2OjE3ODM1NTg2MTZfVjM)

\(标头增加 Authorization 头， 标头:  Authorization ,   值为:   Bearer  你的MCP Token ）



3. 授权 SnowBall 访问权限

    Codex 里首次 MCP使用 ，会出现请求 Snow MCP 授权。AI 回答中提示授权时，点击 “SnowBall MCP 授权”， 浏览器登录你的 SnowBall 账户，即可完全授权。

    

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTYwMDE3MDU3ZWNiMDdlOTU3ZDNhNGM2M2Q5ZWFhZDFfOGU4Y2Q1ZWM4MzMzYTM5ZDM2MTdlYmUwODZiZWQ1ZWJfSUQ6NzY0MTYwNjAyMzg4Njc1MjcxOV8xNzgzNDcyMjE2OjE3ODM1NTg2MTZfVjM)

# 目前 MCP 功能支持

### **项目营收**

**MCP 工具：**

- `get_profit_report`

用于查看项目整体营收、利润、成本、RTS \(每日收入花费比）、DAU、DNU 等经营指标。



**典型提问词：**

- 项目近期收入变化

- 广告收入和内购收入结构

- 项目整体 利润趋势

- 国家维度收入拆解

    

常用指标包括：

- `revenue`

- `profit`

- `total_cost`

- `roi`

- `ads_revenue`

- `sale_revenue`

- `dau`

- `dnu`

- `arpdau`

- `ecpm`

- `retention_1`

### **ROI  分析**

**工具：**`get_roi_report`

买量分析最常用接口，用于查看项目在日期、国家、渠道、Campaign、Adgroup 等维度下的 ROI 表现。

常用指标： 花费，安装数，转化数， CPI ， ROI X （`roi0`, `roi1`, `roi3`, `roi7`, `roi14` 等）， 留存 （`retention_1`, `retention_2`, `retention_3`等 Web 报告都支持。



**典型提问词：**

- 分析某一个项目 近 3 天 / 近 5 天 ROI0 变化

- 按国家级分析投放效果，考核 ROI 0 在 45% 以上，同时关注 次留和 ROI 14

- 渠道、Campaign 买量计划 ROI 排名

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NzhhOGNiZTBhMjIyZWFiMjNiMTYxZjUzN2IzNzYyOThfYzY2NGM0ZDg2MDg0Mzc2M2I5Y2U3NjI2YjNkZGJhZGFfSUQ6NzY0MTU5MzkzMTg1MTE4OTQ2NV8xNzgzNDcyMjE2OjE3ODM1NTg2MTZfVjM)



### **广告变现**

**工具入口：**

- `get_ads_revenue_table_data`

- `get_est_ads_revenue_table_data`



用于分析广告收入、展示、eCPM、填充率、广告位表现等。



**典型提问词：**

- 分国家 eCPM 对比

- 插屏、开屏、激励视频收益表现

- 变现平台对比

- 广告展示率分析



**指标：**

- 广告收入：`ads_revenue`

- 展示：`impressions`

- 点击：`clicks`

- 请求：`requests`

- eCPM：`ecpm`

- DNU/DAU 

- ARPDAU

- IPU



### **用户数据**

**工具入口：**`get_user_report`



用于查看用户规模、留存、安装、卸载、崩溃等用户侧指标。

**常用指标：**

- `installed`

- `dau`

- `dnu`

- `retention`

- `new_uninstall_rate`

- `keep_alive`

- `app_crashes`

- `anrs`

    

**典型提问词：**

- 用户增长趋势

- 新增质量变化

- 留存趋势

- 崩溃 / ANR 风险

    

### **内购与订阅分析**

**核心工具：**

- `get_iap_report`

- `get_subscription_report`

    

用于分析订单、订阅、新购、续订、退款等 IAP 相关数据。



**常用指标：**

- 新购订单：`new_orders`

- 续订订单：`renew_orders`

- 总订单：`orders`

- 退款：`refund`

- 新购收入：`new_sale_revenue`

- 续订收入：`renew_sale_revenue`

- 总内购收入：`total_sale_revenue`

- 退款率：`refund_rate`



# **AI Agent 分析实践**

在 AI Agent 工具里分析业务数据，AI 会自动理解 MCP 的工具功能声明，一般会自动按如下的过程分析数据。使用中不用特别指明 MCP 工具名，仅需说明清楚需要分析的数据指标，明确指明需要分析的目标和分析方法。



（AI 推理执行过程如下：）

```Plain Text
提到的项目名
→ get_projects 定位 project_id
→ get_roi_report 拉 ROI / CPI / 留存 / Campaign 数据
→ get_profit_report 或 get_profit_chart 看整体收入与利润
→ get_ads_revenue_table_data 看广告变现拆解
→ 输出 Markdown / HTML 报告
```



**常见的分析场景**

1. 买量效果分析

主要依赖 `get_roi_report`，看 ROI0、ROI1、ROI3、CPI、次留、Campaign 表现。



2. 收入与利润分析

主要依赖 `get_profit_report` / `get_profit_chart`，看收入、成本、利润、ROAS。



3. 广告变现分析

主要依赖 `get_ads_revenue_table_data`，看广告收入、eCPM、展示、广告位和变现平台表现。

