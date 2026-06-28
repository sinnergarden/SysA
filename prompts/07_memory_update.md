# 第七步：memory 更新建议

目的：

- 基于稳定结论，提出长期 memory 的压缩更新建议。

应该做：

- 只写长期可复用的公司或行业认知。
- 保持简短、稳定、可跨期复用。
- 如果没有必要更新，应明确说明。
- memory patch 必须输出为结构化对象数组，而不是字符串数组。
- patch 对象字段为：`op`、`target`、`text`、`reason`、`evidence_ids`。
- `op` 只能是 `add / update / delete / no_change`。
- `target` 只能是 `company / industry`。

不要做：

- 不存单日情绪
- 不存短期价格波动
- 不存未验证传闻
- 不给交易建议
