# 第六步：最终评级

目的：

- 汇总前五步的结构化输出，给出最终研究评级。

应该做：

- 输出 `A / B / C / D`
- 输出 `high / medium / low`
- 汇总模型逻辑、财务验证、行业验证、新闻催化和反证情况
- 输出 `rating_rationale`
- 说明为什么不能给更高评级
- 说明为什么也不该给更低评级
- 如果 `financial_validation = against`，最高评级不得超过 `C`，除非 `rating_rationale` 明确解释例外。
- 如果关键 step 存在 `evidence_insufficient = true`，则 `confidence` 不得为 `high`。
- 如果 `catalyst_heat = overheated` 且 `bear_cases` 非空，则最高评级通常不得超过 `B`。
- 最终评级是研究优先级，不是交易建议。

不要做：

- 不发明新证据
- 不给交易建议
- 不输出 JSON 之外的散文
