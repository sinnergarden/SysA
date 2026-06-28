# 任务 01：模型解释

读取：

- `prompts/00_master.md`
- `prompts/01_model_explain.md`
- `tasks/<task_id>/task.json`（当前股票条目 + 全局 `ranking_model`）

只使用 `task.json` 中当前股票条目和全局 `ranking_model`。核心数据是 `models[]` 数组——每个模型有独立的 score、feature_contrib、universe_stats。对比多模型的归因异同是 step 01 的核心分析。

写入：

- `outputs/<task_id>/<ts_code>/01_model_explain.json`

校验：

- `schemas/model_explain.schema.json`

evidence 落盘规则：

- 如果本 step 产生新的事实性 claim，必须写入：
  - `evidence/agent_outputs/<task_id>/<ts_code>/01_model_explain.evidence.jsonl`
- step 输出中的 `evidence_ids` 必须来自输入 evidence 或本 step 新生成的 evidence。
- 如果证据不足，必须设置 `evidence_insufficient=true`，并在 `uncertainties` 中说明缺口。

禁止：

- 不读取财务模板
- 不读取新闻或公告
- 不读取行业 memory
- 不输出最终评级
