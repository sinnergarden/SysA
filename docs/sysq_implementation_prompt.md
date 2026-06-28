# SysQ 实现 prompt — 候选股票每日输出

## 需求

SysA 是一个 LLM 研究 agent，对 SysQ 每天产出的 TopK 候选股票做基本面研究，产出 A/B/C/D 评级。

你需要做的是：每天推理后，将结果写入 `outputs/{trade_date}/candidates.json`（逐日新增，不覆盖）。

## 数据要求

每只候选股票需要：

```json
{
  "ts_code": "002130.SZ",
  "name": "沃尔核材",
  "ranking_score": 1.0945,
  "models": [
    {
      "name": "60d_return", "horizon": "60d", "target": "return",
      "weight": 0.3, "score": 0.101,
      "feature_contrib": {
        "method": "shap",
        "values": {"holder_num_stale_days": -0.1003, "ret_60d": 0.0408},
        "universe_stats": {
          "holder_num_stale_days": {"min": -0.1064, "max": -0.0156, "mean": -0.0572, "p50": -0.0553, "p75": -0.0455, "p90": -0.0345}
        }
      }
    },
    {
      "name": "180d_return", "horizon": "180d", "target": "return",
      "weight": 0.7, "score": 1.5203,
      "feature_contrib": {
        "method": "shap",
        "values": {"turnover_rate": 0.1644, "margin_eligible": 0.1626},
        "universe_stats": {
          "turnover_rate": {"min": -0.0237, "max": 0.1644, "mean": 0.0366, "p50": 0.0288, "p75": 0.059, "p90": 0.0903}
        }
      }
    }
  ],
  "industry": "电气设备"
}
```

### 关键字段

| 字段 | 要求 |
|------|------|
| `ranking_score` | 融合排序分 |
| `models[].feature_contrib.values` | 最多保留 15 个 \|contrib\| 最高的因子，降序 |
| `models[].feature_contrib.universe_stats` | 必填。全量候选集分布 |
| `models[].feature_contrib.method` | 如实填写归因方法 |

### 约束

- `feature_contrib.values` 不含自然语言解释
- 不需要任何 NL 分析
- 不需要 memory 或外部数据
