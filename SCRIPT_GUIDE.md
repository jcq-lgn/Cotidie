# Guide d'écriture d'une vidéo Cotidie

Lire aussi `DA.md` (charte visuelle, validée par le propriétaire du compte — ne pas la modifier).
Exemple complet : `videos/001_milon_revolt.json`.

## Fond
- Niche : motivation, discipline, stoïcisme, musculation. Histoires **vraies** et vérifiables : Antiquité (Rome, Grèce, Sparte), philosophes stoïciens (Marc Aurèle, Sénèque, Épictète), athlètes antiques. Les figures modernes (David Goggins…) seulement en clin d'œil, voir ci-dessous.
- **Les images doivent coller au sujet.** La banque ne contient que des œuvres antiques : chaque vidéo raconte une histoire antique (personnage, lieu, objet visibles dans la banque). Une figure moderne (Goggins…) ne peut être qu'un clin d'œil d'une phrase, jamais le sujet. Si l'idée du jour est moderne, la raconter à travers un équivalent antique.
- Exactitude : pas de fausse citation ni de chiffre inventé. En cas de doute, formuler « la légende raconte… ».
- **Vouvoiement**. Phrases courtes, rythmées, qui se terminent par un appel à l'action concret.
- Structure : accroche choc en 1 phrase (≤ 3 s) → histoire → leçon → application concrète « aujourd'hui… » → chute forte.
- Longueur : **80 à 110 mots, 30 à 40 s**. Les statistiques des vidéos 001-002 montrent que le visionnage complet chute au-delà de 35-40 s : plus court = plus de vidéos regardées jusqu'au bout.
- **La 1re seconde décide de tout** (38 % des spectateurs partaient à 0:01 sur la 001) :
  - 1re scène = l'image la plus forte (visage de statue, regard), jamais une silhouette sombre ;
  - 1re phrase = un fait choc ou une question, ≤ 8 mots si possible ;
  - champ `hook` : 4 à 8 mots en MAJUSCULES affichés en haut dès la 1re image (1 mot-clé entre *étoiles*). Par défaut = `cover_title`.
- **Relance à mi-vidéo** (vers 12-18 s) : une phrase de rupture qui relance l'attention (« Mais le plus fou, c'est… », « Et c'est là que tout bascule. »), avec `hit: true` et un fond `blue`.
- Public (statistiques TikTok) : surtout 25-34 ans puis 18-24 ans, France/Belgique/Suisse. Ancrer la leçon dans leur quotidien : travail, procrastination, salle de sport après le boulot, réveil, téléphone, argent, constance.
- **Contenu « utile » = boost TikTok.** La 001 (Milon) a reçu +284 vues gratuites parce que « les spectateurs l'ont trouvée très utile ». Chaque vidéo doit donc laisser **une action précise, faisable aujourd'hui, en moins de 5 minutes**, formulée comme une consigne (« Ce soir, notez 3 victoires passées. », « Demain, réglez le réveil 15 min plus tôt et levez-vous au 1er son. »). Pas une morale vague (« Soyez discipliné »). Placer cette consigne juste avant la chute, avec `tag` (ex. « À FAIRE ») ou `big`. L'histoire reste le cœur de la vidéo ; la consigne en est la conséquence directe.
- Fin : terminer sur une phrase qui donne envie de revoir le début (boucle) ; l'écran de fin ne dure qu'1 s.

## Format JSON
```json
{
 "title": "...", "brand": "COTIDIE",
 "title": "Titre court et accrocheur",
 "description": "voir « Style de la description » ci-dessous",
 "hashtags": ["#stoicisme", "#motivation", "#discipline", "#musculation", "#mindset", "+ 3 à 5 liés au sujet"],
 "hook": "4 à 8 mots en MAJUSCULES affichés dès la 1re image, 1 mot-clé entre *étoiles*",
 "cover_title": "4 à 7 mots en MAJUSCULES, 1 mot-clé entre *étoiles* (bleu glacé)",
 "cover_label": "petite ligne en haut (date, époque, nom)",
 "cover_img": "clé de l'image la plus forte de la banque pour la couverture",
 "music": {"file": "music/revolt/music.wav", "beats": "music/revolt/beats.json", "offset": 0.51},
 "pool": ["... recopier la liste pool de scripts/today.py ..."],
 "scenes": [ { "t": "texte lu", ... }, ... ]
}
```
Champs d'une scène (une scène = un bout de phrase, 14 à 24 scènes par vidéo) :
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
   La question renvoie de préférence à l'action donnée dans la vidéo (« Vous commencez ce soir ? », « Quelle est votre 1re victoire ? »).

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
