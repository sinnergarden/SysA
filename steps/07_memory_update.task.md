# 任务 07：memory 更新建议

读取：

- `prompts/00_master.md`
- `prompts/07_memory_update.md`
- `outputs/<task_id>/<ts_code>/06_final_rating.json`
- 当前股票的 `company_memory_json`
- 当前股票的 `industry_memory_json`

写入：

- `outputs/<task_id>/<ts_code>/07_memory_update.json`

校验：

- `schemas/memory_update.schema.json`

禁止：

- 不改写原始 evidence
- 不把短期噪音写入 memory
- 不输出交易建议
