# axzq-profile-tagging · 客户画像标签服务

`axzq-profile-tagging` 是经纪业务条线的客户画像标签计算服务，负责把行情活跃度、
持仓结构、服务触点三路信号汇聚为标签，供 App 首页与投顾工作台消费。线上版本 `2.3.1`。

## 目录

| 文件 | 说明 |
|---|---|
| `src/profile_tagging.py` | 标签计算主体：信号汇总、阈值判定、标签写回 |
| `conf/tag_rules.yaml` | 标签规则与阈值 |

## 标识

服务在配置中心注册为 `axzq-profile-tagging`（见 `conf/tag_rules.yaml` 的 `service` 段），
代码侧常量为 `src/profile_tagging.py` 的 `SERVICE_NAME`。

## 标签体系

| 标签 | 口径 | 最低样本 |
|---|---|---|
| `active_trader` | 近 30 日有成交且日均登录 ≥ 3 次 | 1 |
| `dormant_reactivate` | 60–180 日无成交、近 7 日有登录 | 1 |
| `wealth_migrate` | 现金类持仓占比下降 ≥ 15pp 且非货基净申购为正 | 1 |
| `margin_watch` | 维持担保比例 < 180% | 1 |

## 使用

```bash
axzq-profile-tagging compute --date 2026-10-25 --scope all
axzq-profile-tagging compute --date 2026-10-25 --customer-id C008124431
```

## 已知问题

1. `wealth_migrate` 在月末最后一个交易日会因净值未更新而漏判，需 T+1 补算。
2. 标签写回是覆盖式的，未做版本留痕；下游若要回溯历史标签需读归档表。
3. 单客户计算耗时约 40ms，全量 320 万客户跑批约 55 分钟（8 并发）。

## 维护

经纪业务数据组（内部 IM 群 `#broker-dw`）。
