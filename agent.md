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

整个过程要求可审计、可重跑。

## 非目标

`SysA` 不做以下事情：

- 不生成交易指令
- 不连接券商或交易系统
- 不自动下单
- 不接入数据库、消息队列、Web 服务
- 不在 Python 中写研究推理逻辑
- 不内置 LLM API 调用
- 不实现复杂抓取框架

## 输入

研究数据分散存储在 `research/{trade_date}/data/` 下，不组装成单一 task.json：

### 1. SysQ 产出（`data/sysq_signals/`）

- `ranking_score` — 融合排序分
- `models[]` — 多模型归因数组，每个模型有独立的 score、feature_contrib
- `industry` — 行业分类标签

### 2. 外部数据源（`data/financial/`、`data/news/`、`data/announcements/`）

- 财报模板 JSON（按 ts_code 存放）
- 新闻搜索结果 JSON
- 公告 JSON

### 3. SysA 积累（`data/memory/`，可选）

- 公司长期记忆（按 ts_code 存放）
- 行业长期记忆（按 industry 存放）

## 输出

### `output/stock_opinions/{ts_code}.json`

遵守 `schemas/stock_opinion.schema.json`，含：

- 模型信号解读（各模型 score、top_drivers、多模型一致性）
- 财务验证（support/neutral/against/insufficient）
- 催化分析
- 行业支撑
- 反证与风险
- 综合评级 A/B/C/D + confidence
- memory 更新建议（op/target/text）

### `output/industry_summary/{industry}.json`

遵守 `schemas/industry_summary.schema.json`，含：

- 行业供需、景气度、概念炒作风险
- 本次覆盖的成员股票

### `output/data_readiness.json`

第一步的产出，记录各数据源的可用性。

## 执行方式

### Step A：数据就绪

读取 `research/{trade_date}/data/` 下各目录，检查是否存在、是否可读。对财报做轻量汇总（营收、利润率、杠杆、现金流等关键指标）。输出 `data_readiness.json`。

### Step B：综合研究

按行业分组，先写行业判断（`industry_summary/`），再逐股输出研究意见（`stock_opinions/`）。两步由同一 agent 顺序执行。

## evidence / memory / output 的区别

### evidence

证据层，不是结论层。保存来源、标题、claim、可靠度、原始引用位置。B_research 中可使用 System prompt 要求 LLM 标注关键判断的 sources，落盘为 evidence 待后续规范化。

### memory

长期认知层，只存稳定、可复用、跨期仍有意义的认知。B_research 的每个 stock_opinion 中带 memory_patch（add/update/delete），需人工确认后写入 `data/memory/`。

### output

结论层。每只股票一个 JSON 文件，包含评级、依据、反证、memory 建议。

评级标准：

- `A`：模型逻辑清楚，财务或行业验证强，近期催化明确，反证有限，值得优先人工深挖
- `B`：存在一定支持证据，但关键不确定性仍在，值得继续跟踪
- `C`：支持一般、证据不完整、催化偏弱或反证较多，暂不优先
- `D`：主要证据不支持模型逻辑，或风险明显高于研究价值，低优先级

confidence 标准：

- `high`：关键判断有多条高可靠证据支撑，冲突较少
- `medium`：有部分证据支持，但仍有缺口或冲突
- `low`：证据明显不足、来源较弱或关键问题未解决

## 禁止自动交易

`SysA` 不得自动生成买卖建议、目标价、仓位建议、执行指令或自动下单动作。它只输出研究评级与研究依据。
