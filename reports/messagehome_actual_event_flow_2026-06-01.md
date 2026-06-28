# MessageHome 实机事件发生过程与上手体验问题分析

项目：MessageHome  
APK：`/Users/suacker/dev/DataAnalysis/BI/app_builds /messageHome-debug.apk`  
包名：`sms.messenger.mms.text.ai.home`  
版本：`2.3.47` / `versionCode=2347`  
入口 Activity：`xyz.klinker.messenger.activity.LandingActivity`  
验证时间：2026-06-01 00:22-00:28  
验证环境：Android Emulator `Pixel_9`  

## 验证方法

1. 启动最近使用的 Android 模拟器 `Pixel_9`。
2. 安装最新 debug APK。
3. 由于卸载返回 `DELETE_FAILED_INTERNAL_ERROR`，本次使用 `pm clear sms.messenger.mms.text.ai.home` 清空应用数据，模拟新用户首次启动。
4. 启动 App，按真实用户路径完成：
   - 首次启动
   - 点击设置默认短信
   - 在系统弹窗中选择 MessageHome
   - 关闭默认短信完成后的插屏广告
   - 在短信主界面按提示右滑进入 Home
   - 点击设置默认桌面
   - 在系统默认桌面设置页选择 MessageHome
5. 通过 `adb logcat` 过滤 `EasyTracker` / `sendEvent` 相关日志，记录实际事件发生顺序。

原始证据：

- 完整 logcat：`/Users/suacker/dev/DataAnalysis/BI/output/messagehome_actual_events/logcat_full_2026-06-01.txt`
- EasyTracker 过滤日志：`/Users/suacker/dev/DataAnalysis/BI/output/messagehome_actual_events/easytracker_events_2026-06-01.txt`
- 截图目录：`/Users/suacker/dev/DataAnalysis/BI/output/messagehome_actual_events/`

## 实际事件发生顺序

| 时间 | 用户/系统阶段 | 实际事件 | 关键参数 | 说明 |
|---|---|---|---|---|
| 00:22:42.167 | App 进程启动 | `th_process_daily_alive` | 空 | 进程日活事件最早发送。 |
| 00:22:42.458 | 安装归因 | `th_install_referrer` | `utm_source=google-play&utm_medium=organic` | 连续发送了 2 次，疑似重复。 |
| 00:22:42.461 | 安装归因 | `th_install_referrer` | `utm_source=google-play&utm_medium=organic` | 与上一条重复。 |
| 00:22:43.239 | Push 用户初始化 | `track_push_user` | 空 | 首启早期即发送。 |
| 00:22:44.166 | 内部首开 | `th_first_open` | `app_installer => null` | EasyTracker 内部首开事件。 |
| 00:22:44.724 | 首次 UI 打开 | `th_first_ui_open` | `null` | 首个 UI view 后发送。 |
| 00:22:45.195 | UMP 状态 | `ump_disabled_status` | 空 | UMP 状态事件，后续重复多次。 |
| 00:22:47.477 | 首启广告尝试 | `th_ad_no_impression` | 空 | 首启阶段已有广告场景尝试，但没有展示。 |
| 00:22:48.335 | 进入 Home | `ACT_EnterHomePage` | `default_app => 0` | 进入 Home，尚未是默认桌面。 |
| 00:22:48.630 | 展示默认桌面引导 | `ACT_ShowSetUp` | `null` | 首屏虽然是默认短信引导，但日志记录了默认桌面 setup 展示。 |
| 00:22:48.915 | 再次进入 Home | `ACT_EnterHomePage` | `default_app => 0` | 同一首启阶段重复触发。 |
| 00:24:41.144 | 点击设置默认短信 | `CLK_SetAsDefault` | `null` | 用户点击首屏 `Set Default SMS App`。事件名过于通用。 |
| 00:24:41.521 | 展示默认短信系统设置 | `ACT_ShowSetupMSGPlus` | `null` | 系统默认短信选择弹窗出现。 |
| 00:25:06.707 | 默认短信设置成功 | `ACT_SuccessSetupMSGPlus` | `null` | 用户选择 MessageHome 为默认短信后发送。 |
| 00:25:07.139 | 进入广告场景 | `th_ad_enter_scene` | 空 | 默认短信成功后立刻进入广告场景。 |
| 00:25:07.277 | 优化完成 | `ACT_FinishOptimizing` | `null` | 插屏展示前后发送，语义不清。 |
| 00:25:09.154 | 插屏展示成功 | `th_ad_impression` | 空 | 默认短信成功后约 2.4 秒出现全屏广告。 |
| 00:25:45.407 | 插屏关闭 | `th_ad_close` | 空 | 用户关闭广告后进入短信主页面。 |
| 00:27:43.338 | 点击设置默认桌面 | `CLK_SetAsDefault` | `null` | 与默认短信点击共用同一个事件名，无法区分。 |
| 00:27:43.341 | 进入系统默认桌面设置 | `ACT_EnterSystemSelectLauncher` | `null` | 进入 Android 默认 Home App 设置页。 |
| 00:28:21.646 | 点击说明弹窗 | `CLK_GotIt` | `null` | 系统设置页上叠加 App 指引弹窗，用户点击 GOT IT。 |
| 00:28:33.028 | 默认桌面后进入 Home | `ACT_EnterHomePage` | `default_app => 1` | 选择 MessageHome 为默认桌面后回到 Home。 |

本次实测没有观察到 `ACT_SuccessSetAsDefaultLauncher`，但 Snowball 漏斗此前使用过该事件作为默认桌面成功事件。实机日志只看到 `ACT_EnterHomePage default_app => 1`，需要研发确认默认桌面成功事件是否漏发、延迟发送，或事件名与 BI 配置不一致。

## 实际界面过程

### 1. 首屏直接要求设置默认短信

截图：`/Users/suacker/dev/DataAnalysis/BI/output/messagehome_actual_events/step1_default_sms_intro.png`

首屏文案为：

- `Welcome to Message Home`
- `SMART. SIMPLE. PRIVATE`
- `To use function, Message Home needs to be the default SMS app to access messages`
- 主按钮：`Set Default SMS App`

问题：用户还没有看到短信功能价值、会话列表能力、垃圾短信防护效果，就被要求设置系统默认短信。这个请求属于高心理成本授权，转化天然偏低。

### 2. Android 系统默认短信弹窗

截图：`/Users/suacker/dev/DataAnalysis/BI/output/messagehome_actual_events/step2_system_sms_dialog.png`

系统弹窗默认选中 `Messages Current default`，`Set as default` 初始禁用。用户必须先选择 `#Message Home`，再点击确认。

问题：这是两步操作，而且弹窗标题里 App 名带 `#`，不如产品品牌自然，可能降低信任感。

### 3. 默认短信成功后立刻出现插屏广告

截图：`/Users/suacker/dev/DataAnalysis/BI/output/messagehome_actual_events/step3_interstitial_after_sms.png`

事件链路：

```text
ACT_SuccessSetupMSGPlus
-> th_ad_enter_scene
-> ACT_FinishOptimizing
-> th_ad_impression
```

问题：用户刚完成默认短信授权，还没有进入主功能，就被全屏广告打断。这是当前上手体验里最严重的问题，会直接影响次留、默认桌面后续转化和用户信任。

### 4. 广告关闭后进入短信主页面，但立即引导右滑进入 Home

广告关闭后进入 `Message Home` 的短信页，页面为空会话状态，同时出现遮罩：

```text
Swipe right to unlock your home.
Experience your home features instantly.
```

问题：用户刚设置默认短信，预期应该看到“短信是否导入、如何发消息、是否有会话”等 SMS 主功能。此时马上切到 Home/Launcher 概念，会造成产品身份混乱。

### 5. 默认桌面设置引导文案不一致

进入 Home 后出现默认桌面卡片：

```text
Set as default home app
Set Message Home as your default message app to enjoy enhanced spam protection.
```

问题：标题是 `default home app`，说明却写 `default message app`，而理由是 `spam protection`。桌面权限、短信默认、垃圾短信防护三个概念混在一起。

### 6. 系统默认桌面设置页又叠加 App 指引浮层

截图：`/Users/suacker/dev/DataAnalysis/BI/output/messagehome_actual_events/step8_default_home_done.png`

点击默认桌面后进入 Android 系统设置页，App 再叠加一个说明弹窗，要求用户点击 `GOT IT` 后再选择 MessageHome。

问题：流程从“点击默认桌面”到“真正选择默认桌面”之间又多了一步，实际路径变长，用户容易中断。

## 事件埋点问题

### P0：默认短信成功事件与 Snowball 漏斗口径不一致

实测默认短信成功事件是：

```text
ACT_SuccessSetupMSGPlus
```

此前 Snowball 漏斗查询使用过：

```text
ACT_SetDefaultSuccess
```

如果线上 BI 配置仍使用 `ACT_SetDefaultSuccess`，会低估默认短信完成转化。需要马上确认生产版本真实发送事件名，并统一 Snowball 漏斗口径。

### P0：默认桌面成功事件未在本次实测日志中出现

实测选择 MessageHome 为默认桌面后只看到：

```text
ACT_EnterHomePage, default_app => 1
```

没有观察到：

```text
ACT_SuccessSetAsDefaultLauncher
```

需要检查默认桌面成功事件是否：

1. 没有发送。
2. 只在特定页面 resume 时发送。
3. 事件名不是 `ACT_SuccessSetAsDefaultLauncher`。
4. 被日志级别或进程切换漏掉。

如果 Snowball 漏斗以 `ACT_SuccessSetAsDefaultLauncher` 作为成功事件，而 App 实际不稳定发送，漏斗结论会不可信。

### P0：`CLK_SetAsDefault` 同时用于默认短信和默认桌面

本次两次点击都发送：

```text
CLK_SetAsDefault
```

无法区分用户点击的是：

- 设置默认短信
- 设置默认桌面

建议拆分：

- `CLK_SetDefaultSMS`
- `CLK_SetDefaultLauncher`

### P1：首启 `th_install_referrer` 重复发送

同一秒内连续发送 2 次：

```text
th_install_referrer
th_install_referrer
```

需要检查 install referrer 回调是否重复注册或 App/WeatherHome 两层都发送。

### P1：`ACT_EnterHomePage` 首启阶段重复发送

首启阶段短时间内重复发送 `ACT_EnterHomePage default_app => 0`，默认桌面成功后又发送 `default_app => 1`。

建议保留 `default_app` 参数，但增加去重策略或明确区分：

- `ACT_EnterLauncherHome`
- `ACT_EnterSMSHome`

### P1：广告事件缺少可读参数

实测广告事件均为空参数：

```text
th_ad_enter_scene
th_ad_impression
th_ad_close
```

如果日志层没有输出 scene/ad_format/placement，排查体验问题时很难定位具体广告场景。至少应确保 Snowball 入库参数包含：

- `scene`
- `ad_format`
- `mediation`
- `is_new_user`
- `trigger_source`

## 产品上手体验问题

### P0：默认短信完成后立即插屏，强烈建议禁止

默认短信成功后 2.4 秒出现全屏插屏。这个时机非常差：

1. 用户刚完成高成本系统授权。
2. 还没看到授权带来的产品价值。
3. 插屏内容与 Message/SMS 无关，破坏信任。
4. 会降低继续设置默认桌面和次日留存的概率。

建议策略：

- 新用户首日完成默认短信后的前 3 分钟禁止插屏。
- 完成默认短信后的第一次返回主界面禁止 AppOpen/Interstitial。
- 等用户至少完成一次核心行为后再开放插屏，例如：
  - 进入会话列表并停留 20 秒
  - 发送/打开一条短信
  - 进入 Home 并完成一次有效交互

### P0：两个系统默认权限连续出现，认知负担太高

当前路径：

```text
首屏设置默认短信
-> 系统默认短信弹窗
-> 插屏广告
-> 短信页
-> 右滑 Home 引导
-> 设置默认桌面
-> 系统默认桌面设置页
```

这对新用户太重。建议分阶段：

1. 首次只聚焦默认短信，让用户看到短信主功能。
2. 默认桌面改为 D0 后段或 D1 再引导。
3. 只有当用户主动右滑 Home 或点击 Home 功能时，再解释默认桌面的价值。

### P0：默认桌面引导文案错误

当前文案把 `home app`、`message app`、`spam protection` 混在一起。建议改为：

```text
Set Message Home as your home app
Access messages, weather, news, and search from your home screen.
```

不要用 `default message app` 描述默认桌面权限。

### P1：首屏价值解释不足

首屏主张是 `SMART. SIMPLE. PRIVATE`，但马上要求默认短信。建议首屏补充更具体价值：

- Block spam messages
- Organize conversations
- Search messages faster
- Read messages from your home screen

并在按钮下增加低成本解释：

```text
Required by Android to send and receive SMS in Message Home.
You can change it anytime in Settings.
```

### P1：默认短信成功后应先给正反馈

默认短信成功后不应直接广告。建议出现轻量成功页或 toast：

```text
You're all set.
Message Home can now protect and organize your SMS.
```

然后进入短信主界面，展示下一步：

- Importing messages
- Start a conversation
- Try spam protection

### P1：Home 引导时机应后置

在短信主页面立刻引导右滑 Home，会打断用户对 SMS 产品的理解。建议：

- 首次进入短信页不要强制遮罩。
- 在用户停留 15-30 秒后，以非强制卡片介绍 Home。
- 或者等用户点击 Home 入口/底部入口时再触发说明。

## 立即修复策略

### 1. 先修广告时机

规则建议：

```text
new_user && default_sms_just_succeeded => block interstitial/appopen for 3 minutes
new_user && first_session && core_onboarding_not_done => block interstitial
```

这是最优先，因为它直接影响信任和留存。

### 2. 统一默认短信事件

建议正式口径：

| 动作 | 事件 |
|---|---|
| 展示默认短信引导页 | `ACT_ShowDefaultSMSGuide` |
| 点击设置默认短信 | `CLK_SetDefaultSMS` |
| 打开系统默认短信弹窗 | `ACT_OpenDefaultSMSDialog` |
| 默认短信设置成功 | `ACT_SuccessSetDefaultSMS` |
| 默认短信设置失败/取消 | `ACT_FailSetDefaultSMS` |

短期至少确认 Snowball 漏斗用的是当前真实事件 `ACT_SuccessSetupMSGPlus`，不要用不存在或旧版本事件。

### 3. 统一默认桌面事件

建议正式口径：

| 动作 | 事件 |
|---|---|
| 展示默认桌面引导 | `ACT_ShowDefaultLauncherGuide` |
| 点击设置默认桌面 | `CLK_SetDefaultLauncher` |
| 进入系统默认桌面设置页 | `ACT_EnterSystemSelectLauncher` |
| 默认桌面设置成功 | `ACT_SuccessSetDefaultLauncher` |
| 默认桌面设置失败/取消 | `ACT_FailSetDefaultLauncher` |

短期需要修复或确认 `ACT_SuccessSetAsDefaultLauncher` 的实际发送。

### 4. 重排上手流程

推荐新流程：

```text
Welcome / SMS value
-> Set Default SMS
-> System SMS dialog
-> Success feedback
-> SMS main page / import messages
-> Non-blocking Home feature card
-> User主动点击或D1再引导 Set Default Home
```

不建议在同一首启会话连续强推默认短信、插屏、默认桌面。

### 5. 建立可验证漏斗

修复后在 Snowball 查以下漏斗：

1. 默认短信：

```text
first_open
-> ACT_ShowDefaultSMSGuide
-> CLK_SetDefaultSMS
-> ACT_OpenDefaultSMSDialog
-> ACT_SuccessSetDefaultSMS
```

2. 默认桌面：

```text
first_open
-> ACT_ShowDefaultLauncherGuide
-> CLK_SetDefaultLauncher
-> ACT_EnterSystemSelectLauncher
-> ACT_SuccessSetDefaultLauncher
```

3. 广告影响：

```text
ACT_SuccessSetDefaultSMS
-> th_ad_impression
-> ACT_EnterSMSMainPage / ACT_EnterHomePage
```

同时按是否首日新用户、是否默认短信成功、是否默认桌面成功分组看 D1 留存、广告 IPU、LTV。

## 结论

本次实机验证证明，MessageHome 当前首启事件链路和用户体验存在三个最关键问题：

1. 默认短信完成后立即插屏，严重破坏新用户信任。
2. 默认短信与默认桌面连续强推，且文案混乱，用户认知负担高。
3. 关键转化事件命名和实际发送不一致，Snowball 漏斗可能存在口径偏差。

马上应优先做两件事：

1. 新用户默认短信成功后的首会话禁插屏。
2. 统一并修复默认短信、默认桌面的成功事件，再重跑 Snowball 漏斗验证真实转化。
