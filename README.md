# ⏱️ DACH Mindestlohn-, Mindestvergütungs- & Arbeitszeit-Prüfer 2026 (DE, AT, CH)

[![CI Tests](https://github.com/DACHDigitalwerk/mindestlohn-arbeitszeit-rechner-dach/actions/workflows/ci.yml/badge.svg)](https://github.com/DACHDigitalwerk/mindestlohn-arbeitszeit-rechner-dach/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![BGH Smartlaw Compliant](https://img.shields.io/badge/Compliance-BGH%20Smartlaw%20(I%20ZR%20226%2F20)-green.svg)](https://dachdigitalwerk.github.io/haftungsausschluss/)

Reine kaufmännische und arbeitszeitrechtliche Berechnungs- und Prüfungsmathematik für Arbeitgeber, Personalabteilungen, Lohnbuchhalter und Betriebsräte im DACH-Raum (Deutschland, Österreich, Schweiz).

🔗 **Interaktiver Web-Rechner & § 17 MiLoG Stundenzettel-Generator (100% Client-Side):**  
👉 **[https://dachdigitalwerk.github.io/mindestlohn-arbeitszeit-rechner/](https://dachdigitalwerk.github.io/mindestlohn-arbeitszeit-rechner/)**

---

## 📌 Gesetzliche Grundlagen 2026

### 🇩🇪 Deutschland
- **Gesetzlicher Mindestlohn 2026 (§ 1 MiLoG):**  
  **12,82 € brutto je Zeitstunde**. Gilt ausnahmslos für alle volljährigen Arbeitnehmer, Minijobber, Praktikanten nach 3 Monaten und ausländische Beschäftigte im Inland.
- **Minijob- & Übergangsbereich (§ 8 / § 20 SGB IV):**  
  Minijob-Grenze: **538,00 € / Monat** (maximal **41,97 Stunden** bei 12,82 €/h). Übergangsbereich (Midijob): bis 2.000,00 €.
- **Arbeitszeitgesetz (ArbZG):**
  - **§ 3 ArbZG:** Tägliche Höchstarbeitszeit grundsätzlich **8 Stunden**, Verlängerung auf **10 Stunden** nur bei 6-Monats-Ausgleich auf durchschnittlich 8h.
  - **§ 4 ArbZG Ruhepausen:** Bei > 6 bis 9 Stunden Arbeit: mindestens **30 Minuten** Pause. Bei > 9 Stunden: mindestens **45 Minuten** Pause. Pausenteilung nur in Abschnitten von mindestens 15 Minuten.
  - **§ 5 ArbZG:** Ununterbrochene Ruhezeit von mindestens **11 Stunden** nach Schichtende.
- **Dokumentationspflicht (§ 17 MiLoG):**  
  Beginn, Ende und Dauer der täglichen Arbeitszeit müssen spätestens bis zum Ablauf des 7. auf den Tag der Arbeitsleistung folgenden Kalendertags aufgezeichnet und **mindestens 2 Jahre aufbewahrt** werden. Zoll-Prüfungen durch die Finanzkontrolle Schwarzarbeit (FKS). Bußgelder bis zu **500.000 €** gem. § 21 MiLoG.

### 🇦🇹 Österreich
- **Arbeitszeitgesetz (AZG):**
  - **Normalarbeitszeit:** 8 Stunden täglich, 40 Stunden wöchentlich (Kollektivverträge oft 38,5h).
  - **Höchstarbeitszeit:** Maximal 12 Stunden täglich, maximal 60 Stunden wöchentlich (§ 9 AZG).
  - **Überstundenzuschlag (§ 10 AZG):** Mindestens **50 % Zuschlag** auf Normalstundenlohn; **100 % Zuschlag** für Sonn-/Feiertags- und Nachtarbeit.
  - **Ruhepausen (§ 11 AZG):** Mindestens 30 Minuten bei mehr als 6 Stunden Arbeit.

### 🇨🇭 Schweiz
- **Kantonale Mindestlöhne 2026:**
  - **Genf (GE):** **24,32 CHF/h** (weltweiter Spitzenwert)
  - **Neuenburg (NE):** **21,09 CHF/h**
  - **Jura (JU):** **20,60 CHF/h**
  - **Basel-Stadt (BS):** **21,45 CHF/h**
  - **Tessin (TI):** **20,25 CHF/h**
- **Arbeitsgesetz (ArG):**
  - Wöchentliche Höchstarbeitszeit: **45 Stunden** (Büro, Industrie) bzw. **50 Stunden** (Gewerbe, Gastronomie).
  - Ruhepausen (Art. 15 ArG): 15 Min bei > 5.5h, 30 Min bei > 7h, 60 Min bei > 9h.

---

## ⚡ Schnellstart & Installation

```bash
git clone https://github.com/DACHDigitalwerk/mindestlohn-arbeitszeit-rechner-dach.git
cd mindestlohn-arbeitszeit-rechner-dach
pip install -e .
```

### CLI Verwendung

```bash
# Deutschland: Monatsgehalt 2.200 € bei 160h Arbeitszeit auf Mindestlohn prüfen
dach-milog check --salary 2200 --hours 160

# Deutschland: Schicht 8,5h mit 30 Min Pause auf ArbZG-Pausenkonformität prüfen
dach-milog shift --gross 8.5 --pause 30

# Österreich: Schicht 10h mit Überstundenberechnung (50% Zuschlag)
dach-milog at --hours 10.5 --pause 30

# Schweiz: Genf Mindestlohn-Prüfung (25 CHF/h vs. kantonal 24.32 CHF/h)
dach-milog ch --canton GE --wage 25.00 --gross 8.0 --pause 30
```

---

## 🧪 Tests ausführen

```bash
pytest -v
# 30 Tests bestanden (100% Pass Rate)
```

---

## 🛡️ Rechtlicher Hinweis & Compliance

Dieses Tool ist ein rein mathematisches Berechnungs- und Simulationstool. Es erfolgt keine individuelle Rechtsberatung im Sinne des Rechtsdienstleistungsgesetzes (§ 2 RDG). Konform mit dem BGH-Smartlaw-Urteil (Az. I ZR 226/20).

Offizielle Plattform & Nutzungsbedingungen:  
- Web-App: [https://dachdigitalwerk.github.io/mindestlohn-arbeitszeit-rechner/](https://dachdigitalwerk.github.io/mindestlohn-arbeitszeit-rechner/)  
- AGB: [https://dachdigitalwerk.github.io/agb/](https://dachdigitalwerk.github.io/agb/)  
- Haftungsausschluss: [https://dachdigitalwerk.github.io/haftungsausschluss/](https://dachdigitalwerk.github.io/haftungsausschluss/)

---

## 📄 Lizenz

MIT License — Copyright (c) 2026 DACH Digitalwerk.
