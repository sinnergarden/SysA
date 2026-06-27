# SysA 构建 Prompt

下面保留的是用于搭建本仓库骨架的完整需求 prompt。

---

你是资深工程化 agent framework 架构师。请为 `Qsys` 量化选股系统新增一个 **最小可运行** 的 `Research Agent` repo 骨架。

目标不是做交易系统，也不是做一个大 prompt 一次跑完，而是做一个 **基于文件系统、可重跑、可审计、step-based 的研究任务链**。该 repo 只依赖 Claude Code / OpenClaw / Codex 这类代码 agent 去执行 markdown task，不依赖 OpenAI API，不内置 LLM 调用。

`Qsys` 已经能产出每日 `TopK` 候选股票、模型分数、feature contribution、财报模板数据。现在需要一个 research repo，让 agent 基于这些输入，再结合外部新闻/公告搜索结果、company memory、industry memory，产出：

- 结构化 research evidence
- 分步 JSON 输出
- 最终研究评级
- 压缩后的长期 memory 更新建议

只输出研究结论和人工关注等级，**不得生成自动交易指令，不得接交易，不得下单**。

## 一、核心原则

1. 不是一个大 prompt 一次跑完，而是 `step-based task chain`。
2. 每一步都是独立 markdown task，可单独执行、失败可重跑。
3. 每一步只读取 **必要输入** 与 **指定前序 JSON 输出**，不反复塞入所有原始材料。
4. 所有中间结果必须落盘。
5. `evidence` 全量保存，`memory` 只保存压缩后的长期认知。
6. Python 只做确定性状态机、schema 校验、文件读写辅助，不负责 LLM 推理。
7. 不接交易，不自动下单，只输出研究结论和人工关注等级。
8. 所有路径使用相对路径。
9. repo 初始状态应可直接 commit。

## 二、系统目标

这个 repo 的目标是：

- 接收 `Qsys` 生成的每日研究任务输入
- 对每只股票按固定步骤完成研究链
- 每一步输出结构化 JSON
- 形成最终 `A/B/C/D` 评级与 `high/medium/low` confidence
- 保留证据、分步结论、最终结论与长期 memory 更新建议
- 支持失败恢复和从 `state.json` 继续执行

## 三、非目标

以下内容 **不要实现**：

- 不要接入真实交易
- 不要生成买卖下单指令
- 不要写复杂爬虫
- 不要写任何 LLM API 调用
- 不要做复杂调度框架
- 不要引入数据库、消息队列、Web 服务
- 不要做过度复杂 schema
- 不要在 Python 中硬编码研究推理逻辑

## 四、目录结构

请创建如下目录结构：

```text
qsys_agent/
  README.md
  agent.md

  prompts/
    00_master.md
    01_model_explain.md
    02_financial_check.md
    03_news_catalyst.md
    04_industry_check.md
    05_bear_case.md
    06_final_rating.md
    07_memory_update.md

  steps/
    01_model_explain.task.md
    02_financial_check.task.md
    03_news_catalyst.task.md
    04_industry_check.task.md
    05_bear_case.task.md
    06_final_rating.task.md
    07_memory_update.task.md
    run_chain.task.md

  schemas/
    task.schema.json
    state.schema.json
    model_explain.schema.json
    financial_check.schema.json
    news_catalyst.schema.json
    industry_check.schema.json
    bear_case.schema.json
    final_rating.schema.json
    memory_update.schema.json
    evidence.schema.json

  tasks/
    sample_2026-06-27/
      task.json
      state.json

  outputs/
    sample_2026-06-27/
      000001.SZ/
        .gitkeep
      600000.SH/
        .gitkeep

  evidence/
    raw/
      .gitkeep
    parsed/
      .gitkeep
    agent_outputs/
      .gitkeep

  memory/
    company/
      sample_company_memory.json
    industry/
      sample_industry_memory.json

  tools/
    README.md
    validate_json.py
    advance_state.py
```

## 五、执行粒度与输出组织

必须采用 **单股票独立输出目录**。

也就是说：

- `tasks/sample_2026-06-27/task.json` 可以包含多只股票
- 但每只股票的 step 输出必须分别写入：
  - `outputs/sample_2026-06-27/000001.SZ/01_model_explain.json`
  - `outputs/sample_2026-06-27/000001.SZ/02_financial_check.json`
  - ...
  - `outputs/sample_2026-06-27/000001.SZ/06_final_rating.json`
  - `outputs/sample_2026-06-27/000001.SZ/07_memory_update.json`
- 另一只股票同理，写到自己的目录

这样做是为了：

- 支持按股票单独失败恢复
- 避免多股票混写一个 JSON 导致定位困难
- 方便未来扩展成并行执行

## 六、evidence / memory / output 的区别

请在 `agent.md` 中明确说明：

### 1. evidence

- 是研究过程中引用的事实性材料或从事实材料中抽取出的结构化证据
- 可以来自财报、公告、新闻、研报标题、互动易摘要、行业数据摘要等
- 必须尽量保留原始出处信息
- 必须允许后续 step 通过 `evidence_id` 引用
- `evidence` 是“证据层”，不是结论层

### 2. memory

- 是压缩后的长期认知摘要
- 只保存稳定、可复用、跨期仍有意义的认识
- 不能把短期噪音、单日新闻情绪、单日价格波动直接写入 memory
- `memory` 是“长期知识层”，不是原始材料层

### 3. output

- 是每个研究 step 的结构化判断结果
- 属于“阶段结论层”
- 必须是 JSON
- 必须绑定 evidence_id，或明确标注 `evidence_insufficient`

## 七、evidence_id 规则

请在 schema 与文档中固定如下约束：

- 每条 evidence 必须有唯一 `evidence_id`
- 推荐格式：`{ts_code}_{step}_{index}`
- 例如：`000001.SZ_news_001`
- `evidence_id` 在单个任务日内必须唯一
- step 输出中的所有关键判断，都必须引用至少一个 `evidence_id`
- 如果没有足够证据支撑，必须显式写 `evidence_insufficient: true`

`evidence.schema.json` 至少包含这些字段：

- `evidence_id`
- `ts_code`
- `step`
- `source_type`
- `source_path_or_url`
- `title`
- `claim`
- `extracted_fact`
- `as_of_date`
- `reliability`
- `raw_ref`

其中：

- `source_type` 可取：`filing / earnings / news / announcement / memo / industry_note / other`
- `reliability` 可取：`high / medium / low`

## 八、task.json 与 state.json 最小契约

### task.json

`tasks/sample_2026-06-27/task.json` 必须表示一个“某交易日的研究任务包”，至少包含：

- `task_id`
- `trade_date`
- `universe`

其中 `universe` 是数组，每个元素至少包含：

- `ts_code`
- `name`
- `model_score`
- `feature_contrib`
- `industry`
- `input_paths`

`input_paths` 至少允许以下键：

- `financial_template_json`
- `company_memory_json`
- `industry_memory_json`
- `news_search_results_json`
- `announcements_json`

这些路径允许部分缺失，但 step 必须对缺失输入做出 `insufficient` 或 `unknown` 处理，不能编造。

### state.json

`state.schema.json` 请至少支持这些字段：

- `task_id`
- `trade_date`
- `status`
- `current_symbol`
- `next_step`
- `completed_steps`
- `failed_step`
- `failure_reason`
- `updated_at`

约束：

- `status` 取值：`pending / running / failed / completed`
- `next_step` 取值：`01_model_explain / 02_financial_check / 03_news_catalyst / 04_industry_check / 05_bear_case / 06_final_rating / 07_memory_update / done`
- `completed_steps` 可按 symbol 维度记录，例如对象结构：
  - `{"000001.SZ": ["01_model_explain", "02_financial_check"]}`

## 九、step 依赖与职责边界

每个 prompt 只定义该 step 的研究规则，不写执行链。
每个 step task 文件要显式说明读取哪些输入、哪些前序输出、输出到哪里、遵守哪个 schema、禁止越界做什么。

### Step 01: model_explain

职责：

- 只解释模型为什么选中该股票
- 只围绕 `model_score` 与 `feature_contrib`
- 不看财报、新闻、行业、风险反证

输入：

- `task.json` 中该股票条目

输出：

- `outputs/<task_id>/<ts_code>/01_model_explain.json`
- 遵守 `model_explain.schema.json`

禁止：

- 不做基本面验证
- 不做新闻催化分析
- 不给最终评级

### Step 02: financial_check

职责：

- 只检查财报模板数据是否支持模型逻辑
- 只验证，不扩写新闻逻辑

输入：

- `task.json` 中该股票条目
- 财务模板 JSON
- `01_model_explain.json`

输出：

- `outputs/<task_id>/<ts_code>/02_financial_check.json`
- 遵守 `financial_check.schema.json`

禁止：

- 不分析新闻
- 不分析行业景气
- 不给最终评级

### Step 03: news_catalyst

职责：

- 只分析近期新闻、公告、研报标题、互动易等近期信息
- 区分“基本面催化”与“情绪/题材热度”
- 不把热度直接当利好

输入：

- `task.json` 中该股票条目
- `news_search_results_json`
- `announcements_json`

输出：

- `outputs/<task_id>/<ts_code>/03_news_catalyst.json`
- 遵守 `news_catalyst.schema.json`

禁止：

- 不做财报验证
- 不做最终评级

### Step 04: industry_check

职责：

- 只判断行业供需、景气度、产业链位置、概念炒作风险
- 可以参考 industry memory
- 不直接引用股价表现代替行业判断

输入：

- `task.json` 中该股票条目
- `industry_memory_json`

输出：

- `outputs/<task_id>/<ts_code>/04_industry_check.json`
- 遵守 `industry_check.schema.json`

禁止：

- 不做公司财报验证
- 不给最终评级

### Step 05: bear_case

职责：

- 只寻找反证、脆弱点、风险暴露、逻辑漏洞
- 主动挑战前面步骤形成的乐观叙事

输入：

- `01_model_explain.json`
- `02_financial_check.json`
- `03_news_catalyst.json`
- `04_industry_check.json`

输出：

- `outputs/<task_id>/<ts_code>/05_bear_case.json`
- 遵守 `bear_case.schema.json`

禁止：

- 不给最终评级
- 不更新 memory

### Step 06: final_rating

职责：

- 只汇总 `01~05` 的结构化输出
- 输出最终 `A/B/C/D` 评级与 `confidence`
- 输出一句话总结

输入：

- `01_model_explain.json`
- `02_financial_check.json`
- `03_news_catalyst.json`
- `04_industry_check.json`
- `05_bear_case.json`

输出：

- `outputs/<task_id>/<ts_code>/06_final_rating.json`
- 遵守 `final_rating.schema.json`

禁止：

- 不补造新证据
- 不写交易建议

### Step 07: memory_update

职责：

- 只基于前序已形成的稳定结论，产出 memory 更新建议
- 只输出压缩摘要，不改写原始 evidence

输入：

- `06_final_rating.json`
- `company_memory_json`
- `industry_memory_json`

输出：

- `outputs/<task_id>/<ts_code>/07_memory_update.json`
- 遵守 `memory_update.schema.json`

禁止：

- 不写交易建议
- 不把单日情绪和短期噪音写成长期记忆

## 十、评级与 confidence 标准

请在 `agent.md` 与 `06_final_rating.md` 中明确：

### Rating

- `A`：模型逻辑清楚，财务或产业验证较强，近期催化明确，反证有限，值得优先人工深挖
- `B`：存在一定支持证据，但仍有关键不确定性，值得继续跟踪
- `C`：支持一般、证据不完整、催化偏弱或反证较多，暂不优先
- `D`：主要证据不支持模型逻辑，或风险明显高于研究价值，低优先级

评级含义是 **研究优先级与人工关注等级**，不是交易指令。

### Confidence

- `high`：关键判断有多条高可靠证据支撑，冲突较少
- `medium`：有部分证据支持，但仍存在缺口或冲突
- `low`：证据明显不足、来源较弱或关键问题未解决

## 十一、00_master.md 全局规则

`prompts/00_master.md` 必须包含且明确强调：

- 不迎合模型高分
- 不把新闻热度直接当利好
- 必须区分 `事实 / 推断 / 不确定性`
- 所有判断必须绑定 `evidence_id`，否则必须声明 `evidence_insufficient`
- 输出必须是 JSON
- 不允许编造数据
- 不允许越权做交易建议
- 只做研究评级
- 先证据，后结论
- 不能因为模型分高而倒推叙事
- 若输入缺失，必须显式输出 `insufficient / unknown`，不得脑补

## 十二、每个 prompts/xx.md 的要求

每个 `prompts/xx.md` 只定义该 step 的研究规则，不写执行链。

例如：

- `01_model_explain.md` 只解释模型为何选中，不看财报新闻。
- `02_financial_check.md` 只验证财报是否支持模型逻辑。
- `03_news_catalyst.md` 只分析新闻、公告、研报标题、互动易等近期信息。
- `04_industry_check.md` 只判断行业供需、景气度、概念炒作风险。
- `05_bear_case.md` 只寻找反证和风险。
- `06_final_rating.md` 只汇总前序 JSON，输出 `A/B/C/D`。
- `07_memory_update.md` 只更新 `company_memory / industry_memory` 的压缩摘要建议。

## 十三、每个 steps/xx.task.md 的要求

每个 step task 文件必须明确写出：

- 读取哪些 prompt
- 读取哪些 input JSON
- 读取哪些 previous output
- 输出到哪里
- 严格遵守哪个 schema
- 不允许做哪些越界工作

要让 Claude Code / OpenClaw 读完该 task 文件后，可以明确知道：

- 自己这一步要干什么
- 不该干什么
- 读哪些文件
- 写哪个 JSON
- 如何校验输出

## 十四、run_chain.task.md 的要求

`run_chain.task.md` 只做任务链调度说明，不要求真的调用 API。

必须说明：

- 按 `01 -> 07` 顺序执行
- 对 `task.json` 中每只股票分别执行完整链条
- 每步完成后检查输出文件存在
- 每步完成后更新 `state.json`
- 如果失败，停止并记录 `failed_step` 与 `reason`
- 支持从 `state.json` 的 `current_symbol + next_step` 恢复
- 如果某步输出文件存在且通过 schema 校验，可选择跳过重跑

## 十五、schemas 要求

schema 只表达核心字段即可，不要过度复杂，但必须够用。

`final_rating.schema.json` 必须包含：

- `trade_date`
- `ts_code`
- `name`
- `model_logic_summary`
- `financial_validation`: `support / neutral / against / insufficient`
- `industry_validation`: `support / neutral / against / insufficient`
- `catalyst_heat`: `cold / warming / hot / overheated / unknown`
- `bear_cases`
- `rating`: `A / B / C / D`
- `confidence`: `high / medium / low`
- `one_line_summary`
- `evidence_ids`

建议其他 schema 也尽量包含：

- `trade_date`
- `ts_code`
- `name`
- `summary`
- `evidence_ids`
- `evidence_insufficient`

## 十六、sample task 要求

`tasks/sample_2026-06-27/task.json` 请给一个最小示例，包含 `2` 只股票的 **假数据**，仅用于演示，不构成真实投资建议。

每只股票至少包含：

- `ts_code`
- `name`
- `model_score`
- `feature_contrib`
- `industry`
- `input_paths`

请使用明显的示例化内容，并在 README 中明确声明：

- sample 数据是虚构示例
- 不构成投资建议

## 十七、memory 示例要求

请提供：

- `memory/company/sample_company_memory.json`
- `memory/industry/sample_industry_memory.json`

内容只需最小示例，体现：

- 历史稳定认知摘要
- 已知风险点
- 不应写入短期市场噪音

## 十八、tools 要求

`tools/` 下只写两个很薄的工具：

### validate_json.py

功能：

- 给定 schema 文件路径和 json 文件路径
- 做基本 JSON Schema 校验
- 命令行可运行
- 返回清晰的成功/失败提示

### advance_state.py

功能：

- 根据 step 成功/失败更新 `state.json`
- 支持传入：`task_id / ts_code / step / status / reason`
- 成功时推进 `next_step`
- 失败时写入 `failed_step / failure_reason / status=failed`

不要写：

- 爬虫
- LLM 调用
- 真实数据源接入
- 复杂 orchestration

## 十九、README.md 要求

README 必须清楚说明如何使用：

1. `Qsys` 生成 `task.json`
2. 执行 `steps/01...07`
3. 每一步输出 JSON
4. 最终得到 `06_final_rating.json`
5. `07_memory_update.json` 只是 memory 更新建议，不是自动写回
6. evidence 和 memory 如何保存
7. 如何通过 `state.json` 恢复执行

README 风格要求：

- 简洁
- 可读
- 可扩展
- 不要长篇空话

## 二十、agent.md 要求

`agent.md` 是总设计说明书，必须说明：

- 系统目标
- 非目标
- 输入输出
- evidence / memory / output 的区别
- task chain 执行方式
- 每个 step 的职责边界
- 失败恢复机制
- JSON 落盘规范
- 单股票目录粒度设计
- 评级标准 `A/B/C/D`
- confidence 标准 `high/medium/low`
- 不得自动生成交易指令

## 二十一、实现风格

- 简洁、可读、可扩展
- 不要引入复杂框架
- 不要生成大量无用样板
- markdown prompt 要实用，不要空泛
- JSON schema 要够用，不要过度设计
- 所有路径使用相对路径
- repo 初始状态可以直接 commit

## 二十二、完成后必须输出

完成 repo 骨架后，请输出：

1. 创建/修改的文件列表
2. 关键设计说明
3. 还未实现但后续可扩展的部分
4. 如何运行一次 sample task chain

注意：

- 你现在要做的是 **创建 repo 骨架与文档/样例/轻量工具**
- 不是实现真实研究系统
- 不是接入真实数据源
- 不是接入 LLM API
- 不是生成交易策略

---
