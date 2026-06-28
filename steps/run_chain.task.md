# 任务链执行说明

目的：

- 对 `tasks/<task_id>/task.json` 中的每只股票执行完整研究链
- 支持失败停止与基于 `state.json` 的恢复

执行顺序：

1. `01_model_explain`
2. `02_financial_check`
3. `03_news_catalyst`
4. `04_industry_check`
5. `05_bear_case`
6. `06_final_rating`
7. `07_memory_update`

规则：

- 每只股票独立执行。
- 每一步都读取对应的 `steps/<step>.task.md`。
- 每步结束后必须：
  - 检查输出文件存在
  - 用对应 schema 做校验
  - 更新 `tasks/<task_id>/state.json`
- 如果输出文件已经存在且通过 schema 校验，可选择跳过重跑。
- 任一步失败时：
  - 立即停止
  - 记录 `failed_step`
  - 记录 `failure_reason`
  - 把 `status` 设为 `failed`
- 恢复时使用：
  - `current_symbol`
  - `next_step`

状态含义：

- `pending`：尚未开始
- `running`：执行中
- `failed`：某一步失败后停止
- `completed`：所有股票都执行到 `07_memory_update`
