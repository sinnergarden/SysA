# 第一步：数据就绪

目的：

- 检查 `research/{trade_date}/` 下各数据源是否可用，如果缺失则拉取或标记。
- 对原始数据做轻量汇总，减少第二步的阅读负担。

## 数据目录约定

```
research/{trade_date}/
  data/
    sysq_signals/candidates.json   ← SysQ 产出
    financial/                     ← 财报数据（最近 3 年年报 + 所有季度报）
      {ts_code}.json
    news/{ts_code}.json            ← 新闻搜索
    announcements/{ts_code}.json   ← 公告
    memory/company/{ts_code}.json  ← 公司记忆（可选）
    memory/industry/{industry}.json ← 行业记忆（可选）
```

## 应该做

- 逐目录检查数据是否存在。缺失的标记为 `unavailable`，不得失败。
- **财务数据的拉取**：对每只股票，下载最近 3 个完整财年的年报和所有可用的季度报告。从报告中提取：
  - 关键财务指标：营收、净利润、毛利率、ROE、负债率、现金流（逐期对比）
  - **管理层讨论与分析（MD&A）的核心变化**：行业判断、经营计划调整、风险提示等表述的变化趋势
- 对 `financial/{ts_code}.json` 做轻量汇总：记录覆盖了哪些年份/季度的报告，摘录 MD&A 中相比上期的核心变化。
- 对 `news/{ts_code}.json` 统计近 60 天新闻数量、主要主题。
- 输出一份数据就绪报告到 `research/{trade_date}/output/data_readiness.json`，说明每个股票有哪些数据可用、哪些缺失。

## 不要做

- 不做任何研究判断或评级
- 不改写原始数据
- 不改写 SysQ 信号
