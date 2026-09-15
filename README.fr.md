# IAA

**IRIS · ARGOS · AORATOS**

IAA est une architecture expérimentale, pilotée par contrats, qui compose des
organes et composants remplaçables autour de trois noyaux agnostiques du métier.

> **État actuel : squelette d’architecture avec chemins de référence bornés.**
> Ce dépôt ne contient pas de runtime de production et ne doit pas être
> présenté comme un système sécurisé de communication, réservation ou accès.

## Filiation

IAA succède aux recherches conservées dans
[`whisper-core01/whisper`](https://github.com/whisper-core01/whisper). Whisper
est **déprécié et n’est plus maintenu** ; il reste public uniquement comme
origine historique. IAA n’hérite pas de ses affirmations de sécurité non
vérifiées.

## Activation

L’utilisateur lance **IRIS**. IRIS initie SOL et active ARGOS et AORATOS
indépendamment. ARGOS admet et exécute les logiques métier. AORATOS s’occupe
exclusivement de la sécurité des données et n’intervient jamais dans la logique
métier ni dans son chargement.

Le chemin exécutable actuel accepte uniquement des scénarios déjà canoniques :
la normalisation exécutable par SOL n’est pas encore implémentée.

## ARKÉ

ARKÉ est l’interface mobile permettant les échanges entre chercheurs ou avec
des personnes présentes dans le répertoire téléphonique de l’utilisateur. La
mise en relation est assurée par IRIS. Tout flux entrant ou sortant traverse un
SOL. Les échanges passent par Reticulum ou TCP ; LoRa est réservé aux messages
texte de 100 caractères maximum.

## Démonstrations exécutables

- [Collatz Scan](components/argos/engines/collatz/README.md) publie des calculs
  numériques bornés et 15 contrôles. **Il ne prouve pas la conjecture de
  Collatz.**
- [Hotel Reservation](components/argos/business/hotel_reservation/README.md)
  applique les règles de réservation et produit le planning des chambres,
  nettoyages et activations de clés, ainsi qu’une fiche client fictive avec
  historique hôtelier et restaurant.

## Règles fondatrices

- la doctrine précède l’implémentation ;
- une responsabilité explicite par organe ;
- aucune logique métier dans IRIS, ARGOS ou AORATOS ;
- dépendance aux contrats, jamais aux implémentations concrètes ;
- organes et composants remplaçables sans modifier la sémantique des noyaux ;
- invariants explicites, versionnés et testables ;
- toute affirmation de sécurité ou de résilience exige une preuve reproductible.

La définition canonique du SOL se trouve dans
[`docs/architecture/SOL.md`](docs/architecture/SOL.md).
