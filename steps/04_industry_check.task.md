# 任务 04：行业检查

读取：

- `prompts/00_master.md`
- `prompts/04_industry_check.md`
- `tasks/<task_id>/task.json`
- 当前股票的 `industry_memory_json`（如果路径不存在或文件缺失，视为 memory unavailable）

写入：

- `outputs/<task_id>/<ts_code>/04_industry_check.json`

校验：

- `schemas/industry_check.schema.json`

memory 缺失规则：

- 如果 `industry_memory_json` 路径缺失或文件不存在，本 step **不得失败**。
- 此时 memory 视为 unavailable，在 `uncertainties` 中说明缺少历史行业 memory。
- step 仍应基于行业标签和 agent 自身知识完成基本的行业检查。
- agent 自身知识只能作为背景推断，不得写入 `facts`；若无外部 evidence 支撑，必须放入 `inferences` 或 `uncertainties`，并根据证据充分性设置 `evidence_insufficient`。

evidence 落盘规则：

- 如果本 step 产生新的事实性 claim，必须写入：
  - `evidence/agent_outputs/<task_id>/<ts_code>/04_industry_check.evidence.jsonl`
- step 输出中的 `evidence_ids` 必须来自输入 evidence 或本 step 新生成的 evidence。
- 如果证据不足，必须设置 `evidence_insufficient=true`，并在 `uncertainties` 中说明缺口。

禁止：

- 不重复公司财务分析
- 不输出最终评级
