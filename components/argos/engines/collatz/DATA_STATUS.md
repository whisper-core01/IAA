# Statut des données et de la reproductibilité

Date de contrôle : 2026-09-15.

> Tous les résultats de ce dossier sont des observations finies. Aucun ne prouve
> la conjecture de Collatz/Syracuse.

## Reproduit dans l'environnement de publication

| Artefact | Commande ou contrôle | Résultat |
| --- | --- | --- |
| `data/records/records_1e6.csv` | Scan exhaustif des impairs jusqu'à 10^6, profondeur 3 000 | Enregistrements identiques ; empreinte brute du résultat régénéré publiée |
| `data/champions/champion_2788008987.csv` | `analyze_champion.py`, profondeur 1 000 | 282 enregistrements identiques |
| `data/agreements/agreement_63728127.csv` | `verify_lift.py`, profondeur 237, max-q 20 | Enregistrements identiques |
| `data/agreements/agreement_217740015.csv` | profondeur 249, max-q 20 | Enregistrements identiques |
| `data/agreements/agreement_2788008987.csv` | profondeur 282, max-q 20 | Enregistrements identiques |

Le test autonome de `verify_lift.py` termine également sans échec pour 27,
35 655 et 2 788 008 987.

## Cohérence vérifiée sans rejeu exhaustif

Pour `records_1e8.csv`, `records_1e9.csv` et `records_1e10.csv` :

- chaque ligne a été recalculée avec `analyze_n` ;
- les champs entiers et booléens concordent ;
- les records (R) et (L) progressent strictement dans chaque fichier.

Ce contrôle ne prouve pas à lui seul que tous les entiers de l'intervalle ont
été scannés. Les traces `progress_1e8.log`, `progress_1e9.log` et
`progress_1e10.log` contiennent un marqueur `DONE` et le record final annoncé,
mais restent des sorties historiques fournies par l'auteur, pas une attestation
indépendante.

## Données historiques non régénérées

- `data/attractor/topk_bands.csv` ;
- `data/attractor/attractor_law.csv` ;
- `data/attractor/attractor_surface.csv` ;
- `figures/attractor_law.png` ;
- `evidence/increment58-recorded-2026-07-29.md`.

Les fichiers `topk_bands.csv` et `attractor_law.csv` sont identiques. La
figure et la surface sont cohérentes par leurs libellés et dimensions, mais le
pipeline complet ayant produit les bandes et le tracé n'a pas été retrouvé sous
forme de sources individuellement auditables. Ils restent donc des artefacts
historiques, pas des résultats reproduits par cette publication.

Les captures montrent que les fichiers `trajectory.py`, `scanner.py`,
`scan_1e10.py`, `attractor_law.py` et d'autres sources existaient sur la
machine de recherche. Leurs octets n'ont toutefois pas été transmis. Trois
scripts dépendants sont conservés dans `archive/incomplete-vmean/`, hors du
chemin validé, afin de rendre cette lacune visible.

## Empreintes

Les empreintes SHA-256 de tous les fichiers publiés dans ce composant sont
listées dans [SHA256SUMS](SHA256SUMS). Une empreinte contrôle l'identité des
octets ; elle ne transforme pas un résultat expérimental en preuve.
