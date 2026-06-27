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

禁止：

- 不用新闻或公告逻辑代替验证
- 不输出行业结论
- 不输出最终评级
