# 第二步：综合研究

目的：

- 基于第一步确认已就绪的所有数据，对每只候选股票给出独立研究意见。
- 按行业汇总行业判断。

## 读取

- `prompts/00_master.md`
- `prompts/B_research.md`
- `research/{trade_date}/output/data_readiness.json`
- `research/{trade_date}/data/sysq_signals/candidates.json`
- `research/{trade_date}/data/financial/{ts_code}.json`
- `research/{trade_date}/data/news/{ts_code}.json`
- `research/{trade_date}/data/announcements/{ts_code}.json`
- `research/{trade_date}/data/memory/company/{ts_code}.json`（如有）
- `research/{trade_date}/data/memory/industry/{industry}.json`（如有）

## 研究流程

### 1. 行业先行

对本次覆盖的所有股票按行业分组，先写行业判断：

- 写入 `research/{trade_date}/output/industry_summary/{industry}.json`
- 遵守 `schemas/industry_summary.schema.json`
- 内容包括：供需格局、景气度、概念炒作风险、该行业本次覆盖的股票名单

### 2. 逐股研究

对每只候选股票：

```
研究框架：
- 模型信号解读：各模型的 score 含义、top_drivers 解读、多模型一致性
- 财务验证：财报数据是否支持模型逻辑
- 催化分析：近期新闻/公告是否存在基本面催化
- 行业支撑：引用步骤 1 的 industry_summary
- 反证挑战：最强的反向论证和风险点
- 综合评级：A/B/C/D, high/medium/low
- memory 更新建议：如果当前研究有新认知，输出 memory patch
```

- 写入 `research/{trade_date}/output/stock_opinions/{ts_code}.json`
- 遵守 `schemas/stock_opinion.schema.json`

### 3. 评级规则

- `financial_assessment = against` 时，最高评级不得超过 C
- 关键数据缺失超过 2 项时，`confidence` 不得为 `high`
- 行业判断仅作为背景参考，不得替代个股财务验证

## 不要做

- 不输出交易建议、目标价、仓位
- 不改写原始证据
- 不把短期噪音写入 memory patch
