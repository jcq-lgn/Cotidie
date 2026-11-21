# Cotidie — production automatique de vidéos TikTok

Compte : **@cotidie.mentalite** · DA « Glacier » (voir `DA.md`).

## Contenu
- `pipe/render2.py` : moteur de montage (plans rapides calés sur le tempo, sous-titres mot à mot, effets).
- `pipe/audio2.py` : voix (edge-tts, Remy énergique), bruitages, mixage. Musique : piste externe calée sur ses temps, ou thème hard tek généré (`pipe/hardtek.py`).
- `pipe/prep2.py` + `library.json` : banque d'images (Met Museum, domaine public) classées par thème, rendu marbre froid → `assets/lib/`.
- `videos/*.json` : scripts des vidéos (texte, images, fonds, effets).
- `music/revolt/beats.json` : temps du son « revolt » (kil krook) pour caler le montage. Le son lui-même n'est pas stocké (droits) : on l'ajoute dans TikTok.
- `branding/` : photo de profil.

## Générer une vidéo
```bash
pip install -r requirements.txt
python3 pipe/render2.py videos/001_milon_revolt.json out/001.mp4
```
Sortie : `out/001.mp4` et `out/001_sans_musique.mp4` (à publier, son ajouté dans TikTok, démarrage au début, volume 30-40 %), plus `out/001.json` (légende).

Réseau requis : `speech.platform.bing.com` (voix), `collectionapi.metmuseum.org` / `images.metmuseum.org` (nouvelles images).
