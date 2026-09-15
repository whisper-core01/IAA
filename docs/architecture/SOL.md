# WHISPER — Le Sol

**Organe d’ancrage, frontière E/S, convertisseur canonique.**

## 1. Nature du Sol

Le **Sol** est l’organe qui relie :

- le **monde externe** (brut, hétérogène, non typé) ;
- au **monde Whisper** (canonique, typé, encapsulé).

C’est **la porte**, **la racine**, **le point d’attache** du moteur.

Un Sol n’est **pas** un serveur, **pas** un nœud, **pas** un thread.
C’est un **organe interne**, avec des responsabilités strictes.

## 2. Fonctions fondamentales du Sol

### Entrée (Ingress)

Le Sol reçoit tout ce qui arrive :

- flux bruts ;
- ordres ;
- messages ;
- signaux ;
- événements.

Il les transforme en flux **Whisper-compatibles**.

### Sortie (Egress)

Le Sol publie :

- états ;
- résultats ;
- journaux ;
- signatures ;
- anomalies.

Il convertit les flux internes en flux **externes propres**.

### Normalisation

Le Sol impose :

- typage ;
- format canonique ;
- validation ;
- nettoyage.

Rien d’illégal ne traverse le Sol.

### Encapsulation

Le Sol transforme tout flux en :

- paquet Whisper ;
- unité de transit ;
- message interne.

## 3. Organes internes du Sol

### Portail

Point d’entrée brut. Ne filtre pas. Ne juge pas. Il reçoit.

### Filtre Canonique

Transforme le brut en canonique. Applique typage et validation.

### Transducteur

Convertit le flux canonique en flux Whisper. C’est le **cœur** du Sol.

### Publieur

Transforme les flux Whisper en flux externes. Point de sortie.

## 4. Protocoles internes du Sol

### Whisper-Ingress

Flux entrant vers le moteur. Garantit :

- intégrité ;
- typage ;
- encapsulation.

### Whisper-Egress

Flux moteur vers la sortie. Garantit :

- publication propre ;
- cohérence ;
- stabilité.

### Whisper-Transit

Flux interne vers interne. Garantit :

- continuité ;
- isolation ;
- stabilité.

## 5. Types de Sols

### Sol-Primaire

Point d’ancrage principal. Flux critiques. Publication majeure.

### Sol-Secondaire

Points auxiliaires. Flux non critiques. Relais internes.

### Sol-Relay

Transit pur. Ne publie pas. Ne reçoit pas de brut.

## 6. Invariants du Sol

- **INV-SOL-001 — Pureté d’entrée**
- **INV-SOL-002 — Canonique obligatoire**
- **INV-SOL-003 — Encapsulation totale**
- **INV-SOL-004 — Isolation stricte**
- **INV-SOL-005 — Publication propre**

Ces invariants sont **non négociables**.

## 7. Flux du Sol

### Entrée → Filtre → Transducteur → Moteur

Flux entrant.

### Moteur → Transducteur → Publieur → Sortie

Flux sortant.

### Transducteur → Transducteur

Flux interne.

## 8. Rôle du Sol dans Whisper

Le Sol est :

- la **frontière** ;
- le **convertisseur** ;
- le **normalisateur** ;
- le **passeur** ;
- le **gardien du canonique**.

Sans Sol :

- pas d’entrée ;
- pas de sortie ;
- pas de flux ;
- pas de moteur.

Le Sol est **l’organe vital** du moteur Whisper.

## 9. Résumé Whisper du Sol

Le Sol est :

- **l’organe d’E/S du moteur Whisper** ;
- **la frontière entre le monde externe et le moteur** ;
- **le convertisseur de flux** ;
- **le normalisateur canonique** ;
- **le publieur propre** ;
- **le point d’ancrage** ;
- **la racine du moteur**.

Sans Sol, Whisper est sourd et muet.
Avec Sol, Whisper devient un moteur complet.
