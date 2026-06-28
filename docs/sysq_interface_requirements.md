# SysA 对 SysQ 的数据接口需求

SysA 消费 SysQ 每日产出的候选股票信号，做 LLM 研究评级。SysQ 只出数值，SysA 做 NL 解释。

## SysQ 每日输出（`outputs/{trade_date}/`）

每只候选股票（TopK，约 20 只）：

| 字段 | 说明 |
|------|------|
| `ts_code` / `name` | 代码和名称 |
| `model_score` | 模型打分。SysA 只在 universe 内做相对比较 |
| `feature_contrib` | 因子贡献度。需附带 **method**（shap / importance_weight / 其他）和 **universe_stats**（各因子在全量候选中的 min/max/mean/p50/p75/p90），否则 LLM 无法判断 0.31 是高是低 |
| `industry` | 行业分类标签 |

## 因子定义（非每日，因子变更时更新）

SysQ 独立维护一份因子 catalog（`features/factor_definitions.json`），每个因子含 `name`、`definition`、`type`、`range_note`。不改就不需要更新。

## 不开心路径

- 不要在 `feature_contrib` 里塞 NL 解释
- 不要预生成"选中原因"的文字说明
- 不要生成 memory
- `model_rank` 不需要，universe 已按 score 排序
- `factor_definitions` 不要塞入每日 task.json
