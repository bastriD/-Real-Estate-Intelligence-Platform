# BC01 — C2 — Veille technologique

**Bloc de compétences :** BC01  
**Compétence :** C2 — Réaliser une veille technologique et contribuer aux choix d'architecture  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** En cours de constitution des preuves

---

# 1. Objectif

Ce dossier rassemble les preuves démontrant que les choix technologiques du projet résultent :

- d'une analyse du besoin ;
- d'une comparaison de solutions ;
- de critères techniques et organisationnels ;
- de contraintes d'infrastructure ;
- de contraintes de sécurité ;
- de contraintes de souveraineté ;
- de contraintes de coût et d'exploitation ;
- d'une décision documentée.

La démarche suivie est :

```text
Besoin
  |
  v
Contraintes
  |
  v
Solutions candidates
  |
  v
Comparaison
  |
  v
Décision
  |
  v
ADR
  |
  v
Implémentation
  |
  v
Réévaluation
```

---

# 2. Sources de preuve

Les principales sources du projet sont :

```text
../../../00-FOUNDATION/01-Architecture-Principles.md
../../../00-FOUNDATION/04-Architecture-Decisions.md
../../../00-FOUNDATION/05-Technology-Stack.md
../../../00-FOUNDATION/Architecture-Playbook.md

../../../95-GOVERNANCE/03-Decision-Governance.md
../../../95-GOVERNANCE/06-Technology-Governance.md
../../../95-GOVERNANCE/10-Architecture-Roadmap.md

../../../98-ADR/
```

Les décisions détaillées sont conservées dans les Architecture Decision Records.

---

# 3. Critères d'évaluation

Les technologies ne sont pas sélectionnées uniquement sur leurs fonctionnalités.

Les critères utilisés comprennent :

| Critère | Question |
|---|---|
| Fonctionnel | La solution répond-elle au besoin ? |
| Architecture | S'intègre-t-elle à la plateforme ? |
| Open source | Peut-elle être exploitée sans dépendance propriétaire forte ? |
| Kubernetes | Est-elle adaptée à Kubernetes ? |
| Automatisation | Peut-elle être gérée comme du code ? |
| Sécurité | Permet-elle un niveau de contrôle suffisant ? |
| Observabilité | Peut-elle être supervisée ? |
| Gouvernance | Peut-elle être intégrée à la gouvernance ? |
| Maintenabilité | Peut-elle être exploitée durablement ? |
| Communauté | Dispose-t-elle d'un écosystème viable ? |
| Documentation | La documentation est-elle suffisante ? |
| Coût | Quel est son coût d'exploitation ? |
| Complexité | Quel coût opérationnel introduit-elle ? |
| Souveraineté | Les données peuvent-elles rester locales ? |
| Réversibilité | Peut-elle être remplacée ? |
| Compétences | Est-elle cohérente avec les compétences disponibles ? |

---

# 4. Principe de sélection

Le projet applique le principe :

```text
Maximum Technology
       !=
Best Architecture
```

La cible recherchée est :

```text
Minimum Necessary Complexity
          +
Required Capability
          +
Maintainability
          +
Security
          +
Observability
          +
Governance
```

Une technologie supplémentaire doit résoudre un besoin identifiable.

---

# 5. Kubernetes

## Besoin

Disposer d'une plateforme permettant :

- l'orchestration de conteneurs ;
- le self-healing ;
- la standardisation des déploiements ;
- le scaling ;
- l'intégration GitOps ;
- l'hébergement de workloads Data et AI.

## Alternatives

```text
Docker Compose
Docker Swarm
Nomad
Kubernetes
Managed Kubernetes
```

## Décision

```text
Kubernetes
Status: ADOPTED
```

## Raisons principales

- standard cloud-native ;
- écosystème important ;
- déclaratif ;
- compatible GitOps ;
- adapté aux workloads Data / AI ;
- extensible ;
- portable.

Référence :

```text
../../../98-ADR/ADR-0001-Kubernetes.md
```

---

# 6. GitOps — Argo CD

## Besoin

Garantir que l'état Kubernetes puisse être :

- versionné ;
- reproduit ;
- audité ;
- réconcilié automatiquement.

## Alternatives

```text
kubectl manuel
Scripts de déploiement
GitLab CI direct deployment
Flux
Argo CD
```

## Décision

```text
Argo CD
Status: ADOPTED
```

## Justification

Le modèle recherché est :

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
Kubernetes
```

Cela réduit le drift et améliore la traçabilité.

Référence :

```text
../../../98-ADR/ADR-0002-ArgoCD-GitOps.md
```

---

# 7. CNI Kubernetes

## Solutions considérées

```text
Flannel
Calico
Cilium
```

## Décision actuelle

```text
Flannel
Status: ADOPTED
```

## Avantages

- simplicité ;
- faible complexité ;
- adapté aux besoins actuels ;
- fonctionnement éprouvé dans le cluster.

## Limites

Les besoins futurs de sécurité réseau pourraient justifier une réévaluation.

La décision actuelle ne signifie donc pas :

```text
Flannel forever
```

mais :

```text
Flannel
=
sufficient for current requirements
```

Référence :

```text
../../../98-ADR/ADR-0003-Flannel-CNI.md
```

---

# 8. Base de données

## Solutions possibles

```text
PostgreSQL
MySQL / MariaDB
MongoDB
Distributed databases
```

## Décision

```text
PostgreSQL
Status: ADOPTED
```

## Raisons

- ACID ;
- SQL mature ;
- extensions ;
- analytics ;
- intégration Python ;
- intégration Data ;
- possibilité de pgvector ;
- forte communauté ;
- administration connue.

Référence :

```text
../../../98-ADR/ADR-0005-PostgreSQL.md
```

---

# 9. Orchestration Data

## Solutions considérées

```text
Cron
Custom Python scheduler
Prefect
Dagster
Argo Workflows
Apache Airflow
```

## Décision

```text
Apache Airflow
Status: ADOPTED
```

## Justification

Airflow permet de représenter explicitement les dépendances :

```text
Extract
  |
  v
Transform
  |
  v
Validate
  |
  v
Load
```

Il dispose également d'un écosystème Data mature.

Référence :

```text
../../../98-ADR/ADR-0006-Airflow.md
```

---

# 10. Transformation Data

## Solutions

```text
SQL scripts
Python transformations
Stored procedures
dbt
```

## Décision

```text
dbt
Status: ADOPTED
```

## Principe

```text
Airflow
=
orchestration

dbt
=
SQL transformation
```

Cette séparation réduit le couplage entre orchestration et logique analytique.

---

# 11. Metadata et gouvernance Data

## Besoin

Disposer de :

- catalogue ;
- ownership ;
- lineage ;
- profiling ;
- glossary ;
- Data Quality ;
- gouvernance.

## Solutions possibles

```text
Documentation manuelle
DataHub
Apache Atlas
OpenMetadata
```

## Décision

```text
OpenMetadata
Status: ADOPTED
```

Référence :

```text
../../../98-ADR/ADR-0008-OpenMetadata.md
```

---

# 12. MLOps

## Besoin

Tracer :

- expériences ;
- paramètres ;
- métriques ;
- artifacts ;
- modèles ;
- versions.

## Solutions possibles

```text
Fichiers manuels
Custom database
Weights & Biases
Kubeflow
MLflow
```

## Décision

```text
MLflow
Status: ADOPTED
```

MLflow est utilisé pour le lifecycle ML.

Il n'est pas utilisé comme orchestrateur général.

```text
Airflow = workflow
MLflow  = ML lifecycle
```

Référence :

```text
../../../98-ADR/ADR-0007-MLflow.md
```

---

# 13. Local LLM

## Besoin

Exécuter des modèles IA avec :

- données locales ;
- contrôle de l'infrastructure ;
- coût maîtrisé ;
- souveraineté ;
- intégration API.

## Approches possibles

```text
Cloud AI API
Self-hosted inference server
Ollama
Dedicated inference framework
```

## Décision

```text
Ollama
Status: ADOPTED
```

avec actuellement :

```text
Qwen
```

## Facteur déterminant

La souveraineté des données.

```text
Enterprise Data
      |
      v
Local AI
```

est préféré à :

```text
Enterprise Data
      |
      v
External Provider
```

lorsque l'infrastructure locale permet de satisfaire le besoin.

Référence :

```text
../../../98-ADR/ADR-0009-Ollama-Local-AI.md
```

---

# 14. Vector Database

Ce cas démontre qu'une technologie étudiée n'est pas automatiquement adoptée.

## Besoin

Support futur pour :

- embeddings ;
- semantic search ;
- RAG.

## Candidats

```text
PostgreSQL + pgvector
Qdrant
```

## Statut

```text
pgvector = CANDIDATE
Qdrant   = CANDIDATE
```

Aucune base vectorielle dédiée n'est actuellement déclarée obligatoire.

## Critères de décision

- volume de vecteurs ;
- latence ;
- filtrage ;
- performance ;
- exploitation ;
- backup ;
- gouvernance ;
- empreinte Kubernetes ;
- complexité.

Principe :

```text
Existing PostgreSQL
       |
       v
Can satisfy requirement?
       |
   +---+---+
   |       |
  YES      NO
   |       |
   v       v
pgvector  Evaluate dedicated
          vector database
```

Cette décision reste ouverte jusqu'à l'obtention de besoins mesurables.

---

# 15. Kafka

Kafka constitue également un exemple de veille sans adoption automatique.

## Cas d'usage

Kafka peut apporter :

- streaming ;
- event log ;
- forte volumétrie ;
- plusieurs consommateurs ;
- architecture événementielle.

## Statut

```text
Kafka
=
FUTURE
```

La plateforme ne possède actuellement pas un besoin justifiant cette complexité.

Principe :

```text
No Streaming Requirement
        |
        v
     No Kafka
```

Un ADR sera nécessaire avant adoption.

---

# 16. Identity Management

## Besoin cible

- SSO ;
- OAuth 2.0 ;
- OpenID Connect ;
- fédération ;
- identité centralisée.

## Candidat cible

```text
Keycloak
Status: TARGET
```

Keycloak représente une direction architecturale mais ne doit pas être présenté comme déjà implémenté.

---

# 17. Secrets Management

## État actuel

```text
Kubernetes Secrets
+
GitLab Protected Variables
```

## Besoin futur

- rotation ;
- credentials dynamiques ;
- PKI ;
- secrets centralisés ;
- credentials temporaires.

## Technologie cible

```text
HashiCorp Vault
Status: TARGET
```

L'introduction de Vault doit être justifiée par l'évolution du niveau de maturité et des besoins de sécurité.

---

# 18. Observabilité

## Technologies sélectionnées

```text
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
Alertmanager
```

## Architecture

```text
Metrics ---> Prometheus ---+
                           |
Logs -----> Loki ----------+---> Grafana
                           |
Traces ---> Tempo ---------+
             ^
             |
       OpenTelemetry
```

Cette sélection permet une stack majoritairement open source et intégrée à Kubernetes.

Références :

```text
../../../98-ADR/ADR-0010-Prometheus-Grafana.md
../../../98-ADR/ADR-0011-Loki-Tempo-OpenTelemetry.md
```

---

# 19. Diagrammes d'architecture

## Solutions possibles

```text
Draw.io
Mermaid
PlantUML
Manual diagrams
```

## Décision

```text
PlantUML
Status: ADOPTED
```

## Justification

PlantUML permet :

- version control ;
- diff ;
- génération automatique ;
- documentation as code ;
- reproductibilité.

```text
*.puml
   |
   v
PlantUML
   |
   v
*.svg
```

Les sources `.puml` constituent la source de vérité des diagrammes.

---

# 20. Synthèse des choix

| Besoin | Solution | Statut |
|---|---|---|
| Orchestration | Kubernetes | ADOPTED |
| GitOps | Argo CD | ADOPTED |
| Database | PostgreSQL | ADOPTED |
| Workflow | Airflow | ADOPTED |
| Transformation | dbt | ADOPTED |
| Metadata | OpenMetadata | ADOPTED |
| ML Lifecycle | MLflow | ADOPTED |
| Local AI | Ollama / Qwen | ADOPTED |
| Metrics | Prometheus | ADOPTED |
| Dashboards | Grafana | ADOPTED |
| Logs | Loki | ADOPTED |
| Traces | Tempo | ADOPTED |
| Diagram as Code | PlantUML | ADOPTED |
| Enterprise IAM | Keycloak | TARGET |
| Enterprise Secrets | Vault | TARGET |
| Vector Search | pgvector / Qdrant | CANDIDATE |
| Event Streaming | Kafka | FUTURE |

---

# 21. Veille continue

La veille technologique n'est pas considérée comme une activité ponctuelle.

Le cycle retenu est :

```text
Observe
  |
  v
Identify Requirement
  |
  v
Research
  |
  v
Compare
  |
  v
Prototype if necessary
  |
  v
Decide
  |
  v
ADR
  |
  v
Implement
  |
  v
Measure
  |
  +---------> Re-evaluate
```

---

# 22. Sources de veille à documenter

Pour la preuve finale, les sources réellement utilisées doivent être conservées.

Catégories pertinentes :

- documentation officielle ;
- release notes ;
- CNCF ;
- CVE / security advisories ;
- GitHub releases ;
- documentation Kubernetes ;
- documentation PostgreSQL ;
- documentation Airflow ;
- documentation MLflow ;
- documentation OpenMetadata ;
- documentation Ollama ;
- retours d'expérience techniques.

Une source doit être reliée à une décision ou à une analyse.

Accumuler des liens sans exploitation ne constitue pas une veille démontrée.

---

# 23. Preuves à ajouter

Les preuves futures pourront inclure :

```text
01-technology-comparison.md
02-source-register.md
03-pgvector-vs-qdrant.md
04-cni-comparison.md
05-workflow-orchestrators.md
06-ai-inference-comparison.md
```

Elles doivent être créées uniquement lorsqu'elles apportent une preuve utile.

---

# 24. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Requirement
    |
    v
Research
    |
    v
Alternatives
    |
    v
Comparison
    |
    v
Decision
    |
    v
ADR
```

et comprendre pourquoi une technologie a été :

```text
ADOPTED
TARGETED
REJECTED
or
DEFERRED
```

---

# 25. Statut actuel

| Élément | Statut |
|---|---|
| Critères de sélection | DOCUMENTÉ |
| Technologies principales | DOCUMENTÉES |
| Alternatives | DOCUMENTÉES |
| Architecture Decisions | DISPONIBLES |
| ADR | DISPONIBLES |
| Technologies candidates | IDENTIFIÉES |
| Technologies futures | IDENTIFIÉES |
| Registre formel des sources de veille | À COMPLÉTER |
| Comparaison chiffrée pgvector / Qdrant | À FAIRE SI NÉCESSAIRE |
| Preuves de PoC comparatifs | À COMPLÉTER SELON BESOIN |

---

# 26. Conclusion

La démarche technologique du projet repose sur :

```text
Requirements
     +
Comparison
     +
Architecture Principles
     +
Operational Constraints
     +
Security
     +
Governance
     |
     v
Documented Decision
```

La veille technologique sert à **réduire l'incertitude architecturale**, et non à multiplier les technologies.

---

**BC01 / C2 — Veille technologique : DOCUMENTATION BASELINE COMPLETE**