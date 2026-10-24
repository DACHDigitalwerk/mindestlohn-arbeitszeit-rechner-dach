"""
milog_de.py - Mindestlohn & Arbeitszeitregelungen Deutschland 2026
Rechtsgrundlagen:
- Mindestlohngesetz (MiLoG) §§ 1, 17, 21 (12,82 €/h)
- Arbeitszeitgesetz (ArbZG) §§ 3, 4, 5
- Viertes Buch Sozialgesetzbuch (SGB IV) § 8 (Minijob 538 €) & § 20 (Übergangsbereich)
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class MindestlohnCheckResult:
    monthly_gross: float
    monthly_hours: float
    effective_hourly_wage: float
    statutory_minimum_wage: float
    is_compliant: bool
    wage_difference_per_hour: float
    total_monthly_backpay_due: float
    is_minijob: bool
    max_minijob_hours_allowed: float
    fks_fine_risk: bool


@dataclass
class DailyWorktimeResult:
    gross_hours: float
    pause_minutes_taken: float
    net_hours: float
    statutory_min_pause_minutes: float
    pause_compliant: bool
    max_daily_hours_exceeded: bool
    daily_hours_warning: Optional[str]


class MindestlohnDE:
    STATUTORY_MINIMUM_WAGE_2026 = 12.82 # € pro Zeitstunde
    MINIJOB_LIMIT_2026 = 538.00         # € monatlich
    MIDIJOB_UPPER_LIMIT_2026 = 2000.00  # € monatlich

    @classmethod
    def check_salary(cls, monthly_gross: float, monthly_hours: float) -> MindestlohnCheckResult:
        """
        Prüft, ob ein Monatsfestgehalt bei gegebener Stundenzahl den gesetzlichen Mindestlohn einhält.
        """
        if monthly_hours <= 0:
            eff_rate = 0.0
        else:
            eff_rate = round(monthly_gross / monthly_hours, 2)

        diff = round(cls.STATUTORY_MINIMUM_WAGE_2026 - eff_rate, 2)
        compliant = eff_rate >= cls.STATUTORY_MINIMUM_WAGE_2026

        backpay = round(diff * monthly_hours, 2) if diff > 0 else 0.0
        is_mini = monthly_gross <= cls.MINIJOB_LIMIT_2026
        max_mini_hours = round(cls.MINIJOB_LIMIT_2026 / cls.STATUTORY_MINIMUM_WAGE_2026, 2)

        return MindestlohnCheckResult(
            monthly_gross=monthly_gross,
            monthly_hours=monthly_hours,
            effective_hourly_wage=eff_rate,
            statutory_minimum_wage=cls.STATUTORY_MINIMUM_WAGE_2026,
            is_compliant=compliant,
            wage_difference_per_hour=max(0.0, diff),
            total_monthly_backpay_due=backpay,
            is_minijob=is_mini,
            max_minijob_hours_allowed=max_mini_hours,
            fks_fine_risk=not compliant,
        )


class ArbeitszeitDE:
    @classmethod
    def validate_daily_shift(
        cls,
        gross_hours: float,
        pause_minutes: float
    ) -> DailyWorktimeResult:
        """
        Validiert einen Arbeitstag nach §§ 3, 4 ArbZG.
        - Bis 6h: 0 Min gesetzliche Mindestpause
        - > 6h bis 9h: mind. 30 Min Pause
        - > 9h: mind. 45 Min Pause
        - Max 10h Arbeitszeit (netto)
        """
        if gross_hours <= 6.0:
            min_pause = 0.0
        elif gross_hours <= 9.0:
            min_pause = 30.0
        else:
            min_pause = 45.0

        pause_ok = pause_minutes >= min_pause
        net_hours = round(gross_hours - (pause_minutes / 60.0), 2)

        # § 3 ArbZG: Maximal 10 Stunden Netto-Arbeitszeit pro Tag
        exceeded = net_hours > 10.0
        warning = None
        if exceeded:
            warning = f"Verstoß gegen § 3 ArbZG: Netto-Arbeitszeit von {net_hours}h überschreitet die Höchstgrenze von 10,0h!"
        elif not pause_ok:
            warning = f"Verstoß gegen § 4 ArbZG: Gesetzliche Mindestpause von {min_pause} Min unterschritten ({pause_minutes} Min erfasst)!"

        return DailyWorktimeResult(
            gross_hours=gross_hours,
            pause_minutes_taken=pause_minutes,
            net_hours=net_hours,
            statutory_min_pause_minutes=min_pause,
            pause_compliant=pause_ok,
            max_daily_hours_exceeded=exceeded,
            daily_hours_warning=warning,
        )
