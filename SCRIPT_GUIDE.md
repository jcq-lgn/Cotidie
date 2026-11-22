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
 "description": "voir « Style de la description » ci-dessous",
 "hashtags": ["#stoicisme", "#motivation", "#discipline", "#musculation", "#mindset", "+ 3 à 5 liés au sujet"],
 "cover_title": "4 à 7 mots en MAJUSCULES, 1 mot-clé entre *étoiles* (bleu glacé)",
 "cover_label": "petite ligne en haut (date, époque, nom)",
 "cover_img": "clé de l'image la plus forte de la banque pour la couverture",
 "music": {"file": "music/revolt/music.wav", "beats": "music/revolt/beats.json", "offset": 0.51},
 "pool": ["... recopier la liste pool de scripts/today.py ..."],
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

## Style de la description (validé par le propriétaire)
Exactement 3 temps, 2 à 3 phrases au total, 25 à 40 mots :
1. **Accroche** : un fait historique précis et intrigant (époque/chiffre + personnage + promesse), ex. « Il y a 2500 ans, un lutteur grec a découvert le seul secret de la force qui marche encore aujourd'hui. »
2. **Chute courte** avec points de suspension, qui révèle le secret sans tout dire, ex. « Juste un veau… et de la constance. »
3. **Un emoji 🏛️** puis **une question courte au vouvoiement** qui pousse à commenter, ex. « Vous ajoutez quoi aujourd'hui ? »

Modèle de référence (vidéo 001) :
> Il y a 2500 ans, un lutteur grec a découvert le seul secret de la force qui marche encore aujourd'hui. Juste un veau… et de la constance. 🏛️ Vous ajoutez quoi aujourd'hui ?

Pas de listes, pas de « Pas d'appli. Pas de coach. » en rafale, pas plus d'un emoji, pas de hashtags dans la description (ils vont dans `hashtags`).

## Banque d'images (121 images) et sélection du jour
`python3 scripts/today.py` donne la **sélection du jour** (`pool`, ~45 images, différente chaque jour) et son classement par thème (`by_tag`).
**Choisir les `img` uniquement dans `pool`** et recopier la liste `pool` telle quelle dans le JSON (champ `"pool"`) : les plans rapides seront tirés de cette sélection, ce qui évite de revoir les mêmes statues d'une vidéo à l'autre.

Banque complète (pour information) :
- `anger` : marcus_7, roman_2
- `armor` : aic_armr_1, aic_armr_3, aic_armr_4, aic_armr_5, aic_armr_8, aic_armr_9, aic_helm_1, aic_helm_3, aic_helm_5, aic_helm_6, aic_helm_7, aic_helm_9, aic_shield_2, aic_shield_6, aic_warr_2, armor_0, armor_7, helmet_0, helmet_3, helmet_6
- `athlete` : aic_athl_4, aic_spart_0, athlete_1, diad_2, protes_0
- `battle` : aic_atlas_2, aic_battle_0, aic_battle_4, aic_battle_6, aic_death_1, aic_gladi_4, aic_herc_5, aic_horse_4, aic_ruins_5, battle_4, battle_6, sarc_6
- `beast` : aic_death_4, aic_herc_0, aic_horse_1, aic_horse_3, aic_horse_8, aic_horse_9, aic_lion_1, aic_lion_2, bull_1, bull_4, greek_0, labors_3, labors_6, lionfight_1
- `bull` : aic_death_4, bull_1, bull_4, labors_6
- `death` : aic_battle_0, aic_death_1, aic_ruins_8, aic_skull_0, hourglass_3, skull_1, skull_5
- `doubt` : aic_bronzefig_5, aic_colos_1, aic_philo_6, aic_ruins_2, aic_ruins_6, aic_sea_0, aic_warr_8, bronze_2, melen_0, titan_0
- `eagle` : aic_eagle_9
- `emperor` : aic_eagle_9, aic_rhead_3, aic_rhead_4, emperor_1, marcus_7, roman_0, roman_2, roman_3, roman_4
- `gladiator` : aic_gladi_4
- `head` : aic_philo_7, aic_rhead_1, aic_rhead_2, aic_rhead_3, aic_rhead_4, aic_rhead_6, aic_stoic_1, emperor_1, marcus_7, philo_1, philo_5, philo_6, roman_0, roman_2, roman_3, roman_4, roman_5
- `hero` : aic_battle_8, aic_bronzefig_2, aic_herc_3, aic_herc_9, goltz_0, goltz_3, herc_0, herc_1, hercprint_7
- `horse` : aic_armr_1, aic_death_1, aic_horse_1, aic_horse_3, aic_horse_4, aic_horse_9
- `lion` : aic_horse_8, aic_lion_0, aic_lion_1, aic_lion_2, greek_0, lionfight_1
- `milo` : milo_4
- `old` : aic_athl_5, aic_philo_5, aic_philo_7, aic_stoic_2, aic_stoic_4, philo_1, roman_5
- `philosopher` : aic_athl_5, aic_bronzefig_5, aic_colos_1, aic_philo_5, aic_philo_7, aic_stoic_1, aic_stoic_2, aic_stoic_4, bronze_2, philo_1, philo_2, philo_5, philo_6, roman_5
- `prison` : aic_ruins_2, aic_ruins_6, aic_ruins_7, titan_0
- `ruins` : aic_colos_8, aic_ruins_0, aic_ruins_1, aic_ruins_2, aic_ruins_7, aic_ruins_8, aic_temple_0, aic_temple_2, aic_temple_8
- `seneca` : aic_stoic_1, aic_stoic_2, aic_stoic_4
- `silhouette` : protes_0_sil
- `spartan` : aic_spart_0
- `storm` : aic_mount_9, aic_sea_0
- `strength` : aic_athl_4, aic_battle_8, aic_battle_9, aic_bronzefig_2, aic_herc_3, aic_herc_9, aic_lion_0, aic_wrest_4, atlas_1, diad_2, goltz_0, goltz_3, herc_0, herc_1, hercprint_7, labors_0, lionfight_7
- `struggle` : aic_battle_6, aic_battle_8, aic_battle_9, aic_herc_0, aic_herc_9, aic_horse_1, aic_horse_8, aic_lion_0, aic_mount_9, aic_ruins_5, aic_warr_8, aic_wrest_4, labors_0, labors_3, labors_6, lionfight_1, lionfight_7, milo_4, sarc_6, titan_2
- `time` : aic_colos_1, aic_colos_8, aic_ruins_0, aic_ruins_1, aic_ruins_8, aic_skull_0, aic_temple_0, aic_temple_2, aic_temple_8, hourglass_3, melen_0, skull_1, titan_0
- `warrior` : aic_armr_1, aic_armr_3, aic_armr_4, aic_armr_5, aic_armr_9, aic_atlas_2, aic_battle_4, aic_gladi_4, aic_helm_1, aic_helm_3, aic_helm_5, aic_helm_6, aic_helm_7, aic_helm_9, aic_herc_5, aic_shield_2, aic_shield_6, aic_swd_3, aic_swd_4, aic_swd_7, aic_swd_8, aic_warr_2, armor_0, armor_7, battle_4, battle_6, helmet_0, helmet_3, helmet_6, hourglass_3, protes_0, sword_2, sword_4
- `weapon` : aic_armr_8, aic_swd_3, aic_swd_4, aic_swd_7, aic_swd_8, sword_2, sword_4
- `weight` : atlas_1, titan_2
- `youth` : aic_rhead_1, aic_rhead_2, aic_rhead_4, aic_spart_0, athlete_1, roman_0

Si une histoire demande une image absente (ex. un objet précis), réutiliser les tags existants plutôt que d'en télécharger : la DA et la qualité des détourages ont été validées sur cette banque.
