# 任务 04：行业检查

读取：

- `prompts/00_master.md`
- `prompts/04_industry_check.md`
- `tasks/<task_id>/task.json`
- 当前股票的 `industry_memory_json`

写入：

- `outputs/<task_id>/<ts_code>/04_industry_check.json`

校验：

- `schemas/industry_check.schema.json`

evidence 落盘规则：

- 如果本 step 产生新的事实性 claim，必须写入：
  - `evidence/agent_outputs/<task_id>/<ts_code>/04_industry_check.evidence.jsonl`
- step 输出中的 `evidence_ids` 必须来自输入 evidence 或本 step 新生成的 evidence。
- 如果证据不足，必须设置 `evidence_insufficient=true`，并在 `uncertainties` 中说明缺口。

禁止：

- 不重复公司财务分析
- 不输出最终评级
