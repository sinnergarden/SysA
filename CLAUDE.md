# CLAUDE.md

This file provides guidance to **developers maintaining this repo**. For runtime agent guidance, see [agent.md](agent.md).

## 项目定位

SysA 的使命是**接收 SysQ 的数值模型信号（分数、因子贡献），叠加外部原始材料（财报、新闻、公告），用 LLM 产出带证据链的结构化研究结论和 A/B/C/D 评级**。它定义一套 `prompts/`（研究规则） + `steps/`（task 文件） + `schemas/`（JSON 契约） + `tools/`（确定性工具），让代码 agent 按固定 7 步研究链逐票执行、全程结构化落盘。

Fork/clone 此 repo 后可直接 commit 使用。SysA 框架本身不内置外部服务调用；实际执行 step 需要本地已登录的 Claude Code CLI / Codex CLI 等代码 agent。

## 接口边界：SysQ 产出 vs SysA 研究

SysQ 作为一个量化系统，产出数值信号和结构化标签。SysA 填补的是量化模型做不到、需要大语言模型推理的部分。边界如下：

| 维度 | SysQ 能产出 | SysA 做（需要 LLM） |
|------|------------|-------------------|
| 股票名单与排序 | TopK 名单 + `model_score`（数值），按主信号排序 | —— |
| 主信号定义 | `primary_model`（horizon / target / description） | **step 01** — 理解"预测 60 天收益"的业务含义 |
| 因子贡献度 | `feature_contrib.values` + `method` + `universe_stats` | **step 01** — 结合 method 和 universe_stats 判断贡献度高低 |
| 辅助信号 | `auxiliary_signals[]`（其他维度的 z-score、概率等） | **step 01** — 对比主信号与辅助信号方向一致性 |
| 财务数据 | ——（外部数据源提供原始指标模板） | **step 02** — 验证财报是否支持模型逻辑 |
| 新闻与公告 | ——（外部数据源提供原始文本） | **step 03** — 分析催化和情绪，区分基本面 vs 题材热度 |
| 行业分类 | `industry` 标签 | **step 04** — 判断供需、景气度、产业链位置、概念炒作风险 |
| 反证 | —— | **step 05** — 主动找反证、脆弱点和逻辑漏洞 |
| 评级 | —— | **step 06** — 汇总给出 A/B/C/D 评级 |
| 长期记忆 | —— | **step 07** — 产出 memory 更新建议 |

**关键约束**：`feature_contrib` 是结构化的（method + values + 可选 universe_stats），不是单纯的数值字典。`method` 如实说明归因方法，`universe_stats` 提供各因子在全量候选上的分布统计，否则 LLM 无法判断 0.31 是高是低。`auxiliary_signals` 只用于交叉验证，不作为独立选股依据。所有"为什么选中该股"的文字说明都必须由 SysA step 01 产出，不得由 SysQ 预生成。

## 架构概述

```
SysQ (数值信号)                  SysA (研究框架)                  代码 Agent (执行者)
   ┌──────────────────┐       ┌──────────────────┐    读取 steps/*  ┌────────────────┐
   │ primary_model     │       │  prompts/        │ ←───────────  │ Claude Code CLI │
   │ model_score       │task.json│  steps/        │    写入        │ Codex CLI       │
   │ feature_contrib   │────→  │  schemas/         │ ────────────→ │ 等代码 agent    │
   │ auxiliary_signals │       │  tools/           │                └────────────────┘
   │ industry          │       │  memory/ (自积累) │
   └──────────────────┘       └──────────────────┘

外部数据源（原始材料）                ↑
   ┌──────────────────┐     input_paths 指向
   │ 财报模板 JSON     │ ────────────
   │ 新闻检索结果 JSON  │
   │ 公告 JSON         │
   └──────────────────┘

memory/ (SysA 自身积累，非 SysQ 产出)
   ┌──────────────────┐
   │ company_memory   │ ←──── 历次研究的长期认知沉淀
   │ industry_memory  │
   └──────────────────┘
```

- **SysA 不内置 LLM 调用**，agent 负责 LLM 交互。
- **SysA 不在 Python 中写推理逻辑**，研究规则在 `prompts/` 中。
- **SysA 不下单、不接交易**，只输出 A/B/C/D 研究评级。
- **SysQ 产出数值信号**：`primary_model`（主信号定义）、`model_score`、`feature_contrib`（含 method + values + 可选 universe_stats）、`auxiliary_signals[]`（可选辅助信号）、`industry`。不含 per-stock NL 解释。所有"为什么选中该股票"的逐股解释必须由 SysA step 01 生成。
- **外部数据源提供原始材料**：财报模板、新闻结果、公告全文。这些不是 SysQ 产出，由独立数据源获取。
- **SysA 积累自己的 memory**：`memory/` 下的 company/industry memory 是 SysA 在历次研究中积累的长期认知，不是 SysQ 的产出。

## 执行方式（当前 MVP）

当前 MVP 的执行方式是**手动逐步执行**：

```bash
# 手动执行单个 step（示例）
claude --print steps/01_model_explain.task.md
```

实际运行流程：

1. 读取 `steps/<step>.task.md` —— 该文件写明读取哪个 prompt、哪些输入、输出到哪里、遵守哪个 schema。
2. 手动或让 agent 按 state.json 的 `current_symbol + next_step` 确定从哪步继续。
3. 每步完成后调用 `validate_json.py` 校验输出，再调用 `advance_state.py` 推进状态。
4. 失败时停止，修复后从同一位置恢复。

`steps/run_chain.task.md` 是任务链执行说明文档，不能当作直接可执行的脚本。它指导 agent 理解完整序列和恢复规则，但执行仍依赖 agent 的遵守，repo 目前没有内置调度器或自动 runner。

### 后续计划：cron runner

更稳定的自动化方案是在 `tools/` 中新增 `run_next_step.py`，其职责是：

1. 读取 `tasks/<task_id>/state.json`，定位 `current_symbol + next_step`。
2. 根据 step 名称自动组装单步 prompt（依赖关系在 `steps/*.task.md` 中定义）。
3. 调用 `claude --print` 执行该步。
4. 执行完成后调用 `advance_state.py` 推进状态。
5. 配合 cron + `flock` 防并发 wrapper 实现每日定时调度。

该 runner 当前**尚未实现**，待后续迭代添加。

## 关键命令

```bash
# 安装依赖（仅 jsonschema）
pip install -r requirements.txt

# 校验 step 输出是否符合 schema
python3 tools/validate_json.py schemas/final_rating.schema.json \
  outputs/sample_2026-06-27/000001.SZ/06_final_rating.json

# 推进 state.json（每步成功/失败后调用）
python3 tools/advance_state.py \
  --state tasks/sample_2026-06-27/state.json \
  --task tasks/sample_2026-06-27/task.json \
  --task-id sample_2026-06-27 \
  --ts-code 000001.SZ \
  --step 01_model_explain \
  --status success

# 手动执行单个 step 测试
claude --print steps/01_model_explain.task.md
```

> 注意：以上 `claude --print` 命令以本机 Claude Code CLI 实际命令名为准，当前文档示例假设 CLI 为 `claude`。实际运行时请先确认本地 CLI 命令（`claude --version` 或 `claude-code --version`）。

## tools/ 说明

两个 Python 工具只做确定性操作：

- **`validate_json.py`** — 给定 schema 路径 + JSON 路径，校验后返回退出码。依赖 `jsonschema`。
- **`advance_state.py`** — 解析 task.json 中的股票列表，按成功/失败推进 state.json 状态机：
  - 成功：将 step 加入 `completed_steps[symbol]`，推进 `next_step`；完成 07 后自动切换到下一只股票。
  - 失败：设置 `status=failed`，记录 `failed_step` + `failure_reason`，停止等待人工恢复。
  - 跨股票逻辑：当某票 07 完成后，自动寻找下一只未完成的股票，重置 `next_step` 为 `01_model_explain`。

## 如何新增一个 step

需要同时创建/修改 4 个文件：

1. **`prompts/<step>.md`** — 研究规则，只定义该步的分析范围、应该做什么、禁止做什么。
2. **`steps/<step>.task.md`** — task 执行文件，写明读取哪些 prompt、哪些输入、哪些前序输出、输出路径、schema 路径、禁止越界事项。
3. **`schemas/<step>.schema.json`** — 输出 JSON 的 schema，至少包含 `trade_date`、`ts_code`、`name`、`summary`、`evidence_ids`、`evidence_insufficient`。
4. **`tools/advance_state.py`** — 在 `STEP_ORDER` 列表中加入新 step 名称。

## schema 设计惯例

- 每个 step 的输出 schema 独立，不共用。
- 必含字段：`trade_date`、`ts_code`、`name`、`evidence_ids`。
- 关键判断必须有证据支撑，否则输出 `evidence_insufficient: true`。
- `final_rating.schema.json` 是唯一的聚合 schema，包含来自前序 step 的汇总字段（`financial_validation`、`industry_validation`、`catalyst_heat`、`bear_cases` 等）。

## 执行粒度设计

- **单股票独立输出目录**：`outputs/<task_id>/<ts_code>/`。不允许多只股票混写一个 JSON。这种粒度的设计目的是支持单票重跑、失败恢复、和未来并行化。
- **每一 step 只读必要输入**，不默认塞入所有原始材料。依赖关系在 `steps/*.task.md` 中显式列出。

## Git 约定

- 默认分支为 `main`。
- 运行时产物（`outputs/`、`evidence/` 下的动态内容）被 `.gitignore` 挡住，不入库。
- sample 数据（`tasks/sample_2026-06-27/`）和 `outputs/sample_.../06_final_rating.json` 作为框架演示保留入库。
- 后续新增真实任务包应保持不入库，除非是刻意做样例沉淀。

## 当前状态 vs 后续计划

### 已具备

- `prompts/` + `steps/` + `schemas/` 构成完整的研究任务链协议
- `tools/validate_json.py` schema 校验工具
- `tools/advance_state.py` 状态机推进工具（支持按股票切换、失败记录、恢复）
- `steps/run_chain.task.md` 链执行指导文档（依赖 agent 遵守）
- `state.json` 断点恢复设计（current_symbol + next_step 定位）
- sample 任务包与 demo 输出

### 尚未实现

- `tools/run_next_step.py` —— 读取 state.json 自动组装单步 prompt 的 thin runner
- `tools/run_next_step.py` 内调用 `claude --print` 的能力
- cron + `flock` 防并发 wrapper 实现每日定时调度
- CLI 命令可配置化（如 `CLAUDE_CMD` 环境变量）

## 关键设计原则（影响扩展决策）

| 原则 | 含义 |
|------|------|
| 文件系统即接口 | 不引入数据库、消息队列、Web 服务。输入输出都是文件。 |
| evidence / memory / output 三层分离 | evidence = 事实出处层，memory = 长期知识层，output = 阶段结论层。不可混用。 |
| 代码 agent 是执行者 | repo 不内置调度器，不控制 agent 如何调用 LLM。agent 读取 task 文件自行执行。 |
| schema 够用不过度 | 核心字段必须覆盖，但不追求完全的形式化完备。 |
| 失败可恢复 | state.json 记录逐票进度；output 文件存在且通过校验时可跳过重跑。 |
