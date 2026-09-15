# Non-revendications

## Énoncé principal

**Collatz Scan ne prouve rien au sujet de la vérité générale de la conjecture
de Collatz.**

Le projet ne revendique pas :

- une preuve de convergence pour tous les entiers positifs ;
- une réfutation de la conjecture ;
- une réduction démontrée du problème infini à un domaine fini ;
- la découverte d'un invariant suffisant pour conclure ;
- une validation mathématique par GPU, par volume de calcul ou par hachage.

## Sens des sorties

- `PASS` : le programme a terminé les contrôles techniques prévus.
- `EXACT` : les données comparées dans ce contrôle étaient identiques.
- `SUPPORTED` : l'hypothèse statistique locale a satisfait le seuil programmé
  sur l'échantillon considéré.
- `NOT_SUPPORTED` : elle ne l'a pas satisfait selon la règle programmée.
- `INCONCLUSIVE` : la règle programmée ne permet pas de trancher.

Aucun de ces mots ne constitue une conclusion sur la conjecture.

## Formulation de citation recommandée

« Collatz Scan est un outil expérimental reproductible qui explore des
trajectoires finies et produit des observations statistiques bornées. Il ne
fournit aucune preuve de la conjecture de Collatz. »

