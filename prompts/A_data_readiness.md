# 第一步：数据就绪

目的：

- 检查 `resources/` 下各数据源是否可用，如果缺失则拉取或标记。
- 对原始数据做轻量汇总，减少第二步的阅读负担。

## 数据目录约定

```
resources/                          ← 全局复用资源，按 stock 或 trade_date 组织
  sysq_signals/{trade_date}.json    ← SysQ 每日产出
  financial/
    raw_pdfs/{ts_code}/{report_type}_{end_date}.pdf ← 原始财报 PDF（如 2024_ann_2024-12-31.pdf、2026Q1_季报_2026-03-31.pdf），一次下载永不复拉
    parsed/{ts_code}.json           ← 解析后结构化数据
  news/{ts_code}.json               ← 新闻（每条含 date 字段）
  announcements/{ts_code}.json      ← 公告（每条含 date 字段）
  memory/
    company/{ts_code}.json
    industry/{industry}.json

research/{trade_date}/
  output/                           ← 仅存放当天研究产出
```

## 应该做

- 逐数据源检查是否存在。缺失的标记为 `unavailable`，不得失败。
- **财务数据与公告**：对每只股票，确认 `financial/parsed/{ts_code}.json` 是否存在。如果不存在：
  - 来源：**巨潮资讯网（www.cninfo.com.cn）**，A 股指定信息披露平台
  - 下载 `financial/raw_pdfs/{ts_code}/` 下最近 3 个完整财年年报和所有季度报 PDF
  - 下载 `announcements/{ts_code}.json` 下近 60 天所有公告
  - 解析每份 PDF 提取：
    - 关键财务指标：营收、净利润、毛利率、ROE、负债率、现金流（逐期对比）
    - **管理层讨论与分析（MD&A）的核心变化**：行业判断、经营计划调整、风险提示等表述的变化趋势
- 新闻数据从公开新闻 API 或搜索接口拉取，存入 `news/{ts_code}.json`。
- 输出数据就绪报告到 `research/{trade_date}/output/data_readiness.json`。

## 不要做

- 不做任何研究判断或评级
- 不改写原始数据
