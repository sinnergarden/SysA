# 任务 06：最终评级

读取：

- `prompts/00_master.md`
- `prompts/06_final_rating.md`
- `outputs/<task_id>/<ts_code>/01_model_explain.json`
- `outputs/<task_id>/<ts_code>/02_financial_check.json`
- `outputs/<task_id>/<ts_code>/03_news_catalyst.json`
- `outputs/<task_id>/<ts_code>/04_industry_check.json`
- `outputs/<task_id>/<ts_code>/05_bear_case.json`

写入：

- `outputs/<task_id>/<ts_code>/06_final_rating.json`

校验：

- `schemas/final_rating.schema.json`

evidence 落盘规则：

- 如果本 step 产生新的事实性 claim，必须写入：
  - `evidence/agent_outputs/<task_id>/<ts_code>/06_final_rating.evidence.jsonl`
- step 输出中的 `evidence_ids` 必须来自输入 evidence 或本 step 新生成的 evidence。
- 如果证据不足，必须设置 `evidence_insufficient=true`，并在 `uncertainties` 中说明缺口。

禁止：

- 不发明新证据
- 不写交易建议
