# 第二步：综合研究

读取：

- `prompts/00_master.md`
- `prompts/B_research.md`
- `research/{trade_date}/output/data_readiness.json`
- `research/{trade_date}/data/` 下的完整数据

写入：

- `research/{trade_date}/output/industry_summary/{industry}.json`
- `research/{trade_date}/output/stock_opinions/{ts_code}.json`

校验：

- `schemas/stock_opinion.schema.json`
- `schemas/industry_summary.schema.json`
