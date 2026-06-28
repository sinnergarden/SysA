# 第一步：数据就绪

读取：

- `prompts/00_master.md`
- `prompts/A_data_readiness.md`
- `resources/` 下的各数据源

写入：

- `research/{trade_date}/output/data_readiness.json`

校验：

- `schemas/data_readiness.schema.json`

缺失数据不得失败，但必须如实写入 `missing_data` 和 `uncertainties`。不做研究判断，只做数据可用性检查和轻量汇总。
