# BC01 — C3 — Architecture OLTP / OLAP

**Bloc de compétences :** BC01 — Définir la stratégie du système d'information  
**Compétence travaillée :** Comparer les types d'architecture, leurs cas d'usage et leurs conditions d'évolution  
**Projet :** Real Estate Intelligence Platform / Chasse Immobilière  
**Plateforme :** Enterprise AI Platform  
**SGBD actuel :** PostgreSQL  
**Version :** 1.0  
**Statut :** EVIDENCED — architecture implémentée documentée, évolutions de scalabilité qualifiées sans sur-déclaration

---

# 1. Objectif

Ce dossier démontre la capacité à comparer des architectures de données et à justifier les choix retenus pour le projet.

Il explique :
- pourquoi le système sépare les traitements transactionnels et analytiques ;
- pourquoi cette séparation est actuellement logique plutôt que physique ;
- pourquoi le modèle OLTP est normalisé et le modèle OLAP dimensionnel ;
- comment les données passent du système opérationnel vers le système analytique ;
- dans quels cas réplication, partitionnement, sharding ou moteur OLAP dédié deviendraient pertinents ;
- pourquoi ces mécanismes ne doivent pas être introduits sans mesure.

Principe :

```text
Separate responsibilities first.
Measure second.
Scale physically only when justified.
```

# 2. Sources et hiérarchie de preuve

Sources principales :

```text
docs/40-DATA/01-Data-Architecture.md
docs/40-DATA/02-Data-Model.md
docs/98-ADR/ADR-0013-Data-Architecture.md
database/migrations/003_warehouse_schema.sql
database/olap/load_warehouse.py
database/tests/007_warehouse_data_quality.sql
docs/evidence/05-BC05/C2-OLTP-Optimisation/README.md
docs/evidence/05-BC05/C3-OLAP-Alimentation/README.md
```

Hiérarchie retenue :

```text
Runtime > Repository/implementation > CI > GitOps desired state > Documentation > Historical assumptions
```

Un ancien modèle candidat ne prévaut pas sur l'implémentation actuelle.

# 3. Contexte métier

La plateforme supporte le cycle de chasse immobilière :

```text
Client
  -> Demande
  -> Demande Version
  -> qualification / affectation chasseur
  -> Mandat possible
  -> Biens
  -> Eligibilité déterministe
  -> Classement / Matching
  -> Recommandation
  -> Présentation
  -> Visite / Feedback
  -> Transaction / Paiement
```

Une demande peut exister avant un mandat. Le système doit supporter à la fois l'état métier courant, l'historique, l'analyse, les KPI, le matching et la gouvernance.

# 4. Architecture Data actuelle

```text
Sources / Generated Data
          |
          v
         raw
          |
          v
       staging
          |
          v
+-----------------------+
|      real_estate      |
|         OLTP          |
| normalized / ACID     |
+-----------+-----------+
            |
            | controlled analytical load
            v
+-----------------------+
|       warehouse       |
|         OLAP          |
| dimensions / facts    |
+-----------+-----------+
            |
            v
       analytics
            |
            +--> KPI / reporting
            +--> decision support
            +--> governed AI/ML datasets
```

| Couche | Responsabilité |
|---|---|
| `raw` | Préservation source et traçabilité d'ingestion |
| `staging` | Nettoyage, normalisation technique, validation |
| `real_estate` | État opérationnel canonique et transactions |
| `warehouse` | Modèle analytique dimensionnel |
| `analytics` | KPI, marts et consommation analytique |

# 5. OLTP — rôle transactionnel

Le schéma `real_estate` porte le modèle transactionnel canonique : créations, modifications, lectures ciblées, transactions courtes, contraintes d'intégrité et état courant.

Il comprend notamment :

```text
client, chasseur, secteur, source, mandat, mandat_secteur,
demande, demande_version, bien, presentation, visite,
commentaire, document, piece_jointe, bareme_commission,
paiement, utilisateur, audit_log
```

Le modèle est normalisé afin de limiter duplication, anomalies de mise à jour et incohérences. PostgreSQL fournit ACID, clés primaires/étrangères, contraintes `UNIQUE`, `CHECK`, `NOT NULL` et transactions.

# 6. OLAP — rôle analytique

Le warehouse répond à des besoins différents : agrégations, historique, KPI, reporting, aide à la décision et préparation de données analytiques.

Il utilise les concepts :

```text
FACTS + DIMENSIONS + GRAIN + MEASURES
```

Le code examiné matérialise notamment :

```text
Dimensions:
dim_date
dim_source
dim_localisation
dim_bien
dim_client
dim_chasseur
dim_secteur
dim_demande_version

Bridge:
bridge_mandat_secteur

Facts:
fact_annonce
fact_mandat
fact_presentation
fact_paiement
```

Les faits définissent explicitement leur grain : une observation d'annonce par batch, un mandat OLTP, une présentation OLTP ou un paiement OLTP.

# 7. Normalisation versus modèle dimensionnel

| Critère | OLTP | OLAP |
|---|---|---|
| Finalité | Opérations métier | Analyse / décision |
| État | Principalement courant | Historique / observations |
| Modèle | Normalisé | Dimensionnel |
| Requêtes | Courtes et ciblées | Agrégations / scans |
| Écritures | Fréquentes/unitaires | Chargements contrôlés |
| Relations | Relations métier | Dimensions / faits / bridge |
| Optimisation | Transactions/lookups | Agrégations/parcours analytiques |
| Consommateurs | API/services métier | KPI/reporting/Data/ML |

Le warehouse utilise des surrogate keys tout en conservant certains identifiants source nécessaires au rapprochement ETL et au lineage.

# 8. Préservation du sens métier

L'OLAP ne doit pas fabriquer des relations absentes de l'OLTP.

La relation `mandat N:N secteur` est conservée par `bridge_mandat_secteur`. De même, `fact_paiement` ne fabrique pas de relation directe paiement→bien lorsque le modèle opérationnel relie le paiement au mandat.

Le warehouse possède également une stratégie de membre inconnu avec clé `0`. Elle permet de représenter une relation légitimement absente sans inventer une entité. C'est notamment pertinent lorsqu'une présentation provient d'une demande sans mandat.

# 9. Historisation

`demande_version` contient déjà l'historique des critères de recherche dans l'OLTP. Il n'est donc pas nécessaire de reconstruire artificiellement cet historique.

Certaines dimensions possèdent aussi `valid_from`, `valid_to` et `is_current` lorsque cette forme d'historisation est utile. Une stratégie SCD2 ne doit pas être appliquée partout sans besoin analytique.

# 10. Privacy by Design

Le warehouse n'est pas une copie complète de l'OLTP.

`dim_client` exclut volontairement nom, prénom, email et téléphone. `dim_chasseur` exclut également les informations de contact directes. Les identifiants source conservés pour ETL/lineage restent à contrôler : pseudonymisation ne signifie pas anonymisation.

Principe :

```text
Only propagate data required for the analytical purpose.
```

# 11. Séparation logique versus physique

Actuellement :

```text
PostgreSQL
|
+--> real_estate   OLTP
+--> raw
+--> staging
+--> warehouse     OLAP
+--> analytics
```

La séparation est **logique**, pas physique.

Ce choix réduit le nombre de technologies, les coûts d'exploitation, la consommation de ressources et les mécanismes de synchronisation. ADR-0013 impose de réévaluer un moteur analytique séparé seulement si volume, concurrence, latence, stockage colonne ou traitement distribué le justifient.

# 12. Pourquoi PostgreSQL reste suffisant actuellement

La décision est :

```text
PostgreSQL for OLTP
+
PostgreSQL for logically separated OLAP
```

tant que les mesures montrent que cette architecture satisfait le besoin.

Une séparation physique ajouterait réplication/synchronisation, gestion de fraîcheur, sauvegardes, sécurité, observabilité, PRA et compétences supplémentaires.

La stratégie suit :

```text
Reuse before adding technology.
```

# 13. Alimentation OLTP vers OLAP

`database/olap/load_warehouse.py` charge les dimensions avant les faits :

```text
dim_source
dim_localisation
dim_bien
dim_client
dim_chasseur
dim_secteur
dim_demande_version
        |
        v
fact_annonce
fact_mandat
bridge_mandat_secteur
fact_presentation
fact_paiement
```

Le chargement transforme les données, par exemple `prix/surface -> prix_m2`, `date_fin-date_debut -> duree_jours`, et mappe les identifiants OLTP vers les surrogate keys.

Il utilise `ON CONFLICT ... DO UPDATE` ou `DO NOTHING` selon le cas afin de contrôler les réexécutions.

Le chemin concret n'oblige pas toutes les entités à repasser par une copie staging : plusieurs objets sont chargés depuis `real_estate`, tandis que `fact_annonce` utilise aussi `staging.annonces` pour les métadonnées `ingestion_batch` et `source_file`.

# 14. Réplication

Une read replica peut servir à déporter des lectures ou contribuer à une architecture HA :

```text
Primary
  +--> Read Replica
```

Avantages possibles : réduction de certaines lectures sur le primaire, isolation partielle de workloads, disponibilité et maintenance.

Coûts : stockage, réseau, monitoring, replication lag, failover, cohérence asynchrone et procédures supplémentaires. Une replica ne remplace pas un backup.

**État projet :**

```text
Read replica: NOT IMPLEMENTED
```

Elle deviendrait candidate en cas de saturation mesurée du primaire, besoin de disponibilité supérieur, besoin d'isoler des lectures ou objectifs RTO/RPO différents.

# 15. Partitionnement

Le partitionnement divise une grande table en partitions, par exemple temporelles :

```text
fact_annonce
+--> 2026-01
+--> 2026-02
+--> 2026-03
```

Il peut devenir utile pour de grandes tables historiques lorsque les requêtes filtrent régulièrement sur la clé de partition ou lorsque la rétention/maintenance par période devient importante.

Des faits comme `fact_annonce`, `fact_presentation` ou `fact_paiement` peuvent devenir candidats, mais uniquement après mesure.

Un mauvais partitionnement augmente le nombre d'objets, complique migrations/index/maintenance et peut dégrader certaines requêtes.

**État projet :**

```text
Partitioning: NOT IMPLEMENTED
Status: DEFERRED UNTIL MEASURED NEED
```

# 16. Sharding

Le sharding distribue les données entre plusieurs nœuds selon une clé.

Il peut permettre un scale-out massif mais introduit : shard key, rebalancing, transactions distribuées, joins inter-shards, routage, backup/restauration multi-nœuds, cohérence et exploitation complexes.

**État projet :**

```text
Sharding: NOT IMPLEMENTED
Status: DEFERRED
```

Avant de l'envisager, il faudrait démontrer que l'optimisation SQL, les index, le dimensionnement vertical, la séparation OLTP/OLAP, la réplication et le partitionnement ne répondent pas au problème.

# 17. Comparaison des mécanismes de scalabilité

| Mécanisme | Problème traité | Complexité | État |
|---|---|---:|---|
| Indexation | Accès ciblés | Faible/moyenne | IMPLEMENTED / à mesurer |
| Optimisation SQL | Plans coûteux | Faible/moyenne | Méthode définie |
| Vertical scaling | CPU/RAM/I/O | Faible/moyenne | Disponible selon infra |
| Séparation logique OLTP/OLAP | Responsabilités/workloads | Moyenne | IMPLEMENTED |
| Réplication | HA / lectures | Moyenne/élevée | NOT IMPLEMENTED |
| Partitionnement | Grandes tables | Moyenne/élevée | NOT IMPLEMENTED |
| Séparation physique OLTP/OLAP | Contention/spécialisation | Élevée | DEFERRED |
| Sharding | Scale-out | Très élevée | DEFERRED |
| Moteur OLAP spécialisé | Analytics dépassant PostgreSQL | Élevée | DEFERRED |

# 18. Ordre d'évolution retenu

```text
Measure
  -> Optimize query/schema
  -> Review indexes
  -> Right-size PostgreSQL
  -> Separate workloads if necessary
  -> Evaluate replication/partitioning
  -> Evaluate specialized analytical engine
  -> Distributed architecture only if required
```

Cette séquence limite la surarchitecture.

# 19. Déclencheurs d'évolution

| Trigger observé | Première réponse à évaluer |
|---|---|
| Requête OLTP lente | EXPLAIN / SQL / index |
| Primaire saturé en lecture | Optimisation puis replica |
| Facts très volumineuses | Index puis partitionnement |
| Analytics perturbe OLTP | Séparation physique |
| Agrégations très coûteuses | Pré-agrégation / vue matérialisée / OLAP spécialisé |
| Batch trop long | Incremental load / optimisation |
| Besoin near-real-time réel | CDC / streaming |
| Limite verticale démontrée | Scale-out |
| Distribution massive d'écritures | Sharding après alternatives |
| Besoin colonne/distribué | Moteur analytique spécialisé |

# 20. Technologies spécialisées

Snowflake, BigQuery, ClickHouse, Trino, Spark ou un lakehouse Iceberg peuvent répondre à certains besoins, mais ne sont pas nécessaires à la baseline actuelle.

Leur adoption devrait suivre :

```text
Requirement
  -> Measured limitation
  -> Technology comparison
  -> Decision matrix
  -> ADR
  -> Implementation
```

Le projet dispose déjà de PostgreSQL, Airflow, dbt, MinIO, OpenMetadata, MLflow, Kubernetes, GitLab CI, Argo CD et observabilité. Ajouter Snowflake ou une architecture Databricks-like sans besoin démontré créerait surtout de la duplication et de la complexité.

# 21. Gouvernance et Data Quality

La séparation des couches facilite le lineage :

```text
Source
 -> Raw/Staging
 -> OLTP canonical state
 -> Warehouse
 -> Analytics
 -> Consumer
```

OpenMetadata fournit la couche de métadonnées, ownership, gouvernance et lineage ; il ne remplace ni PostgreSQL, ni le warehouse, ni un Data Lake.

La Data Quality doit couvrir selon le périmètre : nullité, unicité, intégrité référentielle, domaines, montants, dates, mappings, fraîcheur et volumes.

# 22. Performance et preuves

C3 définit la stratégie architecturale et ne fabrique aucun benchmark.

Les mesures OLTP détaillées appartiennent à :

```text
docs/evidence/05-BC05/C2-OLTP-Optimisation/
```

La preuve attendue comprend `EXPLAIN ANALYZE` avant, optimisation, mesure après et interprétation. Les résultats manquants restent à produire/rattacher dans BC05.

# 23. Sécurité, RGPD et éco-conception

La séparation analytique respecte :
- moindre privilège ;
- secrets protégés ;
- accès contrôlé aux schémas ;
- PII minimisée ;
- auditabilité ;
- finalités analytiques explicites.

L'éco-conception privilégie :
- réutilisation de PostgreSQL avant ajout d'un moteur ;
- minimisation des copies ;
- mesure avant scaling ;
- rétention contrôlée ;
- refus d'une architecture distribuée sans besoin démontré.

# 24. Relation avec la stratégie SI

C3 applique directement :
- **S3 — Data Governance** : séparation des couches, lineage, qualité et finalités ;
- **S6 — Maîtrise de la complexité et des ressources** : séparation logique aujourd'hui, évolution physique seulement si mesurée.

# 25. Relation avec C4, C5 et C6

**C4** approfondira composants, interactions, dépendances et points de performance.

**C5** comparera les solutions avec des critères pondérés : performance, scalabilité, sécurité, maintenabilité, complexité, coût, résilience et éco-conception.

**C6** approfondira les recommandations d'éco-conception.

# 26. Relation avec BC05

```text
BC01-C3
  -> Why this architecture?
  -> Which alternatives?
  -> When should it evolve?

BC05
  -> How is OLTP implemented/optimized?
  -> How is OLAP populated?
  -> What do runtime measurements show?
```

Les preuves BC05 sont référencées plutôt que dupliquées.

# 27. Matrice CURRENT / TARGET / DEFERRED

| Élément | Statut | Justification |
|---|---|---|
| PostgreSQL OLTP | IMPLEMENTED | Schéma `real_estate` |
| Modèle normalisé | IMPLEMENTED | Modèle/migrations |
| Séparation logique OLTP/OLAP | IMPLEMENTED | Schémas distincts |
| Warehouse dimensionnel | IMPLEMENTED | Migration 003 |
| Dimensions/facts | IMPLEMENTED | DDL warehouse |
| Chargement OLTP→warehouse | IMPLEMENTED | `load_warehouse.py` |
| Analytics layer | IMPLEMENTED / évolutive | Couche dédiée |
| Read replica | NOT IMPLEMENTED | Pas justifiée actuellement |
| Partitionnement | NOT IMPLEMENTED | À évaluer après mesure |
| Sharding | DEFERRED | Complexité disproportionnée |
| OLAP physique séparé | DEFERRED | PostgreSQL retenu |
| Moteur columnar dédié | DEFERRED | Aucun besoin mesuré |
| Streaming/Kafka | DEFERRED | Pas de besoin sub-seconde démontré |
| Lakehouse | DEFERRED | Non requis pour la baseline |

# 28. Architecture CURRENT

```text
          Sources / Generated Data
                    |
                    v
                   raw
                    |
                    v
                 staging
                    |
                    v
        +-----------------------+
        |      PostgreSQL       |
        |  real_estate (OLTP)   |
        |          |            |
        |          v            |
        |  warehouse (OLAP)     |
        |          |            |
        |          v            |
        |     analytics         |
        +-----------+-----------+
                    |
             KPI / BI / ML
```

# 29. Architecture TARGET conditionnelle

```text
                PostgreSQL OLTP
                     |
              +------+------+
              |             |
              v             v
        Read Replica    Data Pipeline
        if required          |
                             v
                    Dedicated OLAP
                     if required
                             |
                             v
                         Analytics
```

Il s'agit d'options conditionnelles, pas d'un état promis.

# 30. Ce que cette preuve ne prétend pas

Ce document ne prétend pas que :
- PostgreSQL dispose d'une read replica ;
- le warehouse est partitionné ;
- le système est shardé ;
- Snowflake, Databricks, Spark ou Kafka sont déployés ;
- un lakehouse est déployé ;
- tous les faits disposent déjà d'un volume métier significatif ;
- tous les benchmarks sont terminés ;
- toute la lineage est à jour pour chaque objet ajouté.

Ces affirmations nécessitent des preuves spécifiques.

# 31. Matrice de preuve

| Élément attendu | Preuve | Statut |
|---|---|---|
| Comparer OLTP et OLAP | Sections 5–7 | EVIDENCED |
| Justifier séparation | Sections 11–12 | EVIDENCED |
| Décrire implémentation OLAP | Migration 003 + chargeur | EVIDENCED |
| Comparer réplication | Section 14 | EVIDENCED |
| Comparer partitionnement | Section 15 | EVIDENCED |
| Comparer sharding | Section 16 | EVIDENCED |
| Stratégie de scaling | Sections 17–20 | EVIDENCED |
| Sécurité/RGPD/éco-conception | Section 23 | EVIDENCED |
| CURRENT/TARGET/DEFERRED | Sections 27–30 | EVIDENCED |
| Performance avant/après | BC05-C2 | À CONSOLIDER DANS BC05 |
| Décision pondérée | BC01-C5 | À PRODUIRE |

# 32. Argumentaire jury

> Le projet sépare OLTP et OLAP parce que les deux workloads ont des objectifs et des modèles différents. L'OLTP `real_estate` est normalisé et protège l'état transactionnel, tandis que le warehouse utilise dimensions et faits pour l'analyse. Aujourd'hui cette séparation est logique mais reste sur PostgreSQL, car aucune mesure ne justifie encore un second moteur. La réplication, le partitionnement et le sharding sont étudiés comme mécanismes de scalabilité, mais ne sont pas déclarés implémentés. Nous appliquons une progression mesurée : optimiser, dimensionner, séparer les workloads, puis distribuer uniquement si les limites sont démontrées.

# 33. Questions de défense

**Pourquoi PostgreSQL pour les deux ?**  
Parce que le workload actuel ne démontre pas encore la nécessité d'un deuxième moteur et que les responsabilités sont déjà logiquement séparées.

**Pourquoi pas Snowflake ou Databricks ?**  
Une technologie supplémentaire doit résoudre une limitation mesurée. Elle ajouterait aujourd'hui davantage de complexité que de valeur démontrée.

**Pourquoi ne pas partitionner immédiatement ?**  
Le partitionnement doit répondre à un volume, un pattern de requêtes et un problème mesurés.

**Pourquoi pas de sharding ?**  
Le projet n'a pas atteint une limite de scale-out justifiant la complexité des transactions distribuées, joins, routage, backup et restauration.

**Pourquoi une read replica pourrait être utile ?**  
Pour déporter certaines lectures ou contribuer à la HA, mais avec un coût en lag, stockage, monitoring et failover.

# 34. Conclusion

L'architecture applique :

```text
Normalized OLTP
  -> Logical workload separation
  -> Dimensional OLAP
  -> Measure
  -> Optimize
  -> Scale only when required
```

Le projet dispose actuellement de PostgreSQL, d'un modèle OLTP normalisé, d'un warehouse dimensionnel, d'un chargement contrôlé OLTP→OLAP, d'une couche analytics, de gouvernance et de Data Quality, sans déclarer prématurément réplication, partitionnement, sharding ou moteur OLAP dédié.

La prochaine étape BC01 est **C4 — Composants, interactions, dépendances et points de performance**.

---

**BC01 / C3 — ARCHITECTURE OLTP / OLAP — EVIDENCED**
