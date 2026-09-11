# BC03 — C4 — Patterns d'architecture

**Bloc de compétences :** BC03  
**Compétence :** C4 — Identifier, justifier et appliquer des patterns d'architecture adaptés  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Baseline documentaire — preuves d'implémentation à consolider

---

# 1. Objectif

Ce dossier démontre que les choix de conception applicative reposent sur des patterns identifiables et justifiés.

L'objectif n'est pas d'utiliser le plus grand nombre de patterns possible.

Le principe est :

```text
Business / Technical Problem
        |
        v
Architecture Constraint
        |
        v
Suitable Pattern
        |
        v
Implementation
        |
        v
Validation
```

Un pattern doit résoudre un problème réel.

---

# 2. Sources de référence

Documents principaux :

```text
../../../20-APPLICATION/01-Application-Architecture.md
../../../00-FOUNDATION/01-Architecture-Principles.md
../../../00-FOUNDATION/04-Architecture-Decisions.md
../../../00-FOUNDATION/Architecture-Playbook.md
```

Documents complémentaires :

```text
../../../40-DATA/01-Data-Architecture.md
../../../50-AI/01-AI-Platform-Architecture.md
../../../70-DEVOPS/01-DevOps-Architecture.md
../../../70-DEVOPS/02-GitOps-Architecture.md
```

Diagrammes :

```text
../../../99-DIAGRAMS/06-Application-Architecture.puml
../../../99-DIAGRAMS/07-Data-Architecture.puml
../../../99-DIAGRAMS/08-AI-Architecture.puml
../../../99-DIAGRAMS/10-DevOps-GitOps-Architecture.puml
```

---

# 3. Principe général

Les patterns utilisés doivent améliorer :

- séparation des responsabilités ;
- testabilité ;
- maintenabilité ;
- résilience ;
- sécurité ;
- lisibilité ;
- évolutivité ;
- traçabilité.

Ils ne doivent pas devenir une source de complexité inutile.

---

# 4. Pattern — Layered Architecture

Le backend suit une séparation en couches.

```text
Presentation / API
       |
       v
Business Logic
       |
       v
Service Layer
       |
       v
Data Access
       |
       v
Persistence
```

Cette architecture réduit le couplage entre :

- HTTP ;
- logique métier ;
- persistence.

---

# 5. Justification

Sans séparation :

```text
Route
 |
 +-- Validation
 +-- Business Logic
 +-- SQL
 +-- Logging
 +-- External Calls
```

la maintenance devient difficile.

Avec séparation :

```text
Route
 |
 v
Service
 |
 v
Repository
```

les responsabilités deviennent explicites.

---

# 6. Pattern — Service Layer

La couche service porte la logique d'orchestration métier.

Exemple :

```text
API
 |
 v
PropertyService
 |
 +-- Repository
 +-- Analytics
 +-- AI Client
```

Elle évite d'implémenter toute la logique dans les endpoints HTTP.

---

# 7. Exemple conceptuel

```python
class PropertyService:
    def __init__(self, repository):
        self.repository = repository

    def get_property(self, property_id):
        return self.repository.get_by_id(property_id)
```

La structure exacte dépendra de l'application finale.

---

# 8. Pattern — Repository

Le Repository encapsule l'accès aux données.

```text
Business Service
      |
      v
Repository
      |
      v
PostgreSQL
```

Il permet de séparer :

```text
Business Logic
```

de :

```text
SQL / ORM
```

---

# 9. Avantages Repository

- testabilité ;
- remplacement de l'accès données ;
- centralisation des requêtes ;
- réduction du SQL dispersé ;
- responsabilité claire.

---

# 10. Limites Repository

Un Repository inutilement générique peut devenir une abstraction coûteuse.

Le pattern doit rester simple.

Exemple à éviter :

```text
GenericRepositoryFactoryManagerProvider
```

sans besoin démontré.

---

# 11. Pattern — Dependency Injection

Les dépendances peuvent être injectées plutôt que créées directement dans la logique métier.

Exemple conceptuel :

```text
FastAPI
 |
 v
Dependency Provider
 |
 +-- Database Session
 +-- Service
 +-- Authentication Context
```

Cela améliore :

- testabilité ;
- configuration ;
- découplage.

---

# 12. Exemple FastAPI

```python
from fastapi import Depends

def get_service():
    return PropertyService(...)

@app.get("/properties/{property_id}")
def get_property(
    property_id: int,
    service: PropertyService = Depends(get_service),
):
    return service.get_property(property_id)
```

L'exemple illustre le pattern, pas nécessairement le code final.

---

# 13. Pattern — API-first

L'application expose ses fonctionnalités via une API clairement définie.

```text
Frontend
   |
   v
API Contract
   |
   v
Backend
```

Avantages :

- découplage frontend/backend ;
- automatisation ;
- intégration ;
- documentation OpenAPI ;
- tests API.

---

# 14. Pattern — DTO / Schema

Les objets exposés par API ne doivent pas nécessairement refléter directement le modèle de persistence.

```text
Database Entity
      |
      v
Mapping
      |
      v
API Schema
```

Pydantic peut servir à cette séparation.

---

# 15. Avantage

Cela évite d'exposer :

- colonnes internes ;
- champs sensibles ;
- structures techniques ;
- détails de persistence.

---

# 16. Pattern — Configuration externe

La configuration est séparée du code.

```text
Application
   |
   +-- Environment Variables
   +-- ConfigMap
   +-- Secret
```

Le même artifact peut être déployé dans plusieurs environnements avec des configurations différentes.

---

# 17. Anti-pattern — Hardcoded Configuration

Exemple à éviter :

```python
DB_PASSWORD = "password123"
```

ou :

```python
DB_HOST = "192.168.1.20"
```

si ces valeurs dépendent de l'environnement.

---

# 18. Pattern — Secrets Externalization

Les secrets sont séparés de :

- code ;
- Git ;
- image container.

État actuel :

```text
Kubernetes Secrets
GitLab Protected Variables
```

État cible possible :

```text
Vault
```

---

# 19. Pattern — Health Check

Les applications exposent des endpoints de santé.

```text
Kubernetes
    |
    v
Health Endpoint
    |
    v
Application Status
```

Cela supporte :

- readiness ;
- liveness ;
- monitoring.

---

# 20. Pattern — Retry

Certains appels temporaires peuvent être retentés.

Exemple :

```text
Request
 |
 v
Temporary Failure
 |
 v
Retry
```

Le retry doit être :

- limité ;
- observable ;
- appliqué uniquement aux erreurs appropriées.

---

# 21. Anti-pattern — Infinite Retry

```text
Failure
 |
 v
Retry
 |
 v
Retry
 |
 v
Retry forever
```

peut augmenter :

- charge ;
- latence ;
- consommation ;
- saturation.

---

# 22. Pattern — Timeout

Les appels externes ou AI doivent avoir un timeout.

```text
Application
    |
    v
External Service
```

ne doit pas attendre indéfiniment.

---

# 23. Pattern — Graceful Degradation

Pour les capacités non critiques :

```text
AI Available?
 +----+----+
 |         |
YES        NO
 |         |
 v         v
AI feature Core service remains available
```

Ce pattern réduit le couplage aux services AI.

---

# 24. Pattern — Circuit Breaker

Un circuit breaker peut être envisagé pour des dépendances instables.

```text
Application
   |
   v
Circuit Breaker
   |
   v
External Service
```

États conceptuels :

```text
CLOSED
OPEN
HALF-OPEN
```

Ce pattern reste à introduire uniquement lorsqu'un besoin réel le justifie.

---

# 25. Pattern — Idempotency

Les opérations répétables doivent éviter des effets secondaires multiples.

Exemple :

```text
Retry same request
      |
      v
Same business outcome
```

Particulièrement important pour :

- ingestion ;
- jobs ;
- API de création sensibles ;
- GitOps ;
- scripts de gouvernance.

---

# 26. Pattern — Stateless Service

Les services applicatifs doivent rester stateless lorsque possible.

```text
Request
 |
 v
Any Replica
```

L'état persistant reste dans :

```text
Database
Object Storage
External State Service
```

Cela facilite le scaling Kubernetes.

---

# 27. Pattern — Containerized Application

L'application est packagée dans une image.

```text
Source
 |
 v
Container Image
 |
 v
Kubernetes
```

Cela améliore :

- reproductibilité ;
- portabilité ;
- CI/CD.

---

# 28. Pattern — GitOps

GitOps est un pattern d'exploitation transversal.

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
Runtime
```

Il apporte :

- auditabilité ;
- reconciliation ;
- rollback ;
- version control.

---

# 29. Pattern — Infrastructure as Code

L'infrastructure doit progressivement être représentée par du code.

```text
Terraform
Ansible
Kubernetes YAML
Helm
```

L'objectif est :

```text
Reproducible Infrastructure
```

---

# 30. Pattern — Observability by Design

L'observabilité est intégrée dans la conception.

```text
Application
 |
 +-- Metrics
 +-- Logs
 +-- Traces
 +-- Health
```

et non ajoutée uniquement après incident.

---

# 31. Pattern — Correlation ID

Les requêtes peuvent disposer d'un identifiant de corrélation.

```text
Client
 |
 v
request_id
 |
 v
API
 |
 v
Logs / Trace
```

Cela facilite le diagnostic.

---

# 32. Pattern — Structured Logging

Les logs utilisent idéalement une structure stable.

Exemple :

```json
{
  "timestamp": "...",
  "level": "INFO",
  "service": "api",
  "request_id": "...",
  "message": "request completed"
}
```

---

# 33. Pattern — Retry + Backoff

Lorsqu'un retry est utilisé :

```text
Attempt 1
 |
 wait
 |
Attempt 2
 |
 longer wait
 |
Attempt 3
```

réduit le risque de surcharge immédiate.

---

# 34. Pattern — Data Layering

La Data Platform applique un pattern de couches.

```text
RAW
 |
 v
STAGING
 |
 v
WAREHOUSE
 |
 v
ANALYTICS
```

Chaque couche possède une responsabilité distincte.

---

# 35. Pattern — ELT

Une partie du traitement suit :

```text
Extract
  |
  v
Load
  |
  v
Transform
```

avec :

```text
Airflow
+
PostgreSQL
+
dbt
```

---

# 36. Pattern — Orchestrator + Transformation Engine

Séparation :

```text
Airflow
=
Orchestration

dbt
=
Transformation
```

Ce pattern évite de mettre toute la logique SQL dans les DAGs.

---

# 37. Pattern — Data Quality Gate

```text
Transform
   |
   v
Quality Check
   |
 +--+--+
 |     |
PASS  FAIL
 |     |
 v     v
Publish Stop / Alert
```

---

# 38. Pattern — Metadata Catalog

```text
Data Systems
   |
   v
Metadata Ingestion
   |
   v
OpenMetadata
```

Le catalogue devient un point central de découverte et de gouvernance.

---

# 39. Pattern — Model Registry

MLflow fournit :

```text
Training
  |
  v
Experiment
  |
  v
Candidate Model
  |
  v
Registry
  |
  v
Deployment
```

---

# 40. Pattern — External Artifact Store

Séparation :

```text
MLflow Metadata
     |
     v
Database

MLflow Artifacts
     |
     v
MinIO
```

---

# 41. Pattern — Local AI Gateway

Le backend ne doit idéalement pas dépendre directement de détails spécifiques du modèle.

```text
Application
    |
    v
AI Interface
    |
    v
Ollama
    |
    v
Qwen
```

Cela facilite le remplacement futur du modèle.

---

# 42. Pattern — RAG

```text
Question
 |
 v
Retriever
 |
 v
Relevant Context
 |
 v
LLM
 |
 v
Answer
```

Le LLM reçoit uniquement le contexte utile.

---

# 43. Pattern — Human in the Loop

Pour certaines décisions AI :

```text
AI Output
   |
   v
Human Review
   |
 +--+--+
 |     |
Accept Reject
```

---

# 44. Pattern — Policy as Code

```text
Policy
 |
 v
Git
 |
 v
Validation
 |
 v
Enforcement
```

La politique devient versionnable et contrôlable.

---

# 45. Pattern — Governance as Code

```text
Governance Requirement
      |
      v
Machine-readable Definition
      |
      v
Git
      |
      v
Automation
      |
      v
Runtime Governance State
```

---

# 46. Pattern — Backup / Restore Validation

```text
Backup
 |
 v
Restore
 |
 v
Validate
```

Un backup non restauré ne constitue pas une preuve suffisante.

---

# 47. Pattern — Bulkhead / Isolation

Les services critiques peuvent être séparés des services lourds ou moins critiques.

Exemple :

```text
Core API
   |
   +--> Database

AI Workload
   |
   +--> GPU Host
```

Une saturation AI ne doit pas nécessairement entraîner l'indisponibilité de l'application principale.

---

# 48. Pattern — CQRS

CQRS sépare :

```text
Commands
```

et :

```text
Queries
```

Ce pattern **n'est pas actuellement adopté** comme besoin général.

Il pourrait être étudié si la complexité métier l'exige.

---

# 49. Pattern — Event-driven Architecture

Architecture possible :

```text
Producer
 |
 v
Event Broker
 |
 +--> Consumer A
 +--> Consumer B
```

Kafka pourrait soutenir ce pattern.

Mais :

```text
Kafka = FUTURE
```

car aucun besoin actuel ne justifie encore cette complexité.

---

# 50. Pattern — Microservices

Les microservices ne sont pas une obligation architecturale.

Principe :

```text
Split Service
only when
there is a clear boundary or scaling need.
```

Un monolithe modulaire peut être préférable pour certains périmètres.

---

# 51. Modular Monolith

Pattern possible pour l'application métier :

```text
Application
 |
 +-- Search Module
 +-- Analytics Module
 +-- Document Module
 +-- AI Integration Module
```

tout en partageant :

```text
single deployment
```

si cela réduit la complexité.

---

# 52. Pourquoi éviter les microservices prématurés

Ils introduisent :

- réseau ;
- discovery ;
- tracing ;
- retries ;
- distributed failures ;
- deployment complexity.

Sans bénéfice métier clair, cela peut être contre-productif.

---

# 53. Pattern — Adapter

Un Adapter permet d'isoler une intégration externe.

Exemple :

```text
Application
    |
    v
AIAdapter
    |
    v
Ollama
```

Si le moteur change :

```text
AIAdapter
    |
    v
Another Provider
```

la logique métier reste plus stable.

---

# 54. Pattern — Facade

Une Facade peut simplifier l'accès à plusieurs sous-services.

```text
Business API
    |
    v
SearchFacade
    |
    +-- Repository
    +-- Analytics
    +-- Metadata
```

À utiliser seulement lorsque cela améliore réellement la lisibilité.

---

# 55. Pattern — Strategy

Pour plusieurs stratégies possibles :

```text
VectorSearchStrategy
    |
    +-- PgVectorStrategy
    +-- QdrantStrategy
```

Cela pourrait permettre une comparaison future sans couplage fort.

Ce pattern reste conceptuel tant que le besoin n'est pas implémenté.

---

# 56. Pattern — Factory

Une factory peut être utile lorsque plusieurs implémentations doivent être instanciées selon la configuration.

Elle ne doit pas être utilisée pour des objets simples sans variation réelle.

---

# 57. Pattern — Mapper

Permet de transformer :

```text
Database Model
      |
      v
Domain Model
      |
      v
API Schema
```

lorsque les modèles doivent rester distincts.

---

# 58. Pattern — Pagination

```text
Large Collection
      |
      v
Page / Limit
      |
      v
Partial Result
```

Évite de charger inutilement de grandes collections.

---

# 59. Pattern — Cache-aside

Si Redis devient nécessaire :

```text
Application
 |
 v
Cache
 +---+
 |   |
Hit Miss
 |   |
 v   v
Return DB
       |
       v
      Cache
```

Redis reste :

```text
TARGET
```

et non dépendance obligatoire.

---

# 60. Pattern — Secure by Default

La configuration par défaut doit tendre vers :

```text
Denied
until
explicitly allowed
```

lorsque cela est applicable.

---

# 61. Pattern — Least Privilege

```text
Identity
 |
 v
Minimum Required Permission
```

s'applique à :

- users ;
- service accounts ;
- database accounts ;
- CI runners ;
- Kubernetes RBAC.

---

# 62. Pattern — Defense in Depth

```text
Identity
 |
 v
Network
 |
 v
Runtime
 |
 v
Application
 |
 v
Data
 |
 v
Monitoring
```

Aucun contrôle unique ne protège l'ensemble du système.

---

# 63. Anti-patterns identifiés

Le projet cherche à éviter :

```text
God Object
Fat Controller
Hardcoded Secrets
Manual Drift
Shared Root Credentials
Infinite Retry
Technology for Technology's Sake
Premature Microservices
Unbounded Logging
Unbounded Data Retention
```

---

# 64. Exemple — Fat Controller

À éviter :

```python
@app.post("/search")
def search():
    # authentication
    # validation
    # SQL
    # AI
    # formatting
    # logging
    # business rules
    ...
```

Préférer :

```text
Controller
 |
 v
Service
 |
 +-- Repository
 +-- AI Adapter
```

---

# 65. Pattern selection criteria

Avant adoption d'un pattern :

```text
What problem does it solve?
What complexity does it add?
Is the problem currently real?
Can a simpler approach solve it?
How will it be tested?
```

---

# 66. Pattern → besoin

| Pattern | Besoin |
|---|---|
| Layered Architecture | Separation of concerns |
| Service Layer | Business orchestration |
| Repository | Persistence isolation |
| DI | Testability |
| Adapter | External integration isolation |
| GitOps | Desired-state reconciliation |
| RAG | Contextual AI |
| Data Layering | Data lifecycle separation |
| Registry | Model lifecycle |
| Policy as Code | Automated control |
| Graceful Degradation | Dependency resilience |

---

# 67. Pattern → preuve

| Pattern | Preuve possible |
|---|---|
| Layered | Source tree |
| Repository | Repository classes |
| DI | FastAPI dependencies |
| API-first | OpenAPI |
| GitOps | Argo CD reconciliation |
| Data layering | PostgreSQL schemas |
| Model registry | MLflow |
| RAG | Retrieval test |
| Policy as Code | CI / runtime policy |
| Graceful degradation | Failure test |

---

# 68. Architecture actuelle vs pattern cible

Tous les patterns documentés ne sont pas nécessairement déjà implémentés.

Statuts possibles :

```text
IMPLEMENTED
TARGET
CANDIDATE
NOT REQUIRED
```

Le statut doit être explicite.

---

# 69. Patterns actuellement fortement établis

```text
GitOps
Containerization
Kubernetes orchestration
Data layering
Workflow orchestration
Metadata catalog
ML lifecycle registry
Observability by design
Documentation as Code
Diagrams as Code
Governance as Code
```

---

# 70. Patterns applicatifs à prouver dans le code final

## Patterns observables dans le backend

| Pattern | Problème traité | Implémentation depuis la racine |
|---|---|---|
| Architecture en couches | Séparer HTTP, règles et persistence | `src/api/api/`, `services/`, `repositories/`, `db/` |
| Service Layer | Porter les règles de création, modification et recommandation | `src/api/services/` |
| Repository | Isoler les accès aux entités | `src/api/repositories/` |
| Dependency Injection | Fournir session, utilisateur et services aux routes | Dépendances FastAPI dans `src/api/core/dependencies.py` et les endpoints |
| Validation de schémas | Contrôler les entrées et les réponses | `src/api/schemas/` |
| Audit transactionnel | Relier mutation et audit avant commit | `src/api/services/visite.py`, `presentation.py`, `recommendation.py` |
| Health Checks | Distinguer santé et préparation du service | `src/api/api/v1/endpoints/health.py` |

Les tests de services et d'API montrent l'intérêt du découplage : ils remplacent les dépendances externes pour vérifier les règles et les erreurs. Ils ne constituent pas une preuve d'intégration PostgreSQL complète.

```text
../C6-Tests-Executes/visite-audit-2026-09-09/README.md
../../../60-SECURITY/RECOMMENDATION-AUDIT-RUNTIME-EVIDENCE.md
```

Les patterns Adapter généralisé, journalisation structurée complète et dégradation automatique d'un service LLM restent à démontrer selon leur implémentation effective.

Rappel du périmètre applicatif :

```text
Layered Architecture
Service Layer
Repository
Dependency Injection
Schema Validation
Adapter
Health Checks
Structured Logging
```

---

# 71. Preuves attendues

Les preuves pourront inclure :

```text
source tree
Python modules
FastAPI routes
services
repositories
schemas
tests
OpenAPI
Dockerfile
CI output
```

---

# 72. Exemple de structure cible

La structure réelle du backend est :

```text
src/api/
├── main.py
├── api/v1/endpoints/
├── core/
├── db/models/
├── observability/
├── repositories/
├── schemas/
└── services/
```

L'exemple ci-dessous décrit seulement une organisation générique comparable :

```text
app/
├── main.py
├── api/
│   └── routes/
├── services/
├── repositories/
├── schemas/
├── models/
├── clients/
├── config/
└── tests/
```

La structure finale doit refléter le code réel.

---

# 73. Traceabilité

```text
Problem
 |
 v
Pattern
 |
 v
Code
 |
 v
Test
 |
 v
Evidence
```

---

# 74. Critère de réussite

La compétence est démontrée si le jury peut répondre à :

```text
Which architectural patterns were used?
Why?
Where are they implemented?
What problem do they solve?
How were they validated?
```

---

# 75. État actuel

| Élément | Statut |
|---|---|
| Architecture patterns identified | COMPLETE |
| GitOps pattern | IMPLEMENTED |
| Data layering | IMPLEMENTED |
| Registry pattern | IMPLEMENTED |
| Observability pattern | IMPLEMENTED |
| Governance as Code | IMPLEMENTED / EVOLVING |
| Application layered pattern | IMPLEMENTED — `src/api/` |
| Repository pattern | IMPLEMENTED — `src/api/repositories/` |
| DI | IMPLEMENTED — FASTAPI DEPENDENCIES |
| Adapter pattern | TARGET |
| Graceful degradation | TO TEST |
| Pattern runtime evidence | TO CONSOLIDATE |

---

# 76. Conclusion

Les patterns du projet sont sélectionnés selon :

```text
Problem
+
Context
+
Trade-off
```

et non selon :

```text
Pattern Popularity
```

Le principe directeur est :

```text
Use the simplest pattern
that creates a meaningful improvement
in maintainability, security,
testability or reliability.
```

---

**BC03 / C4 — Patterns d'architecture : DOCUMENTATION BASELINE COMPLETE**
