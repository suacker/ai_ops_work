---
name: 事件漏斗自动化查询
description: 在 Snowball 事件分析中自动创建/配置漏斗并查询转化率。支持以 first_open 为起点，查询默认桌面完成、默认短信完成、进入主界面等关键事件转化。适用于“查漏斗”“点开始分析”“按事件重跑转化率”等场景。
---

# 事件漏斗自动化查询

## 目标

在 `Snowball -> 事件分析 -> 漏斗分析` 中，稳定执行：

1. 选择第1步事件（默认 `first_open`）。
2. 选择第2步目标事件（如 `ACT_EnterHomePage`、`ACT_SuccessSetAsDefaultLauncher`、`ACT_SetDefaultSuccess`）。
3. 点击“开始分析”。
4. 等待结果图表和表格加载完成。
5. 读取整体转化率、分日转化率、第1步人数、第2步人数。

## 前置条件

- 用户已登录 Snowball（若 SSO 失效，先让用户在当前浏览器完成登录）。
- 推荐使用同一个已打开的 Chrome 窗口，不要用 `playwright-cli open` 新建独立自动化窗口。
- 若从终端启动 Chrome，必须开启 CDP 调试端口，后续通过 `connectOverCDP` 附着同一窗口：
  - `--remote-debugging-port=9222`
- 可选固定 profile：
  - `/Users/suacker/dev/DataAnalysis/BI/.chrome-profile-codex`

## 标准执行流程

1. 进入 `事件分析` 页面（项目级）。
2. 左侧菜单点 `漏斗分析`，若无报告先点 `创建漏斗`。
3. 第1步（上方第一个“请选择事件”）选择 `first_open`。
4. 第2步（下方第二个“请选择事件”）选择目标事件。
5. 点击 `开始分析`。
6. 点击后等待结果图表和表格加载完成，再读取：
   - 整体转化率（总计）
   - 分日转化率（最近7天）
   - 第1步人数（新增用户数 / `first_open`）
   - 第2步人数（目标事件完成人数）
   - 分子分母（如 `570 -> 13`）

## 推荐事件映射（MessageHome / A182）

- 进主界面：`ACT_EnterHomePage`
- 默认桌面完成：`ACT_SuccessSetAsDefaultLauncher`
- 默认短信完成：`ACT_SetDefaultSuccess`

## 稳定命令模板（推荐）

```bash
'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --user-data-dir='/Users/suacker/dev/DataAnalysis/BI/.chrome-profile-codex' \
  --remote-debugging-port=9222 \
  'https://snowball.thinkyeah.com/event/A182/analysis/funnel_analysis/create'
```

后续不要再调用 `playwright-cli open`；改用 Node + Playwright CDP 附着到同一窗口：

```bash
NODE_PATH='/Users/suacker/.npm/_npx/e41f203b7505f1fb/node_modules' node -e '
(async () => {
  const { chromium } = require("playwright");
  const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
  const page = browser.contexts()[0].pages()[0];
  console.log(await page.title());
  await browser.close();
})();
'
```

## 查询口径约定

- 默认起点事件固定为 `first_open`。
- 日期范围默认页面值（常见：最近7天）。
- 如用户指定日期或国家维度，先在筛选区修改后再点“开始分析”。
- 选择事件必须按从上到下顺序：
  - 第1个下拉：`first_open`
  - 第2个下拉：目标事件（例如 `ACT_SuccessSetAsDefaultLauncher`）

## 自动化实现要点

### 1. 附着当前 Chrome，而不是新开窗口

```js
const { chromium } = require("playwright");
const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
const page = context.pages()[0] || await context.newPage();
await page.bringToFront();
```

### 2. 页面就绪判断

不要只判断 URL。必须等 `document.body.innerText` 同时包含：

- `请选择事件`
- `开始分析`

如果只看到顶栏或左侧菜单，说明漏斗主体还未加载，继续等待或让用户刷新。

### 3. 事件选择顺序

```js
const dropdowns = page.locator("div").filter({ hasText: /^请选择事件$/ });

// 第1步：first_open
await dropdowns.nth(0).click();
let search = page.getByRole("textbox", { name: "搜索" });
await search.nth((await search.count()) - 1).fill("first_open");
await page.getByText("first_open (first_open)", { exact: true }).click();

// 第2步：目标事件
await dropdowns.nth(1).click();
search = page.getByRole("textbox", { name: "搜索" });
await search.nth((await search.count()) - 1).fill("ACT_SuccessSetAsDefaultLauncher");
await page.getByText("ACT_SuccessSetAsDefaultLauncher (ACT_SuccessSetAsDefaultLauncher)", { exact: true }).click();
```

### 4. 查询后等待

点击 `开始分析` 后至少等待 10-12 秒，直到结果区出现：

- `漏斗分析图表`
- `整体转化率`
- `总计`
- 目标事件名

### 5. 结果表读取方式

Snowball 的结果表文本结构不是标准 HTML `tr`，不要依赖 `querySelectorAll("tr")`。

已验证的读取逻辑：

1. 从 `document.body.innerText` 中定位 `漏斗分析图表` 后的文本块。
2. 先按顺序提取日期和转化率：
   - `总计`
   - `2026-xx-xx`
3. 再从人数区按相同顺序每 3 个值解析：
   - 第1步人数（新增用户数 / `first_open`）
   - 第2步人数（目标事件人数）
   - 转化率

示例解析输出字段：

```json
{
  "date": "2026-05-31",
  "conversion": "1.35%",
  "newUsers": "148",
  "completed": "2",
  "completionRate": "1.35%"
}
```

## MessageHome 默认桌面查询示例

漏斗：`first_open -> ACT_SuccessSetAsDefaultLauncher`

最近一次成功读取结果：

| 日期 | 新增用户数 first_open | 默认桌面完成数 | 转化率 |
|---|---:|---:|---:|
| 总计 | 570 | 13 | 2.28% |
| 2026-05-31 | 148 | 2 | 1.35% |
| 2026-05-30 | 125 | 5 | 4.00% |
| 2026-05-29 | 112 | 4 | 3.57% |
| 2026-05-28 | 66 | 1 | 1.52% |
| 2026-05-27 | 101 | 0 | 0.00% |
| 2026-05-26 | 13 | 0 | 0.00% |
| 2026-05-25 | 5 | 1 | 20.00% |

## 异常处理

- 跳转 `not_found`：
  - 点击“返回首页”，再从顶部 `事件分析` 进入，不直接硬跳失效地址。
- 会话丢失到登录页：
  - 让用户在当前浏览器登录一次后继续。
- 事件同名/相近名：
  - 必须在事件下拉中精确核对英文事件名后再选（如 `first_open` 与 `th_first_open`）。
- `NOT_READY`：
  - 如果 URL 正确但主体区不可见，先等待 10 秒，再读取 `document.body.innerText`。
  - 若仍不可见，要求用户刷新到能看到“请选择事件”和“开始分析”的状态，再继续附着同一窗口。
- 结果为 `null`：
  - 通常是点击后读取过早。必须等待结果表出现再读。
  - 不要只读图表；以表格文本为准输出每日新增用户数和目标完成人数。

## 结果输出规范

输出至少包含：

1. 漏斗定义（第1步/第2步事件名）
2. 总体转化率 + 分子/分母
3. 分日转化率表（日期、新增用户数、目标完成人数、百分比）
4. 异常说明（如样本量过小导致 100%）
