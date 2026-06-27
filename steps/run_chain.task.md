# Run Chain

Purpose:

- Execute the research chain for each symbol in `tasks/<task_id>/task.json`
- Support stop-on-failure and resume from `state.json`

Execution order:

1. `01_model_explain`
2. `02_financial_check`
3. `03_news_catalyst`
4. `04_industry_check`
5. `05_bear_case`
6. `06_final_rating`
7. `07_memory_update`

Rules:

- Process each symbol independently.
- For each step, read the matching `steps/<step>.task.md`.
- After each step:
  - confirm output file exists
  - validate with the matching schema
  - update `tasks/<task_id>/state.json`
- If step output already exists and passes schema validation, rerun may skip it.
- If any step fails:
  - stop immediately
  - record `failed_step`
  - record `failure_reason`
  - set `status` to `failed`
- Resume uses:
  - `current_symbol`
  - `next_step`

State expectations:

- `pending`: chain not started
- `running`: currently in progress
- `failed`: stopped due to a step error
- `completed`: all symbols finished through `07_memory_update`
