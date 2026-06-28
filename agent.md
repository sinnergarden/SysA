# SysA 总设计说明

## 系统目标

`SysA` 是一个面向 `SysQ` 候选股票研究的文件系统研究框架。它的使命是：**接收 SysQ 的融合排序信号和多模型因子归因（N 个模型 × N 套 SHAP），叠加外部原始材料（财报、新闻、公告），用 LLM 产出带证据链的结构化研究结论。**

SysQ 产出排序信号和多模型归因：

- 排序信号：`ranking_score`（融合分，仅用于 TopK 选股，不参与归因解释）
- 多模型归因：`models[]` 数组，每个模型有独立的 `score`、`feature_contrib`（含 method/values/universe_stats）、`horizon`、`target`
- 结构化标签：`industry`

SysQ 不产出 per-stock natural-language explanation。所有分析由 SysA 的 LLM agent 在综合研究阶段完成。

## 非目标

`SysA` 不做：交易指令、连接券商、自动下单、数据库/消息队列/Web 服务、Python 研究推理、内置 LLM 调用、复杂抓取框架。

## 资源目录

所有数据全局复用，以资源 ID 或日期标注：

| 路径 | 内容 | 来源 |
|------|------|------|
| `resources/sysq_signals/{trade_date}.json` | ranking_score + models[]（SHAP） | SysQ 每日产出 |
| `resources/financial/parsed/{ts_code}.json` | 财报解析结果（最近 3 年年报 + 所有季度报 + MD&A） | Step A 下载并解析 |
| `resources/financial/raw_pdfs/{ts_code}/` | 原始财报 PDF | Step A 下载 |
| `resources/news/{ts_code}.json` | 新闻（每条含 date） | Step A 拉取 |
| `resources/announcements/{ts_code}.json` | 公告（每条含 date） | Step A 拉取 |
| `resources/memory/company/{ts_code}.json` | 公司长期记忆 | SysA 积累 |
| `resources/memory/industry/{industry}.json` | 行业长期记忆 | SysA 积累 |

## 执行方式

### Step A：数据就绪

检查 `resources/` 下各数据源可用性。对缺失的财务数据：下载 PDF → 解析 → 填 `financial/parsed/`。输出 `research/{trade_date}/output/data_readiness.json`。

### Step B：综合研究

按行业分组，先写行业判断（`industry_summary/`），再逐股输出研究意见（`stock_opinions/`）。

## 输出

`research/{trade_date}/output/` 下：

- `data_readiness.json` — 各数据源可用性报告
- `industry_summary/{industry}.json` — 行业供需、景气度、概念风险
- `stock_opinions/{ts_code}.json` — 个股意见（评级、依据、反证、memory 建议）

## 评级标准

- `A`：强验证，反证有限，值得优先深挖
- `B`：支持证据存在但关键不确定性仍在
- `C`：支持一般、证据不完整
- `D`：主要证据不支持模型逻辑

## 禁止自动交易

`SysA` 不得自动生成买卖建议、目标价、仓位建议。只输出研究评级与研究依据。
