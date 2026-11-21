#!/usr/bin/env bash
# Prépare une session cloud neuve pour le rendu (idempotent).
set -e
pip install -q edge-tts numpy scipy pillow 2>&1 | grep -v -i warn || true
# edge-tts (aiohttp) n'utilise pas le magasin de certificats système : on ajoute celui du proxy.
CERT=$(python3 -c "import certifi;print(certifi.where())")
if [ -f /root/.ccr/ca-bundle.crt ] && ! grep -q "$(sed -n 2p /root/.ccr/ca-bundle.crt)" "$CERT"; then
  cat /root/.ccr/ca-bundle.crt >> "$CERT"
fi
echo "setup ok"
