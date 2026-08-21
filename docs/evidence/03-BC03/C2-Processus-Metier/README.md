# BC03 — C2 — Processus métier applicatifs

**Bloc de compétences :** BC03  
**Compétence :** C2 — Traduire les processus métier en flux applicatifs exploitables  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Baseline documentaire — scénarios métier finaux à aligner avec l'application réellement implémentée

---

# 1. Objectif

Ce dossier démontre la capacité à transformer un besoin métier en processus applicatif.

Le chemin attendu est :

```text
Business Need
      |
      v
Business Process
      |
      v
Use Case
      |
      v
Application Flow
      |
      v
API / Data / AI
      |
      v
Result
      |
      v
Business Validation
```

La modélisation doit rester orientée utilisateur et métier.

---

# 2. Sources de référence

Documents métier :

```text
../../../10-BUSINESS/01-Business-Architecture.md
```

Architecture applicative :

```text
../../../20-APPLICATION/01-Application-Architecture.md
```

Architecture Data :

```text
../../../40-DATA/01-Data-Architecture.md
../../../40-DATA/02-Data-Model.md
```

Architecture AI :

```text
../../../50-AI/01-AI-Platform-Architecture.md
../../../50-AI/04-RAG-Architecture.md
```

Diagrammes :

```text
../../../99-DIAGRAMS/01-Enterprise-Context.puml
../../../99-DIAGRAMS/06-Application-Architecture.puml
../../../99-DIAGRAMS/07-Data-Architecture.puml
../../../99-DIAGRAMS/08-AI-Architecture.puml
```

---

# 3. Principe de traduction métier → application

Un besoin ne devient pas directement un composant technique.

Le modèle est :

```text
Need
 |
 v
Use Case
 |
 v
Process
 |
 v
Application Service
 |
 v
Technical Components
```

Exemple :

```text
Need:
Trouver rapidement une information immobilière consolidée

        |
        v

Use Case:
Search Property

        |
        v

Application Flow:
Search Form -> API -> Database -> Results

        |
        v

Technical:
FastAPI + PostgreSQL
```

---

# 4. Acteurs applicatifs

Les principaux acteurs possibles sont :

```text
Business User
Analyst
Administrator
Application Service
Data Platform
AI Service
```

Les rôles doivent être adaptés à l'application réellement implémentée.

---

# 5. Cas d'usage principal — Recherche

## Objectif

Permettre à un utilisateur de rechercher une information métier selon plusieurs critères.

Flux :

```text
User
 |
 v
Search Interface
 |
 v
Input Validation
 |
 v
Search API
 |
 v
Query Service
 |
 v
PostgreSQL
 |
 v
Results
 |
 v
User
```

---

# 6. Entrées de recherche

Exemples possibles :

```text
City
Property Type
Price
Surface
Identifier
Keyword
```

Les critères exacts doivent correspondre au modèle de données final.

---

# 7. Validation de recherche

Le processus comprend :

```text
Input
 |
 v
Valid?
 +---+---+
 |       |
YES      NO
 |       |
 v       v
Query    Validation Error
```

Le backend doit être responsable de la validation réelle.

---

# 8. Résultat de recherche

Le résultat doit fournir uniquement les informations nécessaires à l'utilisateur.

Exemple :

```text
Property ID
Title
Location
Price
Surface
Source
Status
```

Les champs réels doivent correspondre à l'application finale.

---

# 9. Cas d'usage — Consultation détaillée

Flux :

```text
Search Result
     |
     v
Select Item
     |
     v
GET Detail
     |
     v
Business Service
     |
     v
Database
     |
     v
Detailed View
```

---

# 10. Données détaillées

Une fiche peut agréger plusieurs catégories :

```text
Core Information
Analytics
Documents
Metadata
AI Assistance
```

La vue utilisateur ne doit pas exposer inutilement les détails techniques de stockage.

---

# 11. Cas d'usage — Analyse

Un utilisateur peut vouloir analyser une opportunité.

Flux cible :

```text
Business Object
      |
      v
Retrieve Data
      |
      v
Compute Indicators
      |
      v
Business Rules
      |
      v
Display Analysis
```

Support possible :

```text
PostgreSQL analytics
dbt models
Business API
```

---

# 12. Cas d'usage — Dashboard

Flux :

```text
User
 |
 v
Dashboard
 |
 v
Analytics API
 |
 v
Analytics Views
 |
 v
KPI
 |
 v
Visualization
```

Les KPI doivent être issus de règles métier documentées.

---

# 13. Cas d'usage — Document

Lorsqu'un processus implique un document :

```text
Document
  |
  v
Upload / Acquire
  |
  v
Validation
  |
  v
Storage
  |
  v
Metadata
  |
  v
Search / Analysis
```

Les documents sensibles doivent rester soumis aux contrôles d'accès.

---

# 14. Cas d'usage — AI Assistance

Flux :

```text
User
 |
 v
Question
 |
 v
Business API
 |
 v
AI Integration
 |
 v
AI Service
 |
 v
Ollama
 |
 v
Qwen
 |
 v
Response
```

L'AI doit rester intégrée comme un service et non comme une dépendance incontrôlée.

---

# 15. Cas d'usage — RAG

Flux cible :

```text
User
 |
 v
Question
 |
 v
Authentication / Authorization
 |
 v
Retriever
 |
 v
Authorized Knowledge
 |
 v
Context
 |
 v
Ollama / Qwen
 |
 v
Response
 |
 v
Sources
```

---

# 16. Contrôle d'autorisation RAG

Le modèle correct est :

```text
User permissions
      |
      v
Filter accessible documents
      |
      v
Retrieval
```

et non :

```text
Retrieve all
then
hope the LLM hides sensitive data
```

---

# 17. Cas d'usage — Administration

Fonctions possibles :

```text
Manage Reference Data
Manage Users
Manage Configuration
Review Metadata
Review AI Assets
```

Les fonctions réellement implémentées doivent être distinguées des fonctions cible.

---

# 18. Processus d'authentification

Architecture cible :

```text
User
 |
 v
Authentication
 |
 v
Identity
 |
 v
Token / Session
 |
 v
Application
```

Keycloak reste une technologie TARGET jusqu'à son implémentation.

---

# 19. Processus d'autorisation

```text
Authenticated User
       |
       v
Requested Action
       |
       v
Authorized?
 +-----+-----+
 |           |
YES          NO
 |           |
 v           v
Execute     403
```

---

# 20. Processus d'erreur

Les erreurs doivent suivre un comportement prévisible.

```text
Request
  |
  v
Error?
 +--+--+
 |     |
NO    YES
 |     |
 v     v
Result Error Response
```

Les erreurs ne doivent pas révéler :

- secrets ;
- stack traces sensibles ;
- credentials ;
- données privées.

---

# 21. Processus de santé applicative

```text
Monitoring
   |
   v
GET /health
   |
   v
Application
   |
   v
Dependency Status
   |
   v
Health Result
```

---

# 22. Processus de journalisation

```text
Request
 |
 v
Application
 |
 v
Structured Log
 |
 v
Loki
 |
 v
Grafana
```

---

# 23. Processus de tracing

```text
Ingress
  |
  v
API
  |
  v
Database
  |
  v
AI Service
```

Le même `trace_id` peut relier les étapes lorsque l'instrumentation le permet.

---

# 24. Processus de déploiement

```text
Developer
  |
  v
Commit
  |
  v
GitLab
  |
  v
CI
  |
  v
Build
  |
  v
GitOps Change
  |
  v
Argo CD
  |
  v
Kubernetes
```

---

# 25. Processus de rollback

```text
Regression
  |
  v
Identify Previous Version
  |
  v
Git Revert / Version Change
  |
  v
Argo CD
  |
  v
Runtime Reconciliation
```

---

# 26. Processus Data derrière l'application

```text
Source
  |
  v
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
  |
  v
Application API
```

Cela permet de séparer le processus de préparation des données du processus de consultation utilisateur.

---

# 27. Processus Data Quality

```text
Data
 |
 v
Quality Test
 |
 +---+---+
 |       |
PASS    FAIL
 |       |
 v       v
Consume Investigate
```

Une donnée invalide peut devoir être bloquée avant consommation applicative.

---

# 28. Processus Metadata

```text
Data Asset
 |
 v
OpenMetadata
 |
 +-- Ownership
 +-- Classification
 +-- Lineage
 +-- Profile
 +-- Quality
```

Ces informations peuvent soutenir les décisions applicatives et de gouvernance.

---

# 29. Processus AI gouverné

```text
AI Request
   |
   v
Risk / Data Context
   |
   v
Allowed?
 +--+--+
 |     |
YES    NO
 |     |
 v     v
Execute Reject / Review
```

---

# 30. Human in the loop

Certaines décisions doivent rester humaines.

Exemple :

```text
AI Recommendation
      |
      v
Business User
      |
      v
Validate / Reject
```

Une réponse AI n'est pas automatiquement une décision métier.

---

# 31. BPMN logique — recherche

```text
(Start)
   |
   v
Enter Search Criteria
   |
   v
Validate Criteria
   |
   +--------------------+
   |                    |
 Invalid               Valid
   |                    |
   v                    v
Display Error        Query Data
                        |
                        v
                    Results?
                     +--+--+
                     |     |
                    YES    NO
                     |     |
                     v     v
                  Display Display Empty State
                     |
                     v
                   (End)
```

---

# 32. BPMN logique — AI

```text
(Start)
   |
   v
Enter Question
   |
   v
Validate Request
   |
   v
Check Access
   |
   +------------------+
   |                  |
 Denied             Allowed
   |                  |
   v                  v
Return 403       Retrieve Context
                      |
                      v
                 Call Local LLM
                      |
                      v
                 Validate Output
                      |
                      v
                 Return Response
                      |
                      v
                    (End)
```

---

# 33. Processus métier et règles métier

Une règle métier doit être distincte du code qui l'implémente.

Exemple :

```text
Rule:
Only active records can be proposed.

Implementation:
SQL / Service filter
```

Cette séparation facilite les tests.

---

# 34. Règles de validation

Exemples :

```text
Required field
Valid identifier
Valid numeric range
Allowed status
User permission
```

Les règles doivent être testables.

---

# 35. Use case → API

| Use Case | API possible |
|---|---|
| Search | `POST /search` |
| List | `GET /properties` |
| Detail | `GET /properties/{id}` |
| Analytics | `GET /analytics/...` |
| AI query | `POST /ai/query` |
| Health | `GET /health` |

Les routes finales doivent être alignées sur le code réel.

---

# 36. API → Data

| API | Source principale |
|---|---|
| Search | PostgreSQL |
| Detail | PostgreSQL |
| Analytics | Analytics views |
| AI Query | AI service + governed context |

---

# 37. API → contrôles

| API | Contrôles |
|---|---|
| Search | Validation |
| Detail | Authorization |
| Analytics | Authorization |
| AI Query | Authorization + AI governance |
| Administration | Strong RBAC |

---

# 38. Processus et observabilité

Chaque processus critique doit pouvoir produire un signal observable.

Exemples :

```text
Search latency
Search errors
DB errors
AI inference latency
AI errors
HTTP status counts
```

---

# 39. Processus et performance

Les flux doivent permettre d'identifier les points de latence.

```text
Client
 |
 v
Ingress
 |
 v
API
 |
 v
DB / AI
```

Le tracing peut aider à déterminer la contribution de chaque couche.

---

# 40. Processus et sécurité

Le contrôle doit apparaître dans le flux.

Exemple incorrect :

```text
User
 |
 v
Database
```

Exemple correct :

```text
User
 |
 v
Application
 |
 v
Authentication
 |
 v
Authorization
 |
 v
Business Service
 |
 v
Database
```

---

# 41. Processus et RGPD

Pour un processus utilisant des données personnelles :

```text
Input
 |
 v
Purpose Check
 |
 v
Minimum Required Data
 |
 v
Authorized Processing
 |
 v
Retention Rule
```

---

# 42. Processus et accessibilité

Le parcours utilisateur doit permettre :

- clavier ;
- focus logique ;
- messages compréhensibles ;
- champs labellisés ;
- navigation cohérente.

---

# 43. Processus et eco-conception

Un processus doit éviter :

- appels inutiles ;
- polling excessif ;
- requêtes SQL inefficaces ;
- payloads inutiles ;
- génération AI sans besoin ;
- conservation inutile.

---

# 44. Preuves attendues

Les preuves peuvent comprendre :

```text
Business process diagram
BPMN
PlantUML sequence
API implementation
Application screenshot
Test scenario
Trace
Logs
Metrics
```

---

# 45. Processus spécifiques à finaliser

Les processus suivants doivent être adaptés au périmètre métier réellement développé :

```text
Property Search
Property Detail
Property Qualification
Opportunity Analysis
Document Analysis
AI Assistant
```

Les processus non implémentés doivent rester marqués comme cibles.

---

# 46. Critères de réussite

Un processus applicatif est correctement démontré si le jury peut suivre :

```text
Actor
 |
 v
Trigger
 |
 v
Input
 |
 v
Application Steps
 |
 v
Business Rules
 |
 v
Systems
 |
 v
Output
 |
 v
Validation
```

---

# 47. Statut actuel

| Élément | Statut |
|---|---|
| Process model | DOCUMENTÉ |
| Search flow | BASELINE |
| Detail flow | BASELINE |
| Analytics flow | BASELINE |
| AI flow | BASELINE |
| RAG flow | TARGET DOCUMENTÉ |
| Deployment flow | DOCUMENTÉ |
| Error flow | DOCUMENTÉ |
| Security flow | DOCUMENTÉ |
| Final business BPMN | À ALIGNER SUR MVP |
| Runtime application proof | À CONSOLIDER |

---

# 48. Conclusion

La conception applicative doit préserver la chaîne :

```text
Business Need
      |
      v
Business Process
      |
      v
Use Case
      |
      v
Application Flow
      |
      v
Technical Implementation
      |
      v
Business Result
```

Le processus métier reste la justification de la fonctionnalité technique.

---

**BC03 / C2 — Processus métier applicatifs : DOCUMENTATION BASELINE COMPLETE**