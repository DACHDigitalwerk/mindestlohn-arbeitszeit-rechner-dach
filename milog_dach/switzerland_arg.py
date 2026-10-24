"""
switzerland_arg.py - Arbeitszeit- & Mindestlohnregelungen Schweiz 2026
Rechtsgrundlagen:
- Schweizer Arbeitsgesetz (ArG) Art. 9, 13, 15, 15a
- Kantonale Mindestlohngesetze (GE, NE, JU, BS, TI)
"""

from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class SwissShiftResult:
    net_hours: float
    pause_minutes_taken: float
    statutory_min_pause_minutes: float
    pause_compliant: bool
    is_daily_max_exceeded: bool
    cantonal_minimum_wage: Optional[float]
    effective_hourly_wage: Optional[float]
    is_wage_compliant: Optional[bool]
    warning: Optional[str]


class SwitzerlandArbeitszeit:
    # Kantonale Mindestlöhne (Stand 2026)
    CANTONAL_MINIMUM_WAGES: Dict[str, float] = {
        "GE": 24.32,  # Genf
        "NE": 21.09,  # Neuenburg
        "JU": 20.60,  # Jura
        "BS": 21.45,  # Basel-Stadt
        "TI": 20.25,  # Tessin
    }

    WEEKLY_MAX_HOURS_OFFICE = 45.0  # Art. 9 Abs. 1 Bst. a ArG
    WEEKLY_MAX_HOURS_OTHER = 50.0   # Art. 9 Abs. 1 Bst. b ArG
    DAILY_MAX_SPAN_HOURS = 14.0     # Art. 10 Abs. 3 ArG (Tagesarbeit innerhalb von 14h)

    @classmethod
    def calculate_shift(
        cls,
        gross_hours: float,
        pause_minutes: float,
        canton: Optional[str] = None,
        hourly_wage: Optional[float] = None
    ) -> SwissShiftResult:
        if gross_hours <= 5.5:
            min_pause = 0.0
        elif gross_hours <= 7.0:
            min_pause = 15.0
        elif gross_hours <= 9.0:
            min_pause = 30.0
        else:
            min_pause = 60.0

        net_h = round(gross_hours - (pause_minutes / 60.0), 2)
        pause_ok = pause_minutes >= min_pause
        exceeded = net_h > 12.5

        min_wage = cls.CANTONAL_MINIMUM_WAGES.get(canton.upper()) if canton else None
        wage_ok = None
        if min_wage is not None and hourly_wage is not None:
            wage_ok = hourly_wage >= min_wage

        warning = None
        if not pause_ok:
            warning = f"Verstoß gegen Art. 15 ArG: Gesetzliche Mindestpause von {min_pause} Min unterschritten ({pause_minutes} Min erfasst)!"
        elif wage_ok is False:
            warning = f"Kantonales Mindestlohngesetz {canton}: Stundenlohn von {hourly_wage:.2f} CHF unterschreitet Minimum von {min_wage:.2f} CHF!"

        return SwissShiftResult(
            net_hours=net_h,
            pause_minutes_taken=pause_minutes,
            statutory_min_pause_minutes=min_pause,
            pause_compliant=pause_ok,
            is_daily_max_exceeded=exceeded,
            cantonal_minimum_wage=min_wage,
            effective_hourly_wage=hourly_wage,
            is_wage_compliant=wage_ok,
            warning=warning,
        )
