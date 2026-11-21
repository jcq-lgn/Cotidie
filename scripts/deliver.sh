#!/usr/bin/env bash
# Rend une vidéo puis produit une version légère pour le téléphone.
# Usage : scripts/deliver.sh videos/NNN_slug.json
set -e
cd "$(dirname "$0")/.."
src="$1"; base=$(basename "$src" .json)
mkdir -p out
python3 pipe/render2.py "$src" "out/$base.mp4"
in="out/${base}_sans_musique.mp4"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
# Fichier livré < 14 Mo (limite des pages de livraison) : encodage 2 passes.
vb=$(python3 -c "print(int(13.2*8*1024*1024/$d - 128000))")
( cd out && ffmpeg -y -v error -i "../$in" -c:v libx264 -preset slow -b:v $vb -pass 1 -passlogfile "$base" -an -f null /dev/null \
  && ffmpeg -y -v error -i "../$in" -c:v libx264 -preset slow -b:v $vb -pass 2 -passlogfile "$base" \
     -c:a aac -b:a 128k -movflags +faststart "${base}_A_PUBLIER.mp4" && rm -f "$base"-0.log* )
ffmpeg -y -v error -i "out/$base.mp4" -vf "fps=1/2,scale=150:-1,tile=8x4" -frames:v 1 "out/${base}_controle.png"
python3 pipe/cover.py "$src" "out/${base}_couverture.jpg"
python3 - "$src" "out/${base}_texte.txt" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
desc = d.get("description") or d.get("caption", "")
tags = " ".join(d.get("hashtags", []))
txt = f"TITRE : {d.get('title','')}\n\nDESCRIPTION :\n{desc}\n\nHASHTAGS :\n{tags}\n\nA COPIER DANS TIKTOK :\n{desc}\n\n{tags}\n"
open(sys.argv[2], "w").write(txt); print(txt)
PY
python3 pipe/page.py "$src" "out/${base}_page.html"
ls -la "out/${base}_A_PUBLIER.mp4"
echo "out/${base}_A_PUBLIER.mp4"
echo "out/${base}_couverture.jpg"
echo "out/${base}_page.html"
