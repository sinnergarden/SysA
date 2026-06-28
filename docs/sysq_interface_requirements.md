# SysA 对 SysQ 的数据接口需求

SysA 消费 SysQ 每日产出的候选股票信号，做 LLM 研究评级。

## SysQ 每日输出

SysQ 每日推理后，在 `outputs/{trade_date}/candidates.json` 写入候选股票数据。文件格式自定，关键字段见下方说明。SysA 直接读取该目录。

### 数据要求

每只候选股票（按融合分降序 Top20）：

```json
{
  "trade_date": "2026-06-27",
  "ranking_model": {
    "description": "0.3 * 60d_return + 0.7 * 180d_return 融合排序分，按此分选股"
  },
  "universe": [
    {
      "ts_code": "000001.SZ",
      "name": "平安银行",
      "ranking_score": 0.80,
      "models": [
        {
          "name": "60d_return",
          "horizon": "60d",
          "target": "return",
          "weight": 0.3,
          "score": 0.82,
          "feature_contrib": {
            "method": "shap",
            "values": {"earnings_revision": 0.31, "valuation_spread": 0.22},
            "universe_stats": {
              "earnings_revision": {"min": -0.50, "max": 0.80, "mean": 0.10, "p50": 0.08, "p75": 0.25, "p90": 0.45}
            }
          }
        },
        {
          "name": "180d_return",
          "horizon": "180d",
          "target": "return",
          "weight": 0.7,
          "score": 0.76,
          "feature_contrib": {
            "method": "shap",
            "values": {"earnings_revision": 0.18, "valuation_spread": 0.09},
            "universe_stats": { ... }
          }
        }
      ],
      "industry": "银行"
    }
  ]
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `ranking_score` | 融合分，仅用于排名选股，不参与因子解释 |
| `models[]` | N 个独立模型的归因数组。每个模型有 score、feature_contrib（method + values + universe_stats）、horizon/target |
| `models[].weight` | 可选。在融合排序中的权重 |
| `models[].feature_contrib.values` | 最多保留 15 个 \|contrib\| 最高的因子，按绝对值降序 |
| `models[].feature_contrib.universe_stats` | 该因子在全量候选上的分布（min/max/mean/p50/p75/p90），必填 |
| `industry` | 行业分类标签 |

### 约束

- `feature_contrib.values` 不含 NL 解释
- `models[]` 不存在"主/辅"等级，所有模型是平等独立的归因视角
- `ranking_score` 仅用于选股，不带"选中原因"说明
- SysQ 不管理 memory
- SysQ 不产出外部数据（财报/新闻/公告）
