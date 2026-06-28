# SysA

`SysA` 是一个面向 `SysQ` 候选股票研究的最小可运行框架。它的使命是**接收 SysQ 的融合排序信号和多模型因子归因（N 个模型 × N 套 SHAP），叠加外部原始材料（财报、新闻、公告），用 LLM 产出带证据链的结构化研究结论和 A/B/C/D 评级**。

它不是交易系统，也不是内置大模型调用的应用。它定义两份 prompt + 两份 schema，让 Claude Code / Codex 按两步法执行研究。

## 两步法流程

```
               数据层 (research/{trade_date}/data/)
               ┌────────────────────────────────────────┐
               │ sysq_signals/candidates.json  ← SysQ   │
               │ financial/{ts_code}.json     ← 数据源  │
               │ news/{ts_code}.json          ← 数据源  │
               │ announcements/{ts_code}.json ← 数据源  │
               │ memory/company/              ← SysA 积累│
               │ memory/industry/             ← SysA 积累│
               └────────────────────────────────────────┘
                              │
              Step A: 数据就绪 │ 检查各目录可用性 + 轻量汇总
                              ↓
               research/{trade_date}/output/data_readiness.json
                              │
              Step B: 综合研究 │ 行业判断 → 逐股研究 → A/B/C/D
                              ↓
               research/{trade_date}/output/
               ├── industry_summary/{industry}.json
               └── stock_opinions/{ts_code}.json
```

| Step | 做什么 | 输出 |
|------|--------|------|
| A 数据就绪 | 检查各数据目录是否存在、拉取缺失数据、财务/新闻轻量汇总 | `data_readiness.json` |
| B 综合研究 | 先写行业判断，再逐股输出研究意见 | `industry_summary/` + `stock_opinions/` |

## 定位

- 输入：SysQ 产出的融合排序分 `ranking_score` + 多模型归因 `models[]` + 外部原始材料（财报、新闻、公告）。数据分散存储在 `research/{trade_date}/data/` 下
- 过程：两步。数据就绪检查 → 综合研究。所有需要自然语言推理的步骤都在 LLM 中完成
- 输出：`stock_opinions/{ts_code}.json`（含 A/B/C/D 评级 + 依据 + memory 建议）
- 积累：`research/{trade_date}/data/memory/` 是 SysA 历次研究积累的长期认知，**不是 SysQ 的产出**
- 边界：不下单、不接交易、不自动给买卖指令

## 目录说明

- `prompts/`：`00_master.md`（全局规则）+ `A_data_readiness.md` + `B_research.md`
- `steps/`：`A_data_readiness.task.md` + `B_research.task.md`
- `schemas/`：`stock_opinion.schema.json` + `industry_summary.schema.json` + `evidence.schema.json`
- `tools/`：`validate_json.py`（schema 校验工具）
- `research/`：运行时数据与输出（被 .gitignore 挡住）
- `memory/`：公司与行业长期记忆样例
- `docs/`：SysQ 接口需求文档

## 使用方式

1. 确认 `research/{trade_date}/data/` 下已有 SysQ 信号和外部数据
2. 执行 `steps/A_data_readiness.task.md` 检查数据可用性
3. 执行 `steps/B_research.task.md` 进行综合研究
4. 最终意见在 `research/{trade_date}/output/stock_opinions/` 下
5. 用 `tools/validate_json.py` 校验输出

```bash
# 校验单只股票意见
python3 tools/validate_json.py schemas/stock_opinion.schema.json \
  research/2026-06-26/output/stock_opinions/002130.SZ.json

# 校验行业汇总
python3 tools/validate_json.py schemas/industry_summary.schema.json \
  research/2026-06-26/output/industry_summary/电气设备.json
```

## Git 使用约束

- 运行时产物（`research/{trade_date}/` 下的动态数据）默认不入库
- 框架文件、schema、prompt 必须入库
- memory 积累沉淀到 `research/{trade_date}/data/memory/`，需人工确认后入库
