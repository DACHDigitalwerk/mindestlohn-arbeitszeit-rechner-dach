"""
austria_azg.py - Arbeitszeit- & Kollektivvertragsregelungen Österreich 2026
Rechtsgrundlagen:
- Arbeitszeitgesetz (AZG) §§ 3, 6, 9, 10, 11, 12
- Arbeitsruhegesetz (ARG)
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class AustriaShiftResult:
    net_hours: float
    normal_hours: float
    overtime_50_hours: float
    overtime_100_hours: float
    is_daily_max_exceeded: bool
    pause_compliant: bool
    warning: Optional[str]


class AustriaArbeitszeit:
    DAILY_NORMAL_HOURS = 8.0
    DAILY_MAX_HOURS = 12.0 # § 9 Abs. 1 AZG
    WEEKLY_MAX_HOURS = 60.0 # § 9 Abs. 1 AZG
    MANDATORY_PAUSE_MINUTES = 30.0 # ab 6 Stunden Arbeit (§ 11 AZG)

    @classmethod
    def calculate_shift(
        cls,
        worked_hours: float,
        pause_minutes: float,
        is_holiday_or_night: bool = False
    ) -> AustriaShiftResult:
        net_h = round(worked_hours - (pause_minutes / 60.0), 2)
        pause_ok = pause_minutes >= cls.MANDATORY_PAUSE_MINUTES if worked_hours > 6.0 else True
        exceeded = net_h > cls.DAILY_MAX_HOURS

        normal_h = min(net_h, cls.DAILY_NORMAL_HOURS)
        ot_total = max(0.0, net_h - cls.DAILY_NORMAL_HOURS)

        ot_50 = 0.0 if is_holiday_or_night else ot_total
        ot_100 = ot_total if is_holiday_or_night else 0.0

        warning = None
        if exceeded:
            warning = f"Verstoß gegen § 9 AZG: Tägliche Höchstarbeitszeit von 12,0h überschritten ({net_h}h)!"
        elif not pause_ok:
            warning = f"Verstoß gegen § 11 AZG: Mindestpause von 30 Min ab 6h Arbeit unterschritten ({pause_minutes} Min erfasst)!"

        return AustriaShiftResult(
            net_hours=net_h,
            normal_hours=round(normal_h, 2),
            overtime_50_hours=round(ot_50, 2),
            overtime_100_hours=round(ot_100, 2),
            is_daily_max_exceeded=exceeded,
            pause_compliant=pause_ok,
            warning=warning,
        )
