# 第一步：模型解释

目的：

- 解释模型为什么选中这只股票。

只使用：

- `primary_model` — 主信号定义（horizon / target / description），理解 model_score 的业务语义。例如 "未来 60 天截面收益排序，越高越看好"
- `model_score` — 主信号打分，在 universe 内相对比较
- `feature_contrib.values` — 主信号因子贡献度数值
- `feature_contrib.universe_stats` — 各因子在全量候选中的分布，用于判断贡献度高低
- `feature_contrib.method` — 归因方法（SHAP / 线性权重 / 等），评估数值可靠性
- `auxiliary_signals[]` — 辅助信号列表。每项有 `name`、`description`、`value`、可选 `feature_contrib`。用于交叉验证主信号方向是否与其他信号一致

应该做：

- 对照 `primary_model.description` 理解 model_score 的业务含义
- 对照 `universe_stats` 判断各因子贡献的幅度（该值处于什么分位）
- 对照 `method` 评估归因可靠性
- 如果存在 `auxiliary_signals`，对比主信号与辅助信号的方向一致性。例如：主信号 60d return 高，辅助 180d z-score 也高 → 加分；主信号高但 60d_pos_prob 接近 0.5 → 不确定性高
- 总结驱动入选的主要特征，区分强驱动与弱驱动
- 说明模型逻辑中不完整或模糊的部分

约束：

- `feature_contrib.values` 的数值贡献可以解释模型信号的强弱和方向，**不能**替代财报、新闻、公告等外部证据。高的贡献度不等于基本面利好，低的贡献度也不等于基本面利空。
- `auxiliary_signals` 只用于对比信号方向的一致性，**不能**作为独立于主信号的选股依据。

不要做：

- 不看财务报表
- 不看新闻或公告
- 不展开行业周期讨论
- 不给最终评级
