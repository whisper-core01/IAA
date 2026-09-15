# IAA

**IRIS · ARGOS · AORATOS**

IAA est une architecture expérimentale, pilotée par contrats, qui compose des
organes et composants remplaçables autour de trois noyaux agnostiques du métier.

> **État actuel : squelette d’architecture.** Ce dépôt ne contient pas encore
> de runtime de production et ne doit pas être présenté ni déployé comme un
> système de communication sécurisé.

## Filiation

IAA succède aux recherches conservées dans
[`whisper-core01/whisper`](https://github.com/whisper-core01/whisper). Whisper est déprécié, n’est plus maintenu et reste public uniquement comme
origine historique. IAA repart d’une règle plus stricte :
aucune affirmation ne dépasse ce que le dépôt permet réellement de démontrer.

IAA n’est pas un simple renommage, n’efface pas l’historique de Whisper et
n’hérite pas automatiquement de ses affirmations de sécurité non vérifiées.

## ARKÉ

ARKÉ est l’interface mobile permettant les échanges entre chercheurs ou avec
des personnes présentes dans le répertoire téléphonique de l’utilisateur.
La mise en relation est assurée par IRIS. Tout flux entrant ou sortant traverse
un Sol, organe interne d’ancrage et frontière E/S chargé de la normalisation,
de l’encapsulation et de la publication. Les échanges passent par Reticulum ou
TCP. LoRa est réservé aux messages texte de 100 caractères maximum.

La définition canonique du Sol se trouve dans
[`docs/architecture/SOL.md`](docs/architecture/SOL.md).

## Règles fondatrices

- la doctrine précède l’implémentation ;
- une responsabilité explicite par organe ;
- aucune logique métier dans IRIS, ARGOS ou AORATOS ;
- dépendance aux contrats, jamais aux implémentations concrètes ;
- organes et composants remplaçables sans modifier la sémantique des noyaux ;
- invariants explicites, versionnés et testables ;
- toute affirmation de sécurité ou de résilience exige une preuve reproductible.

La présentation complète et maintenue se trouve dans [`README.md`](README.md).

