# SysA → TradingAgents-CN 设计迁移备忘

SysA repo 停止开发，设计成果迁移到 TradingAgents-CN。以下是在 SysA 中已确认的关键设计，直接复用，不要重新发明。

## 1. SysQ 信号接口（已跑通）

TradingAgents-CN 需要一个 pre-screener agent 接收以下格式：

```json
{
  "ts_code": "600580.SH",
  "name": "卧龙电驱",
  "ranking_score": 2.9594,
  "models": [
    {
      "name": "60d_return", "horizon": "60d", "target": "return", "weight": 0.3, "score": 1.3776,
      "feature_contrib": {
        "method": "shap",
        "values": {"$op_cashflow": 0.0118, "ret_60d": 0.0104},
        "universe_stats": {"$op_cashflow": {"min": -0.0231, "max": 0.0161, "mean": 0.0013, "p50": 0.0026, "p75": 0.0063, "p90": 0.009}}
      }
    }
  ],
  "industry": "电气设备"
}
```

**关键约束**：
- `feature_contrib.values` 最多 15 个因子，按 |contrib| 降序
- `universe_stats` **必填**，否则 LLM 无法判断 0.0118 是高是低
- `feature_contrib.method` 如实填写（shap / 等），LLM 据此评估归因可靠性

## 2. 两步法研究流程

| 步骤 | 做什么 | 注意事项 |
|------|--------|---------|
| Step A 数据就绪 | 检查数据可用性，拉取缺失数据，做轻量汇总 | 缺失不得失败，诚实标记 |
| Step B 综合研究 | 先行业判断，再逐股 A/B/C/D 评级 | 每个结论绑定 evidence source |

**不要做 7 步串行链**——01~07 之间没有实质依赖，LLM 一次读完出结论更高效。

## 3. 研究输出结构

```json
{
  "rating": "B",
  "confidence": "medium",
  "evidence_ids": ["2026-06-26_600580.SH_models"],
  "evidence_insufficient": true,
  "facts": [],
  "inferences": [],
  "uncertainties": [],
  "memory_patch": [{"op": "add", "target": "company", "text": "", "reason": ""}]
}
```

**硬规则**：
- 每个关键结论必须绑定 `evidence_id` 或设 `evidence_insufficient=true`
- `facts`/`inferences`/`uncertainties` 三层严格分离
- `data_sufficiency` 标记为 missing 的数据不得在 B 中假装已读取
- `financial_assessment = against` 时最高评级不超过 C

## 4. 财务数据策略

| 数据类型 | 推荐来源 | 说明 |
|---------|---------|------|
| 结构化财务指标 | Tushare / AKShare | TradingAgents-CN 已接入 |
| MD&A 变化趋势 | 巨潮资讯网 PDF | 如有余力再从 PDF 解析 |
| 新闻/公告 | AKShare / Tushare | TradingAgents-CN 已接入 |

**数据结构化指标已经够做基本面验证了。MD&A 是加分项，不是必须项。**

## 5. 评级含义（不是交易信号）

- `A`：强验证，反证有限，值得优先深挖
- `B`：支持证据存在但关键不确定性仍在
- `C`：支持一般、证据不完整
- `D`：主要证据不支持模型逻辑

## 6. 跨期 memory

每次研究的 stable conclusion 沉淀为 `memory_patch`，含 `op`（add/update/delete/no_change）、`target`（company/industry）、`text`、`reason`。下期研究时作为先验输入，减少重复分析。
