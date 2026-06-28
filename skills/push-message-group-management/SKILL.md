---
name: Push消息组管理
description: 在 Snowball Push 推送管理系统的“消息库”中，执行消息组创建与消息新建。覆盖“新建消息组（如 test）”和“在目标组中新增 English 消息并应用”的稳定操作流程。适用于用户提到“消息组管理”“新建消息组”“新建消息”“English title/body 填写”“点击应用”等场景。
---

# Push消息组管理

## 目标

在 `https://snowball.thinkyeah.com/push/{project_id}/template` 页面稳定完成两件事：

1. 创建消息组（示例：`test`）。
2. 在目标消息组中点击“新增消息”，仅填写 English 的 `title` 和 `body`，然后点击“应用”。

## 前置条件

- 用户已登录 Snowball SSO（若未登录，先让用户在浏览器完成登录）。
- 可用 Playwright CLI 会话（推荐 `PLAYWRIGHT_CLI_SESSION=default`）。

## 标准执行流程（推荐）

1. 打开页面并抓取快照。
2. 在“消息组”区域点击“新增”。
3. 在弹窗中填写消息组名称，点击“确认”。
4. 找到目标组（如 `test`），点击右侧“新增消息”。
5. 在“默认-英语（en）”中填写：
   - 标题：`title`
   - 内容：`body`
6. 点击“应用”。
7. 再次抓快照，确认消息已出现在目标组中。

## 关键定位策略

- 以页面快照中的结构化 ref 为第一优先（例如 `click e346`）。
- 只在目标组上下文内操作，避免误点其他组（如 `daily_evening`）。
- 若“新增/新建消息”点击无效，先重新 `snapshot` 再点击。

## 稳定命令模板

```bash
export PLAYWRIGHT_CLI_SESSION=default
npx --yes --package @playwright/cli playwright-cli open https://snowball.thinkyeah.com/push/A170/template --headed
npx --yes --package @playwright/cli playwright-cli snapshot
```

```bash
# 示例：点 test 组右侧“新增消息”（ref 以当前 snapshot 为准）
npx --yes --package @playwright/cli playwright-cli click e346
npx --yes --package @playwright/cli playwright-cli fill e396 "Test  messge"
npx --yes --package @playwright/cli playwright-cli fill e400 "Test  mesage body"
npx --yes --package @playwright/cli playwright-cli click e419
```

## 实操沉淀（本次成功路径）

- 已创建消息组：`test`。
- 已在 `test` 组点击“新增消息”。
- 已填写 English：
  - `title`: `Test  messge`
  - `body`: `Test  mesage body`
- 已点击“应用”。

## 异常处理

- 弹窗未出现：
  - 重新 `snapshot`，确认 ref 变化后重试。
  - 必要时让用户手动点出弹窗，再由自动化接续填写。
- 点击命中但无响应：
  - 优先重新抓取 ref。
  - 再考虑 DOM 文本定位或系统级 GUI 辅助（仅作兜底）。
- 字段定位错位：
  - 以输入框语义名定位（`请输入标题` / `请输入内容`）替代旧 ref。

## 结果校验

- 目标组卡片下不再显示“尚无消息”。
- 可见新增消息卡片，且 English 标题与正文与输入一致。
