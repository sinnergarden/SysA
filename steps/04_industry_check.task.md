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

禁止：

- 不重复公司财务分析
- 不输出最终评级
