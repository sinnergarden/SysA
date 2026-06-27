# 任务 03：新闻催化

读取：

- `prompts/00_master.md`
- `prompts/03_news_catalyst.md`
- `tasks/<task_id>/task.json`
- 当前股票的 `news_search_results_json`
- 当前股票的 `announcements_json`

写入：

- `outputs/<task_id>/<ts_code>/03_news_catalyst.json`

校验：

- `schemas/news_catalyst.schema.json`

禁止：

- 不重复做财务验证
- 不输出最终评级
