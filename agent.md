# SysA 总设计说明

## 系统目标

`SysA` 是一个面向 `Qsys` 候选股票研究的文件系统任务链框架。它的目标是把：

- 模型候选股票
- 财报模板
- 新闻与公告检索结果
- 公司 memory
- 行业 memory

转成：

- 结构化 research evidence
- 分步 JSON 输出
- 最终研究评级
- memory 更新建议

整个过程要求可审计、可重跑、可恢复。

## 非目标

`SysA` 不做以下事情：

- 不生成交易指令
- 不连接券商或交易系统
- 不自动下单
- 不接入数据库、消息队列、Web 服务
- 不在 Python 中写研究推理逻辑
- 不内置 LLM API 调用
- 不实现复杂抓取框架

## 输入

主输入是 `tasks/<task_id>/task.json`，其中包含：

- 任务元信息
- 候选股票列表
- 每只股票对应的输入文件路径

可选支持材料包括：

- 财务模板 JSON
- 公司 memory JSON
- 行业 memory JSON
- 新闻检索结果 JSON
- 公告 JSON

## 输出

每只股票独立输出到自己的目录：

- `outputs/<task_id>/<ts_code>/01_model_explain.json`
- `outputs/<task_id>/<ts_code>/02_financial_check.json`
- `outputs/<task_id>/<ts_code>/03_news_catalyst.json`
- `outputs/<task_id>/<ts_code>/04_industry_check.json`
- `outputs/<task_id>/<ts_code>/05_bear_case.json`
- `outputs/<task_id>/<ts_code>/06_final_rating.json`
- `outputs/<task_id>/<ts_code>/07_memory_update.json`

这种单股票目录粒度是故意设计的，目的是：

- 方便单票重跑
- 方便失败恢复
- 方便未来并行化
- 避免多股票混写一个 JSON

## evidence / memory / output 的区别

### evidence

`evidence` 是证据层，不是结论层。它保存：

- 来源
- 标题
- 抽取事实
- claim
- 可靠度
- 原始引用位置

后续 step 通过 `evidence_id` 引用它。

### memory

`memory` 是长期认知层，只存稳定、可复用、跨期仍有意义的认知，比如：

- 公司长期经营特征
- 重复出现的风险点
- 行业景气与供需的结构性规律

以下内容不应进入 memory：

- 单日新闻情绪
- 短期价格波动
- 未验证传闻
- 一次性题材噪音

### output

`output` 是阶段结论层。每一步都必须输出 JSON，所有关键判断必须：

- 绑定 `evidence_id`
- 或显式标注 `evidence_insufficient`

## 任务链执行方式

执行顺序固定为：

1. `01_model_explain`
2. `02_financial_check`
3. `03_news_catalyst`
4. `04_industry_check`
5. `05_bear_case`
6. `06_final_rating`
7. `07_memory_update`

每一步都只读取：

- 当前股票
- 该步所需输入
- 该步明确依赖的前序输出

不默认重新塞入所有原始材料。

## 每个 step 的职责边界

### 01 模型解释

只解释模型为何选中该股票，只看 `model_score` 与 `feature_contrib`，不看财报、新闻、行业。

### 02 财务验证

只检查财务模板是否支持模型逻辑，不扩写新闻、行业或最终评级。

### 03 新闻催化

只看近期新闻、公告、研报标题、互动易等近期信息，区分基本面催化与情绪热度，不把热度直接当利好。

### 04 行业检查

只判断行业供需、景气度、产业链位置、概念炒作风险，可参考行业 memory。

### 05 反证与风险

只主动找反证、脆弱点和逻辑漏洞，挑战前面形成的乐观叙事。

### 06 最终评级

只汇总 `01~05` 的结构化输出，给出研究评级和置信度，不补造新证据，不写交易建议。

### 07 memory 更新建议

只输出压缩后的长期认知更新建议，不自动写回 memory 文件，不把短期噪音沉淀进去。

## 失败恢复机制

`tasks/<task_id>/state.json` 负责保存执行状态，包括：

- 当前股票
- 下一步
- 已完成步骤
- 失败步骤
- 失败原因
- 更新时间

恢复规则：

- 任一步失败，立即停止
- 写入 `failed_step`、`failure_reason`、`status=failed`
- 修复后从 `current_symbol + next_step` 恢复
- 如果输出文件已存在且通过 schema 校验，可跳过重跑

## JSON 落盘规范

- 所有输出必须是合法 JSON
- 所有路径应尽量使用相对路径
- 每步每票只写一个 JSON 输出文件
- 所有关键判断绑定 `evidence_id`
- 输入不足时输出 `insufficient` 或 `unknown`
- 不允许脑补和编造

## evidence_id 规范

推荐格式：

- `{ts_code}_{step}_{index}`

例如：

- `000001.SZ_news_001`

同一任务日内，`evidence_id` 必须唯一。

## 评级标准

- `A`：模型逻辑清楚，财务或行业验证强，近期催化明确，反证有限，值得优先人工深挖
- `B`：存在一定支持证据，但关键不确定性仍在，值得继续跟踪
- `C`：支持一般、证据不完整、催化偏弱或反证较多，暂不优先
- `D`：主要证据不支持模型逻辑，或风险明显高于研究价值，低优先级

这里的评级含义是研究优先级和人工关注等级，不是交易指令。

## confidence 标准

- `high`：关键判断有多条高可靠证据支撑，冲突较少
- `medium`：有部分证据支持，但仍有缺口或冲突
- `low`：证据明显不足、来源较弱或关键问题未解决

## 禁止自动交易

`SysA` 不得自动生成：

- 买卖建议
- 目标价
- 仓位建议
- 执行指令
- 自动下单动作

它只输出研究评级与研究依据。
