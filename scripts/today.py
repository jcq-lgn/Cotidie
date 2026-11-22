#!/usr/bin/env python3
"""Idée, numéro et images du jour, d'après la date (heure de Paris).

La vidéo 001 date du 21/11/2026 ; chaque jour suivant prend l'idée suivante de IDEAS.md.
Les images tournent : chaque jour reçoit une sélection (~45) de la banque, décalée d'un jour
à l'autre pour éviter de revoir les mêmes statues d'une vidéo à la suivante.
Usage : python3 scripts/today.py [AAAA-MM-JJ]   -> JSON {num, idea, pool, by_tag}
"""
import datetime, json, os, random, re, sys
from zoneinfo import ZoneInfo

START = datetime.date(2026, 11, 21)
POOL = 45
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
today = datetime.datetime.now(ZoneInfo("Europe/Paris")).date()
if len(sys.argv) > 1: today = datetime.date.fromisoformat(sys.argv[1])
n = (today - START).days + 1
ideas = [re.sub(r"^- \[[ x]\]\s*(\d{3}\s*)?", "", l).strip()
         for l in open(os.path.join(here, "IDEAS.md"), encoding="utf-8") if re.match(r"^- \[[ x]\]", l)]
lib = json.load(open(os.path.join(here, "library.json")))
keys = sorted(k for k in lib if not k.endswith("_sil"))
random.Random(2026).shuffle(keys)          # fixed order, then a sliding window per day
start = ((n - 1) * POOL) % len(keys)
pool = [keys[(start + i) % len(keys)] for i in range(POOL)] + ["protes_0_sil"]
by_tag = {}
for k in pool:
    for t in lib[k][2]: by_tag.setdefault(t, []).append(k)
print(json.dumps(dict(num=f"{n:03d}", idea=ideas[(n - 1) % len(ideas)], pool=pool,
                      by_tag=dict(sorted(by_tag.items()))), ensure_ascii=False, indent=1))
