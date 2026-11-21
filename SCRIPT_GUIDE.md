# Guide d'écriture d'une vidéo Cotidie

Lire aussi `DA.md` (charte visuelle, validée par le propriétaire du compte — ne pas la modifier).
Exemple complet : `videos/001_milon_revolt.json`.

## Fond
- Niche : motivation, discipline, stoïcisme, musculation. Histoires **vraies** et vérifiables : Antiquité (Rome, Grèce, Sparte), philosophes stoïciens (Marc Aurèle, Sénèque, Épictète), athlètes antiques, et figures modernes de la discipline (David Goggins, etc.) citées sans montrer leur visage.
- Exactitude : pas de fausse citation ni de chiffre inventé. En cas de doute, formuler « la légende raconte… ».
- **Vouvoiement**. Phrases courtes, rythmées, qui se terminent par un appel à l'action concret.
- Structure : accroche choc en 1 phrase (≤ 3 s) → histoire → leçon → application concrète « aujourd'hui… » → chute forte.
- Longueur : 120 à 150 mots, **45 à 55 s** (le son « revolt » est calé jusqu'à ~55 s).

## Format JSON
```json
{
 "title": "...", "brand": "COTIDIE",
 "title": "Titre court et accrocheur",
 "description": "Description TikTok : 1-3 phrases qui donnent envie + une question pour faire commenter + 1 emoji",
 "hashtags": ["#stoicisme", "#motivation", "#discipline", "#musculation", "#mindset", "+ 3 à 5 liés au sujet"],
 "cover_title": "4 à 7 mots en MAJUSCULES, 1 mot-clé entre *étoiles* (bleu glacé)",
 "cover_label": "petite ligne en haut (date, époque, nom)",
 "cover_img": "clé de l'image la plus forte de la banque pour la couverture",
 "music": {"file": "music/revolt/music.wav", "beats": "music/revolt/beats.json", "offset": 0.51},
 "scenes": [ { "t": "texte lu", ... }, ... ]
}
```
Champs d'une scène (une scène = un bout de phrase, 20 à 32 scènes par vidéo) :
- `t` (obligatoire) : texte lu. `*mots*` = mot-clé bleu glacé, `^mots^` = mot fort en bloc blanc (1 à 2 marquages par scène max).
- `join: true` : la scène continue la même phrase que la précédente (pas de coupure dans la voix).
- `img` : image principale (clé de la banque ci-dessous). `tags` : thèmes pour les plans rapides suivants (sinon ceux de l'image).
- `bg` : `dark` (défaut), `light` (marbre clair), `blue` (moments forts). Pas plus d'1 scène sur 3 en `light`/`blue`.
- `hit: true` : flash + secousse + impact (accroche, révélation, chute). 3 à 5 par vidéo.
- `drop: true` : sur la 2e ou 3e scène (fin de l'accroche).
- `label` : petit titre en haut (date, nom). `tag` : bande blanche « scotch » (2-3 mots MAJUSCULES). `big` : gros texte plein écran (chiffre, mot latin). `counter: [a, b]` : compteur animé. `hold: true` : pas de plans rapides (silhouette, compteur).
- `size` : taille de l'image (0.6-1.2). `fx: "blur"` : entrée floue.
- `pause` : inutile en général (les phrases s'enchaînent naturellement).
- Ne pas mettre `voice`, `rate`, `bpm` : les réglages par défaut sont ceux validés.

## Banque d'images (tags → clés)
- `anger` : marcus_7, roman_2
- `armor` : armor_0, armor_7, helmet_0, helmet_3, helmet_6
- `athlete` : athlete_1, diad_2, protes_0
- `battle` : battle_4, battle_6, sarc_6
- `beast` : bull_1, bull_4, greek_0, labors_3, labors_6, lionfight_1
- `bull` : bull_1, bull_4, labors_6
- `death` : hourglass_3, skull_1, skull_5
- `doubt` : bronze_2, melen_0, titan_0
- `emperor` : emperor_1, marcus_7, roman_0, roman_2, roman_3, roman_4
- `head` : emperor_1, marcus_7, philo_1, philo_5, philo_6, roman_0, roman_2, roman_3, roman_4, roman_5
- `hero` : goltz_0, goltz_3, herc_0, herc_1, hercprint_7
- `lion` : greek_0, lionfight_1
- `milo` : milo_4
- `old` : philo_1, roman_5
- `philosopher` : bronze_2, philo_1, philo_2, philo_5, philo_6, roman_5
- `prison` : titan_0
- `silhouette` : protes_0_sil
- `strength` : atlas_1, diad_2, goltz_0, goltz_3, herc_0, herc_1, hercprint_7, labors_0, lionfight_7
- `struggle` : labors_0, labors_3, labors_6, lionfight_1, lionfight_7, milo_4, sarc_6, titan_2
- `time` : hourglass_3, melen_0, skull_1, titan_0
- `warrior` : armor_0, armor_7, battle_4, battle_6, helmet_0, helmet_3, helmet_6, hourglass_3, protes_0, sword_2, sword_4
- `weapon` : sword_2, sword_4
- `weight` : atlas_1, titan_2
- `youth` : athlete_1, roman_0

Si une histoire demande une image absente (ex. un objet précis), réutiliser les tags existants plutôt que d'en télécharger : la DA et la qualité des détourages ont été validées sur cette banque.
