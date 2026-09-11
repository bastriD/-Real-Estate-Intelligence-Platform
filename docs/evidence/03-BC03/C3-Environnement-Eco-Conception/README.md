# BC03 — C3 — Environnement & Éco-conception

**Bloc de compétences :** BC03  
**Compétence :** C3 — Prendre en compte les impacts environnementaux et appliquer des principes d'éco-conception  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Baseline documentaire — mesures réelles à consolider

---

# 1. Objectif

Ce dossier démontre la prise en compte de l'impact environnemental dans la conception et l'exploitation de la solution.

L'éco-conception ne consiste pas uniquement à réduire la consommation électrique.

Elle concerne l'ensemble du cycle :

```text
Architecture
    |
    v
Development
    |
    v
Build
    |
    v
Deployment
    |
    v
Execution
    |
    v
Storage
    |
    v
Observability
    |
    v
Retention
    |
    v
Decommissioning
```

L'objectif est de rechercher un équilibre entre :

```text
Business Value
+
Performance
+
Reliability
+
Security
+
Resource Efficiency
```

---

# 2. Documents de référence

Document Fil Rouge associé :

```text
NOTE-ECO-CONCEPTION.md
```

Documents d'architecture :

```text
../../../00-FOUNDATION/01-Architecture-Principles.md
../../../00-FOUNDATION/05-Technology-Stack.md
../../../20-APPLICATION/01-Application-Architecture.md
../../../30-INFRASTRUCTURE/01-Infrastructure-Architecture.md
../../../30-INFRASTRUCTURE/07-Compute-Architecture.md
../../../30-INFRASTRUCTURE/09-Capacity-Planning.md
```

Documents Data / AI :

```text
../../../40-DATA/09-Data-Lifecycle.md
../../../50-AI/01-AI-Platform-Architecture.md
../../../50-AI/02-LLM-Architecture.md
```

Documents Operations / Observability :

```text
../../../80-OPERATIONS/05-Capacity-Management.md
../../../90-OBSERVABILITY/01-Observability-Architecture.md
```

---

# 3. Principes

L'approche repose sur plusieurs principes :

```text
Avoid
Reduce
Reuse
Measure
Optimize
Retain Only What Is Needed
```

La première optimisation consiste à éviter les traitements inutiles.

---

# 4. Sobriété architecturale

Une architecture plus complexe n'est pas automatiquement meilleure.

Chaque nouveau composant entraîne potentiellement :

```text
CPU
Memory
Storage
Network
Operational Complexity
Monitoring
Backup
Maintenance
```

Principe :

```text
New Technology
      |
      v
Does it solve a demonstrated requirement?
      |
   +--+--+
   |     |
  YES    NO
   |     |
   v     v
Evaluate  Do Not Add
```

---

# 5. Réutilisation de l'infrastructure

La plateforme privilégie l'exploitation de l'infrastructure existante lorsque celle-ci satisfait les besoins.

Cela permet de limiter :

- achat matériel inutile ;
- remplacement prématuré ;
- fabrication de nouveaux équipements ;
- déchets électroniques.

La capacité disponible doit néanmoins être surveillée.

---

# 6. Virtualisation

La virtualisation permet de mutualiser les ressources physiques.

```text
Physical Host
     |
     +-- VM
     +-- VM
     +-- VM
```

Avantages potentiels :

- consolidation ;
- meilleur taux d'utilisation ;
- isolation ;
- allocation dynamique.

Une sur-allocation excessive doit cependant être évitée.

---

# 7. Kubernetes

Kubernetes permet de partager les ressources entre workloads.

```text
Cluster
 |
 +-- Application
 +-- Data
 +-- Monitoring
 +-- MLOps
```

Les workloads doivent progressivement définir :

```text
requests
limits
```

afin de réduire :

- surdimensionnement ;
- contention ;
- consommation incontrôlée.

---

# 8. Resource Requests

Les requests doivent refléter les besoins réels.

Exemple :

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
```

Les valeurs ne doivent pas être copiées arbitrairement d'un environnement externe.

---

# 9. Resource Limits

Les limites permettent d'éviter qu'un workload monopolise les ressources.

Exemple :

```yaml
resources:
  limits:
    cpu: "500m"
    memory: "512Mi"
```

Les valeurs finales doivent être déterminées à partir de mesures.

---

# 10. Right-sizing

Le processus cible est :

```text
Deploy
 |
 v
Measure
 |
 v
Observe CPU / RAM
 |
 v
Adjust Requests / Limits
 |
 v
Measure Again
```

Le right-sizing doit être fondé sur des données réelles.

---

# 11. Capacity Planning

L'ajout de ressources doit être justifié par :

```text
Observed Utilization
+
Growth
+
SLO
+
Business Requirement
```

et non simplement par :

```text
More Hardware = Better
```

---

# 12. Autoscaling

L'autoscaling peut améliorer l'utilisation des ressources lorsque la charge varie.

Cependant :

```text
Autoscaling
!=
Automatic Eco-Design
```

Un mauvais dimensionnement peut multiplier inutilement les instances.

L'autoscaling doit être piloté par des métriques pertinentes.

---

# 13. Images conteneurs

Les images doivent rester raisonnablement petites.

Bonnes pratiques :

- base image adaptée ;
- dépendances strictement nécessaires ;
- multi-stage builds lorsque pertinent ;
- suppression des caches de build ;
- exclusion des fichiers inutiles.

---

# 14. Exemple Docker

Approche :

```dockerfile
FROM python:3.12-slim
```

peut être préférable à une image générique beaucoup plus lourde si les dépendances sont compatibles.

L'objectif n'est pas de rechercher systématiquement l'image la plus petite, mais un compromis :

```text
Size
Security
Compatibility
Maintainability
```

---

# 15. Build CI

Les pipelines CI consomment également des ressources.

Il faut éviter :

- builds identiques inutiles ;
- tests dupliqués sans justification ;
- artifacts sans expiration ;
- images inutilisées ;
- pipelines déclenchés sans besoin.

---

# 16. Cache CI

Le cache peut réduire les téléchargements et calculs répétés.

Exemple :

```text
Dependencies
     |
     v
CI Cache
     |
     v
Reuse
```

Le cache doit cependant disposer d'une stratégie de nettoyage.

---

# 17. Container Registry

Les anciennes images ne doivent pas être conservées indéfiniment sans raison.

Politique cible :

```text
Active versions
+
Rollback versions
+
Retention
+
Cleanup
```

---

# 18. GitOps

GitOps permet de limiter les opérations manuelles et de reconstruire l'état attendu.

```text
Git
 |
 v
Desired State
 |
 v
Argo CD
 |
 v
Cluster
```

La reproductibilité réduit les opérations de reconstruction improvisées.

---

# 19. Application

Une application efficace doit éviter :

- appels réseau inutiles ;
- polling agressif ;
- payloads trop volumineux ;
- calculs répétés ;
- lectures complètes lorsque seules quelques colonnes sont nécessaires.

---

# 20. API

Une API doit retourner les données utiles au besoin.

Exemple :

```text
SELECT *
```

n'est pas automatiquement approprié.

Lorsque seuls trois champs sont nécessaires :

```text
SELECT id, name, status
```

peut réduire :

- traitement ;
- mémoire ;
- réseau.

---

# 21. Pagination

Les grandes collections doivent être paginées lorsque nécessaire.

```text
GET /properties?page=1&limit=50
```

au lieu de charger systématiquement l'ensemble du dataset.

---

# 22. Cache

Un cache peut éviter certains calculs répétitifs.

Architecture :

```text
Request
 |
 v
Cache?
 +--+--+
 |     |
Hit   Miss
 |     |
 v     v
Return Compute
        |
        v
       Cache
```

Cependant, le cache lui-même consomme des ressources.

Il doit être utilisé uniquement lorsqu'il apporte une valeur mesurable.

---

# 23. PostgreSQL

L'optimisation SQL contribue à l'éco-conception.

Une requête inefficace consomme davantage :

```text
CPU
Memory
Disk I/O
Time
```

---

# 24. Indexation

Un index peut réduire fortement le coût de certaines requêtes.

Mais :

```text
More Indexes
!=
Always Better
```

Les index consomment :

- stockage ;
- mémoire ;
- coût d'écriture.

Ils doivent correspondre aux requêtes réelles.

---

# 25. EXPLAIN

Les requêtes importantes peuvent être analysées avec :

```sql
EXPLAIN
```

ou :

```sql
EXPLAIN ANALYZE
```

afin d'identifier :

- sequential scans ;
- index usage ;
- join cost ;
- execution time.

---

# 26. OLTP / OLAP

La séparation logique des workloads évite de faire exécuter des analyses coûteuses directement sur les opérations transactionnelles.

```text
OLTP
 |
 +--> Operational Queries

OLAP
 |
 +--> Analytical Queries
```

---

# 27. Data Pipeline

Une pipeline doit éviter de retraiter inutilement l'ensemble des données.

Lorsque possible :

```text
Full Reload
```

peut évoluer vers :

```text
Incremental Processing
```

si le besoin et la complexité le justifient.

---

# 28. Airflow

Les DAGs doivent être planifiés selon le besoin métier réel.

Exemple :

```text
Every Minute
```

n'est pas justifié si les données ne changent qu'une fois par jour.

La fréquence doit correspondre à :

```text
Business Freshness Requirement
```

---

# 29. Data Quality

Les tests Data Quality consomment des ressources mais permettent d'éviter des traitements ultérieurs incorrects.

Le compromis est :

```text
Useful Validation
vs
Redundant Validation
```

---

# 30. Cycle de vie des données

Toutes les données ne doivent pas être conservées indéfiniment.

Le cycle est :

```text
Create
 |
 v
Use
 |
 v
Retain
 |
 v
Archive
 |
 v
Delete
```

---

# 31. Retention

La politique de rétention doit prendre en compte :

- besoin métier ;
- réglementation ;
- audit ;
- restauration ;
- coût de stockage.

---

# 32. Logs

Les logs représentent une source importante de croissance du stockage.

Il faut éviter :

- DEBUG permanent en production ;
- duplication ;
- payload complet ;
- secrets ;
- rétention infinie.

---

# 33. Loki

La stratégie Loki doit considérer :

```text
Volume
Retention
Cardinality
Query Patterns
```

Une forte cardinalité peut dégrader les performances.

---

# 34. Metrics

Prometheus peut également générer beaucoup de séries.

Il faut contrôler :

```text
Metric Count
Label Cardinality
Scrape Frequency
Retention
```

---

# 35. Traces

Toutes les requêtes ne nécessitent pas forcément une conservation permanente de traces détaillées.

Le sampling peut être envisagé selon :

- criticité ;
- trafic ;
- besoin diagnostic.

---

# 36. Dashboards

Les dashboards doivent répondre à une question opérationnelle.

Un dashboard inutilisé représente :

```text
Queries
+
Storage
+
Maintenance
```

sans valeur réelle.

---

# 37. Alerting

Les alertes inutiles ont également un coût humain.

L'objectif est :

```text
Actionable Alerts
```

et non :

```text
Maximum Number of Alerts
```

---

# 38. IA et consommation

L'inférence LLM est généralement plus coûteuse qu'une requête applicative classique.

Le processus doit donc vérifier :

```text
Does this request really need AI?
```

avant de déclencher une inférence.

---

# 39. Local AI

Le projet utilise une approche local-first pour l'AI.

Architecture :

```text
Application
    |
    v
Local AI Host
    |
    v
Ollama
    |
    v
Qwen
```

Cela permet notamment :

- réutilisation du matériel existant ;
- contrôle des données ;
- expérimentation locale ;
- réduction de dépendance externe.

Cela ne signifie pas automatiquement que l'inférence locale est toujours énergétiquement supérieure à une solution cloud.

---

# 40. GPU existant

La plateforme privilégie l'exploitation des GPU disponibles.

Principe :

```text
Use Existing Capacity
before
Buying New Hardware
```

si les besoins de performance restent satisfaits.

---

# 41. Taille des modèles

Le plus grand modèle n'est pas automatiquement le meilleur choix.

Sélection :

```text
Business Need
      |
      v
Required Quality
      |
      v
Smallest Adequate Model
```

---

# 42. Quantification

La quantification peut réduire :

- VRAM ;
- RAM ;
- temps de chargement ;
- certaines consommations de calcul.

Elle peut toutefois affecter la qualité.

Le choix doit être mesuré.

---

# 43. Prompt Engineering

Un prompt inutilement long augmente le nombre de tokens traités.

Le principe est :

```text
Necessary Context
+
Clear Instruction
```

plutôt que :

```text
Maximum Context
```

---

# 44. RAG

RAG peut limiter la quantité de contexte envoyée au LLM en sélectionnant uniquement les passages pertinents.

```text
Large Knowledge Base
       |
       v
Retriever
       |
       v
Relevant Chunks
       |
       v
LLM
```

---

# 45. Chunking

Des chunks excessivement grands peuvent :

- augmenter les tokens ;
- augmenter la latence ;
- réduire la précision de retrieval.

Des chunks trop petits peuvent perdre le contexte.

Le dimensionnement doit être testé.

---

# 46. Vector Database

Une base vectorielle dédiée ne doit pas être introduite sans besoin démontré.

Avant Qdrant, une solution comme :

```text
PostgreSQL + pgvector
```

peut être comparée.

Le choix doit considérer :

- performance ;
- volume ;
- complexité ;
- infrastructure supplémentaire.

---

# 47. Kafka

Kafka n'est pas nécessaire si le besoin ne nécessite pas réellement :

- streaming ;
- event replay ;
- forte volumétrie événementielle ;
- découplage asynchrone avancé.

Éviter un composant inutile est également une mesure d'éco-conception.

---

# 48. Keycloak et Vault

Keycloak et Vault sont des capacités cibles.

Ils ne doivent être ajoutés que lorsque :

```text
Security Benefit
>
Operational Complexity
```

pour le niveau de maturité concerné.

---

# 49. Disponibilité

Une architecture HA consomme plus de ressources qu'une instance unique.

Exemple :

```text
1 instance
vs
3 replicas
```

Le niveau de disponibilité doit être aligné sur :

```text
Business Criticality
+
SLO
```

---

# 50. Backup

Les backups consomment du stockage.

Mais leur suppression pour réduire le stockage serait une fausse optimisation.

Il faut optimiser :

```text
Frequency
Retention
Compression
Criticality
```

sans compromettre la recoverability.

---

# 51. Compression

La compression peut réduire :

- stockage ;
- réseau.

Mais elle augmente parfois :

- CPU.

Il faut donc raisonner en coût global.

---

# 52. Environnements

Multiplier les environnements complets augmente fortement la consommation.

Une stratégie adaptée peut distinguer :

```text
Development
Test
Production-like
```

sans dupliquer inutilement chaque composant lourd.

---

# 53. Environnements éphémères

Les environnements temporaires peuvent être supprimés après utilisation.

```text
Create
 |
 v
Test
 |
 v
Destroy
```

au lieu de rester actifs indéfiniment.

---

# 54. Observabilité environnementale

La plateforme dispose déjà de briques permettant d'observer :

```text
CPU
RAM
Disk
Network
GPU where available
```

Ces mesures peuvent servir de base à l'amélioration continue.

---

# 55. Métriques utiles

Exemples :

```text
CPU utilization
Memory utilization
Disk usage
Network traffic
Pod resource consumption
GPU utilization
GPU memory
Execution duration
```

---

# 56. Mesure avant optimisation

Principe :

```text
Measure
   |
   v
Identify Waste
   |
   v
Optimize
   |
   v
Measure Again
```

Il faut éviter d'optimiser sans mesure.

---

# 57. KPI techniques

Exemples de KPI :

```text
CPU per request
Memory per workload
Storage growth
Pipeline duration
Inference duration
GPU utilization
Container image size
```

Les KPI réellement utilisés doivent être documentés.

---

# 58. KPI Data

Exemples :

```text
Rows processed
Duration
Rows/sec
Data volume
Failed records
```

Ces indicateurs peuvent aider à identifier les traitements disproportionnés.

---

# 59. KPI AI

Exemples :

```text
Inference latency
Prompt tokens
Generated tokens
GPU utilization
VRAM utilization
Requests
```

Ils permettent de comparer différentes stratégies AI.

---

# 60. Éco-conception UX

Une interface efficace peut également réduire les traitements.

Exemples :

- pagination ;
- filtres avant requête ;
- pas d'auto-refresh inutile ;
- lazy loading lorsque pertinent ;
- compression des assets ;
- limitation des dépendances frontend.

---

# 61. Accessibilité

Accessibilité et éco-conception peuvent partager certains principes :

```text
Simple Interfaces
Clear Navigation
Reduced Complexity
Efficient Content
```

Mais ce sont deux exigences distinctes.

---

# 62. Maintenance

Une solution maintenable évite :

- duplication ;
- reconstruction ;
- remplacement prématuré ;
- multiplication des outils.

La simplicité opérationnelle participe donc indirectement à la sobriété.

---

# 63. Dette technique

Une dette technique excessive peut conduire à :

```text
More Incidents
More Rework
More Deployments
More Infrastructure
```

La gestion de la dette contribue à la durabilité du système.

---

# 64. Choix Open Source

L'utilisation de solutions open source peut favoriser :

- réutilisation ;
- interopérabilité ;
- longévité ;
- réduction du vendor lock-in.

Ce n'est cependant pas à elle seule une preuve d'éco-conception.

---

# 65. FinOps et GreenOps

Deux perspectives peuvent être combinées :

```text
FinOps
  |
  +--> Resource Cost

GreenOps
  |
  +--> Environmental Resource Efficiency
```

Une réduction des ressources peut parfois améliorer les deux.

---

# 66. Arbitrage

L'éco-conception ne doit pas dégrader arbitrairement :

- sécurité ;
- intégrité ;
- disponibilité critique ;
- conformité.

Exemple :

```text
Remove backups
```

pour économiser du stockage serait un mauvais arbitrage.

---

# 67. Architecture Decision

Une décision significative peut intégrer une section :

```text
Environmental Consequences
```

afin d'analyser :

- ressources supplémentaires ;
- stockage ;
- réseau ;
- dépendances ;
- durée de vie.

---

# 68. Cycle de décision

```text
Requirement
    |
    v
Possible Solution
    |
    v
Resource Impact
    |
    v
Alternative
    |
    v
Decision
    |
    v
Measure
```

---

# 69. Exemple — Kafka

```text
Requirement
   |
   v
Need real event streaming?
   |
 +--+--+
 |     |
YES    NO
 |     |
 v     v
Evaluate Kafka
       |
       v
Do not deploy Kafka
```

Éviter Kafka lorsqu'il n'est pas nécessaire réduit :

- CPU ;
- RAM ;
- stockage ;
- exploitation.

---

# 70. Exemple — Qdrant

```text
Vector Search Requirement
       |
       v
Can PostgreSQL/pgvector satisfy it?
       |
   +---+---+
   |       |
  YES      NO
   |       |
   v       v
Reuse DB   Evaluate Qdrant
```

---

# 71. Exemple — AI

```text
User Request
     |
     v
Can deterministic logic solve it?
     |
   +---+---+
   |       |
  YES      NO
   |       |
   v       v
Normal     AI
Processing Inference
```

L'AI doit être utilisée lorsqu'elle apporte une valeur réelle.

---

# 72. Exemple — Scheduling

Si une pipeline doit fournir des données chaque matin :

```text
Once per day
```

peut être plus approprié que :

```text
Every minute
```

---

# 73. Exemple — Logging

Approche incorrecte :

```text
DEBUG
24/7
All Payloads
Infinite Retention
```

Approche cible :

```text
Appropriate Log Level
+
Useful Fields
+
Retention
+
No Sensitive Data
```

---

# 74. Preuves existantes

## Choix effectivement matérialisés

Le manifeste backend précise les ressources demandées et limitées :

| Paramètre | Valeur configurée |
|---|---|
| Réplicas backend | 1 |
| CPU demandé | 100m |
| Mémoire demandée | 128Mi |
| Limite CPU | 500m |
| Limite mémoire | 512Mi |

Source :

```text
../../../../deploy/kubernetes/backend/deployment.yaml
```

Ces valeurs sont des paramètres de configuration. Elles ne représentent pas une mesure de consommation ni la preuve d'un dimensionnement optimal.

D'autres choix contribuent à la maîtrise des traitements :

- matching déterministe dans l'API sans appel LLM pour chaque recommandation ;
- sélection des biens actifs avant scoring ;
- réutilisation de PostgreSQL pour les couches du projet ;
- orchestration Data par tâches plutôt qu'ajout systématique d'une plateforme de streaming ;
- technologies RAG, Kafka et plateformes supplémentaires différées selon la stratégie SI.

Sources complémentaires :

```text
../../../../src/api/services/recommendation.py
../../../../src/ai/matching/repository.py
../../../../pipelines/airflow/real_estate_ingestion_dag.py
../../01-BC01/C2-Strategie-SI/README.md
```

La preuve d'éco-conception porte ici sur les choix et les configurations. Un gain énergétique, carbone ou financier reste à mesurer sur un périmètre défini.

| Élément | Statut |
|---|---|
| Note éco-conception | PRINCIPES DOCUMENTÉS / NOTE AUTONOME À RATTACHER |
| Capacity Planning | DOCUMENTÉ |
| Data Lifecycle | DOCUMENTÉ |
| Resource efficiency principles | DOCUMENTÉS |
| Local AI strategy | DOCUMENTÉE |
| Technology rationalization | DOCUMENTÉE |
| Observability | DISPONIBLE |
| Actual consumption measurements | À CONSOLIDER |
| Before/after optimization evidence | À PRODUIRE |

---

# 75. Preuves à produire

Les preuves réelles pourront comprendre :

```text
01-resource-baseline.txt
02-kubernetes-resource-usage.txt
03-storage-usage.txt
04-container-image-sizes.txt
05-ai-gpu-measurements.txt
06-optimization-comparison.md
```

Elles ne doivent être créées qu'à partir de mesures réellement exécutées.

---

# 76. Exemple de mesure Kubernetes

Commande possible :

```bash
kubectl top nodes
```

et :

```bash
kubectl top pods -A
```

Les résultats réels peuvent ensuite être archivés comme preuves.

---

# 77. Exemple de mesure stockage

Exemples :

```bash
df -h
```

ou :

```bash
kubectl get pvc -A
```

selon le périmètre étudié.

---

# 78. Exemple de mesure images

```bash
docker images
```

ou les informations du registry peuvent permettre de comparer les tailles d'images.

---

# 79. Exemple AI

Un benchmark peut comparer :

```text
Model A
vs
Model B
```

selon :

```text
VRAM
Latency
Quality
```

L'objectif est de sélectionner le modèle le plus petit satisfaisant correctement le besoin.

---

# 80. Tableau d'amélioration

| Domaine | Mesure | Objectif |
|---|---|---|
| Kubernetes | CPU/RAM | Right-sizing |
| Containers | Image size | Réduire transfert/stockage |
| PostgreSQL | Query time | Réduire calcul |
| Airflow | Duration | Éviter retraitement |
| Logs | Volume | Maîtriser stockage |
| Metrics | Cardinality | Maîtriser ingestion |
| AI | VRAM/latency | Adapter le modèle |
| Storage | Growth | Retention |
| CI | Duration | Éviter calcul inutile |

---

# 81. Démarche d'amélioration continue

```text
Baseline
   |
   v
Measure
   |
   v
Identify
   |
   v
Optimize
   |
   v
Validate
   |
   v
Document
   |
   +----------+
   |          |
   +----------+
```

---

# 82. Ce qui ne constitue pas une preuve suffisante

Les affirmations suivantes seules ne suffisent pas :

```text
"We use Kubernetes"
"We use containers"
"We use local AI"
"We use open source"
```

Il faut démontrer le raisonnement et, lorsque possible, les mesures.

---

# 83. Limites actuelles

Le projet ne dispose pas encore nécessairement :

- d'un wattmètre ;
- de mesures électriques précises ;
- d'un PUE datacenter ;
- d'un calcul carbone complet ;
- d'une analyse de cycle de vie matériel.

Ces données ne doivent pas être inventées.

---

# 84. Niveau de preuve réaliste

Pour le projet, la preuve peut donc reposer sur :

```text
Architecture Decisions
+
Resource Measurements
+
Capacity Data
+
Optimization Tests
+
Lifecycle Policies
+
Documented Trade-offs
```

---

# 85. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Technical Choice
      |
      v
Resource Impact
      |
      v
Measurement
      |
      v
Optimization
      |
      v
Validation
```

---

# 86. État actuel

```text
Eco-design principles        COMPLETE
Architecture reasoning       COMPLETE
Technology rationalization   COMPLETE
Data lifecycle               COMPLETE
AI sobriety principles       COMPLETE
Capacity approach            COMPLETE
Observability capability     COMPLETE
Runtime resource baseline    TO COMPLETE
Optimization comparison      TO COMPLETE
Measured evidence            TO COMPLETE
```

---

# 87. Conclusion

L'approche d'éco-conception du projet repose sur :

```text
Use What Is Needed
        +
Reuse Existing Capacity
        +
Avoid Unnecessary Services
        +
Right-size Workloads
        +
Optimize Data Processing
        +
Control Retention
        +
Use AI Deliberately
        +
Measure Before Optimizing
```

Le principe directeur est :

```text
The most efficient workload
is the unnecessary workload
that is never executed.
```

L'objectif n'est donc pas de maximiser le nombre de technologies utilisées, mais de construire une plateforme qui fournisse la valeur attendue avec une consommation de ressources maîtrisée.

---

**BC03 / C3 — Environnement & Éco-conception : DOCUMENTATION BASELINE COMPLETE**
