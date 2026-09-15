> **Note historique, non-preuve.** Cette note décrit des observations finies.
> La mention de WHISPER à la fin est conservée comme contexte historique :
> [Whisper est déprécié et n'est plus maintenu](https://github.com/whisper-core01/whisper).
> IAA ne transforme aucune hypothèse ci-dessous en logique opérationnelle.

# Archive de recherche — Dynamique dissipative de Syracuse

## Objet

Corpus d'observations numériques sur l'évolution des trajectoires de Syracuse jusqu'à \(N = 10^9\).

## Avertissement

Ce document ne constitue ni une preuve de la conjecture de Syracuse, ni une démonstration mathématique.

Il s'agit d'un corpus d'observations numériques et d'hypothèses structurées issues d'une exploration expérimentale.

## 1. Pipeline expérimental

L'exploration repose sur la décomposition des trajectoires en blocs \((L_j, k_j)\).

Pour chaque bloc, on définit l'observable cinétique :

\[
V_j = (L_j + 1)\log_2(3) - (L_j + k_j)
\]

La moyenne de trajectoire est :

\[
\overline V(n) = \frac{1}{m(n)}\sum_{j=0}^{m(n)-1} V_j
\]

où \(m(n)\) désigne le nombre de blocs de la trajectoire issue de \(n\).

Les grandeurs étudiées sont :

- la dissipation moyenne \(\overline V\),
- la dette cumulée \(\sum V_j\),
- les purges \(k_j\),
- l'inertie locale,
- la relation entre durée de vie et dissipation,
- la renormalisation des paramètres selon l'échelle \(N\).

## 2. Faits expérimentaux observés

### 2.1 Dissipation globale

Sur les trajectoires testées jusqu'à \(N = 10^9\), toutes les valeurs observées de \(\overline V\) sont strictement négatives.

\[
\overline V < 0
\]

Aucune trajectoire testée n'a présenté de dissipation moyenne positive.

### 2.2 Loi empirique durée / dissipation

La durée de vie en blocs \(L\) est fortement corrélée à l'inverse de la dissipation moyenne :

\[
L \approx \frac{a(N)}{-\overline V} + b(N)
\]

La corrélation observée augmente avec l'échelle d'exploration.

### 2.3 Renormalisation de \(a(N)\)

Sur les échelles \(10^4, 10^5, 10^6, 10^7, 10^8\), le paramètre \(a(N)\) est ajusté par :

\[
a(N) \approx 1.462421 \ln(N) - 1.625865
\]

avec un ajustement numérique très élevé sur les points mesurés.

Cette relation doit être considérée comme expérimentale, non démontrée.

### 2.4 Bandes de dissipation

Les populations extrêmes, par exemple top100, top1000 ou top10000 des trajectoires les plus longues, forment des bandes de dissipation distinctes.

Ces bandes semblent plus informatives que les records individuels, lesquels sont instables et doivent être interprétés comme fluctuations extrêmes.

## 3. Hypothèses de recherche

### 3.1 Attracteur statistique

Il pourrait exister une mesure de probabilité limite \(\mu\), portée par \(\mathbb{R}_{<0}\), décrivant la distribution asymptotique de \(\overline V\) dans certaines classes de trajectoires longues.

### 3.2 Séparation Bulk / Queue

Les trajectoires longues ordinaires forment un régime statistique de type bulk.

Les records individuels appartiennent à une queue extrême et ne doivent pas être confondus avec le régime stationnaire.

### 3.3 Renormalisation de la dissipation

Le modèle suggère une structure d'échelle où la forme de la relation durée/dissipation reste stable tandis que ses paramètres varient avec \(N\).

## 4. Questions ouvertes

- Les bandes top-k convergent-elles vers des valeurs limites ?
- Existe-t-il une mesure limite unique ou plusieurs régimes de dissipation ?
- Quelle est la signification mathématique du coefficient \(1.462421\) ?
- La relation \(a(N) \sim \alpha \ln N + \beta\) persiste-t-elle au-delà de \(10^9\) ?
- Les records vérifient-ils une loi de puissance, ou relèvent-ils d'une statistique d'extrêmes plus complexe ?
- Peut-on relier \(\overline V < 0\) aux résultats classiques sur le ratio étapes impaires / étapes paires ?

## 5. Statut

Ce dossier est placé en quarantaine scientifique.

Il ne doit pas être intégré tel quel dans une architecture opérationnelle.

Toute transposition vers WHISPER devra passer par une étape doctrinale séparée, sans télémétrie comportementale, sans surveillance utilisateur et sans logique système fondée sur une hypothèse non démontrée.

