# -*- coding: utf-8 -*-
"""axzq-profile-tagging 客户画像标签计算。

三路信号：行情活跃度（成交+登录）、持仓结构（现金占比/净申购）、服务触点。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

__version__ = "2.3.1"

SERVICE_NAME = "axzq-profile-tagging"
API_PREFIX = "/openapi/v2/axzq-profile-tagging"
TRADE_WINDOW_DAYS = 30
LOGIN_WINDOW_DAYS = 7
DORMANT_RANGE = (60, 180)
MARGIN_ALERT_BELOW = 180.0


@dataclass
class CustomerSignal:
    customer_id: str
    trades: int
    login_days: int
    idle_days: int
    cash_ratio: float
    cash_ratio_prev: float
    non_money_fund_inflow: float
    maintenance_ratio: Optional[float] = None

    @property
    def cash_ratio_drop_pp(self) -> float:
        return (self.cash_ratio_prev - self.cash_ratio) * 100.0


def is_active_trader(s: CustomerSignal) -> bool:
    per_day = s.login_days / float(LOGIN_WINDOW_DAYS)
    return s.trades >= 1 and per_day >= 3.0 / LOGIN_WINDOW_DAYS


def is_dormant_reactivate(s: CustomerSignal) -> bool:
    lo, hi = DORMANT_RANGE
    return lo <= s.idle_days <= hi and s.login_days >= 1


def is_wealth_migrate(s: CustomerSignal) -> bool:
    return s.cash_ratio_drop_pp >= 15.0 and s.non_money_fund_inflow > 0


def is_margin_watch(s: CustomerSignal) -> bool:
    return s.maintenance_ratio is not None and s.maintenance_ratio < MARGIN_ALERT_BELOW


RULES = (
    ("active_trader", is_active_trader),
    ("dormant_reactivate", is_dormant_reactivate),
    ("wealth_migrate", is_wealth_migrate),
    ("margin_watch", is_margin_watch),
)


def compute(signals: Iterable[CustomerSignal]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for s in signals:
        for tag, fn in RULES:
            if fn(s):
                out.append({"customer_id": s.customer_id, "tag": tag, "service": SERVICE_NAME})
    return out
