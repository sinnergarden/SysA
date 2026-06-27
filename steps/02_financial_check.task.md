# 任务 02：财务验证

读取：

- `prompts/00_master.md`
- `prompts/02_financial_check.md`
- `tasks/<task_id>/task.json`
- 当前股票的 `financial_template_json`
- `outputs/<task_id>/<ts_code>/01_model_explain.json`

写入：

- `outputs/<task_id>/<ts_code>/02_financial_check.json`

校验：

- `schemas/financial_check.schema.json`

evidence 落盘规则：

- 如果本 step 产生新的事实性 claim，必须写入：
  - `evidence/agent_outputs/<task_id>/<ts_code>/02_financial_check.evidence.jsonl`
- step 输出中的 `evidence_ids` 必须来自输入 evidence 或本 step 新生成的 evidence。
- 如果证据不足，必须设置 `evidence_insufficient=true`，并在 `uncertainties` 中说明缺口。

禁止：

- 不用新闻或公告逻辑代替验证
- 不输出行业结论
- 不输出最终评级
