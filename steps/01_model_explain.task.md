# 任务 01：模型解释

读取：

- `prompts/00_master.md`
- `prompts/01_model_explain.md`
- `tasks/<task_id>/task.json`

只使用 `task.json` 中当前股票条目。

写入：

- `outputs/<task_id>/<ts_code>/01_model_explain.json`

校验：

- `schemas/model_explain.schema.json`

禁止：

- 不读取财务模板
- 不读取新闻或公告
- 不读取行业 memory
- 不输出最终评级
