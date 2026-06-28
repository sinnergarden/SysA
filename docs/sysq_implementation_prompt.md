# SysQ 实现 prompt — 候选股票每日输出

> 这是给 SysQ 开发的 prompt。请按此实现每日候选股票输出。

---

## 需求

SysA 是一个 LLM 研究 agent，对 SysQ 每天产出的 TopK 候选股票做基本面研究，产出 A/B/C/D 评级。

SysA **不**接交易、**不**内置 LLM、**不**写 Python 推理逻辑。它只消费你的数值信号，用 LLM 做解释。

你需要做的是：每天推理后，把结果 dump 到一个约定目录，格式如下。

---

## 你的输出格式

文件位置：**SysQ 项目下 `outputs/{trade_date}/candidates.json`**，逐日新增，不覆盖。

每只股票的内容：

```json
{
  "ts_code": "000001.SZ",
  "name": "平安银行",
  "ranking_score": 0.80,
  "ranking_weight": [0.3, 0.7],
  "ranking_note": "0.3 * 60d_return + 0.7 * 180d_return",
  "models": [
    {
      "name": "60d_return",
      "horizon": "60d",
      "target": "return",
      "weight": 0.3,
      "score": 0.82,
      "feature_contrib": {
        "method": "shap",
        "values": {
          "earnings_revision": 0.31,
          "valuation_spread": 0.22,
          "profit_quality": 0.18
        },
        "universe_stats": {
          "earnings_revision": {"min": -0.50, "max": 0.80, "mean": 0.10, "p50": 0.08, "p75": 0.25, "p90": 0.45},
          "valuation_spread": {"min": -0.30, "max": 0.60, "mean": 0.05, "p50": 0.04, "p75": 0.18, "p90": 0.35},
          "profit_quality": {"min": -0.40, "max": 0.55, "mean": 0.06, "p50": 0.05, "p75": 0.15, "p90": 0.30}
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
        "values": {
          "earnings_revision": 0.18,
          "valuation_spread": 0.09,
          "profit_quality": 0.06
        },
        "universe_stats": {
          "earnings_revision": {"min": -0.50, "max": 0.80, "mean": 0.10, "p50": 0.08, "p75": 0.25, "p90": 0.45},
          "valuation_spread": {"min": -0.30, "max": 0.60, "mean": 0.05, "p50": 0.04, "p75": 0.18, "p90": 0.35}
        }
      }
    }
  ],
  "industry": "银行"
}
```

---

## 每步怎么做

### 1. 推荐信号

具体信号与公式，可以由传入参数来定，这里只是提供一个例子。

| 做什么 | 结果 |
|--------|------|
| 读取两个模型（60d / 180d）当天的原始打分 | `score_60d`, `score_180d` |
| 计算融合分 | `ranking_score = 0.3 * score_60d + 0.7 * score_180d` |
| 按 `ranking_score` 全量降序取前 20 | 进入 SysA 研究候选池 |
| 填入 `ranking_weight`, `ranking_note` | 告知系数的组合方式 |

### 2. 因子贡献度

| 做什么 | 结果 |
|--------|------|
| 对入选的每只股票，分别跑**两个模型的 SHAP** | 每只股票 2 套 `feature_contrib` |
| 保留 | `method`（填 shap/permutation_importance/linear_weight/...) |
| 保留 | `values`（最多 15 个 SHAP 绝对值最高的因子，降序） |
| 保留 | `universe_stats`（每个因子在全量候选上的 min/max/mean/p50/p75/p90） |

> `universe_stats` 用全量候选股票池计算，不是只算这 20 只。

### 3. 不需要做的

- 不需要自然语言解释
- 不需要生成`选中原因`
- 不需要产出 `feature_contrib` 以外的任何推理
- 不需要管理公司/行业 memory

---

## 存放约定

```
SysQ 项目/outputs/2026-06-27/candidates.json     ← 你写这里

SysA 项目/tasks/2026-06-27/task.json             ← thin runner 读完你之后组装到这里
```

不要直接写 SysA 的目录。

---

## 检查清单

- [ ] 每天推理后生成 `outputs/{trade_date}/candidates.json`
- [ ] `feature_contrib.values` 最多 15 个因子
- [ ] `universe_stats` 用全量候选池计算
- [ ] `feature_contrib.method` 如实填写
- [ ] 不包含自然语言解释
- [ ] 每日文件不覆盖前一日
