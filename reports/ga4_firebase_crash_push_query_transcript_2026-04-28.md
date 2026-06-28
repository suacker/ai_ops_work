# 对话转录

## User

https://medium.com/zrealm-robotic-process-automation/crashlytics-google-analytics-%E8%87%AA%E5%8B%95%E6%9F%A5%E8%A9%A2-app-crash-free-users-rate-793cb8f89b72 
理解这个文章，输入确定 如何使用 Google GA4 Query api 以python 程序查询一个 firebase app 项目的crash rate 

## Assistant

结论先说清楚：你要查的不是 Firebase Crashlytics API，而是 **GA4 的 Google Analytics Data API**。你给的文章核心判断是对的：**Crashlytics 本身没有直接给你一个可用来查 `crash-free users rate` 的公开报表 API，所以要通过已经关联 Firebase 的 GA4 Property，用 `runReport` 查 `crashFreeUsersRate` / `crashAffectedUsers`**。官方也明确写了：

- `crashFreeUsersRate` = 无 crash 用户数 / 总用户数，**返回小数**，例如 `0.9243 = 92.43%`。
- `crashAffectedUsers` = 该行范围内至少发生过一次 crash 的用户数。
- App stability 卡片的数据来自 **Firebase Crashlytics**。

如果你说的 “crash rate” 指的是“用户 crash 比例”，最直接就是：

- `crash_rate = 1 - crashFreeUsersRate`

如果你更想看分子分母，也可以同时查：

- `crashAffectedUsers`
- `totalUsers`

然后自己算：

- `crash_rate = crashAffectedUsers / totalUsers`

**前提条件**

1. Firebase 项目已经关联到一个 **GA4 property**。
2. 你的 App 已经接入 **Firebase Crashlytics**。
3. 在 Google Cloud 里启用 **Google Analytics Data API v1**。
4. 你用的用户或 service account 对这个 GA4 property 有读取权限。官方 quickstart 也明确要求给 service account 加 property 权限。

**Python 查询示例**

安装：

```bash
pip install google-analytics-data
```

设置凭证：

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

代码：

```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    FilterExpression,
    Filter,
)

PROPERTY_ID = "123456789"  # GA4 property id

def query_crash_rate(
    property_id: str,
    start_date: str,
    end_date: str,
    platform: str | None = None,   # "iOS" / "Android"
    stream_id: str | None = None,  # 如果同一 property 下有多个 app，建议用 streamId 更精确
):
    client = BetaAnalyticsDataClient()

    filter_expressions = []

    if platform:
        filter_expressions.append(
            FilterExpression(
                filter=Filter(
                    field_name="platform",
                    string_filter=Filter.StringFilter(
                        value=platform,
                        match_type=Filter.StringFilter.MatchType.EXACT,
                    ),
                ),
            )
        )

    if stream_id:
        filter_expressions.append(
            FilterExpression(
                filter=Filter(
                    field_name="streamId",
                    string_filter=Filter.StringFilter(
                        value=stream_id,
                        match_type=Filter.StringFilter.MatchType.EXACT,
                    ),
                ),
            )
        )

    dimension_filter = None
    if len(filter_expressions) == 1:
        dimension_filter = filter_expressions[0]
    elif len(filter_expressions) > 1:
        dimension_filter = FilterExpression(and_group=FilterExpression.FilterExpressionList(
            expressions=filter_expressions
        ))

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="platform")],
        metrics=[
            Metric(name="crashFreeUsersRate"),
            Metric(name="crashAffectedUsers"),
            Metric(name="totalUsers"),
        ],
        dimension_filter=dimension_filter,
    )

    response = client.run_report(request)

    rows = []
    for row in response.rows:
        row_platform = row.dimension_values[0].value
        crash_free_rate = float(row.metric_values[0].value)   # 0~1
        crash_affected_users = int(row.metric_values[1].value)
        total_users = int(row.metric_values[2].value)

        rows.append({
            "platform": row_platform,
            "crash_free_users_rate_pct": round(crash_free_rate * 100, 2),
            "crash_rate_pct": round((1 - crash_free_rate) * 100, 2),
            "crash_affected_users": crash_affected_users,
            "total_users": total_users,
        })

    return rows


if __name__ == "__main__":
    data = query_crash_rate(
        property_id=PROPERTY_ID,
        start_date="2026-04-20",
        end_date="2026-04-26",
        platform="Android",
        # stream_id="1234567890",
    )
    print(data)
```

**会返回什么**

比如：

```python
[
  {
    "platform": "Android",
    "crash_free_users_rate_pct": 99.21,
    "crash_rate_pct": 0.79,
    "crash_affected_users": 158,
    "total_users": 20014
  }
]
```

**几个容易踩坑的点**

- `crashFreeUsersRate` 返回的是 **小数，不是百分比字符串**。
- 如果一个 Firebase 项目下挂了多个 App，同一个 GA4 property 里会混在一起。  
  这时建议用 `streamId` 或至少用 `platform` 过滤。
- 刚把 Firebase 链到 GA4 后，官方说 **最多可能要 24 小时** 数据才流过来。
- 文章里用的是 Apps Script + Query Explorer；换成 Python，本质上只是把同一个 `runReport` 请求改成 Python 客户端调用。

如果你要，我下一步可以直接给你一份：
1. `requirements.txt`  
2. 可执行的 `query_firebase_crash_rate.py`  
3. 支持命令行参数 `--property-id --platform --start-date --end-date` 的完整脚本。

**来源**

- 文章原文：[Medium: Crashlytics + Google Analytics 自動查詢 App Crash-Free Users Rate](https://medium.com/zrealm-robotic-process-automation/crashlytics-google-analytics-%E8%87%AA%E5%8B%95%E6%9F%A5%E8%A9%A2-app-crash-free-users-rate-793cb8f89b72)
- GA4 Data API 指标定义：[API schema](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)
- GA4 `runReport` 权限范围：[properties.runReport](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
- Python quickstart：[Google Analytics Data API quickstart](https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart)
- Firebase 与 GA4 关联：[Connect Firebase to Google Analytics](https://support.google.com/analytics/answer/9289234?hl=en)
- App stability 数据来源：[App stability overview](https://support.google.com/analytics/answer/12995879?hl=en)

## User

请生成完整的代码

## Assistant

完整代码已生成在 [scripts/ga4_crash_rate_query.py](/Users/suacker/dev/DataAnalysis/BI/scripts/ga4_crash_rate_query.py)。我已做过 `python3 -m py_compile` 语法校验，脚本本身可通过。

使用前先安装依赖：

```bash
pip install google-analytics-data google-auth
```

然后准备 service account key，并二选一提供凭证：

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

或直接命令行传：

```bash
python3 scripts/ga4_crash_rate_query.py \
  --property-id 123456789 \
  --start-date 2026-04-20 \
  --end-date 2026-04-26 \
  --platform Android \
  --credentials /path/to/service-account.json
```

按天输出并返回 JSON：

```bash
python3 scripts/ga4_crash_rate_query.py \
  --property-id 123456789 \
  --start-date 2026-04-20 \
  --end-date 2026-04-26 \
  --platform iOS \
  --daily \
  --json
```

这份脚本会查询：
- `crashFreeUsersRate`
- `crashAffectedUsers`
- `totalUsers`

并额外给出：
- `crash_free_users_rate_pct`
- `crash_rate_pct`（即 `1 - crashFreeUsersRate`）

如果你要，我下一步可以继续补一版：
1. 支持读取多个 app 配置批量查询
2. 自动导出 CSV
3. 直接写入 Google Sheet 或飞书表格

## User

是否还能查询 用户的 firebase push  接受情况 

## Assistant

可以，但要先明确你说的“接受情况”是哪一层。Firebase Push 相关数据通常分 3 类：

1. **发送 / 投递层**
   - 消息是否被 FCM 接受
   - 是否送达到设备
   - 送达延迟
   - 这类更适合查 **FCM BigQuery 导出**
   - 官方文档里明确有 `MESSAGE_ACCEPTED`、`MESSAGE_DELIVERED`，还能按 `message_id + instance_id` 跟踪单条消息流程  
   来源：[Understanding message delivery](https://firebase.google.com/docs/cloud-messaging/understand-delivery)

2. **用户交互层**
   - 用户是否收到通知
   - 是否打开通知
   - 是否 dismiss
   - 这类可以走 **GA4 / Firebase Analytics**
   - 官方 SDK 事件列表里有 `notification_receive`、`notification_open`、`notification_dismiss`、`notification_foreground`  
   来源：[FirebaseAnalytics.Event](https://firebase.google.com/docs/reference/android/com/google/firebase/analytics/FirebaseAnalytics.Event)

3. **用户授权层**
   - 用户是否允许系统通知权限
   - 这个 **不能靠 GA4 自动直接查全量标准指标**
   - 通常需要你在 App 里自己上报一个自定义事件或用户属性，比如 `push_permission_granted=true`

**所以结论是：**

- 如果你想查“推送有没有发出去、有没有送到设备”，用 **FCM BigQuery 导出**。
- 如果你想查“用户有没有点开推送”，用 **GA4 Data API** 查通知事件。
- 如果你想查“用户是否同意通知权限”，需要 **App 侧自定义埋点**。

**能不能像 crash rate 一样用 Python 查？可以。**

**A. 查推送打开/接收情况：GA4 Data API**
适合聚合报表，例如：
- 某天 `notification_open` 次数
- 某平台打开通知的用户数
- 某日期范围打开率

你可以用 `eventName` + `eventCount` / `totalUsers` 查询。

示例思路：
- `dimension`: `eventName`, `date`, `platform`
- `metric`: `eventCount`, `totalUsers`
- `filter`: `eventName == notification_open`

**B. 查送达率：FCM BigQuery**
适合更底层的交付分析，例如：
- `MESSAGE_ACCEPTED`
- `MESSAGE_DELIVERED`
- `percent_delivered`
- 某 `message_id` 的逐设备表现

官方示例里已经给了“投递率”SQL：用 `MESSAGE_ACCEPTED` 和 `MESSAGE_DELIVERED` 算 delivered percentage。  
来源：[Understanding message delivery](https://firebase.google.com/docs/cloud-messaging/understand-delivery)

**一个重要限制**

GA4 Data API 主要是**聚合查询**，不适合直接拿“每个用户的明细列表”。  
如果你要：
- 某条 push 被哪些用户打开
- 某个实例 ID 是否收到/打开
- 用户级联表

那要走 **BigQuery 导出**。GA4/Firebase 导出的 BigQuery 数据里有 `user_pseudo_id`。  
来源：
- [GA4 BigQuery Export schema](https://support.google.com/analytics/answer/7029846)
- [Export Firebase data into BigQuery](https://firebase.google.com/docs/projects/bigquery-export)

如果你要，我可以下一步直接给你两份完整代码：

1. **Python + GA4 Data API**：查询 `notification_open` / `notification_receive` 聚合数据  
2. **BigQuery SQL / Python**：查询 FCM `MESSAGE_ACCEPTED` / `MESSAGE_DELIVERED` / 送达率 / 打开链路

如果你的目标是“运营看板”，我建议优先做这两个指标：
- `push_open_users / push_receive_users`
- `delivered_messages / accepted_messages`

如果你愿意，我现在就直接生成：
- `scripts/ga4_push_engagement_query.py`
- `scripts/fcm_delivery_query.py`

## User

直接生成 scripts/ga4_push_engagement_query.py

## Assistant

脚本已生成在 [scripts/ga4_push_engagement_query.py](/Users/suacker/dev/DataAnalysis/BI/scripts/ga4_push_engagement_query.py)，并已通过 `python3 -m py_compile` 语法校验。

它支持查询这些 GA4 / Firebase Analytics 推送事件：
- `notification_open`
- `notification_receive`
- `notification_dismiss`
- `notification_foreground`

常见用法：

```bash
pip install google-analytics-data google-auth
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

查询打开事件：

```bash
python3 scripts/ga4_push_engagement_query.py \
  --property-id 123456789 \
  --start-date 2026-04-20 \
  --end-date 2026-04-26 \
  --event-name notification_open \
  --platform Android
```

按天查接收事件并输出 JSON：

```bash
python3 scripts/ga4_push_engagement_query.py \
  --property-id 123456789 \
  --start-date 2026-04-20 \
  --end-date 2026-04-26 \
  --event-name notification_receive \
  --platform iOS \
  --daily \
  --json
```

直接计算 `open / receive` 打开率：

```bash
python3 scripts/ga4_push_engagement_query.py \
  --property-id 123456789 \
  --start-date 2026-04-20 \
  --end-date 2026-04-26 \
  --platform Android \
  --daily \
  --compare-open-rate
```

这个脚本输出的是 **GA4 聚合数据**，适合做报表。如果你下一步要查：
- 某条 push 的 `message_id`
- 送达率 `MESSAGE_ACCEPTED / MESSAGE_DELIVERED`
- 用户级明细

那就要再补一份 **FCM BigQuery** 脚本，不是 GA4 Data API。

## User

<environment_context>
  <shell>zsh</shell>
  <current_date>2026-04-28</current_date>
  <timezone>Asia/Shanghai</timezone>
</environment_context>

## User

把以上所有内容，一字不差保存到一个 markdown 文档。 
