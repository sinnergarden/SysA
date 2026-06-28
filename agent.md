# SysA 总设计说明

## 系统目标

`SysA` 是一个面向 `SysQ` 候选股票研究的文件系统研究框架。它的使命是：**接收 SysQ 的融合排序信号和多模型因子归因（N 个模型 × N 套 SHAP），叠加外部原始材料（财报、新闻、公告），用 LLM 产出带证据链的结构化研究结论。**

SysQ 产出排序信号和多模型归因：

- 排序信号：`ranking_score`（融合分，仅用于 TopK 选股，不参与归因解释）
- 多模型归因：`models[]` 数组，每个模型有独立的 `score`、`feature_contrib`（含 method/values/universe_stats）、`horizon`、`target`
- 结构化标签：`industry`

SysQ 不产出 per-stock natural-language explanation。所有分析由 SysA 的 LLM agent 在综合研究阶段完成。

具体是把：

- SysQ 给出的融合排序选股名单 + 多模型因子归因
- 外部原始材料：财报模板、新闻摘要、公告文本
- SysA 历次积累的公司/行业长期记忆

转成：

- 每只股票的独立研究意见（A/B/C/D）
- 行业判断汇总
- memory 更新建议

## 非目标

`SysA` 不做：交易指令、连接券商、自动下单、数据库/消息队列/Web 服务、Python 研究推理、内置 LLM 调用、复杂抓取框架。

## 输入

研究数据分散存储在 `research/{trade_date}/data/` 下，不组装成单一 task.json：

| 目录 | 内容 | 来源 |
|------|------|------|
| `sysq_signals/candidates.json` | ranking_score + models[]（SHAP） | SysQ 每日产出 |
| `financial/{ts_code}.json` | 财报模板数据 | 外部数据源 |
| `news/{ts_code}.json` | 新闻搜索结果 | 外部数据源 |
| `announcements/{ts_code}.json` | 公告结果 | 外部数据源 |
| `memory/company/{ts_code}.json` | 公司长期记忆（可选） | SysA 积累 |
| `memory/industry/{industry}.json` | 行业长期记忆（可选） | SysA 积累 |

## 输出

### `output/stock_opinions/{ts_code}.json`

遵守 `schemas/stock_opinion.schema.json`，含：模型信号解读、财务验证、催化分析、行业支撑、反证、评级 A/B/C/D + confidence、memory 建议。

### `output/industry_summary/{industry}.json`

遵守 `schemas/industry_summary.schema.json`，含：行业供需、景气度、概念炒作风险、覆盖成员。

### `output/data_readiness.json`

Step A 产出：各数据源可用性报告。

## 执行方式

### Step A：数据就绪

检查 `research/{trade_date}/data/` 下各目录可用性，对财报/新闻做轻量汇总。输出 `data_readiness.json`。

### Step B：综合研究

按行业分组，先写行业判断（`industry_summary/`），再逐股输出研究意见（`stock_opinions/`）。

## 评级标准

- `A`：强验证，反证有限，值得优先深挖
- `B`：支持证据存在但关键不确定性仍在
- `C`：支持一般、证据不完整
- `D`：主要证据不支持模型逻辑

## confidence 标准

- `high`：多条高可靠证据支撑，冲突较少
- `medium`：部分支持但仍有缺口
- `low`：证据不足、来源弱

## 禁止自动交易

`SysA` 不得自动生成买卖建议、目标价、仓位建议。只输出研究评级与研究依据。
