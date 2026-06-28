# 第一步：数据就绪

目的：

- 检查 `research/{trade_date}/` 下各数据源是否可用，如果缺失则拉取或标记。
- 对原始数据做轻量汇总，减少第二步的阅读负担。

## 数据目录约定

```
research/{trade_date}/
  data/
    sysq_signals/candidates.json   ← SysQ 产出
    financial/{ts_code}.json       ← 财报数据
    news/{ts_code}.json            ← 新闻搜索
    announcements/{ts_code}.json   ← 公告
    memory/company/{ts_code}.json  ← 公司记忆（可选）
    memory/industry/{industry}.json ← 行业记忆（可选）
```

## 应该做

- 逐目录检查数据是否存在。缺失的标记为 `unavailable`，不得失败。
- 对 `financial/{ts_code}.json` 做轻量汇总：营收趋势、利润率、杠杆、现金流等关键指标。
- 对 `news/{ts_code}.json` 统计近 60 天新闻数量、主要主题。
- 输出一份数据就绪报告到 `research/{trade_date}/output/data_readiness.json`，说明每个股票有哪些数据可用、哪些缺失。

## 不要做

- 不做任何研究判断或评级
- 不改写原始数据
- 不改写 SysQ 信号
