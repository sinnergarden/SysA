# SysA 对 SysQ 的数据接口需求

SysA 消费 SysQ 每日产出的候选股票信号，做 LLM 研究评级。

---

## 一、SysQ 每日输出

SysQ 每日推理后，在 **SysQ 自身的 `outputs/{trade_date}/`** 目录（不是 SysA 的 `outputs/`）写一个文件。格式和命名由 SysQ 自定，thin runner 负责读取并组装成 SysA 的 `tasks/{trade_date}/task.json`。

### 内容要求

每只候选股票需要：

| 数据 | 说明 |
|------|------|
| `ts_code` / `name` | 代码和名称 |
| `model_score` | 主信号模型打分。SysA 在 universe 内做相对比较 |
| `feature_contrib` | 因子贡献度。含 `method`（归因方法）、`values`（因子→数值映射，最多保留 15 个 |contrib| 最高的因子）、`universe_stats`（全量候选分布统计，LLM 据此判断 0.31 是高是低） |
| `auxiliary_signals` | （可选）辅助信号数组，如其他时间维度的 z-score、概率预估值。每项含 `name` / `description` / `value` / 可选 `feature_contrib` |
| `industry` | 行业分类标签 |

### 全局元数据

| 字段 | 说明 |
|------|------|
| `primary_model` | 主信号定义。含 `horizon`（如 "60d"）、`target`（如 "return"）、`description`（供 LLM 理解业务语义的自然语言说明） |
| `trade_date` | 交易日 |

### 示例

```json
{
  "date": "2026-06-27",
  "primary_model": {
    "horizon": "60d",
    "target": "return",
    "description": "未来 60 天截面收益排序，越高越看好"
  },
  "universe": [
    {
      "ts_code": "000001.SZ",
      "name": "平安银行",
      "model_score": 0.82,
      "feature_contrib": {
        "method": "shap",
        "values": {"earnings_revision": 0.31, "valuation_spread": 0.22},
        "universe_stats": {
          "earnings_revision": {"min": -0.50, "max": 0.80, "mean": 0.10, "p50": 0.08, "p75": 0.25, "p90": 0.45},
          "valuation_spread": {"min": -0.30, "max": 0.60, "mean": 0.05, "p50": 0.04, "p75": 0.18, "p90": 0.35}
        }
      },
      "auxiliary_signals": [
        {"name": "180d_return_zscore", "description": "180 天收益全量 z-score", "value": 1.24},
        {"name": "60d_pos_prob", "description": "60 天正收益概率", "value": 0.68}
      ],
      "industry": "银行"
    }
  ]
}
```

---

## 二、因子定义目录（非每日）

SysQ 独立维护一份因子 catalog（`features/factor_definitions.json`），每个因子含 `name`、`definition`、`type`、`range_note`。只在因子工程变更时更新。不塞入每日数据。

---

## 三、边界约束

- SysQ 的 `outputs/` 和 SysA 的 `outputs/` 是不同的目录
- `feature_contrib` 不含 NL 解释文本
- model_score 不带"选中原因"的文字说明
- `auxiliary_signals` 只作为参考信号，不作为独立选股依据
- SysQ 不管理 memory
