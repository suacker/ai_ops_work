#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = "/Users/suacker/dev/DataAnalysis/BI";
const OUT_DIR = path.join(ROOT, "reports/ad_monetization");
const DATE_START = "2026-05-13";
const DATE_END = "2026-06-11";
const EXT_START = "2026-04-13";
const EXT_END = "2026-06-11";
const MCP_URL = "https://snowball-ai-api.thinkyeah.com/mcp";

const SEARCHES = [
  { family: "Message", query: "Message" },
  { family: "Photo", query: "Photo" },
  { family: "Weather", query: "Weather" },
  { family: "News", query: "News" },
];

const METRICS = ["ads_revenue", "impressions", "ecpm", "dau", "dnu", "ipu", "ctr"];
const FORMAT_METRICS = ["ipu", "ecpm", "ads_revenue", "impressions", "dnu", "dau"];

function readToken() {
  const config = fs.readFileSync(path.join(process.env.HOME, ".codex/config.toml"), "utf8");
  const match = config.match(/Authorization = "Bearer ([^"]+)"/);
  if (!match) throw new Error("SnowBall MCP bearer token not found in Codex config.");
  return match[1];
}

let sessionId = null;
let rpcId = 1;

async function rpc(method, params = {}) {
  const token = readToken();
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
    Accept: "application/json, text/event-stream",
  };
  if (sessionId) headers["Mcp-Session-Id"] = sessionId;
  const response = await fetch(MCP_URL, {
    method: "POST",
    headers,
    body: JSON.stringify({ jsonrpc: "2.0", id: rpcId++, method, params }),
  });
  sessionId = response.headers.get("mcp-session-id") || sessionId;
  const text = await response.text();
  const lines = text.split(/\r?\n/).filter((line) => line.startsWith("data: "));
  if (!lines.length) throw new Error(`Bad MCP response for ${method}: ${text.slice(0, 400)}`);
  const payload = JSON.parse(lines[lines.length - 1].slice(6));
  if (payload.error) throw new Error(`${method} failed: ${JSON.stringify(payload.error)}`);
  return payload.result;
}

async function callTool(name, args) {
  const result = await rpc("tools/call", { name, arguments: args });
  const text = result.content?.[0]?.text;
  if (!text) throw new Error(`Tool ${name} returned no text content.`);
  const parsed = JSON.parse(text);
  if (!parsed.ok) throw new Error(`Tool ${name} failed: ${text.slice(0, 500)}`);
  return parsed.data;
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function sum(values) {
  return values.reduce((acc, value) => acc + (Number.isFinite(value) && value >= 0 ? value : 0), 0);
}

function avg(values) {
  const valid = values.filter((value) => Number.isFinite(value) && value !== -1);
  return valid.length ? sum(valid) / valid.length : null;
}

function pct(after, before) {
  if (!Number.isFinite(after) || !Number.isFinite(before) || before === 0) return null;
  return (after / before - 1) * 100;
}

function money(value, digits = 2) {
  if (!Number.isFinite(value)) return "数据缺失";
  return `$${value.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits })}`;
}

function intFmt(value) {
  if (!Number.isFinite(value)) return "数据缺失";
  return Math.round(value).toLocaleString("en-US");
}

function pctFmt(value) {
  if (!Number.isFinite(value)) return "数据缺失";
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function pctShare(value) {
  if (!Number.isFinite(value)) return "数据缺失";
  return `${value.toFixed(2)}%`;
}

function numFmt(value, digits = 2) {
  if (!Number.isFinite(value)) return "数据缺失";
  return value.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

function slugName(name) {
  return name.replace(/[^A-Za-z0-9]+/g, "").slice(0, 42) || "Project";
}

function riskLabel(summary) {
  if (!summary.hasData) return "低置信度";
  if (summary.lastVsPrevRevenue <= -20 || summary.lastVsPrevIpu <= -15 || summary.lastVsPrevEcpm <= -15) return "高风险";
  if (summary.lastVsPrevRevenue <= -10 || summary.lastVsPrevIpu <= -10 || summary.lastVsPrevEcpm <= -10 || summary.lastVsPrevDnu <= -15) return "中风险";
  return "观察";
}

function riskClass(label) {
  if (label === "高风险") return "bad";
  if (label === "中风险") return "warn";
  if (label === "低置信度") return "muted";
  return "good";
}

function calcMain(mainData) {
  const detail = mainData?.detail_result;
  const dates = detail?.series || [];
  const row = detail?.rows?.[0]?.values || [];
  if (!dates.length || !row.length) {
    return { hasData: false, dates, rows: [] };
  }
  const rows = row.map((values, index) => ({
    date: dates[index],
    ads_revenue: values[0],
    impressions: values[1],
    ecpm: values[2],
    dau: values[3],
    dnu: values[4],
    ipu: values[5],
    ctr: values[6],
  }));
  const first7 = rows.slice(0, 7);
  const prev7 = rows.slice(-14, -7);
  const last7 = rows.slice(-7);
  const totalRevenue = sum(rows.map((r) => r.ads_revenue));
  const totalImpressions = sum(rows.map((r) => r.impressions));
  const weightedEcpm = totalImpressions ? (totalRevenue / totalImpressions) * 1000 : null;
  const summary = {
    hasData: totalRevenue > 0 || totalImpressions > 0,
    dates,
    rows,
    totalRevenue,
    avgRevenue: avg(rows.map((r) => r.ads_revenue)),
    totalImpressions,
    weightedEcpm,
    avgIpu: avg(rows.map((r) => r.ipu)),
    avgCtr: avg(rows.map((r) => r.ctr)),
    avgDau: avg(rows.map((r) => r.dau)),
    avgDnu: avg(rows.map((r) => r.dnu)),
    first7Revenue: avg(first7.map((r) => r.ads_revenue)),
    prev7Revenue: avg(prev7.map((r) => r.ads_revenue)),
    last7Revenue: avg(last7.map((r) => r.ads_revenue)),
    first7Dnu: avg(first7.map((r) => r.dnu)),
    prev7Dnu: avg(prev7.map((r) => r.dnu)),
    last7Dnu: avg(last7.map((r) => r.dnu)),
    first7Impressions: avg(first7.map((r) => r.impressions)),
    prev7Impressions: avg(prev7.map((r) => r.impressions)),
    last7Impressions: avg(last7.map((r) => r.impressions)),
    first7Ecpm: avg(first7.map((r) => r.ecpm)),
    prev7Ecpm: avg(prev7.map((r) => r.ecpm)),
    last7Ecpm: avg(last7.map((r) => r.ecpm)),
    first7Ipu: avg(first7.map((r) => r.ipu)),
    prev7Ipu: avg(prev7.map((r) => r.ipu)),
    last7Ipu: avg(last7.map((r) => r.ipu)),
    first7Dau: avg(first7.map((r) => r.dau)),
    prev7Dau: avg(prev7.map((r) => r.dau)),
    last7Dau: avg(last7.map((r) => r.dau)),
  };
  summary.lastVsPrevRevenue = pct(summary.last7Revenue, summary.prev7Revenue);
  summary.lastVsFirstRevenue = pct(summary.last7Revenue, summary.first7Revenue);
  summary.lastVsPrevDnu = pct(summary.last7Dnu, summary.prev7Dnu);
  summary.lastVsFirstDnu = pct(summary.last7Dnu, summary.first7Dnu);
  summary.lastVsPrevImpressions = pct(summary.last7Impressions, summary.prev7Impressions);
  summary.lastVsFirstImpressions = pct(summary.last7Impressions, summary.first7Impressions);
  summary.lastVsPrevEcpm = pct(summary.last7Ecpm, summary.prev7Ecpm);
  summary.lastVsFirstEcpm = pct(summary.last7Ecpm, summary.first7Ecpm);
  summary.lastVsPrevIpu = pct(summary.last7Ipu, summary.prev7Ipu);
  summary.lastVsFirstIpu = pct(summary.last7Ipu, summary.first7Ipu);
  summary.lastVsPrevDau = pct(summary.last7Dau, summary.prev7Dau);
  summary.lastVsFirstDau = pct(summary.last7Dau, summary.first7Dau);
  return summary;
}

function calcFormats(formatData, mainDates) {
  const detail = formatData?.detail_result;
  const dates = detail?.series || [];
  const start = dates.indexOf(mainDates[0]);
  const end = dates.indexOf(mainDates[mainDates.length - 1]);
  const formats = [];
  for (const row of detail?.rows || []) {
    const name = row.by_values?.[0] || "Unknown";
    const values = row.values || [];
    const mainValues = start >= 0 && end >= start ? values.slice(start, end + 1) : values.slice(-30);
    const totalRevenue = sum(mainValues.map((v) => v[2]));
    const totalImpressions = sum(mainValues.map((v) => v[3]));
    const first7 = mainValues.slice(0, 7);
    const prev7 = mainValues.slice(-14, -7);
    const last7 = mainValues.slice(-7);
    const turnIpu = turningPoint(dates, values, 0);
    const turnEcpm = turningPoint(dates, values, 1);
    formats.push({
      name,
      totalRevenue,
      totalImpressions,
      weightedEcpm: totalImpressions ? (totalRevenue / totalImpressions) * 1000 : null,
      avgIpu: avg(mainValues.map((v) => v[0])),
      first7Ipu: avg(first7.map((v) => v[0])),
      prev7Ipu: avg(prev7.map((v) => v[0])),
      last7Ipu: avg(last7.map((v) => v[0])),
      first7Ecpm: weighted(first7, 2, 3),
      prev7Ecpm: weighted(prev7, 2, 3),
      last7Ecpm: weighted(last7, 2, 3),
      lastVsPrevIpu: pct(avg(last7.map((v) => v[0])), avg(prev7.map((v) => v[0]))),
      lastVsFirstIpu: pct(avg(last7.map((v) => v[0])), avg(first7.map((v) => v[0]))),
      lastVsPrevEcpm: pct(weighted(last7, 2, 3), weighted(prev7, 2, 3)),
      lastVsFirstEcpm: pct(weighted(last7, 2, 3), weighted(first7, 2, 3)),
      turnIpu,
      turnEcpm,
    });
  }
  const totalRevenue = sum(formats.map((f) => f.totalRevenue));
  for (const f of formats) f.revenueShare = totalRevenue ? (f.totalRevenue / totalRevenue) * 100 : 0;
  formats.sort((a, b) => b.totalRevenue - a.totalRevenue);
  return formats;
}

function weighted(rows, valueIndex, weightIndex) {
  const numerator = sum(rows.map((v) => v[valueIndex]));
  const denominator = sum(rows.map((v) => v[weightIndex]));
  return denominator ? (numerator / denominator) * 1000 : null;
}

function turningPoint(dates, values, metricIndex) {
  let best = null;
  for (let i = 7; i <= values.length - 7; i += 1) {
    const before = avg(values.slice(i - 7, i).map((v) => v[metricIndex]));
    const after = avg(values.slice(i, i + 7).map((v) => v[metricIndex]));
    const change = pct(after, before);
    if (!Number.isFinite(change)) continue;
    if (!best || change < best.change) {
      best = { date: dates[i], before, after, change };
    }
  }
  return best || { date: "数据缺失", before: null, after: null, change: null };
}

function calcScenes(sceneData) {
  const records = sceneData?.records || [];
  const byScene = new Map();
  for (const rec of records) {
    if (!rec || rec.scene === -1 || rec.date === -1 || !rec.scene) continue;
    if (!byScene.has(rec.scene)) byScene.set(rec.scene, []);
    byScene.get(rec.scene).push(rec);
  }
  const scenes = [];
  for (const [name, rows] of byScene.entries()) {
    rows.sort((a, b) => String(a.date).localeCompare(String(b.date)));
    const first7 = rows.slice(0, 7);
    const last7 = rows.slice(-7);
    const totalRevenue = sum(rows.map((r) => r.ads_revenue));
    const totalImpressions = sum(rows.map((r) => r.impressions));
    scenes.push({
      name,
      totalRevenue,
      totalImpressions,
      weightedEcpm: totalImpressions ? (totalRevenue / totalImpressions) * 1000 : null,
      avgIpu: avg(rows.map((r) => r.ipu)),
      first7Revenue: avg(first7.map((r) => r.ads_revenue)),
      last7Revenue: avg(last7.map((r) => r.ads_revenue)),
      changeRevenue: pct(avg(last7.map((r) => r.ads_revenue)), avg(first7.map((r) => r.ads_revenue))),
    });
  }
  scenes.sort((a, b) => b.totalRevenue - a.totalRevenue);
  const total = sum(scenes.map((s) => s.totalRevenue));
  for (const s of scenes) s.revenueShare = total ? (s.totalRevenue / total) * 100 : 0;
  return scenes.slice(0, 10);
}

function buildConclusion(project, summary, formats, scenes) {
  if (!summary.hasData) {
    return [
      "SnowBall 主窗口没有返回有效广告收入或展示数据，本报告只保留低置信度占位。",
      "需要确认该项目是否仍在投放广告、是否为归档/实验/低量项目。",
    ];
  }
  const topFormat = formats[0];
  const topScene = scenes[0];
  const lines = [];
  lines.push(`30 日广告收入 ${money(summary.totalRevenue)}，日均广告收入 ${money(summary.avgRevenue)}；最近 7 日较前 7 日收入 ${pctFmt(summary.lastVsPrevRevenue)}。`);
  lines.push(`新增用户最近 7 日较前 7 日 ${pctFmt(summary.lastVsPrevDnu)}，展示数 ${pctFmt(summary.lastVsPrevImpressions)}，IPU ${pctFmt(summary.lastVsPrevIpu)}，eCPM ${pctFmt(summary.lastVsPrevEcpm)}。`);
  if (topFormat) lines.push(`收入最高广告格式为 ${topFormat.name}，贡献 ${pctShare(topFormat.revenueShare)}，其最近 7 日 IPU ${pctFmt(topFormat.lastVsPrevIpu)}、eCPM ${pctFmt(topFormat.lastVsPrevEcpm)}。`);
  if (topScene) lines.push(`收入最高场景为 ${topScene.name}，贡献 ${pctShare(topScene.revenueShare)}，末 7 日较首 7 日收入 ${pctFmt(topScene.changeRevenue)}。`);
  const risk = riskLabel(summary);
  lines.push(`综合判断：${risk}；所有后台政策、无效流量、Waterfall/出价问题仍需 AdMob 或聚合后台复核。`);
  return lines.slice(0, 5);
}

function writeReport(project, family, summary, formats, scenes) {
  const safe = slugName(project.project_name);
  const mdPath = path.join(OUT_DIR, `${project.project_id}_${safe}_ads_anomaly_${DATE_START}_${DATE_END}.md`);
  const htmlPath = path.join(OUT_DIR, `${project.project_id}_${safe}_ads_anomaly_${DATE_START}_${DATE_END}.html`);
  const risk = riskLabel(summary);
  const conclusions = buildConclusion(project, summary, formats, scenes);
  const topFormats = formats.slice(0, 5);
  const topScenes = scenes.slice(0, 8);
  const totalFormatRevenue = sum(formats.map((f) => f.totalRevenue));
  const md = `# ${project.project_name} 广告变现异常分析报告

- 产品族：${family}
- 项目：${project.project_id} ${project.project_name}
- 平台：${project.platform || "数据缺失"}
- 包名 / Store ID：${project.store_app_id || project.apple_id || "数据缺失"}
- 主分析周期：${DATE_START} ~ ${DATE_END}，30 个完整自然日
- 扩展观察周期：${EXT_START} ~ ${EXT_END}，60 个完整自然日
- 数据源：SnowBall MCP \`get_est_ads_revenue_chart_data\`、\`get_est_ads_revenue_table_data\`

## 总体结论

${conclusions.map((line, index) => `${index + 1}. ${line}`).join("\n")}

## 核心 KPI

| 指标 | 数值 | 变化/说明 |
|---|---:|---|
| 30 日广告收入 | ${money(summary.totalRevenue)} | 最近 7 日 vs 前 7 日 ${pctFmt(summary.lastVsPrevRevenue)} |
| 日均广告收入 | ${money(summary.avgRevenue)} | 最近 7 日 ${money(summary.last7Revenue)} |
| 展示数 | ${intFmt(summary.totalImpressions)} | 最近 7 日 vs 前 7 日 ${pctFmt(summary.lastVsPrevImpressions)} |
| 加权 eCPM | ${money(summary.weightedEcpm)} | 最近 7 日 vs 前 7 日 ${pctFmt(summary.lastVsPrevEcpm)} |
| 平均 IPU | ${numFmt(summary.avgIpu)} | 最近 7 日 vs 前 7 日 ${pctFmt(summary.lastVsPrevIpu)} |
| 平均 DNU | ${intFmt(summary.avgDnu)} | 最近 7 日 vs 前 7 日 ${pctFmt(summary.lastVsPrevDnu)} |

## 用户新增 vs 广告收入

| 指标 | 首 7 日日均 | 前 7 日日均 | 最近 7 日日均 | 最近 7 日 vs 前 7 日 | 最近 7 日 vs 首 7 日 |
|---|---:|---:|---:|---:|---:|
| 广告收入 | ${money(summary.first7Revenue)} | ${money(summary.prev7Revenue)} | ${money(summary.last7Revenue)} | ${pctFmt(summary.lastVsPrevRevenue)} | ${pctFmt(summary.lastVsFirstRevenue)} |
| DNU | ${intFmt(summary.first7Dnu)} | ${intFmt(summary.prev7Dnu)} | ${intFmt(summary.last7Dnu)} | ${pctFmt(summary.lastVsPrevDnu)} | ${pctFmt(summary.lastVsFirstDnu)} |
| DAU | ${intFmt(summary.first7Dau)} | ${intFmt(summary.prev7Dau)} | ${intFmt(summary.last7Dau)} | ${pctFmt(summary.lastVsPrevDau)} | ${pctFmt(summary.lastVsFirstDau)} |
| 展示数 | ${intFmt(summary.first7Impressions)} | ${intFmt(summary.prev7Impressions)} | ${intFmt(summary.last7Impressions)} | ${pctFmt(summary.lastVsPrevImpressions)} | ${pctFmt(summary.lastVsFirstImpressions)} |
| eCPM | ${money(summary.first7Ecpm)} | ${money(summary.prev7Ecpm)} | ${money(summary.last7Ecpm)} | ${pctFmt(summary.lastVsPrevEcpm)} | ${pctFmt(summary.lastVsFirstEcpm)} |
| IPU | ${numFmt(summary.first7Ipu)} | ${numFmt(summary.prev7Ipu)} | ${numFmt(summary.last7Ipu)} | ${pctFmt(summary.lastVsPrevIpu)} | ${pctFmt(summary.lastVsFirstIpu)} |

## 广告格式诊断

| 广告格式 | 30 日收入 | 收入占比 | 展示数 | 加权 eCPM | 平均 IPU | IPU 最近 7 日 vs 前 7 日 | eCPM 最近 7 日 vs 前 7 日 | 观察 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
${topFormats.map((f) => `| ${f.name} | ${money(f.totalRevenue)} | ${pctShare(f.revenueShare)} | ${intFmt(f.totalImpressions)} | ${money(f.weightedEcpm)} | ${numFmt(f.avgIpu)} | ${pctFmt(f.lastVsPrevIpu)} | ${pctFmt(f.lastVsPrevEcpm)} | ${formatObservation(f)} |`).join("\n")}

## 60 日格式级 IPU / eCPM 转折点

| 广告格式 | 指标 | 转折日期 | 前 7 日均值 | 后 7 日均值 | 变化 |
|---|---|---:|---:|---:|---:|
${topFormats.map((f) => `| ${f.name} | IPU | ${f.turnIpu.date} | ${numFmt(f.turnIpu.before)} | ${numFmt(f.turnIpu.after)} | ${pctFmt(f.turnIpu.change)} |
| ${f.name} | eCPM | ${f.turnEcpm.date} | ${money(f.turnEcpm.before)} | ${money(f.turnEcpm.after)} | ${pctFmt(f.turnEcpm.change)} |`).join("\n")}

## 广告场景诊断

| 场景 | 30 日收入 | 收入占比 | 展示数 | 加权 eCPM | 平均 IPU | 末 7 日 vs 首 7 日收入 |
|---|---:|---:|---:|---:|---:|---:|
${topScenes.length ? topScenes.map((s) => `| ${s.name} | ${money(s.totalRevenue)} | ${pctShare(s.revenueShare)} | ${intFmt(s.totalImpressions)} | ${money(s.weightedEcpm)} | ${numFmt(s.avgIpu)} | ${pctFmt(s.changeRevenue)} |`).join("\n") : "| 数据缺失 | 数据缺失 | 数据缺失 | 数据缺失 | 数据缺失 | 数据缺失 | 数据缺失 |"}

## 动作建议

### P0

- 若收入最近 7 日下降超过 20%，先回查最大收入广告格式与最大收入场景在转折日前后的版本、国家、来源分布。
- 若 DNU 与展示数同步下降，先按新增来源和新用户首日路径排查，不直接归因到广告后台。

### P1

- 若 IPU 下降超过 15%，回查广告触发、频控、展示机会、SDK 调用和场景入口。
- 若 eCPM 下降超过 15%，再进入 AdMob / Waterfall / bidding / 价格规则 / 无效流量复核。

### P2

- 收入占比低于 3% 的格式和小样本场景只保留观察，不进入优先排查。
- AdMob 政策、账户级无效流量、实时填充和具体 Mediation Group 表现需后台人工复核。

## 数据限制

- 本报告只使用 SnowBall MCP 返回数据，不使用本地缓存或手工补数。
- \`-1\`、缺失、样本过小统一标记为“数据缺失/低置信度”。
- 当前报告不包含 ${DATE_END} 之后的实时数据。
`;

  const bars = topFormats.map((f) => {
    const width = totalFormatRevenue ? Math.max(1, Math.min(100, f.revenueShare)) : 1;
    return `<div class="bar-row"><span>${escapeHtml(f.name)}</span><div class="track"><div class="fill" style="width:${width.toFixed(2)}%"></div></div><strong>${pctShare(f.revenueShare)}</strong></div>`;
  }).join("");

  const formatCards = topFormats.slice(0, 4).map((f) => `
      <div class="card format-card">
        <div class="top"><div class="name">${escapeHtml(f.name)}</div><span class="tag ${formatTagClass(f)}">${formatTag(f)}</span></div>
        <div class="metric-row">
          <div class="metric"><span>收入</span><strong>${money(f.totalRevenue)}</strong></div>
          <div class="metric"><span>加权 eCPM</span><strong>${money(f.weightedEcpm)}</strong></div>
          <div class="metric"><span>平均 IPU</span><strong>${numFmt(f.avgIpu)}</strong></div>
        </div>
        <p class="desc">收入占比 ${pctShare(f.revenueShare)}。最近 7 日 IPU ${pctFmt(f.lastVsPrevIpu)}，eCPM ${pctFmt(f.lastVsPrevEcpm)}。</p>
      </div>`).join("");

  const turnRows = topFormats.slice(0, 5).map((f) => `
          <tr><td>${escapeHtml(f.name)}</td><td>IPU</td><td>${f.turnIpu.date}</td><td>${numFmt(f.turnIpu.before)}</td><td>${numFmt(f.turnIpu.after)}</td><td>${pctFmt(f.turnIpu.change)}</td><td>${Math.abs(f.turnIpu.change || 0) >= 15 ? "需定位" : "观察"}</td></tr>
          <tr><td>${escapeHtml(f.name)}</td><td>eCPM</td><td>${f.turnEcpm.date}</td><td>${money(f.turnEcpm.before)}</td><td>${money(f.turnEcpm.after)}</td><td>${pctFmt(f.turnEcpm.change)}</td><td>${Math.abs(f.turnEcpm.change || 0) >= 15 ? "需复核" : "观察"}</td></tr>`).join("");

  const sceneCards = topScenes.slice(0, 8).map((s) => `
      <div class="scene"><div><div class="scene-name">${escapeHtml(s.name)}</div><div class="scene-note">占比 ${pctShare(s.revenueShare)}，末7日 vs 首7日 ${pctFmt(s.changeRevenue)}</div></div><div class="scene-value">${money(s.totalRevenue, 0)}</div></div>`).join("") || `<div class="scene"><div><div class="scene-name">数据缺失</div><div class="scene-note">SnowBall 未返回有效场景数据</div></div><div class="scene-value">低置信度</div></div>`;

  const html = `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(project.project_name)} 广告变现异常分析</title>
  <style>${css()}</style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div>
        <h1>${escapeHtml(project.project_name)} 广告变现诊断</h1>
        <div class="subtitle">基于 SnowBall 估算广告收入、用户新增、广告格式 IPU/eCPM 与场景贡献，判断近 30 日是否存在广告变现异常。</div>
      </div>
      <div class="method-box">数据口径<br />${project.project_id} ${escapeHtml(project.platform || "")}<br />${DATE_START} 至 ${DATE_END}<br />扩展观察 60 日</div>
    </section>

    <section class="grid-2">
      <div class="card conclusion">
        <b>核心结论</b>
        <div class="lead">${escapeHtml(conclusions[0] || "数据缺失，低置信度。")}</div>
      </div>
      <div class="card bars">
        <h3>广告格式收入贡献</h3>
        ${bars || "<p>数据缺失/低置信度</p>"}
      </div>
    </section>

    <section class="kpis">
      <div class="kpi"><div class="label">30日广告收入</div><div class="value">${money(summary.totalRevenue)}</div><div class="note">SnowBall 估算</div></div>
      <div class="kpi"><div class="label">日均广告收入</div><div class="value">${money(summary.avgRevenue)}</div><div class="note">最近7日 vs 前7日 ${pctFmt(summary.lastVsPrevRevenue)}</div></div>
      <div class="kpi"><div class="label">展示数</div><div class="value">${compact(summary.totalImpressions)}</div><div class="note">${pctFmt(summary.lastVsPrevImpressions)}</div></div>
      <div class="kpi"><div class="label">整体 eCPM</div><div class="value">${money(summary.weightedEcpm)}</div><div class="note">${pctFmt(summary.lastVsPrevEcpm)}</div></div>
      <div class="kpi"><div class="label">平均 IPU</div><div class="value">${numFmt(summary.avgIpu)}</div><div class="note">${pctFmt(summary.lastVsPrevIpu)}</div></div>
      <div class="kpi"><div class="label">平均 DNU</div><div class="value">${intFmt(summary.avgDnu)}</div><div class="note">${pctFmt(summary.lastVsPrevDnu)}</div></div>
    </section>

    <div class="section-title"><span class="pill ${riskClass(risk)}">${risk}</span><h2>核心广告格式</h2></div>
    <section class="format-grid">${formatCards || "<div class='card'>数据缺失/低置信度</div>"}</section>

    <div class="section-title"><span class="pill orange">转折点</span><h2>60 日格式级 IPU / eCPM</h2></div>
    <section class="card"><table><thead><tr><th>广告格式</th><th>指标</th><th>转折日期</th><th>前7日</th><th>后7日</th><th>变化</th><th>判断</th></tr></thead><tbody>${turnRows}</tbody></table></section>

    <div class="section-title"><span class="pill green">场景贡献</span><h2>重点场景定位</h2></div>
    <section class="scene-grid">${sceneCards}</section>

    <div class="section-title"><span class="pill gray">建议</span><h2>最终处理优先级</h2></div>
    <section class="recommend">
      <div class="card"><h3>P0</h3><p>优先回查最大收入格式和最大收入场景，结合 DNU、展示数、IPU 判断是否是新增或展示机会变化。</p></div>
      <div class="card"><h3>P1</h3><p>IPU 下降查触发与频控；eCPM 下降查 AdMob、Waterfall、bidding、价格规则和无效流量。</p></div>
      <div class="card"><h3>P2</h3><p>低收入占比格式和小样本场景只做观察；后台政策与实时填充需人工复核。</p></div>
    </section>

    <div class="footer">Generated from ${mdPath}</div>
  </main>
</body>
</html>
`;
  fs.writeFileSync(mdPath, md);
  fs.writeFileSync(htmlPath, html);
  return { project, family, mdPath, htmlPath, risk, summary, formats, scenes };
}

function formatObservation(f) {
  if ((f.lastVsPrevIpu || 0) <= -15) return "IPU 明显下降，优先查触发/频控/展示机会";
  if ((f.lastVsPrevEcpm || 0) <= -15) return "eCPM 明显下降，需后台复核";
  if ((f.lastVsPrevIpu || 0) <= -10) return "IPU 轻度回落，观察";
  return "未见强异常";
}

function formatTag(f) {
  if ((f.lastVsPrevIpu || 0) <= -15) return "IPU下滑";
  if ((f.lastVsPrevEcpm || 0) <= -15) return "eCPM下滑";
  if ((f.lastVsPrevIpu || 0) <= -10) return "观察";
  return "稳定";
}

function formatTagClass(f) {
  if ((f.lastVsPrevIpu || 0) <= -15 || (f.lastVsPrevEcpm || 0) <= -15) return "bad";
  if ((f.lastVsPrevIpu || 0) <= -10 || (f.lastVsPrevEcpm || 0) <= -10) return "warn";
  return "good";
}

function compact(value) {
  if (!Number.isFinite(value)) return "数据缺失";
  if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
  return String(Math.round(value));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function css() {
  return `
    :root{--bg:#eef3fb;--card:#fff;--ink:#101828;--muted:#667085;--line:#d9e2f1;--blue:#2563eb;--blue-soft:#eaf1ff;--green:#15945b;--green-soft:#e8f7ee;--orange:#d97706;--orange-soft:#fff4df;--red:#b42318;--red-soft:#ffefed;--gray:#536579;--shadow:0 10px 30px rgba(25,42,70,.08)}
    *{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#e8eefb 0%,#f7f9fd 38%,#eef3fb 100%);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;letter-spacing:0}.page{max-width:1180px;margin:0 auto;padding:58px 32px 42px}.hero{display:grid;grid-template-columns:1fr 250px;gap:24px;align-items:start;margin-bottom:34px}h1{margin:0 0 18px;font-size:46px;line-height:1.08;font-weight:850}.subtitle{max-width:760px;color:var(--muted);font-size:21px;line-height:1.55;font-weight:520}.method-box{background:rgba(255,255,255,.86);border:1px solid var(--line);border-radius:8px;padding:18px 20px;text-align:center;color:#4b5b73;font-weight:750;font-size:17px;line-height:1.5;box-shadow:var(--shadow)}.grid-2{display:grid;grid-template-columns:1.2fr 1fr;gap:20px;margin-bottom:28px}.section-title{display:flex;align-items:center;gap:14px;margin:30px 0 16px}.section-title h2{margin:0;font-size:30px;line-height:1.2}.pill{display:inline-flex;align-items:center;border-radius:999px;padding:6px 12px;font-weight:850;color:#fff;font-size:15px}.pill.good{background:var(--green)}.pill.warn,.pill.orange{background:var(--orange)}.pill.bad{background:var(--red)}.pill.muted,.pill.gray{background:var(--gray)}.pill.green{background:var(--green)}.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:24px;box-shadow:var(--shadow)}.conclusion b{color:var(--blue);font-size:18px}.conclusion .lead{margin-top:16px;font-size:27px;line-height:1.35;font-weight:850}.bars h3,.card h3{margin:0 0 18px;font-size:22px}.bar-row{display:grid;grid-template-columns:120px 1fr 76px;gap:14px;align-items:center;margin:14px 0;font-size:17px;font-weight:740}.track{height:14px;border-radius:999px;background:#e8eef8;overflow:hidden}.fill{height:100%;border-radius:inherit;background:var(--blue)}.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:18px 0 28px}.kpi{background:rgba(255,255,255,.86);border:1px solid var(--line);border-radius:8px;padding:15px}.kpi .label{color:var(--muted);font-weight:700;font-size:13px}.kpi .value{margin-top:7px;font-size:22px;font-weight:850}.kpi .note{margin-top:7px;font-size:12px;color:var(--muted);font-weight:650}.format-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.format-card .top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:16px}.format-card .name{font-size:27px;font-weight:850}.tag{border-radius:999px;padding:6px 10px;font-weight:800;font-size:13px;background:var(--blue-soft);color:var(--blue);white-space:nowrap}.tag.good{color:var(--green);background:var(--green-soft)}.tag.warn{color:var(--orange);background:var(--orange-soft)}.tag.bad{color:var(--red);background:var(--red-soft)}.metric-row{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.metric{border:1px solid #e6edf7;border-radius:8px;padding:12px;background:#fbfcff;min-height:72px}.metric span{display:block;color:var(--muted);font-size:13px;font-weight:700}.metric strong{display:block;margin-top:4px;font-size:21px}.desc{margin:16px 0 0;color:#3f4d61;font-size:16px;line-height:1.55;font-weight:560}table{width:100%;border-collapse:collapse;font-size:15px}th,td{padding:12px 10px;border-bottom:1px solid #e7edf6;text-align:right}th:first-child,td:first-child{text-align:left}th{color:#536579;font-size:13px;background:#f7faff}tr:last-child td{border-bottom:0}.scene-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.scene{display:flex;justify-content:space-between;gap:16px;align-items:center;border:1px solid #e7edf6;border-radius:8px;padding:16px;background:#fff}.scene .scene-name{font-weight:850;font-size:17px}.scene .scene-note{color:var(--muted);margin-top:4px;font-size:13px;font-weight:650}.scene .scene-value{text-align:right;font-size:22px;font-weight:850}.recommend{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.recommend h3{margin-bottom:10px}.recommend p{margin:0;color:#3f4d61;font-size:16px;line-height:1.55;font-weight:560}.footer{margin-top:34px;color:var(--muted);font-size:13px;text-align:center}@media(max-width:900px){.page{padding:34px 18px}.hero,.grid-2,.format-grid,.scene-grid,.recommend{grid-template-columns:1fr}h1{font-size:35px}.subtitle{font-size:18px}.kpis{grid-template-columns:repeat(2,1fr)}.metric-row{grid-template-columns:1fr}table{font-size:13px}th,td{padding:10px 6px}}`;
}

async function getProjects() {
  const projects = new Map();
  const familyByProject = new Map();
  for (const item of SEARCHES) {
    const data = await callTool("get_projects", { project_name: item.query, use_cache: false });
    for (const project of data.matched_projects || []) {
      if (project.is_archive) continue;
      if (!projects.has(project.project_id)) projects.set(project.project_id, project);
      const families = familyByProject.get(project.project_id) || new Set();
      families.add(item.family);
      familyByProject.set(project.project_id, families);
    }
  }
  return [...projects.values()]
    .sort((a, b) => a.project_id.localeCompare(b.project_id, undefined, { numeric: true }))
    .map((project) => ({ project, family: [...familyByProject.get(project.project_id)].join("/") }));
}

async function generateOne(project, family) {
  console.log(`[${project.project_id}] fetching main overview`);
  const mainData = await callTool("get_est_ads_revenue_chart_data", {
    project_id: project.project_id,
    date_start: DATE_START,
    date_end: DATE_END,
    day_period: "daily",
    dimension_list: ["date"],
    indexes: METRICS,
    use_ck: 1,
    is_all_data: 1,
  });
  const summary = calcMain(mainData);

  console.log(`[${project.project_id}] fetching format trend`);
  const formatData = await callTool("get_est_ads_revenue_chart_data", {
    project_id: project.project_id,
    date_start: EXT_START,
    date_end: EXT_END,
    day_period: "daily",
    dimension_list: ["date", "ad_unit_format"],
    indexes: FORMAT_METRICS,
    use_ck: 1,
    is_all_data: 1,
  });
  const formats = calcFormats(formatData, summary.dates || []);

  console.log(`[${project.project_id}] fetching scene table`);
  let scenes = [];
  try {
    const sceneData = await callTool("get_est_ads_revenue_table_data", {
      project_id: project.project_id,
      date_start: DATE_START,
      date_end: DATE_END,
      dimension_list: ["scene"],
    });
    scenes = calcScenes(sceneData);
  } catch (error) {
    console.warn(`[${project.project_id}] scene table failed: ${error.message}`);
  }

  return writeReport(project, family, summary, formats, scenes);
}

function writeIndex(results) {
  const mdPath = path.join(OUT_DIR, `family_ads_anomaly_index_${DATE_START}_${DATE_END}.md`);
  const htmlPath = path.join(OUT_DIR, `family_ads_anomaly_index_${DATE_START}_${DATE_END}.html`);
  const rows = results.map((r) => {
    const relMd = path.relative(ROOT, r.mdPath);
    const relHtml = path.relative(ROOT, r.htmlPath);
    return `| ${r.project.project_id} | ${r.project.project_name} | ${r.family} | ${r.risk} | ${money(r.summary.totalRevenue)} | ${money(r.summary.avgRevenue)} | ${pctFmt(r.summary.lastVsPrevRevenue)} | ${pctFmt(r.summary.lastVsPrevDnu)} | ${pctFmt(r.summary.lastVsPrevIpu)} | [MD](${relMd}) / [HTML](${relHtml}) |`;
  }).join("\n");
  const md = `# Message / Photo / Weather / News 全系广告变现异常报告索引

- 主分析周期：${DATE_START} ~ ${DATE_END}
- 扩展观察周期：${EXT_START} ~ ${EXT_END}
- 数据源：SnowBall MCP
- 覆盖项目：${results.length} 个非归档项目

| 项目ID | 项目 | 产品族 | 状态 | 30日收入 | 日均收入 | 收入最近7日vs前7日 | DNU最近7日vs前7日 | IPU最近7日vs前7日 | 报告 |
|---|---|---|---|---:|---:|---:|---:|---:|---|
${rows}
`;
  const cards = results.map((r) => `<a class="idx-card ${riskClass(r.risk)}" href="${path.basename(r.htmlPath)}"><b>${r.project.project_id} ${escapeHtml(r.project.project_name)}</b><span>${escapeHtml(r.family)} · ${r.risk}</span><strong>${money(r.summary.totalRevenue)}</strong><em>收入 ${pctFmt(r.summary.lastVsPrevRevenue)} / DNU ${pctFmt(r.summary.lastVsPrevDnu)} / IPU ${pctFmt(r.summary.lastVsPrevIpu)}</em></a>`).join("");
  const html = `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>全系广告变现异常报告索引</title><style>${css()}.idx-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.idx-card{display:block;text-decoration:none;color:var(--ink);background:#fff;border:1px solid var(--line);border-radius:8px;padding:18px;box-shadow:var(--shadow)}.idx-card b,.idx-card span,.idx-card strong,.idx-card em{display:block}.idx-card span{color:var(--muted);margin-top:7px;font-style:normal}.idx-card strong{font-size:26px;margin-top:12px}.idx-card em{font-style:normal;color:#3f4d61;margin-top:8px}.idx-card.bad{border-color:#f2b8b5}.idx-card.warn{border-color:#f4c983}.idx-card.good{border-color:#a9dec2}@media(max-width:900px){.idx-grid{grid-template-columns:1fr}}</style></head><body><main class="page"><section class="hero"><div><h1>全系广告变现异常索引</h1><div class="subtitle">Message / Photo / Weather / News 非归档项目，统一使用 ${DATE_START} ~ ${DATE_END} 主窗口和 60 日格式级观察窗口。</div></div><div class="method-box">覆盖项目<br>${results.length} 个<br>SnowBall MCP<br>Generated</div></section><section class="idx-grid">${cards}</section><div class="footer">Generated from ${mdPath}</div></main></body></html>`;
  fs.writeFileSync(mdPath, md);
  fs.writeFileSync(htmlPath, html);
  return { mdPath, htmlPath };
}

async function main() {
  ensureDir(OUT_DIR);
  await rpc("initialize", { protocolVersion: "2025-03-26", capabilities: {}, clientInfo: { name: "codex-snowball-batch", version: "1.0" } });
  const projects = await getProjects();
  console.log(`projects=${projects.length}`);
  const results = [];
  for (const { project, family } of projects) {
    try {
      const result = await generateOne(project, family);
      results.push(result);
      console.log(`[${project.project_id}] wrote ${path.basename(result.htmlPath)}`);
    } catch (error) {
      console.error(`[${project.project_id}] failed: ${error.stack || error.message}`);
    }
  }
  const index = writeIndex(results);
  console.log(`index=${index.htmlPath}`);
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
