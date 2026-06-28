# 第一步：模型解释

目的：

- 解释模型为什么选中这只股票。

只使用：

- `model_horizon` / `model_target` — 模型预测什么、预测多久。例如 `model_horizon: "60d", model_target: "return"` 表示"该模型预测未来 60 天截面收益排序"。这决定了 model_score 的业务含义。
- `model_score` — 模型打分，在 universe 内相对比较
- `feature_contrib.values` — 因子贡献度数值
- `feature_contrib.universe_stats` — 各因子的分布统计，用于判断 0.31 在全量候选中的位置（高/中/低）
- `feature_contrib.method` — 归因方法，用于评估数值可靠性（SHAP / 线性权重 / 等）

应该做：

- 对照 `universe_stats` 判断各因子贡献的幅度（该值处于什么分位）
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
