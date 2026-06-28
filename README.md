# SysA

`SysA` 是一个面向 `SysQ` 候选股票研究的最小可运行框架。它的使命是**接收 SysQ 的融合排序信号和多模型因子归因（N 个模型 × N 套 SHAP），叠加外部原始材料（财报、新闻、公告），用 LLM 产出带证据链的结构化研究结论和 A/B/C/D 评级**。

它不是交易系统，也不是内置大模型调用的应用。它定义两份 prompt + 两份 schema，让代码 agent 按两步法执行研究。

## 两步法流程

```
                   资源层 (resources/)
                   ┌─────────────────────────────────────┐
                   │ sysq_signals/{trade_date}.json      │
                   │ financial/parsed/{ts_code}.json     │
                   │ news/{ts_code}.json                 │
                   │ announcements/{ts_code}.json        │
                   │ memory/company/ + memory/industry/  │
                   └─────────────────────────────────────┘
                                  │
              Step A: 数据就绪    │ 检查全局资源可用性 + 轻量汇总
                                  ↓
                   research/{trade_date}/output/data_readiness.json
                                  │
              Step B: 综合研究    │ 行业判断 → 逐股研究 → A/B/C/D
                                  ↓
                   research/{trade_date}/output/
                   ├── industry_summary/{industry}.json
                   └── stock_opinions/{ts_code}.json
```

| Step | 做什么 | 输出 |
|------|--------|------|
| A 数据就绪 | 检查 `resources/` 下各数据源可用性，标记缺失，做轻量汇总 | `data_readiness.json` |
| B 综合研究 | 先写行业判断，再逐股输出研究意见 | `industry_summary/` + `stock_opinions/` |

## 定位

- 输入：SysQ 信号、财报、新闻、公告、memory。所有资源全局复用，存放在 `resources/` 下
- 过程：两步。数据就绪检查 → 综合研究
- 输出：`research/{trade_date}/output/stock_opinions/{ts_code}.json`
- 边界：不下单、不接交易、不自动给买卖指令

## 目录说明

- `prompts/`：全局规则 + 两步 prompt
- `steps/`：两步 task 文件
- `schemas/`：stock_opinion / industry_summary / data_readiness / evidence
- `tools/`：`validate_json.py`
- `resources/`：全局复用数据（SysQ 信号、财报 PDF 与解析、新闻、公告、memory）
- `research/`：运行期输出
- `examples/`：样例
- `docs/`：SysQ 接口需求文档

## 使用方式

1. 确认 `resources/` 下已有必要数据
2. 执行 `steps/A_data_readiness.task.md`
3. 执行 `steps/B_research.task.md`
4. 最终意见在 `research/{trade_date}/output/stock_opinions/` 下

```bash
python3 tools/validate_json.py schemas/stock_opinion.schema.json \
  research/2026-06-26/output/stock_opinions/002130.SZ.json
```

## Git 使用约束

- `research/{trade_date}/` 下的动态产出默认不入库
- `resources/` 下 PDF 和解析结果需人工确认后入库
- 框架文件、schema、prompt 必须入库
