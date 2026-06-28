# SysA 对 SysQ 的数据接口需求

SysA 消费 SysQ 每日产出的候选股票信号，做 LLM 研究评级。

## 一、SysQ 每日输出

SysQ 每日推理后，在 SysQ 自身的 `outputs/{trade_date}/` 目录写一个文件（非 SysA 的 `outputs/`），格式和命名由 SysQ 自定，thin runner 负责读取解析并组装成 SysA 的 `tasks/{trade_date}/task.json`。

但作为双方约定，建议一份 JSON：

```json
{
  "date": "2026-06-27",
  "model_horizon": "60d",
  "model_target": "return",           // 预测目标：return / rank / excess_return
  "universe": [
    {
      "ts_code": "000001.SZ",
      "name": "平安银行",
      "model_score": 0.82,
      "feature_contrib": {
        "method": "shap",
        "values": {
          "earnings_revision": 0.31,
          "valuation_spread": 0.22
        },
        "universe_stats": {
          "earnings_revision": {"min": -0.50, "max": 0.80, "mean": 0.10, "p50": 0.08, "p75": 0.25, "p90": 0.45},
          "valuation_spread": {"min": -0.30, "max": 0.60, "mean": 0.05, "p50": 0.04, "p75": 0.18, "p90": 0.35}
        }
      },
      "industry": "银行"
    }
  ]
}
```

### model_score 语义

SysQ 的 `model_score` 不是黑盒数值，SysA 的 LLM 需要知道它**代表什么**才能做解释。

| 元数据 | 必需 | 说明 |
|--------|------|------|
| `model_horizon` | 是 | 预测周期，如 `"60d"` / `"180d"`。多个时间段可用数组 |
| `model_target` | 是 | 预测目标：`return`（收益率）/ `rank`（排序分）/ `excess_return`（超额收益） |

示例：`model_horizon: "60d"`, `model_target: "return"` → "该模型预测未来 60 天收益，分数越高预期收益越高，选股依据是截面排序。"

### feature_contrib 语义

原始数值对 LLM 无意义。必须附带归因方法和全量分布统计，否则 LLM 无法判断 0.31 是高是低。

## 二、因子定义目录（非每日）

SysQ 独立维护一份因子 catalog（`features/factor_definitions.json`），每个因子含 `name`、`definition`、`type`、`range_note`。只在因子工程变更时更新。

SysA 在需要时读取，不塞入每日 task.json。

## 三、边界约束

- SysQ 的 `outputs/` 和 SysA 的 `outputs/` 是不同目录
- `feature_contrib` 不包含 NL 解释文本
- model_score 不带"选中原因"的文字说明
- SysQ 不管理 memory
- 候选列表已按 model_score 降序，不需要额外 rank
