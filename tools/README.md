# tools 说明

这个目录只放很薄的确定性工具：

- `validate_json.py`：校验 JSON 是否符合 schema
- `advance_state.py`：在 step 成功或失败后更新 `state.json`

这里不放：

- LLM 调用
- 爬虫
- 真实数据接入
- 复杂调度器
