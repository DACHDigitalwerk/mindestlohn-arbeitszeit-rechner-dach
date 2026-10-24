"""
timesheet.py - MiLoG § 17 Stundennachweis- & Zeiterfassungs-Validator
Prüft vollständige Monats-Stundenzettel auf Einhaltung von ArbZG und MiLoG.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .milog_de import ArbeitszeitDE, MindestlohnDE

@dataclass
class ShiftEntry:
    date_str: str
    start_time: str # "HH:MM"
    end_time: str   # "HH:MM"
    pause_minutes: float
    notes: str = ""

@dataclass
class EvaluatedShift:
    date_str: str
    start_time: str
    end_time: str
    gross_hours: float
    pause_minutes: float
    net_hours: float
    is_valid: bool
    warning: Optional[str]

@dataclass
class MonthlyTimesheetReport:
    employee_name: str
    month_year: str
    contract_monthly_gross: float
    total_net_hours: float
    effective_hourly_wage: float
    statutory_minimum_wage: float
    milog_compliant: bool
    arbzg_compliant: bool
    total_shifts_count: int
    invalid_shifts_count: int
    shifts: List[EvaluatedShift] = field(default_factory=list)
    audit_notes: List[str] = field(default_factory=list)


class TimesheetValidator:
    @staticmethod
    def _parse_time(time_str: str) -> float:
        parts = time_str.strip().split(":")
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        return h + (m / 60.0)

    @classmethod
    def evaluate_month(
        cls,
        employee_name: str,
        month_year: str,
        contract_monthly_gross: float,
        entries: List[ShiftEntry]
    ) -> MonthlyTimesheetReport:
        evaluated: List[EvaluatedShift] = []
        total_net = 0.0
        arbzg_ok = True
        notes: List[str] = []

        for entry in entries:
            t_start = cls._parse_time(entry.start_time)
            t_end = cls._parse_time(entry.end_time)
            gross = round(t_end - t_start, 2)
            if gross < 0:
                gross += 24.0

            res = ArbeitszeitDE.validate_daily_shift(gross_hours=gross, pause_minutes=entry.pause_minutes)
            shift_valid = res.pause_compliant and not res.max_daily_hours_exceeded

            if not shift_valid:
                arbzg_ok = False
                notes.append(f"{entry.date_str}: {res.daily_hours_warning}")

            total_net += res.net_hours
            evaluated.append(
                EvaluatedShift(
                    date_str=entry.date_str,
                    start_time=entry.start_time,
                    end_time=entry.end_time,
                    gross_hours=gross,
                    pause_minutes=entry.pause_minutes,
                    net_hours=res.net_hours,
                    is_valid=shift_valid,
                    warning=res.daily_hours_warning,
                )
            )

        total_net = round(total_net, 2)
        milog_res = MindestlohnDE.check_salary(monthly_gross=contract_monthly_gross, monthly_hours=total_net)

        if not milog_res.is_compliant:
            notes.append(
                f"MiLoG § 1 Verstoß: Effektiver Stundenlohn von {milog_res.effective_hourly_wage:.2f} € unterschreitet 12,82 €! Nachzahlungsanspruch: {milog_res.total_monthly_backpay_due:.2f} €."
            )

        invalid_count = sum(1 for s in evaluated if not s.is_valid)

        return MonthlyTimesheetReport(
            employee_name=employee_name,
            month_year=month_year,
            contract_monthly_gross=contract_monthly_gross,
            total_net_hours=total_net,
            effective_hourly_wage=milog_res.effective_hourly_wage,
            statutory_minimum_wage=MindestlohnDE.STATUTORY_MINIMUM_WAGE_2026,
            milog_compliant=milog_res.is_compliant,
            arbzg_compliant=arbzg_ok,
            total_shifts_count=len(evaluated),
            invalid_shifts_count=invalid_count,
            shifts=evaluated,
            audit_notes=notes,
        )
