# Local News App Emulator Test Flow

## 目标

使用 Android Emulator 和 `adb` 对 `Local News` App 进行一轮可重复的自动化手工测试，覆盖以下内容：

- 启动模拟器并确认设备连接正常
- 启动 `Local News` App
- 捕获启动前后的截图、UI 层级和 `logcat`
- 复现启动后被全屏广告拦截的问题
- 验证按返回键后的落点
- 记录关键异常日志，便于后续排查

## 测试对象

- App 名称: `Local News`
- 包名: `news.local.voice.live.weather.daily.forecast`
- 启动 Activity: `com.weatherlocalnews.main.ui.activity.LandingActivity`
- 测试设备: `Pixel_9` Android Emulator
- 设备序列号: `emulator-5554`

## 前置条件

1. 本机已安装 Android SDK、`adb`、Android Emulator。
2. 本机存在 AVD:
   - `Pixel_9`
3. 模拟器内已安装目标 App。
4. 当前用户对 `adb` 与 Emulator 具备可执行权限。

## 标准测试流程

### 1. 启动模拟器

优先使用无快照启动，避免快照恢复导致模拟器离线或自动退出。

```bash
"$HOME/Library/Android/sdk/emulator/emulator" -avd Pixel_9 -no-snapshot-load
```

等待设备可用：

```bash
adb wait-for-device
adb devices -l
adb -s emulator-5554 shell getprop sys.boot_completed
```

通过标准：

- `adb devices -l` 中出现 `emulator-5554 device`
- `sys.boot_completed=1`

### 2. 确认基线状态

检查当前前台窗口：

```bash
adb -s emulator-5554 shell dumpsys window | rg 'mCurrentFocus|mFocusedApp'
```

期望基线状态：

- 当前前台为 Launcher
- 即 `com.google.android.apps.nexuslauncher`

### 3. 采集启动前基线证据

截图：

```bash
adb -s emulator-5554 shell screencap -p /sdcard/Download/emu-baseline.png
adb -s emulator-5554 pull /sdcard/Download/emu-baseline.png /tmp/emu-baseline.png
```

UI 层级：

```bash
adb -s emulator-5554 shell uiautomator dump /sdcard/Download/emu-baseline.xml
adb -s emulator-5554 pull /sdcard/Download/emu-baseline.xml /tmp/emu-baseline.xml
```

生成 UI 摘要：

```bash
python3 "/Users/suacker/.codex/plugins/cache/openai-curated/test-android-apps/f78e3ad49297672a905eb7afb6aa0cef34edc79e/skills/android-emulator-qa/scripts/ui_tree_summarize.py" /tmp/emu-baseline.xml /tmp/emu-baseline-summary.txt
```

导出基线日志：

```bash
adb -s emulator-5554 logcat -d -f /sdcard/Download/emu-baseline-logcat.txt
adb -s emulator-5554 pull /sdcard/Download/emu-baseline-logcat.txt /tmp/emu-baseline-logcat.txt
```

### 4. 识别目标 App

列出第三方安装包：

```bash
adb -s emulator-5554 shell pm list packages -3
```

本次结果：

```text
package:news.local.voice.live.weather.daily.forecast
```

解析启动 Activity：

```bash
adb -s emulator-5554 shell cmd package resolve-activity --brief news.local.voice.live.weather.daily.forecast
```

本次结果：

```text
news.local.voice.live.weather.daily.forecast/com.weatherlocalnews.main.ui.activity.LandingActivity
```

### 5. 清空日志并启动 App

清空日志：

```bash
adb -s emulator-5554 logcat -c
```

启动 App：

```bash
adb -s emulator-5554 shell am start -n news.local.voice.live.weather.daily.forecast/com.weatherlocalnews.main.ui.activity.LandingActivity
```

确认进程是否存活：

```bash
adb -s emulator-5554 shell pidof -s news.local.voice.live.weather.daily.forecast
```

本次首次启动结果：

- App 进程存在
- 首次 PID: `2301`

### 6. 采集启动后证据

检查前台窗口：

```bash
adb -s emulator-5554 shell dumpsys window | rg 'mCurrentFocus|mFocusedApp'
```

本次结果：

```text
mCurrentFocus=Window{... news.local.voice.live.weather.daily.forecast/com.vungle.ads.internal.ui.VungleActivity}
```

说明：

- App 启动后没有直接进入业务主页
- 前台被 `VungleActivity` 全屏广告页接管

导出启动后截图：

```bash
adb -s emulator-5554 shell screencap -p /sdcard/Download/emu-app.png
adb -s emulator-5554 pull /sdcard/Download/emu-app.png /tmp/emu-app.png
```

导出启动后 UI：

```bash
adb -s emulator-5554 shell uiautomator dump /sdcard/Download/emu-app.xml
adb -s emulator-5554 pull /sdcard/Download/emu-app.xml /tmp/emu-app.xml
```

导出启动后日志：

```bash
adb -s emulator-5554 logcat -d -f /sdcard/Download/emu-app-logcat.txt
adb -s emulator-5554 pull /sdcard/Download/emu-app-logcat.txt /tmp/emu-app-logcat.txt
```

检查日志中的关键字：

```bash
rg -n "AndroidRuntime|FATAL EXCEPTION|ANR|Vungle|Exception|crash|ads|ad" /tmp/emu-app-logcat.txt | head -120
```

### 7. 验证广告页能否退出

执行返回键：

```bash
adb -s emulator-5554 shell input keyevent 4
```

再次确认进程：

```bash
adb -s emulator-5554 shell pidof -s news.local.voice.live.weather.daily.forecast
```

本次结果：

- 返回键后 App 仍在运行
- PID 从 `2301` 变为 `7372`

再次采集状态：

```bash
adb -s emulator-5554 shell dumpsys window | rg 'mCurrentFocus|mFocusedApp'
adb -s emulator-5554 shell screencap -p /sdcard/Download/emu-after-back.png
adb -s emulator-5554 shell uiautomator dump /sdcard/Download/emu-after-back.xml
adb -s emulator-5554 logcat -d -f /sdcard/Download/emu-after-back-logcat.txt

adb -s emulator-5554 pull /sdcard/Download/emu-after-back.png /tmp/emu-after-back.png
adb -s emulator-5554 pull /sdcard/Download/emu-after-back.xml /tmp/emu-after-back.xml
adb -s emulator-5554 pull /sdcard/Download/emu-after-back-logcat.txt /tmp/emu-after-back-logcat.txt
```

本次结果：

- 前台回到了 Launcher
- 没有回到 `Local News` 的业务页面

### 8. 检查关键异常日志

建议重点检索：

```bash
rg -n "news\\.local\\.voice\\.live\\.weather\\.daily\\.forecast|VungleActivity|LandingActivity|ActivityTaskManager|Force finishing|ANR|FATAL EXCEPTION|ForegroundServiceStartNotAllowedException" /tmp/emu-after-back-logcat.txt | tail -120
```

本次观察到的关键日志：

```text
ForegroundServiceStartNotAllowedException: startForegroundService() not allowed due to mAllowStartForeground false: service news.local.voice.live.weather.daily.forecast/com.weatherlocalnews.main.service.ToolbarService
```

## 本次复现结论

本轮测试中，`Local News` 在模拟器上的启动路径存在以下现象：

1. App 启动后立即进入 `com.vungle.ads.internal.ui.VungleActivity`。
2. 启动后截图显示为全屏广告页。
3. UI dump 中没有识别到明确的关闭按钮，仅有全屏 `WebView`。
4. 按返回键后，前台直接退回 Launcher，而不是回到 App 主内容页。
5. 日志中未发现首次启动即崩溃的 `FATAL EXCEPTION`，但后续出现 `ForegroundServiceStartNotAllowedException`。

## 建议的自动化判定标准

可将以下规则作为回归检查项：

- 启动后 5 秒内，前台 Activity 不应停留在广告 SDK Activity
- 启动后应进入 App 自身页面，而不是停留在全屏广告页
- 返回键应回到 App 主内容页或上一级业务页，而不是直接退出到 Launcher
- 日志中不应出现以下关键异常：
  - `FATAL EXCEPTION`
  - `ANR`
  - `ForegroundServiceStartNotAllowedException`

## 产物文件

本次测试生成的证据文件：

- `/tmp/emu-baseline.png`
- `/tmp/emu-baseline.xml`
- `/tmp/emu-baseline-summary.txt`
- `/tmp/emu-baseline-logcat.txt`
- `/tmp/emu-app.png`
- `/tmp/emu-app.xml`
- `/tmp/emu-app-logcat.txt`
- `/tmp/emu-after-back.png`
- `/tmp/emu-after-back.xml`
- `/tmp/emu-after-back-summary.txt`
- `/tmp/emu-after-back-logcat.txt`

## 后续可扩展项

如果后续要把这份流程升级为真正的自动化脚本，建议继续补充：

- 启动后等待与超时逻辑
- 基于 UI dump 自动寻找关闭广告按钮
- 多次重试与稳定性统计
- 关键 Activity 切换的时间线记录
- 日志关键字自动判定与失败退出码
