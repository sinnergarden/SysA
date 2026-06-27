# 任务 05：反证与风险

读取：

- `prompts/00_master.md`
- `prompts/05_bear_case.md`
- `outputs/<task_id>/<ts_code>/01_model_explain.json`
- `outputs/<task_id>/<ts_code>/02_financial_check.json`
- `outputs/<task_id>/<ts_code>/03_news_catalyst.json`
- `outputs/<task_id>/<ts_code>/04_industry_check.json`

写入：

- `outputs/<task_id>/<ts_code>/05_bear_case.json`

校验：

- `schemas/bear_case.schema.json`

evidence 落盘规则：

- 如果本 step 产生新的事实性 claim，必须写入：
  - `evidence/agent_outputs/<task_id>/<ts_code>/05_bear_case.evidence.jsonl`
- step 输出中的 `evidence_ids` 必须来自输入 evidence 或本 step 新生成的 evidence。
- 如果证据不足，必须设置 `evidence_insufficient=true`，并在 `uncertainties` 中说明缺口。

禁止：

- 不输出最终评级
- 不更新 memory
