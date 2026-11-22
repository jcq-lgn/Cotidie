#!/usr/bin/env python3
"""Idée et numéro du jour, d'après la date (heure de Paris).

La vidéo 001 date du 21/11/2026 ; chaque jour suivant prend l'idée suivante de IDEAS.md
(lignes « - [ ] » et « - [x] » dans l'ordre). Aucune écriture dans le dépôt n'est nécessaire.
Usage : python3 scripts/today.py   ->  affiche « NNN|texte de l'idée »
"""
import datetime, os, re, sys
from zoneinfo import ZoneInfo

START = datetime.date(2026, 11, 21)
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
today = datetime.datetime.now(ZoneInfo("Europe/Paris")).date()
if len(sys.argv) > 1: today = datetime.date.fromisoformat(sys.argv[1])
n = (today - START).days + 1
ideas = [re.sub(r"^- \[[ x]\]\s*(\d{3}\s*)?", "", l).strip()
         for l in open(os.path.join(here, "IDEAS.md"), encoding="utf-8") if re.match(r"^- \[[ x]\]", l)]
idea = ideas[(n - 1) % len(ideas)]
print(f"{n:03d}|{idea}")
