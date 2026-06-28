# 第一步：模型解释

目的：

- 解释模型为什么选中这只股票。

只使用：

- `ranking_model.description` — 理解 TopK 排序信号如何生成
- `ranking_score` — 该股的排序分，仅在 universe 内做相对比较
- `models[]` — **核心分析对象**。每个模型有 `name`、`horizon`、`target`、`weight`（可选）、`score`、`feature_contrib`
- `models[].feature_contrib.values` — 该模型的因子贡献度数值
- `models[].feature_contrib.universe_stats` — 各因子在全量候选中的分布，用于判断贡献度高低
- `models[].feature_contrib.method` — 归因方法（SHAP / 线性权重 / 等），评估数值可靠性

应该做：

- 如果只有 1 个模型：正常解释该模型的因子归因
- 如果有多个模型：**对比各模型得分和归因的异同**。例如：60d 模型 earnings_revision 贡献 0.31 驱动 60d 高分，180d 模型同一因子贡献仅 0.18，说明短期信号主要来自盈利上修，长线更看重估值修复
- 根据各模型 weight（如有）说明融合方向偏向哪个时间维度
- 对照 `method` 评估归因可靠性
- 总结驱动入选的主要特征，区分强驱动与弱驱动
- 说明模型逻辑中不完整或模糊的部分

约束：

- `feature_contrib.values` 的数值贡献可以解释模型信号的强弱和方向，**不能**替代财报、新闻、公告等外部证据。高的贡献度不等于基本面利好，低的贡献度也不等于基本面利空。

不要做：

- 不看财务报表
- 不看新闻或公告
- 不展开行业周期讨论
- 不给最终评级
