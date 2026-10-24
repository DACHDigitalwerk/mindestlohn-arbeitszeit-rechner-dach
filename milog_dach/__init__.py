"""
milog_dach - DACH Mindestlohn-, Mindestvergütungs- & Arbeitszeit-Prüfer 2026 (DE, AT, CH)
Reine kaufmännische und arbeitszeitrechtliche Berechnungsmathematik nach MiLoG § 17, ArbZG, AZG und ArG.
Konform mit BGH Smartlaw (Az. I ZR 226/20) - 100% Client-Side / Offline-tauglich.
"""

__version__ = "1.0.0"
__author__ = "DACH Digitalwerk"

from .milog_de import MindestlohnDE, ArbeitszeitDE
from .austria_azg import AustriaArbeitszeit
from .switzerland_arg import SwitzerlandArbeitszeit
from .timesheet import TimesheetValidator, ShiftEntry

__all__ = [
    "MindestlohnDE",
    "ArbeitszeitDE",
    "AustriaArbeitszeit",
    "SwitzerlandArbeitszeit",
    "TimesheetValidator",
    "ShiftEntry",
]
