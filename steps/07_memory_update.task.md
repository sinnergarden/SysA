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

evidence 落盘规则：

- 如果本 step 产生新的事实性 claim，必须写入：
  - `evidence/agent_outputs/<task_id>/<ts_code>/07_memory_update.evidence.jsonl`
- step 输出中的 `evidence_ids` 必须来自输入 evidence 或本 step 新生成的 evidence。
- 如果证据不足，必须设置 `evidence_insufficient=true`，并在 `uncertainties` 中说明缺口。

禁止：

- 不改写原始 evidence
- 不把短期噪音写入 memory
- 不输出交易建议
