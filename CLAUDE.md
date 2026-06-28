# CLAUDE.md

This file provides guidance to **developers maintaining this repo**. For runtime agent guidance, see [agent.md](agent.md).

## 项目定位

SysA 是一个**面向 Qsys 候选股票研究的最小可运行框架**。它定义一套 `prompts/`（研究规则） + `steps/`（task 文件） + `schemas/`（JSON 契约） + `tools/`（确定性工具），让 Claude Code CLI 按固定 7 步研究链逐票执行、全程结构化落盘。

Fork/clone 此 repo 后可直接 commit 使用，不依赖外部服务。

## 架构概述

```
Qsys (上游)                     SysA                           Claude Code CLI (执行者)
   ┌──────┐    task.json       ┌──────────┐    claude code     ┌──────────────────┐
   │ 候选  │ ──────────────→   │ 研究框架  │ ←──────────────  │ cron 定时触发      │
   │ 股票  │                   │          │   读取 steps/*    │ claude code --print  │
   │ 模型分│                   │  prompts │   写入 output/    │ tasks/run_chain.md   │
   │ 输入  │                   │ /schemas │ ──────────────→  │ advance_state.py    │
   └──────┘                   └──────────┘                   └──────────────────┘
```

- **SysA 不内置 LLM 调用**，Claude Code CLI 负责 LLM 交互。
- **SysA 不在 Python 中写推理逻辑**，研究规则在 `prompts/` 中。
- **SysA 不下单、不接交易**，只输出 A/B/C/D 研究评级。
- **运行方式**：cron 定时拉起 `claude code --print steps/run_chain.task.md`，按 state.json 断点续跑。

## 执行方式

通过 cron 定时调度：

```bash
# crontab 示例：每个交易日 9:30 执行
30 9 * * 1-5 cd /path/to/SysA && claude --print steps/run_chain.task.md
```

- `claude --print` 模式：非交互式执行，一次性读取 task 文件并运行，完成后退出。
- 每次执行只跑当前 `state.json` 中 `current_symbol + next_step` 指定的一步，完成后调用 `advance_state.py` 推进状态。
- 下一轮 cron 触发时读取已更新的 state.json，继续下一步。
- `state.json` 支持断点恢复：某步失败后原地停住，下一轮 cron 触发时从同一位置重试。

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

# 手动执行单个 step 测试（不通过 cron）
claude --print steps/01_model_explain.task.md
```

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

## 关键设计原则（影响扩展决策）

| 原则 | 含义 |
|------|------|
| 文件系统即接口 | 不引入数据库、消息队列、Web 服务。输入输出都是文件。 |
| evidence / memory / output 三层分离 | evidence = 事实出处层，memory = 长期知识层，output = 阶段结论层。不可混用。 |
| Claude Code CLI 是执行者 | repo 不内置调度器。cron 定时拉起 `claude --print` 按步执行。 |
| schema 够用不过度 | 核心字段必须覆盖，但不追求完全的形式化完备。 |
| 失败可恢复 | state.json 记录逐票进度；output 文件存在且通过校验时可跳过重跑。 |
