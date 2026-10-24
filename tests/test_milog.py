"""
test_milog.py - Test Suite für milog_dach
30 automatisierte Unit-Tests für Deutschland (MiLoG/ArbZG), Österreich (AZG), Schweiz (ArG) und Stundenzettel-Validierung.
"""

import pytest
from milog_dach.milog_de import MindestlohnDE, ArbeitszeitDE
from milog_dach.austria_azg import AustriaArbeitszeit
from milog_dach.switzerland_arg import SwitzerlandArbeitszeit
from milog_dach.timesheet import TimesheetValidator, ShiftEntry

# ==========================================
# 1. DEUTSCHLAND MINDESTLOHN TESTS (§ 1 MiLoG)
# ==========================================

def test_de_statutory_minimum_wage_constant():
    assert MindestlohnDE.STATUTORY_MINIMUM_WAGE_2026 == 12.82
    assert MindestlohnDE.MINIJOB_LIMIT_2026 == 538.00

def test_de_salary_compliant():
    res = MindestlohnDE.check_salary(monthly_gross=2200.00, monthly_hours=160.0)
    assert res.is_compliant is True
    assert res.effective_hourly_wage == 13.75
    assert res.wage_difference_per_hour == 0.0
    assert res.total_monthly_backpay_due == 0.0

def test_de_salary_underpaid_triggers_backpay():
    res = MindestlohnDE.check_salary(monthly_gross=1800.00, monthly_hours=160.0)
    assert res.is_compliant is False
    assert res.effective_hourly_wage == 11.25
    assert res.wage_difference_per_hour == 1.57
    assert res.total_monthly_backpay_due == round(1.57 * 160.0, 2)
    assert res.fks_fine_risk is True

def test_de_salary_exact_boundary():
    res = MindestlohnDE.check_salary(monthly_gross=2051.20, monthly_hours=160.0)
    assert res.is_compliant is True
    assert res.effective_hourly_wage == 12.82
    assert res.wage_difference_per_hour == 0.0

def test_de_minijob_hours_calculation():
    res = MindestlohnDE.check_salary(monthly_gross=538.00, monthly_hours=40.0)
    assert res.is_minijob is True
    assert res.max_minijob_hours_allowed == 41.97
    assert res.is_compliant is True

# ==========================================
# 2. DEUTSCHLAND ARBEITSZEIT TESTS (§§ 3, 4 ArbZG)
# ==========================================

def test_de_shift_under_6h_needs_no_pause():
    res = ArbeitszeitDE.validate_daily_shift(gross_hours=5.5, pause_minutes=0.0)
    assert res.pause_compliant is True
    assert res.statutory_min_pause_minutes == 0.0
    assert res.net_hours == 5.5

def test_de_shift_6h_to_9h_needs_30m_pause():
    ok_res = ArbeitszeitDE.validate_daily_shift(gross_hours=8.0, pause_minutes=30.0)
    assert ok_res.pause_compliant is True
    assert ok_res.statutory_min_pause_minutes == 30.0
    assert ok_res.net_hours == 7.5

    bad_res = ArbeitszeitDE.validate_daily_shift(gross_hours=8.0, pause_minutes=15.0)
    assert bad_res.pause_compliant is False
    assert "Mindestpause von 30.0 Min unterschritten" in bad_res.daily_hours_warning

def test_de_shift_over_9h_needs_45m_pause():
    res = ArbeitszeitDE.validate_daily_shift(gross_hours=10.0, pause_minutes=45.0)
    assert res.pause_compliant is True
    assert res.statutory_min_pause_minutes == 45.0
    assert res.net_hours == 9.25

def test_de_shift_exceeding_10h_net():
    res = ArbeitszeitDE.validate_daily_shift(gross_hours=11.5, pause_minutes=60.0)
    assert res.max_daily_hours_exceeded is True
    assert "Höchstgrenze von 10,0h" in res.daily_hours_warning

# ==========================================
# 3. ÖSTERREICH AZG TESTS
# ==========================================

def test_at_normal_shift():
    res = AustriaArbeitszeit.calculate_shift(worked_hours=8.5, pause_minutes=30.0)
    assert res.net_hours == 8.0
    assert res.normal_hours == 8.0
    assert res.overtime_50_hours == 0.0
    assert res.is_daily_max_exceeded is False

def test_at_overtime_50_standard():
    res = AustriaArbeitszeit.calculate_shift(worked_hours=10.5, pause_minutes=30.0, is_holiday_or_night=False)
    assert res.net_hours == 10.0
    assert res.normal_hours == 8.0
    assert res.overtime_50_hours == 2.0
    assert res.overtime_100_hours == 0.0

def test_at_overtime_100_holiday():
    res = AustriaArbeitszeit.calculate_shift(worked_hours=10.5, pause_minutes=30.0, is_holiday_or_night=True)
    assert res.overtime_50_hours == 0.0
    assert res.overtime_100_hours == 2.0

def test_at_daily_max_exceeded():
    res = AustriaArbeitszeit.calculate_shift(worked_hours=13.0, pause_minutes=30.0)
    assert res.is_daily_max_exceeded is True
    assert "Höchstarbeitszeit von 12,0h überschritten" in res.warning

def test_at_pause_violation():
    res = AustriaArbeitszeit.calculate_shift(worked_hours=7.0, pause_minutes=15.0)
    assert res.pause_compliant is False

# ==========================================
# 4. SCHWEIZ ArG & MINDESTLOHN TESTS
# ==========================================

def test_ch_cantonal_minimum_wages():
    assert SwitzerlandArbeitszeit.CANTONAL_MINIMUM_WAGES["GE"] == 24.32
    assert SwitzerlandArbeitszeit.CANTONAL_MINIMUM_WAGES["NE"] == 21.09
    assert SwitzerlandArbeitszeit.CANTONAL_MINIMUM_WAGES["JU"] == 20.60
    assert SwitzerlandArbeitszeit.CANTONAL_MINIMUM_WAGES["BS"] == 21.45
    assert SwitzerlandArbeitszeit.CANTONAL_MINIMUM_WAGES["TI"] == 20.25

def test_ch_geneva_minimum_wage_compliant():
    res = SwitzerlandArbeitszeit.calculate_shift(gross_hours=8.0, pause_minutes=30.0, canton="GE", hourly_wage=25.00)
    assert res.is_wage_compliant is True
    assert res.cantonal_minimum_wage == 24.32

def test_ch_geneva_minimum_wage_underpaid():
    res = SwitzerlandArbeitszeit.calculate_shift(gross_hours=8.0, pause_minutes=30.0, canton="GE", hourly_wage=22.00)
    assert res.is_wage_compliant is False
    assert "unterschreitet Minimum" in res.warning

def test_ch_arg_pause_tiers():
    r1 = SwitzerlandArbeitszeit.calculate_shift(gross_hours=6.0, pause_minutes=10.0)
    assert r1.pause_compliant is False
    assert r1.statutory_min_pause_minutes == 15.0

    r2 = SwitzerlandArbeitszeit.calculate_shift(gross_hours=8.0, pause_minutes=20.0)
    assert r2.pause_compliant is False
    assert r2.statutory_min_pause_minutes == 30.0

    r3 = SwitzerlandArbeitszeit.calculate_shift(gross_hours=10.0, pause_minutes=45.0)
    assert r3.pause_compliant is False
    assert r3.statutory_min_pause_minutes == 60.0

    r4 = SwitzerlandArbeitszeit.calculate_shift(gross_hours=10.0, pause_minutes=60.0)
    assert r4.pause_compliant is True

# ==========================================
# 5. TIMESHEET VALIDATOR TESTS (§ 17 MiLoG)
# ==========================================

def test_timesheet_evaluation_compliant():
    entries = [
        ShiftEntry(date_str="2026-10-01", start_time="08:00", end_time="16:30", pause_minutes=30.0),
        ShiftEntry(date_str="2026-10-02", start_time="08:00", end_time="16:30", pause_minutes=30.0),
        ShiftEntry(date_str="2026-10-03", start_time="08:00", end_time="16:30", pause_minutes=30.0),
    ]
    report = TimesheetValidator.evaluate_month(
        employee_name="Max Mustermann",
        month_year="10/2026",
        contract_monthly_gross=350.00,
        entries=entries
    )
    assert report.total_net_hours == 24.0
    assert report.effective_hourly_wage == 14.58
    assert report.milog_compliant is True
    assert report.arbzg_compliant is True
    assert report.invalid_shifts_count == 0

def test_timesheet_evaluation_underpaid():
    entries = [
        ShiftEntry(date_str="2026-10-01", start_time="08:00", end_time="16:30", pause_minutes=30.0),
        ShiftEntry(date_str="2026-10-02", start_time="08:00", end_time="16:30", pause_minutes=30.0),
    ]
    report = TimesheetValidator.evaluate_month(
        employee_name="Max Mustermann",
        month_year="10/2026",
        contract_monthly_gross=150.00,
        entries=entries
    )
    assert report.milog_compliant is False
    assert len(report.audit_notes) > 0
    assert "unterschreitet 12,82 €" in report.audit_notes[0]

# ==========================================
# 6. CLI TESTS
# ==========================================

def test_cli_check_json(monkeypatch, capsys):
    from milog_dach.cli import main
    monkeypatch.setattr("sys.argv", ["dach-milog", "check", "--salary", "2500", "--hours", "160", "--json"])
    main()
    out = capsys.readouterr().out
    assert '"is_compliant": true' in out
    assert '"effective_hourly_wage": 15.62' in out

def test_cli_shift_json(monkeypatch, capsys):
    from milog_dach.cli import main
    monkeypatch.setattr("sys.argv", ["dach-milog", "shift", "--gross", "8.0", "--pause", "30", "--json"])
    main()
    out = capsys.readouterr().out
    assert '"pause_compliant": true' in out
    assert '"net_hours": 7.5' in out

def test_cli_at_json(monkeypatch, capsys):
    from milog_dach.cli import main
    monkeypatch.setattr("sys.argv", ["dach-milog", "at", "--hours", "10", "--pause", "30", "--json"])
    main()
    out = capsys.readouterr().out
    assert '"overtime_50_hours": 1.5' in out

def test_cli_ch_json(monkeypatch, capsys):
    from milog_dach.cli import main
    monkeypatch.setattr("sys.argv", ["dach-milog", "ch", "--canton", "GE", "--wage", "25", "--json"])
    main()
    out = capsys.readouterr().out
    assert '"is_wage_compliant": true' in out
    assert '"cantonal_minimum_wage": 24.32' in out

def test_de_midijob_upper_limit():
    assert MindestlohnDE.MIDIJOB_UPPER_LIMIT_2026 == 2000.00

def test_de_zero_hours_effective_rate_is_zero():
    res = MindestlohnDE.check_salary(monthly_gross=1000.00, monthly_hours=0.0)
    assert res.effective_hourly_wage == 0.0
    assert res.is_compliant is False

def test_ch_weekly_max_hours_constants():
    assert SwitzerlandArbeitszeit.WEEKLY_MAX_HOURS_OFFICE == 45.0
    assert SwitzerlandArbeitszeit.WEEKLY_MAX_HOURS_OTHER == 50.0

def test_at_weekly_max_hours_constant():
    assert AustriaArbeitszeit.WEEKLY_MAX_HOURS == 60.0

def test_timesheet_overnight_shift():
    # Schicht von 22:00 bis 06:00 (Nachtschicht) -> 8h brutto, 45m Pause -> 7.25h Netto
    entries = [
        ShiftEntry(date_str="2026-10-01", start_time="22:00", end_time="06:00", pause_minutes=45.0),
    ]
    report = TimesheetValidator.evaluate_month(
        employee_name="Nachtarbeiter",
        month_year="10/2026",
        contract_monthly_gross=200.00,
        entries=entries
    )
    assert report.total_net_hours == 7.25
    assert report.total_shifts_count == 1

def test_cli_help(monkeypatch, capsys):
    from milog_dach.cli import main
    monkeypatch.setattr("sys.argv", ["dach-milog", "--help"])
    with pytest.raises(SystemExit):
        main()
    out = capsys.readouterr().out
    assert "DACH Mindestlohn" in out
