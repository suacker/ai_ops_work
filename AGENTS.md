# AGENTS.md - BI 增长运营知识库执行规范

> 本文件是 `/Users/suacker/dev/DataAnalysis/BI` 的目录级工作指南，面向 Codex/Claude/其他 AI 编码与分析助手。
> 文档语言默认中文。除非用户明确要求，报告、结论、动作建议、提交说明都使用中文。

---

## 1. 项目定位

这是一个数据驱动的 BI 增长运营知识库，主要服务移动应用的买量、变现、漏斗、留存和运营分析。

本仓库不是传统软件项目。它通常没有统一构建系统、包管理器或测试套件，核心产物是：

- Markdown 分析报告。
- HTML 可视化报告。
- `skills/*/SKILL.md` 中沉淀的可复用分析工作流。
- `config/` 中的项目、账号和动作规则索引。
- `ops_system/`、`scripts/` 中的局部生成器或查询辅助脚本。

核心工作流：

```text
真实数据源/MCP/API -> 口径校验 -> 分析判断 -> Markdown 报告 -> HTML 报告 -> P0/P1/P2 动作建议
```

优先目标不是展示数据，而是形成可执行决策：放量、观察、降量、暂停候选、素材刷新、归因修复或继续验证。

---

## 2. 目录地图

| 路径 | 用途 | 使用规则 |
| --- | --- | --- |
| `AGENTS.md` | 本文件，目录级最高优先级规则 | 开始本目录任务先读 |
| `CLAUDE.md` | 早期项目速览 | 若与本文件冲突，以本文件为准 |
| `config/project_registry.md` | Snowball 项目索引 | 先查项目 ID、产品名、变现类型 |
| `config/ad_account_registry.md` | 投放账号映射 | Meta/Google 分析前先查 |
| `config/action_rules.md` | 动作分级与禁止写操作 | 预算/素材建议必须符合 |
| `grow_base/` | 国家级买量阈值基线 | 阈值唯一来源 |
| `monitor_report/grow/` | 近 5 天增长监控报告 | 产出 `.md` + `.html` |
| `reports/` | 专项分析报告 | 按主题建子目录 |
| `reports/event_funnel/` | Snowball 漏斗报告 | 保存 MD/HTML，记录采样行处理 |
| `reports/ad_monetization/` | 广告变现异常报告 | 保存 MD/HTML |
| `reports/ops_daily/` | 多项目运营日报 | 可复用 `ops_system/` |
| `skills/` | 本目录分析技能 | 命中任务时先读对应 `SKILL.md` |
| `specs/` | BI/UX/报表规格 | 做报告体系或页面规范时读取 |
| `scripts/` | GA4、广告变现等脚本 | 先读脚本再运行，避免误用 |
| `ops_system/` | 运营报告原型系统 | 有代码改动时按普通工程方式验证 |
| `output/` | 截图、Playwright 输出等 | 生成物归档 |
| `chat_history/` | 历史沟通归档 | 用户要求归档时写完整文件 |

---

## 3. 数据源优先级

### 3.1 Snowball MCP 是 BI 定量结论主数据源

涉及以下内容时优先使用 `mcp__snowball_mcp`：

- ROI / ROAS / CPI / 成本 / cohort revenue / cohort profit。
- 国家、network、campaign、adgroup 维度回收。
- 广告变现、eCPM、IPU、广告格式、广告场景。
- 留存、事件、漏斗、用户行为。
- 项目 ID 解析。

禁止：

- 编造或估算数据。
- 用旧报告、本地缓存或记忆替代实时查询。
- 将 `-1`、null、N/A 当作 0。
- 数据缺失时用均值填补。

### 3.2 平台 API/CLI 用于投放侧上下文

Meta / Facebook、Google Ads 等平台数据用于补充：

- account / campaign / adset / ad / creative / asset 状态。
- spend、impressions、clicks、CTR、CPC、CPM、frequency。
- installs / conversions / platform ROAS。
- 素材名称、creative id、asset group、预算和状态。

平台数据不能单独决定强预算动作。预算和素材动作必须结合 Snowball 回收质量。

### 3.3 MCP 和 API 安装/连接类任务

本机 Codex MCP 配置通常在：

```text
/Users/suacker/.codex/config.toml
```

安装或修改 MCP 后必须验证：

1. `codex mcp list` 或 `codex mcp get <name>` 能看到配置。
2. 能完成真实 `initialize` / `tools/list` 或等价 API 检查。
3. 若 UI 当前会话未热加载新 MCP，说明需要新 Codex 会话，不要误判安装失败。

若 MCP 握手失败但 REST API 可用，允许基于同一凭证走 REST fallback，并在报告中注明。

---

## 4. 默认日期窗口

| 场景 | 默认窗口 | 规则 |
| --- | --- | --- |
| 日常增长监控 | `today-5` ~ `today-1` | 近 5 个完整自然日，不含当天 |
| Campaign / 预算 / 素材诊断 | `today-7` ~ `today-1` | 近 7 个完整自然日，不含当天 |
| 周报 | 上一完整 ISO 周 | 周一到周日 |
| 广告变现异常 | `today-30` ~ `today-1`，必要时扩展 60 天 | 不含当天 |
| 阈值计算 | 近 60-90 天 install cohort | 找历史达标样本日 |
| 事件漏斗 | 用户指定优先；否则近完整自然日 | 避免包含采样当天 |

必须在报告中写绝对日期，例如 `2026-06-20 ~ 2026-06-26`。不要只写“最近 7 天”。

---

## 5. 报告硬约束

### 5.1 双格式输出

用户要求报告、分析沉淀、工作流验证时，默认同时产出：

- Markdown：真值来源，可读、可审阅。
- HTML：可视化交付，与 Markdown 数值一致。

除非用户明确只要聊天结论，不要只在对话里输出。

### 5.2 每份分析报告至少包含

1. 标题、项目、绝对日期范围。
2. 数据源与查询口径。
3. 总体结论，控制在 5 行以内。
4. 核心 KPI 或主判断表。
5. 维度下钻表，至少包含国家、network、campaign、adgroup 或素材中与问题相关的层级。
6. 异常与风险定位。
7. P0/P1/P2 动作建议。
8. 方法与置信度说明。
9. HTML 页脚：`Generated from {Markdown 绝对路径}`。

### 5.3 数值展示

| 指标 | 格式 |
| --- | --- |
| ROI / ROAS / 留存 / 转化率 | 百分比，例如 `42.36%` |
| CPI / CPA | 美元，通常 2-4 位小数，按报告精度统一 |
| eCPM | 美元，2 位小数 |
| 花费 / 收入 / 利润 | 美元，2 位小数 |
| 样本不足 | 写 `样本不足` 或 `低置信度` |
| 缺失 | 写 `数据缺失`，不得隐藏 |

Markdown 和 HTML 必须从同一组中间数据生成，不要手动分别改数。

---

## 6. 阈值与状态规则

### 6.1 阈值唯一来源

国家级 ROI0、CPI、次留、eCPM 阈值只能来自：

```text
grow_base/{project_id}_{ProjectName}.md
```

禁止根据当前数据临时推算阈值。若缺少阈值：

- 明确写 `阈值缺失`。
- 可使用账户均值做相对诊断，但必须标为 `低置信度/相对基准`。
- 若用户要求更新阈值，必须执行 `ua-threshold-metrics` 方法论后再更新 `grow_base/`。

### 6.2 风险分层

国家级增长监控默认使用三项：

- ROI0 是否达标。
- CPI 是否达标。
- 次留是否达标。

| 状态 | 定义 |
| --- | --- |
| 健康 | 三项均达标 |
| 中风险 | 恰好一项不达标 |
| 高风险 | 两项或以上不达标 |

### 6.3 动作分级

预算、素材、国家、Campaign 动作必须遵循 `config/action_rules.md`：

- `ready`：可给 P0/P1/P2 明确动作。
- `partial`：只能给 P1/P2 或中低置信度建议。
- `blocked`：只能给数据修复建议。
- `inactive_no_data`：只能给 `no_action_no_data`。

默认只读分析。禁止直接执行 `pause_ad`、`set_budget`、`create_ad`、`delete_ad`、`update_bid` 等平台写操作，除非用户明确授权并再次确认具体对象。

---

## 7. Skill 选择方法

开始任务时先判断是否命中 `skills/*/SKILL.md`。命中后必须先读完整 `SKILL.md`，再执行。

| 任务 | 首选 Skill |
| --- | --- |
| 近 5 天国家增长监控 | `skills/grow-monitor-report/SKILL.md` |
| 买量阈值、国家红线 | `skills/ua-threshold-metrics/SKILL.md` |
| Campaign 生命周期、是否放量/观察/衰退 | `skills/snowball-campaign-lifecycle-diagnosis/SKILL.md` |
| 预算迁移、加预算/降预算/暂停候选 | `skills/ua-budget-reallocation-diagnosis/SKILL.md` |
| 归因、平台与 Snowball 对账 | `skills/ads-attribution-data-quality-check/SKILL.md` |
| Meta 素材疲劳、creative keep/scale/pause | `skills/meta-creative-fatigue-diagnosis/SKILL.md` |
| 素材测试矩阵、winner 变体扩展 | `skills/creative-testing-and-scaling-playbook/SKILL.md` |
| Meta Advantage+ App Campaign | `skills/meta-advantage-app-campaign-diagnosis/SKILL.md` |
| Google App Campaign / PMax asset | `skills/google-app-campaign-asset-diagnosis/SKILL.md` |
| 国家放量优先级 | `skills/country-scaling-priority-diagnosis/SKILL.md` |
| 买量用户质量、安装后行为 | `skills/post-install-quality-diagnosis/SKILL.md` |
| 广告变现异常、eCPM/IPU/场景 | `skills/ad-monetization-anomaly-report/SKILL.md` |
| Snowball 事件漏斗页面自动化 | `skills/event-funnel-automation/SKILL.md` |
| Snowball Push 消息组 | `skills/push-message-group-management/SKILL.md` |

Meta/Facebook 买量决策推荐链路：

```text
ads-attribution-data-quality-check
-> snowball-campaign-lifecycle-diagnosis
-> ua-budget-reallocation-diagnosis
-> meta-creative-fatigue-diagnosis
-> creative-testing-and-scaling-playbook
```

---

## 8. Snowball MCP 工作方法

### 8.1 项目解析

用户只给项目名时，先调用：

```text
mcp__snowball_mcp.list_projects(project_name=..., use_cache=false)
```

只基于工具返回的 `project_id`、项目名、平台、包名继续分析。

### 8.2 ROI/Campaign 查询

典型查询：

```text
mcp__snowball_mcp.view_roi_report(
  project_id="A155",
  date_start="YYYY-MM-DD",
  date_end="YYYY-MM-DD",
  day_period="daily",
  dimension_list=["date", "network", "country", "campaign"],
  network_list=["facebook"],
  roi_fields=["roi_0", "roi_1", "roi_3", "roi_7"],
  is_forecast=1
)
```

需要 adgroup 时使用：

```text
dimension_list=["date", "network", "campaign", "adgroup"]
```

注意：

- ROI7 若是预测值，必须标注。
- weekly 汇总可能按周开始日拆成两段；若用户指定精确日期窗口，要合并同一 campaign/adgroup 的两个周段，并说明计算口径。
- `date=-1` 是总计行，不是实际日期。

### 8.3 漏斗查询

事件漏斗可能先返回 `confirmation_required`，包含扫描量和估算费用。处理方式：

1. 将 `processed_gb`、`estimated_cost_usd`、确认 token 等信息告知用户。
2. 等用户确认后再执行。
3. 若返回当前日采样行且标记 `exampling=true`，完整自然日报告必须排除该行。
4. 报告保存到 `reports/event_funnel/`，文件名包含项目、事件路径和日期范围。

### 8.4 广告变现查询

广告变现异常分析必须拆：

- 日期。
- 广告格式：Interstitial、AppOpen、RewardedVideo、Banner、Native。
- 广告场景：优先高收入场景。
- DNU/DAU、impressions、ads_revenue、eCPM、IPU、CTR。

收入变化不要只归因于 eCPM。必须同时检查新增、活跃、展示机会、IPU 和广告格式结构。

---

## 9. Meta/Facebook 买量分析规范

### 9.1 账号映射

先读：

```text
config/ad_account_registry.md
```

当前已知：

| Project | Account | ID |
| --- | --- | --- |
| A155 StepTracker | Step Tracker 01 | `act_959455393396016` |
| A155 StepTracker | Step Tracker 02 | `act_1302740031791808` |

若任务发生在 Grow 工作区，也可参考：

```text
/Users/suacker/dev/DataAnalysis/Grow/config/product-ad-accounts.md
```

### 9.2 CLI 使用

Meta CLI 标准调用把全局参数放在顶层：

```bash
meta --ad-account-id act_959455393396016 --output json ads campaign list --limit 80
meta --ad-account-id act_959455393396016 --output json ads adset list --limit 120
meta --ad-account-id act_959455393396016 --output json ads ad list --limit 200
meta --ad-account-id act_959455393396016 --output json ads insights get \
  --since 2026-06-20 --until 2026-06-26 \
  --fields spend,impressions,reach,frequency,clicks,ctr,cpc,cpm,actions
```

如果当前 CLI 版本使用环境变量，也可：

```bash
AD_ACCOUNT_ID=act_959455393396016 meta --output json ads campaign list --limit 80
```

不要把 `--ad-account-id`、`--output json` 放到子命令后面；历史上这会失败。

### 9.3 分析顺序

1. 先做平台与 Snowball 对账：spend、install、campaign 映射。
2. 再看账户层：spend、install、CPI、CTR、CPM、placement mix。
3. 再看 campaign/adgroup：Snowball ROI0/ROI3/ROI7、CPI、profit。
4. 再看 active 或高花费 ad/adset/creative，不要一次拉全量历史素材。
5. 最后给动作：scale、small_add、maintain、reduce_or_reallocate、pause_candidate、make_variants。

### 9.4 素材决策规则

Meta 素材判断必须同时看：

- ad spend。
- installs/conversions。
- CPI/CPA。
- CTR、CPC、CPM。
- frequency。
- Snowball parent campaign/adgroup ROI 和留存。

Snowball 当前通常不到 creative 级 ROI。因此 creative ROI 必须写成：

```text
基于所属 campaign/adgroup 回收质量推断
```

不要写成直接 creative ROI。

高 CTR 低 ROI 是劣质流量或素材承诺错配的风险信号，不能作为放量依据。

fresh low-spend 新素材必须标为 `too early to judge`，不要提前判 winner/loser。

### 9.5 StepTracker 历史沉淀

历史分析只作为方法参考，实时任务必须重新拉数。

已验证的稳定经验：

- StepTracker 01 通常是主放量账号，StepTracker 02 更像测试/降量账号。
- 判断必须 gate by Snowball recovery，不要只看 CTR。
- `step en 01.mp4` 曾是明确 winner；后续要继续验证实时数据。
- winner 后续动作是做 hook、first frame、CTA/subtitle 变体，不是盲目复制。

---

## 10. Google Ads / Google App Campaign

若用户询问 Google Ads API/MCP：

- 优先使用官方 Google Ads MCP 或官方文档。
- 该 MCP 是偏只读分析用途，常见工具为 `list_accessible_customers`、`search`、`get_resource_metadata`。
- 本机历史可运行形态：

```bash
pipx run --spec git+https://github.com/googleads/google-ads-mcp.git google-ads-mcp
```

常见环境变量：

```text
GOOGLE_PROJECT_ID
GOOGLE_ADS_DEVELOPER_TOKEN
GOOGLE_ADS_LOGIN_CUSTOMER_ID
```

Google App Campaign / PMax 资产分析先读 `skills/google-app-campaign-asset-diagnosis/SKILL.md`，并用 Snowball ROI 校验真实回收。

---

## 11. Playwright / Chrome 自动化

### 11.1 Snowball Push

使用 `skills/push-message-group-management/SKILL.md`。

```bash
export PLAYWRIGHT_CLI_SESSION=default
npx --yes --package @playwright/cli playwright-cli open \
  https://snowball.thinkyeah.com/push/{project_id}/template --headed
npx --yes --package @playwright/cli playwright-cli snapshot
```

定位优先级：

1. 最新 snapshot 的结构化 ref。
2. 目标组上下文内按钮。
3. 语义输入框，如 `请输入标题`、`请输入内容`。

### 11.2 Snowball 事件漏斗页面

推荐复用已登录 Chrome，而不是反复新开窗口：

```bash
'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --user-data-dir='/Users/suacker/dev/DataAnalysis/BI/.chrome-profile-codex' \
  --remote-debugging-port=9222 \
  'https://snowball.thinkyeah.com/event/{project_id}/analysis/funnel_analysis/create'
```

后续用 Playwright CDP 附着：

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

若 Snowball 页面主体未加载，只看 URL 不够；必须确认页面文本包含目标功能区。

---

## 12. 支持、归档与外部服务分析

本目录也承载一些工具型任务：

- 聊天记录归档：写到 `chat_history/`，尽量完整，不要只摘要。
- Stripe MCP：配置后用 `codex mcp`、REST 和 stdio 三层验证。
- Freshdesk：若 MCP 初始化失败但 REST 可用，直接走 REST fallback，并输出表格化问题分类。

支持类分析要给结构化表格，至少包含：

- 产品/账号/时间范围。
- 总量、有效样本、噪声样本。
- 问题分类。
- 代表性用户问题。
- 下一步处理建议。

---

## 13. HTML 报告设计

通用视觉变量：

```css
:root {
  --bg: #f4f6f8;
  --card: #ffffff;
  --ink: #14212b;
  --muted: #5c6b78;
  --line: #d8e0e7;
  --brand: #1f6f8b;
  --good: #1f8a5b;
  --warn: #b86d00;
  --bad: #b42318;
}
```

状态样式：

- 健康：绿字、浅绿底、绿边框。
- 中风险：黄字、浅黄底、黄边框。
- 高风险：红字、浅红底、红边框。

HTML 验证要求：

- 与 Markdown 数值一致。
- 页脚包含 Markdown 绝对路径。
- 表格可横向滚动或响应式展示。
- 不要让文本重叠或溢出。
- KPI 卡、主表、动作建议要能在第一屏附近快速扫读。

---

## 14. 文件命名

| 报告类型 | 命名 |
| --- | --- |
| 阈值基线 | `grow_base/{ID}_{Name}.md` |
| 5 天监控 | `monitor_report/grow/{ProjectName}_{MMDD}.{md,html}` |
| 周报 | `reports/{family}/{ID}_{Name}_{YYYY-Www}.md` |
| 事件漏斗 | `reports/event_funnel/{ID}_{Project}_{event1}_to_{event2}_{date_start}_{date_end}.{md,html}` |
| 广告变现异常 | `reports/ad_monetization/{ID}_{Project}_ads_anomaly_{date_start}_{date_end}.{md,html}` |
| Campaign 生命周期 | `reports/snowball-campaign-lifecycle-diagnosis/{ID}_{Project}_{date_start}_{date_end}.{md,html}` |
| 临时数据 | `reports/{family}/data/` 或 `output/` |

文件名尽量用 ASCII、项目 ID、项目名和绝对日期，避免只写“最新”“本周”。

---

## 15. Git 与工作区安全

- 默认工作分支通常是 `master`，PR 目标通常是 `main`。
- 本仓库可能长期存在大量未跟踪报告、Chrome profile、输出文件。
- 不要清理、重置或删除用户已有变更。
- 修改前先读目标文件。
- 手工编辑文件使用 `apply_patch`。
- 报告类提交信息描述分析内容，例如 `update StepTracker creative diagnosis`。

---

## 16. 执行检查清单

开始前：

- [ ] 是否读了本文件和相关 `skills/*/SKILL.md`？
- [ ] 是否确认项目 ID、账号映射、日期范围？
- [ ] 是否不含当天，或明确说明包含当天的低置信度？
- [ ] 是否先做平台/Snowball 数据对账？

分析中：

- [ ] 定量数据是否来自 live MCP/API？
- [ ] 是否处理了 `-1`、null、N/A、forecast、sampled current-day？
- [ ] 是否拆到国家、network、campaign/adgroup 或素材等必要层级？
- [ ] 是否避免只看全局均值或 CTR？

产出前：

- [ ] 是否给出 P0/P1/P2 或 action taxonomy？
- [ ] 是否标注置信度和不能判断的范围？
- [ ] Markdown 和 HTML 数值是否一致？
- [ ] HTML 是否包含 `Generated from {absolute md path}`？
- [ ] 是否保存到规范目录？

---

## 17. 已知失败模式

| 失败模式 | 正确处理 |
| --- | --- |
| Snowball funnel 返回 `confirmation_required` | 展示扫描量和费用，等用户确认后重跑 |
| Snowball 返回 `exampling=true` 当前日 | 完整自然日报告排除该行 |
| Meta CLI 参数放在子命令后失败 | 把 `--ad-account-id`、`--output json` 放顶层 |
| 全量 creative/ad list 输出过大 | 先 campaign/adset 摘要，再按关键 ID 定点查 |
| Snowball 无 creative 级 ROI | 用 parent campaign/adgroup ROI 推断并注明 |
| MCP 配好但 UI 没工具 | 用 direct JSON-RPC 验证，并提示可能需要新会话 |
| Freshdesk MCP 403 | 尽快 REST fallback，不重复空转 |
| 数据质量 `blocked` | 不给预算/暂停/放量强建议，只给修复动作 |

---

## 18. 快速命令参考

Meta 账号列表：

```bash
meta --output json ads adaccount list --limit 50
```

Meta 单账号 campaign：

```bash
meta --ad-account-id act_959455393396016 --output json ads campaign list --limit 80
```

Meta 单账号 insights：

```bash
meta --ad-account-id act_959455393396016 --output json ads insights get \
  --since YYYY-MM-DD --until YYYY-MM-DD \
  --fields spend,impressions,reach,frequency,clicks,ctr,cpc,cpm,actions \
  --limit 50
```

Skill 市场发现与安装经验：

```bash
npx skills find "facebook ads"
npx skills add <repo> -g -a '*' -s <skill> -y --full-depth
```

注意：若 Codex 需要识别新 skill，可能还要复制到 `~/.codex/skills` 或重启会话。

---

*文档版本：v2.0*
*更新日期：2026-06-28*
*来源：现有 `AGENTS.md` / `CLAUDE.md`、本目录 `skills/` / `config/`、以及历史会话中已验证的 Snowball MCP、Meta CLI、Google Ads MCP、MCP 安装与报告交付流程。*
