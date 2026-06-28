---
name: country-scaling-priority-diagnosis
description: 分析移动应用买量国家放量优先级，结合 grow_base 阈值、Snowball ROI/CPI/留存/eCPM/ARPDAU/IPU 和平台投放数据，输出国家级 P0/P1/P2 扩量、观察、降量建议。
---

# Country Scaling Priority Diagnosis

## 目标

判断哪些国家可放量、哪些国家只适合观察、哪些国家需要降量或暂停测试。

## 数据源

- `grow_base/{project_id}_{name}.md`：国家阈值，优先级最高。
- Snowball MCP：ROI0/ROI3/ROI7、CPI、retention_1、eCPM、ARPDAU、IPU。
- Google/Meta：国家维度花费、转化和计划状态。

## 判断维度

- ROI 是否达标。
- CPI 是否低于上限。
- retention_1 是否达标。
- eCPM / ARPDAU / IPU 是否支撑 IAA。
- 花费和安装样本是否足够。
- 国家数据是否连续。

## 状态

| 状态 | 说明 |
|---|---|
| `scale_p0` | ROI、CPI、留存均达标且样本成熟 |
| `scale_p1` | 主要指标达标，但样本或预测仍有限 |
| `observe` | 有局部信号，但不能强扩量 |
| `reduce` | 成熟样本下多项指标不达标 |
| `data_gap` | 缺少关键数据 |

## 输出格式

```markdown
# 国家放量优先级

## 阈值来源
## 国家优先级矩阵
| 国家 | 花费 | ROI0 | CPI | 次留 | eCPM | 状态 | 动作 |
## 放量顺序
## 风险国家
## 数据缺口
```

## 规则

- 禁止只看全局均值。
- 禁止因为 CPI 低而忽略 ROI 和留存。
- 国家阈值只能来自 `grow_base` 或明确说明缺失。
