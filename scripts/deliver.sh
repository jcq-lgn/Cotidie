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
vb=$(python3 -c "print(int(min(6e6, 24*8*1024*1024/$d - 128000)))")
ffmpeg -y -v error -i "$in" -c:v libx264 -preset slow -b:v $vb -maxrate $((vb*2)) -bufsize $((vb*4)) \
  -c:a aac -b:a 128k -movflags +faststart "out/${base}_A_PUBLIER.mp4"
ffmpeg -y -v error -i "out/$base.mp4" -vf "fps=1/2,scale=150:-1,tile=8x4" -frames:v 1 "out/${base}_controle.png"
echo "out/${base}_A_PUBLIER.mp4"
