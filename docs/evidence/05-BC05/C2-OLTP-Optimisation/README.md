# BC05 — C2 — OLTP & Optimisation

**Bloc de compétences :** BC05  
**Compétence :** C2 — Concevoir, exploiter et optimiser une base transactionnelle  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**SGBD cible :** PostgreSQL  
**Version :** 1.0  
**Statut :** Baseline documentaire — preuves d'exécution à produire

---

# 1. Objectif

Ce dossier regroupe les preuves relatives à la conception et à l'optimisation de la base transactionnelle OLTP du projet.

L'objectif est de démontrer la chaîne suivante :

```text
Business Transactions
        |
        v
Relational Model
        |
        v
PostgreSQL OLTP
        |
        v
Representative Queries
        |
        v
EXPLAIN ANALYZE
        |
        v
Optimization Decision
        |
        v
Measurement
```

L'optimisation doit être fondée sur des mesures réelles et non sur l'ajout systématique d'index.

---

# 2. Sources du projet

Le modèle transactionnel est dérivé de :

```text
../C1-MCD-Migration-SQL/MCD-MERISE-PROJET.md
../C1-MCD-Migration-SQL/MLD-PROJET.md
../C1-MCD-Migration-SQL/MPD-POSTGRESQL.md
```

La documentation Data générale se trouve notamment dans :

```text
../../../40-DATA/01-Data-Architecture.md
../../../40-DATA/02-Data-Model.md
```

Le projet dispose également d'un support dédié aux concepts OLTP :

```text
OLTP.md
```

Ce support théorique ne constitue pas à lui seul une preuve d'implémentation.

Les preuves BC05 devront provenir de l'environnement PostgreSQL réellement exécuté.

---

# 3. Définition OLTP

OLTP signifie :

```text
Online Transaction Processing
```

Un système OLTP est conçu principalement pour traiter :

- créations ;
- lectures ciblées ;
- mises à jour ;
- suppressions contrôlées ;
- transactions courtes ;
- accès concurrents ;
- contraintes d'intégrité.

Dans le projet, PostgreSQL assure cette responsabilité.

---

# 4. OLTP vs OLAP

La plateforme sépare deux usages.

```text
OLTP
 |
 +--> Operational transactions
 +--> Current business state
 +--> Normalized model
 +--> Short queries
 +--> Strong integrity
```

et :

```text
OLAP
 |
 +--> Analytics
 +--> Aggregations
 +--> Historical analysis
 +--> Reporting
 +--> Decision support
```

La partie OLAP sera traitée dans :

```text
../C3-OLAP-Alimentation/
```

---

# 5. Périmètre transactionnel

Le cœur OLTP V1 repose sur :

```text
client
chasseur
mandat
demande_version
source
bien
presentation
document
```

Le schéma cible est :

```text
real_estate
```

---

# 6. Transactions métier principales

Les opérations transactionnelles principales sont notamment :

```text
Créer un client
Créer un mandat
Affecter un chasseur
Créer une version de demande
Ajouter un bien
Qualifier un bien
Créer une présentation
Enregistrer le feedback client
Ajouter les métadonnées d'un document
Modifier le statut d'un mandat
Modifier le statut d'un bien
```

---

# 7. Exemple — création d'un mandat

La création métier peut nécessiter :

```text
CLIENT
   |
   v
MANDAT
   |
   v
DEMANDE_VERSION
```

Certaines opérations doivent être atomiques.

Exemple logique :

```sql
BEGIN;

-- create mandate

-- create first request version

COMMIT;
```

Une erreur doit permettre un rollback plutôt qu'un état partiellement créé.

---

# 8. Propriétés ACID

PostgreSQL permet de respecter les propriétés :

```text
Atomicity
Consistency
Isolation
Durability
```

## Atomicity

Une transaction est appliquée entièrement ou annulée.

## Consistency

Les contraintes maintiennent le schéma dans un état valide.

## Isolation

Les transactions concurrentes sont isolées selon le niveau choisi.

## Durability

Une transaction validée doit survivre à un incident compatible avec les garanties du système de stockage et de PostgreSQL.

---

# 9. Intégrité

Le modèle utilise :

```text
PRIMARY KEY
FOREIGN KEY
UNIQUE
CHECK
NOT NULL
```

pour protéger l'intégrité au niveau base de données.

Les contrôles applicatifs complètent ces contraintes mais ne doivent pas être leur seul substitut lorsque la règle appartient clairement au modèle de données.

---

# 10. Normalisation

Le modèle transactionnel cherche à limiter :

- duplication ;
- anomalies de mise à jour ;
- incohérences ;
- dépendances inutiles.

Exemple :

```text
CLIENT
```

n'est pas dupliqué dans chaque :

```text
MANDAT
```

Le mandat référence le client.

---

# 11. Historisation

La demande client est historisée grâce à :

```text
MANDAT
   |
   +--> DEMANDE_VERSION 1
   +--> DEMANDE_VERSION 2
   +--> DEMANDE_VERSION N
```

Cela évite d'écraser les critères précédents.

---

# 12. Charge transactionnelle attendue

Le MVP n'est pas conçu comme une plateforme mondiale traitant des millions de transactions par seconde.

Le profil initial est davantage :

```text
Low / Moderate write volume
+
Frequent targeted reads
+
Property search queries
+
Matching operations
```

La conception doit donc rester proportionnée au besoin réel.

---

# 13. Principe d'optimisation

La règle principale est :

```text
Do not optimize blindly.
```

Le cycle retenu est :

```text
Query
  |
  v
Measure
  |
  v
Identify Bottleneck
  |
  v
Optimization
  |
  v
Measure Again
```

---

# 14. EXPLAIN

PostgreSQL permet d'examiner le plan d'exécution :

```sql
EXPLAIN
SELECT ...;
```

Cela montre le plan choisi par l'optimiseur sans nécessairement exécuter complètement la requête selon la forme utilisée.

---

# 15. EXPLAIN ANALYZE

Pour mesurer réellement :

```sql
EXPLAIN ANALYZE
SELECT ...;
```

Le résultat permet notamment d'observer :

- type de scan ;
- coûts estimés ;
- temps réel ;
- lignes estimées ;
- lignes réelles ;
- opérations de tri ;
- joins.

---

# 16. Preuve avant / après

Une optimisation pertinente doit produire une comparaison.

```text
Query
 |
 +--> BEFORE
 |      |
 |      +--> execution plan
 |      +--> execution time
 |
 +--> OPTIMIZATION
 |
 +--> AFTER
        |
        +--> execution plan
        +--> execution time
```

---

# 17. Requête métier candidate n°1

Recherche de biens actifs à Montpellier :

```sql
SELECT
    id_bien,
    titre,
    ville,
    prix,
    surface,
    nb_pieces
FROM real_estate.bien
WHERE statut = 'ACTIF'
  AND ville = 'Montpellier'
  AND prix <= 350000
  AND surface >= 70;
```

Cette requête représente un cas métier crédible.

---

# 18. Requête candidate n°2

Recherche par type :

```sql
SELECT
    id_bien,
    titre,
    type_bien,
    ville,
    prix
FROM real_estate.bien
WHERE statut = 'ACTIF'
  AND type_bien = 'APPARTEMENT'
  AND ville = 'Montpellier';
```

---

# 19. Requête candidate n°3

Présentations d'une demande :

```sql
SELECT
    p.id_presentation,
    p.score_matching,
    p.statut,
    b.reference_externe,
    b.titre,
    b.prix,
    b.surface
FROM real_estate.presentation p
JOIN real_estate.bien b
  ON b.id_bien = p.id_bien
WHERE p.id_demande_version = ?;
```

---

# 20. Requête candidate n°4

Historique des demandes d'un mandat :

```sql
SELECT
    numero_version,
    date_version,
    localisation,
    budget_min,
    budget_max,
    surface_min,
    active
FROM real_estate.demande_version
WHERE id_mandat = ?
ORDER BY numero_version DESC;
```

---

# 21. Requête candidate n°5

Mandats d'un client :

```sql
SELECT
    id_mandat,
    reference_mandat,
    statut,
    date_debut,
    date_fin
FROM real_estate.mandat
WHERE id_client = ?
ORDER BY date_debut DESC;
```

---

# 22. Sequential Scan

Un plan peut contenir :

```text
Seq Scan
```

Cela n'est pas automatiquement un problème.

Pour une petite table, PostgreSQL peut correctement déterminer qu'un scan séquentiel est plus rapide qu'un index.

---

# 23. Index Scan

Avec un index adapté, PostgreSQL peut utiliser :

```text
Index Scan
```

ou :

```text
Bitmap Index Scan
```

selon le contexte.

L'objectif n'est pas de forcer un type de scan mais d'améliorer le comportement réel de la requête.

---

# 24. Index des clés étrangères

Des index sont prévus notamment sur :

```text
mandat.id_client
mandat.id_chasseur
demande_version.id_mandat
bien.id_source
presentation.id_demande_version
presentation.id_bien
document.id_bien
```

Ils facilitent certains :

- joins ;
- lookups ;
- contrôles liés aux relations.

---

# 25. Index métier

Candidats initiaux :

```text
bien.ville
bien.type_bien
```

Les index supplémentaires doivent être évalués à partir du workload.

---

# 26. Index composite

Un candidat pourrait être :

```sql
CREATE INDEX idx_bien_search
ON real_estate.bien (
    ville,
    statut,
    prix,
    surface
);
```

Mais ce document **ne décide pas encore de son adoption**.

Il doit être testé.

---

# 27. Pourquoi l'ordre des colonnes compte

Dans un index composite :

```text
(A, B, C)
```

l'ordre influence les requêtes qui peuvent efficacement exploiter l'index.

La conception doit donc être basée sur les requêtes réelles.

---

# 28. Selectivity

Un index est particulièrement intéressant lorsque le filtre permet de réduire suffisamment le nombre de lignes candidates.

Une colonne contenant seulement :

```text
TRUE
FALSE
```

peut avoir une faible sélectivité.

L'indexation de cette colonne seule n'est donc pas automatiquement pertinente.

---

# 29. Statistiques PostgreSQL

L'optimiseur dépend de statistiques.

Commande :

```sql
ANALYZE real_estate.bien;
```

Les statistiques doivent être suffisamment représentatives pour que le plan soit pertinent.

---

# 30. VACUUM

PostgreSQL utilise MVCC.

Les anciennes versions de lignes doivent être gérées.

Les mécanismes :

```text
VACUUM
AUTOVACUUM
```

font donc partie de l'exploitation OLTP.

---

# 31. MVCC

PostgreSQL utilise :

```text
Multi-Version Concurrency Control
```

pour permettre des accès concurrents sans verrouillage global de toutes les lectures.

---

# 32. Locks

Certaines opérations utilisent néanmoins des verrous.

Une mauvaise conception transactionnelle peut entraîner :

- contention ;
- attentes ;
- deadlocks.

Les transactions doivent donc rester aussi courtes que raisonnablement possible.

---

# 33. Deadlocks

Exemple conceptuel :

```text
Transaction A
locks row 1
waits row 2

Transaction B
locks row 2
waits row 1
```

PostgreSQL détecte les deadlocks et annule une transaction.

Le code applicatif doit pouvoir gérer certains échecs transactionnels.

---

# 34. Isolation level

Le niveau par défaut PostgreSQL est généralement :

```text
READ COMMITTED
```

Il est adapté au MVP sauf exigence particulière.

Une isolation plus forte ne doit pas être activée globalement sans justification.

---

# 35. Connection Pooling

Une application FastAPI ne doit pas créer un nombre incontrôlé de connexions PostgreSQL.

Le pool de connexions doit être maîtrisé via la couche applicative et, si nécessaire à plus grande échelle, un composant dédié tel que PgBouncer peut être évalué.

Il n'est pas une dépendance obligatoire du MVP.

---

# 36. Pagination

Les APIs listant de nombreux biens doivent utiliser une pagination.

Exemple :

```sql
LIMIT 50 OFFSET 0
```

Pour des volumes plus élevés, une pagination par curseur peut être préférable.

---

# 37. SELECT *

Les requêtes applicatives critiques doivent éviter de récupérer inutilement toutes les colonnes.

Préférer :

```sql
SELECT
    id_bien,
    titre,
    prix
```

lorsque seules ces informations sont nécessaires.

---

# 38. N+1 queries

Avec un ORM, un pattern dangereux est :

```text
1 query for list
+
1 query per object
```

Cela produit :

```text
N + 1 queries
```

La couche SQLAlchemy devra être surveillée pour éviter ce comportement.

---

# 39. ORM et performance

SQLAlchemy facilite :

- mapping ;
- transactions ;
- requêtes ;
- maintenabilité.

Mais l'ORM ne supprime pas la nécessité de comprendre :

```text
SQL
Indexes
Execution Plans
Transactions
```

---

# 40. Contraintes et performance

Une contrainte n'est pas uniquement un coût.

Elle protège également la qualité des données.

Exemple :

```text
FOREIGN KEY
```

empêche certaines incohérences qui seraient ensuite coûteuses à corriger.

---

# 41. Optimisation des écritures

Ajouter trop d'index entraîne :

```text
INSERT
  |
  +--> table write
  +--> index 1 update
  +--> index 2 update
  +--> index 3 update
  +--> ...
```

Le nombre d'index doit rester maîtrisé.

---

# 42. Bulk Loading

Les chargements massifs de biens peuvent avoir des caractéristiques différentes des transactions applicatives.

Ils peuvent provenir de :

```text
ETL
Airflow
Imports
```

La stratégie de chargement devra être évaluée séparément des opérations interactives.

---

# 43. Transactions ETL

Un pipeline ne doit pas laisser la base dans un état incohérent si une étape échoue.

Approches possibles :

```text
staging
validation
transaction
merge/upsert
```

---

# 44. UPSERT

PostgreSQL permet :

```sql
INSERT ...
ON CONFLICT ...
```

utile notamment pour des imports idempotents.

Exemple futur :

```text
(id_source, reference_externe)
```

peut servir de clé de déduplication des biens importés.

---

# 45. Déduplication

Le MPD prévoit :

```text
UNIQUE(id_source, reference_externe)
```

afin d'empêcher l'import accidentel répété de la même référence dans une source.

---

# 46. Idempotence

Un pipeline rejoué ne doit pas nécessairement dupliquer les données.

Principe :

```text
Same input
+
Same pipeline
=
Controlled result
```

---

# 47. Performance du matching

Le matching peut nécessiter de comparer :

```text
1 demande
```

à :

```text
N biens
```

Avant de lancer un modèle AI coûteux, des filtres SQL simples peuvent réduire le jeu candidat :

```text
ville
budget
surface
type
```

Architecture :

```text
All properties
      |
      v
SQL filtering
      |
      v
Candidate set
      |
      v
Advanced matching
```

---

# 48. Pourquoi filtrer avant IA

Cela réduit :

- calcul ;
- latence ;
- coût ;
- bruit ;
- nombre de candidats.

PostgreSQL joue donc un rôle direct dans l'efficacité du pipeline IA.

---

# 49. Mesures attendues

Les preuves finales devront conserver :

```text
query
dataset size
execution plan before
execution time before
optimization
execution plan after
execution time after
interpretation
```

---

# 50. Taille du dataset

Une optimisation sur :

```text
10 rows
```

n'est généralement pas une preuve convaincante.

Le dataset de performance devra être suffisamment important pour observer un comportement réaliste.

Exemple cible de laboratoire :

```text
10,000+
```

biens, ou davantage si les ressources disponibles le permettent.

---

# 51. Génération de données

Un dataset synthétique pourra être utilisé pour la mesure de performance.

Il devra être clairement identifié comme :

```text
synthetic benchmark dataset
```

et non comme des données immobilières réelles.

---

# 52. Benchmark reproductible

La procédure devra permettre :

```text
Create schema
Seed dataset
Analyze
Run query
Capture result
Create optimization
Analyze
Run query again
Capture result
```

---

# 53. Evidence files

## Scripts disponibles

Les requêtes et le protocole EXPLAIN existent déjà dans le dépôt :

```text
../../../../database/oltp/001_operational_queries.sql
../../../../database/oltp/002_explain_analyze.sql
../../../../database/tests/003_oltp_constraints.sql
../../../../database/tests/006_oltp_data_quality.sql
```

Les cas couverts comprennent :

- mandats actifs par chasseur ;
- version active d'une demande ;
- secteurs associés au mandat ;
- biens candidats ;
- historique de présentations ;
- commentaires et suivi des paiements.

Le script de mesure utilise `EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT TEXT)` et actualise les statistiques avec `ANALYZE`. Il prépare une mesure réelle ; il ne contient pas un résultat de benchmark déjà obtenu.

## État de la preuve

Les migrations et l'API matérialisent le modèle transactionnel. Le rapport des recommandations documente une présentation persistée et son audit, et le rapport PRA documente des volumes métier restaurés.

```text
../../../60-SECURITY/RECOMMENDATION-AUDIT-RUNTIME-EVIDENCE.md
../../../PCA PRA/PCA-PRA-POSTGRESQL.md
```

Aucun temps avant/après index ni gain de performance n'est déduit de ces preuves fonctionnelles. Les plans, volumes du benchmark et conditions de mesure restent à conserver pour démontrer l'optimisation.

Le dossier final pourra contenir :

```text
C2-OLTP-Optimisation/
│
├── README.md
├── queries.sql
├── benchmark-data.sql
├── explain-before.txt
├── optimization.sql
├── explain-after.txt
└── benchmark-report.md
```

Les sources SQL existantes doivent être référencées sans duplication. Seuls les résultats manquants de mesure restent à produire lors d'une exécution réelle.

---

# 54. benchmark-report.md

Le rapport devra répondre à :

```text
What was slow?
Why?
What did PostgreSQL do?
What was changed?
What did PostgreSQL do afterwards?
Did performance improve?
What was the trade-off?
```

---

# 55. Exemple de preuve

```text
BEFORE
Seq Scan
Execution Time: X ms

       |
       v

CREATE INDEX ...

       |
       v

AFTER
Index / Bitmap Scan
Execution Time: Y ms
```

Les valeurs `X` et `Y` devront provenir de l'exécution réelle.

Elles ne doivent jamais être inventées dans la documentation.

---

# 56. Observabilité PostgreSQL

Une évolution peut exploiter :

```text
pg_stat_activity
pg_stat_database
pg_stat_user_tables
pg_stat_user_indexes
```

pour observer l'utilisation réelle.

---

# 57. Index inutilisés

Un index existant mais jamais utilisé peut devenir un candidat à la suppression après observation suffisante.

La suppression ne doit pas être décidée sur une fenêtre trop courte.

---

# 58. Slow queries

Une capacité telle que :

```text
pg_stat_statements
```

peut être utilisée pour identifier les requêtes coûteuses.

Elle pourra être activée dans l'environnement de benchmark si nécessaire.

---

# 59. Sécurité

L'optimisation ne doit jamais conduire à contourner :

- contrôle d'accès ;
- isolation ;
- contraintes ;
- confidentialité.

Performance et sécurité doivent rester compatibles.

---

# 60. SQL Injection

Les requêtes applicatives doivent utiliser des paramètres.

À éviter :

```text
string concatenation
```

avec entrée utilisateur.

Préférer les paramètres fournis par SQLAlchemy / driver PostgreSQL.

---

# 61. Sauvegarde

Une modification structurelle ou une optimisation importante en production doit être intégrée à la stratégie :

```text
Migration
Backup
Rollback / Recovery
Validation
```

---

# 62. Migration d'index

Les index doivent être versionnés comme les autres changements de schéma.

Ils ne doivent pas être créés manuellement sans traçabilité dans l'environnement cible.

---

# 63. CI

La CI pourra vérifier :

```text
migration executes
constraints exist
SQL tests pass
```

Les benchmarks de performance complets peuvent être séparés des tests rapides de CI.

---

# 64. Data Quality

Une base rapide contenant des données incohérentes ne satisfait pas le besoin.

L'objectif combine :

```text
Integrity
+
Performance
+
Maintainability
```

---

# 65. OLTP et haute disponibilité

L'optimisation locale d'une requête ne suffit pas à assurer la disponibilité.

La HA PostgreSQL relève également :

- réplication ;
- stockage ;
- backup ;
- restore ;
- PRA.

Ces sujets sont documentés dans les sections infrastructure et opérations.

---

# 66. Critères d'évaluation

La compétence est démontrée lorsque nous pouvons présenter :

```text
Working PostgreSQL schema
+
Representative transactional workload
+
Measured query
+
Identified bottleneck
+
Optimization
+
Measured improvement
+
Technical explanation
```

---

# 67. Ce qui ne constitue pas une preuve suffisante

Les éléments suivants seuls ne suffisent pas :

```text
"We use PostgreSQL"

"We created indexes"

"PostgreSQL is fast"

"We use an ORM"

"EXPLAIN exists"
```

Il faut montrer une exécution réelle.

---

# 68. Matrice de preuve

| Élément | Documentation | Preuve runtime |
|---|---|---|
| Modèle OLTP | MCD/MLD/MPD | PostgreSQL schema |
| Contraintes | MPD | `pg_constraint` |
| Transactions | README | SQL/API execution |
| Requête métier | README | `queries.sql` |
| Plan avant | principe | `explain-before.txt` |
| Optimisation | principe | `optimization.sql` |
| Plan après | principe | `explain-after.txt` |
| Comparaison | méthode | `benchmark-report.md` |

---

# 69. Relations avec les autres compétences

```text
C1
MCD / SQL
   |
   v
C2
OLTP optimization
   |
   +----------------+
   |                |
   v                v
C3 OLAP         C5 Matching IA
```

La base transactionnelle constitue une source importante pour les traitements analytiques et IA.

---

# 70. Statut actuel

| Élément | Statut |
|---|---|
| OLTP architecture | DOCUMENTÉE |
| Transaction model | DOCUMENTÉ |
| ACID principles | DOCUMENTÉS |
| Query candidates | REQUÊTES SQL PRÉSENTES |
| Index candidates | IDENTIFIÉS |
| Optimization methodology | DÉFINIE |
| Benchmark methodology | DÉFINIE |
| PostgreSQL runtime | PERSISTANCE MÉTIER DOCUMENTÉE / BENCHMARK À COMPLÉTER |
| Benchmark dataset | À PRODUIRE |
| EXPLAIN before | À PRODUIRE |
| Optimization | À TESTER |
| EXPLAIN after | À PRODUIRE |
| Benchmark report | À PRODUIRE |

---

# 71. Conclusion

La stratégie OLTP du projet repose sur :

```text
PostgreSQL
+
Normalized transactional model
+
ACID
+
Database constraints
+
Measured optimization
```

L'optimisation suivra systématiquement :

```text
Measure
   |
   v
Understand
   |
   v
Optimize
   |
   v
Measure Again
```

Les performances annoncées dans les livrables finaux devront provenir exclusivement des tests exécutés sur l'environnement du projet.

---

**BC05 / C2 — OLTP & OPTIMISATION — DOCUMENTATION BASELINE COMPLETE**
