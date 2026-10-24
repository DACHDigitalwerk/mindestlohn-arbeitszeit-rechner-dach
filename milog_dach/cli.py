"""
cli.py - Command Line Interface für DACH Mindestlohn- & Arbeitszeit-Prüfer 2026
"""

import argparse
import sys
import json
from .milog_de import MindestlohnDE, ArbeitszeitDE
from .austria_azg import AustriaArbeitszeit
from .switzerland_arg import SwitzerlandArbeitszeit
from .timesheet import TimesheetValidator, ShiftEntry

def main():
    parser = argparse.ArgumentParser(
        prog="dach-milog",
        description="DACH Mindestlohn-, Mindestvergütungs- & Arbeitszeit-Prüfer 2026 (DE, AT, CH)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Modus wählen")

    # Command: check (DE Gehaltsprüfung)
    check_p = subparsers.add_parser("check", help="Prüfung Monatsgehalt vs. Mindestlohn (§ 1 MiLoG)")
    check_p.add_argument("--salary", type=float, required=True, help="Monatsbruttogehalt in Euro")
    check_p.add_argument("--hours", type=float, required=True, help="Tatsächlich geleistete Monatsstunden")
    check_p.add_argument("--json", action="store_true", help="JSON-Ausgabe")

    # Command: shift (DE ArbZG Schichtprüfung)
    shift_p = subparsers.add_parser("shift", help="Prüfung Einzelschicht nach §§ 3, 4 ArbZG")
    shift_p.add_argument("--gross", type=float, required=True, help="Brutto-Anwesenheit in Stunden")
    shift_p.add_argument("--pause", type=float, default=30.0, help="Pausenzeit in Minuten")
    shift_p.add_argument("--json", action="store_true", help="JSON-Ausgabe")

    # Command: at (Österreich AZG Schichtprüfung)
    at_p = subparsers.add_parser("at", help="Österreich Arbeitszeit- und Überstundenprüfung (AZG)")
    at_p.add_argument("--hours", type=float, required=True, help="Arbeitsstunden brutto")
    at_p.add_argument("--pause", type=float, default=30.0, help="Pausenzeit in Minuten")
    at_p.add_argument("--holiday", action="store_true", help="Feiertags- oder Nachtarbeit (100 Prozent Zuschlag)")
    at_p.add_argument("--json", action="store_true", help="JSON-Ausgabe")

    # Command: ch (Schweiz ArG & kantonaler Mindestlohn)
    ch_p = subparsers.add_parser("ch", help="Schweiz Arbeitszeit nach ArG & kantonaler Mindestlohn")
    ch_p.add_argument("--canton", choices=["GE", "NE", "JU", "BS", "TI"], default="GE", help="Kanton mit Mindestlohn")
    ch_p.add_argument("--wage", type=float, help="Stundenlohn in CHF")
    ch_p.add_argument("--gross", type=float, default=8.0, help="Brutto-Arbeitszeit in Stunden")
    ch_p.add_argument("--pause", type=float, default=30.0, help="Pausenzeit in Minuten")
    ch_p.add_argument("--json", action="store_true", help="JSON-Ausgabe")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "check":
        res = MindestlohnDE.check_salary(monthly_gross=args.salary, monthly_hours=args.hours)
        if args.json:
            print(json.dumps(res.__dict__, indent=2))
        else:
            print("==========================================================")
            print("  DACH Digitalwerk — Mindestlohn-Prüfung Deutschland 2026")
            print("==========================================================")
            print(f"Monatsgehalt:           {res.monthly_gross:.2f} €")
            print(f"Monatsstunden:          {res.monthly_hours:.2f} h")
            print(f"Effektiver Stundenlohn: {res.effective_hourly_wage:.2f} €/h (Gesetzl. Mindestlohn: {res.statutory_minimum_wage:.2f} €/h)")
            status = "✅ KONFORM (§ 1 MiLoG eingehalten)" if res.is_compliant else "❌ VERSTOSS (§ 1 MiLoG unterschritten!)"
            print(f"Status:                 {status}")
            if not res.is_compliant:
                print(f"Fehlbetrag pro Stunde:  {res.wage_difference_per_hour:.2f} €")
                print(f"Nachzahlungspflicht:    {res.total_monthly_backpay_due:.2f} € / Monat")
                print(f"FKS-Bußgeldrisiko:      {res.fks_fine_risk} (bis zu 500.000 € gem. § 21 MiLoG)")
            if res.is_minijob:
                print(f"Minijob-Prüfung:        Zulässige Höchstarbeitszeit: {res.max_minijob_hours_allowed:.2f} h/Monat (bei 538 €)")
            print("==========================================================")

    elif args.command == "shift":
        res = ArbeitszeitDE.validate_daily_shift(gross_hours=args.gross, pause_minutes=args.pause)
        if args.json:
            print(json.dumps(res.__dict__, indent=2))
        else:
            print("==========================================================")
            print("  DACH Digitalwerk — Arbeitszeit-Prüfung ArbZG")
            print("==========================================================")
            print(f"Brutto-Anwesenheit:     {res.gross_hours:.2f} h")
            print(f"Pausenzeit erfasst:     {res.pause_minutes_taken:.1f} Min (Gesetzl. Minimum: {res.statutory_min_pause_minutes:.1f} Min)")
            print(f"Netto-Arbeitszeit:      {res.net_hours:.2f} h")
            print(f"Pausen-Konformität:     {'✅ Eingehalten' if res.pause_compliant else '❌ Unzulässig verkürzt'}")
            print(f"Höchstarbeitszeit (10h):{'❌ Überschritten!' if res.max_daily_hours_exceeded else '✅ Zulässig'}")
            if res.daily_hours_warning:
                print(f"Hinweis:                {res.daily_hours_warning}")
            print("==========================================================")

    elif args.command == "at":
        res = AustriaArbeitszeit.calculate_shift(
            worked_hours=args.hours,
            pause_minutes=args.pause,
            is_holiday_or_night=args.holiday
        )
        if args.json:
            print(json.dumps(res.__dict__, indent=2))
        else:
            print("==========================================================")
            print("  DACH Digitalwerk — Arbeitszeit & Überstunden Österreich")
            print("==========================================================")
            print(f"Netto-Arbeitszeit:      {res.net_hours:.2f} h")
            print(f"Normalarbeitszeit:      {res.normal_hours:.2f} h")
            print(f"Überstunden (50% Zuschlag):  {res.overtime_50_hours:.2f} h")
            print(f"Überstunden (100% Zuschlag): {res.overtime_100_hours:.2f} h")
            print(f"Tagesmaximum (12h AZG): {'❌ Überschritten!' if res.is_daily_max_exceeded else '✅ Eingehalten'}")
            if res.warning:
                print(f"Warnung:                {res.warning}")
            print("==========================================================")

    elif args.command == "ch":
        res = SwitzerlandArbeitszeit.calculate_shift(
            gross_hours=args.gross,
            pause_minutes=args.pause,
            canton=args.canton,
            hourly_wage=args.wage
        )
        if args.json:
            print(json.dumps(res.__dict__, indent=2))
        else:
            print("==========================================================")
            print("  DACH Digitalwerk — Arbeitszeit & Mindestlohn Schweiz")
            print("==========================================================")
            print(f"Kanton:                 {args.canton}")
            print(f"Netto-Arbeitszeit:      {res.net_hours:.2f} h (Pause: {res.pause_minutes_taken} Min / Gesetzl. Min: {res.statutory_min_pause_minutes} Min)")
            if res.cantonal_minimum_wage:
                print(f"Kantonaler Mindestlohn: {res.cantonal_minimum_wage:.2f} CHF/h")
            if res.effective_hourly_wage:
                print(f"Gezahlter Stundenlohn:  {res.effective_hourly_wage:.2f} CHF/h")
                print(f"Lohn-Konformität:       {'✅ Eingehalten' if res.is_wage_compliant else '❌ Unterschritten!'}")
            if res.warning:
                print(f"Hinweis:                {res.warning}")
            print("==========================================================")

if __name__ == "__main__":
    main()
