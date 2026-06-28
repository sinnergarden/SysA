# CLAUDE.md

This file provides guidance to **developers maintaining this repo**. For runtime agent guidance, see [agent.md](agent.md).

## 项目定位

SysA 的使命是**接收 SysQ 的融合排序信号和多模型因子归因（N 个模型 × N 套 SHAP），叠加外部原始材料（财报、新闻、公告），用 LLM 产出带证据链的结构化研究结论和 A/B/C/D 评级**。它定义两份 prompt + 两份 schema，让代码 agent 按两步法执行研究。

## 接口边界

| 维度 | SysQ 能产出 | SysA 做 |
|------|------------|---------|
| 股票名单与排序 | `ranking_score`（融合排序分） | —— |
| 多模型归因 | `models[]`（每个模型含 score + feature_contrib + horizon/target） | 对比多模型归因异同，判断信号一致性 |
| 财务数据 | ——（外部数据源） | 验证财报是否支持模型逻辑 |
| 新闻与公告 | ——（外部数据源） | 分析催化和情绪 |
| 行业分类 | `industry` 标签 | 判断供需、景气度、概念炒作风险 |
| 反证 | —— | 主动找反证、脆弱点和逻辑漏洞 |
| 评级 | —— | 综合给出 A/B/C/D 评级 + memory 建议 |

## 数据目录约定

```
research/{trade_date}/
  data/
    sysq_signals/candidates.json      ← SysQ 产出
    financial/{ts_code}.json           ← 财报数据
    news/{ts_code}.json                 ← 新闻搜索
    announcements/{ts_code}.json        ← 公告
    memory/company/{ts_code}.json       ← 公司记忆（可选）
    memory/industry/{industry}.json     ← 行业记忆（可选）
  output/
    data_readiness.json                 ← Step A 产出
    industry_summary/{industry}.json    ← Step B 产出
    stock_opinions/{ts_code}.json       ← Step B 产出
```

## 关键命令

```bash
# 安装依赖
pip install -r requirements.txt

# 校验个股意见
python3 tools/validate_json.py schemas/stock_opinion.schema.json \
  research/2026-06-26/output/stock_opinions/002130.SZ.json

# 校验行业汇总
python3 tools/validate_json.py schemas/industry_summary.schema.json

# 执行数据就绪
claude --print steps/A_data_readiness.task.md

# 执行综合研究
claude --print steps/B_research.task.md
```

## schema 说明

| Schema | 用途 |
|--------|------|
| `stock_opinion.schema.json` | 个股研究意见（评级、依据、反证、memory 建议） |
| `industry_summary.schema.json` | 行业级判断汇总 |
| `evidence.schema.json` | 证据项格式 |

## Git 约定

- 默认分支为 `main`
- 运行时产物（`research/{trade_date}/` 下的动态内容）被 `.gitignore` 挡住，不入库
- 框架文件、schema、prompt 必须入库
