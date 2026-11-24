# Cotidie — résumé du projet (à donner à Claude pour reprendre)

## Le compte
- TikTok **Cotidie**, pseudo **@cotidie.mentalite**. Niche : motivation, stoïcisme, discipline, Antiquité (Rome, Grèce, Sparte), Goggins.
- Public mesuré : 25-34 ans (40 %), 18-24 ans (31 %), France 76 %, Belgique, Suisse, Outre-mer. Vouvoiement.
- Publication manuelle par le propriétaire à **18h30** avec le son TikTok **« revolt » (kil krook)**, démarrage au début, volume 30-40 %, couverture importée, case « contenu généré par IA » cochée.
- Photo de profil : fragment de Marc Aurèle sur fond « Glacier » (`branding/photo_profil.jpg`). Bio proposée : « 🏛️ La discipline des Anciens. Un rappel par jour pour devenir inarrêtable. »

## Le dépôt `jcq-lgn/cotidie` (public, branche main)
- `pipe/render2.py` moteur de montage · `pipe/audio2.py` voix + mixage · `pipe/cover.py` couverture · `pipe/page.py` page de livraison · `pipe/hardtek.py` musique générée (non utilisée par défaut).
- `DA.md` charte validée · `SCRIPT_GUIDE.md` règles d'écriture (accroche, durée 30-40 s, style de description, banque d'images) · `IDEAS.md` 38 idées.
- `library.json` + `assets/lib/` : 121 images (Met + Art Institute of Chicago, domaine public), rotation quotidienne via `scripts/today.py`.
- `scripts/setup.sh` (installe, corrige le certificat pour edge-tts) · `scripts/deliver.sh videos/NNN.json` (rendu + compression < 14 Mo + couverture + page).
- `music/revolt/beats.json` : temps du son « revolt » pour caler les coupes (le son lui-même n'est pas stocké).

## La DA « Glacier » (validée)
Noir bleuté, marbre froid, accent bleu glacé ; fonds `dark` / `light` (marbre) / `blue` (lignes de vitesse). Police Anton. Pas de rouge ni de doré. Plans toutes les ~2 temps, pulsation sur chaque temps, flash/glitch sur les `hit`. Voix edge-tts **Remy** (+10 %, variation par phrase, traitement léger, pas de pauses forcées). Cadrage dans la zone sûre TikTok ; couverture cadrée pour le recadrage 3:4.

## La production automatique
- Tâche planifiée **« Cotidie – vidéo TikTok du jour »** (id `trig_01U6r5hX8TVk5zGWotb8i7jW`), chaque jour 14h52 (Paris).
- Elle clone le dépôt public, lit `scripts/today.py` (numéro + idée + sélection d'images), écrit le script, monte la vidéo, publie une **page privée** (vidéo, texte à copier, couverture) et envoie une notification.
- Limites : la tâche ne peut ni pousser dans le dépôt ni utiliser de connecteur (Windsor/TikTok).

## Statistiques
- Connecteur **Windsor.ai for Social Media** relié au compte TikTok (lecture des stats).
- Tableau de bord en direct : **Cotidie Stats** https://claude.ai/artifact/HTdAxmG92XjTih9wN7Zc1C (requêtes sur 30 jours : l'essai Windsor ne donne pas plus d'historique)
- Bilan quotidien : demander « fais le point de la vidéo d'hier » dans une conversation (avec ce dépôt).
- 001 Milon (48 s) : 518 vues, 8,7 s, 2,7 % jusqu'au bout. 002 Marc Aurèle (41 s) : 1 234 vues, 13,1 s, 4,6 %, 74 % à 1 s.
- 23/11 : TikTok a boosté la 001 (+284 vues) car jugée « utile » → chaque vidéo finit par une action précise faisable aujourd'hui (voir `SCRIPT_GUIDE.md`).
- 23/11 : la 001 a été **supprimée** par la modération automatique (lutteurs nus en couverture). Images nues exclues via `library_exclus.json`.
- 24/11 : une vidéo sur deux = personnalité moderne illustrée par ses vraies photos (Wikimedia, `p_*`, crédits dans `credits.json`), alternée avec l'Antiquité. Étiquettes {sujet} dans `IDEAS.md`.
- Leçons : la 1re seconde décide (image forte + accroche écrite dès 0 s), vidéos 30-40 s, relance à mi-vidéo, épingler la question en commentaire.
