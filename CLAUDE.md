# CLAUDE.md

This file provides guidance to **developers maintaining this repo**. For runtime agent guidance, see [agent.md](agent.md).

## 项目定位

SysA 的使命是**接收 SysQ 的融合排序信号和多模型因子归因，叠加外部原始材料（财报、新闻、公告），用 LLM 产出结构化研究结论和 A/B/C/D 评级**。两步法执行：A 数据就绪 → B 综合研究。

## 资源目录约定

```
resources/                              ← 全局复用资源
  sysq_signals/{trade_date}.json        ← SysQ 每日产出
  financial/parsed/{ts_code}.json       ← 财报解析结果（含 MD&A）
  financial/raw_pdfs/{ts_code}/         ← 原始财报 PDF
  news/{ts_code}.json                   ← 新闻
  announcements/{ts_code}.json          ← 公告
  memory/company/{ts_code}.json         ← 公司记忆
  memory/industry/{industry}.json       ← 行业记忆

research/{trade_date}/
  output/                               ← 当天研究产出
    data_readiness.json
    industry_summary/{industry}.json
    stock_opinions/{ts_code}.json
```

## 关键命令

```bash
pip install -r requirements.txt
python3 tools/validate_json.py schemas/stock_opinion.schema.json research/2026-06-26/output/stock_opinions/002130.SZ.json
claude --print steps/A_data_readiness.task.md
claude --print steps/B_research.task.md
```

## Schema 说明

| Schema | 用途 |
|--------|------|
| `stock_opinion.schema.json` | 个股研究意见（评级、依据、反证、memory 建议） |
| `industry_summary.schema.json` | 行业级判断汇总 |
| `data_readiness.schema.json` | 数据就绪报告 |
| `evidence.schema.json` | 证据项格式 |

## Git 约定

- 默认分支为 `main`
- 运行时产物（`research/{trade_date}/`）被 `.gitignore` 挡住，不入库
- 框架文件、schema、prompt 必须入库
- `resources/` 下的 PDF 和解析结果需人工入库
