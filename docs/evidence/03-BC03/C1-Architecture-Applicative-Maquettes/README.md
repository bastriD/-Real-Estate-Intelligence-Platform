# BC03 — C1 — Architecture applicative & maquettes

**Bloc de compétences :** BC03  
**Compétence :** C1 — Concevoir l'architecture applicative et formaliser l'expérience utilisateur  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Backend implémenté et preuves référencées — maquettes fonctionnelles à consolider

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves démontrant la conception de l'application.

Il doit permettre de relier :

```text
Business Need
      |
      v
Use Case
      |
      v
Application Architecture
      |
      v
API
      |
      v
Data / AI Services
      |
      v
User Interface
      |
      v
Tests
```

L'objectif est de démontrer que l'application n'est pas uniquement un assemblage technique mais une réponse structurée à un besoin métier.

---

# 2. Sources principales

Documents de référence :

```text
../../../20-APPLICATION/01-Application-Architecture.md
../../../10-BUSINESS/01-Business-Architecture.md
../../../00-FOUNDATION/02-Project-Vision.md
../../../00-FOUNDATION/03-Business-Objectives.md
```

Documents Data / AI associés :

```text
../../../40-DATA/01-Data-Architecture.md
../../../50-AI/01-AI-Platform-Architecture.md
../../../50-AI/04-RAG-Architecture.md
```

Diagramme principal :

```text
../../../99-DIAGRAMS/06-Application-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/06-Application-Architecture.svg
```

---

# 3. Architecture applicative cible

L'architecture générale est :

```text
User
 |
 v
Frontend / Client
 |
 v
Ingress
 |
 v
Business API
 |
 +-------------+
 |             |
 v             v
Data Services  AI Services
 |             |
 v             v
PostgreSQL     Ollama / RAG
```

Le système doit permettre de séparer :

- interface utilisateur ;
- logique métier ;
- accès aux données ;
- intégration AI ;
- configuration ;
- observabilité ;
- sécurité.

---

# 4. Architecture en couches

Le modèle applicatif suit une séparation logique :

```text
Presentation Layer
        |
        v
API Layer
        |
        v
Business Logic
        |
        v
Service Layer
        |
        +----------------+
        |                |
        v                v
Data Access          AI Integration
        |                |
        v                v
PostgreSQL          Ollama / RAG
```

Cette séparation améliore :

- testabilité ;
- maintenabilité ;
- réutilisation ;
- lisibilité ;
- découplage.

---

# 5. Frontend

## Statut

```text
TARGET
```

React constitue la technologie cible lorsqu'une interface web dédiée est nécessaire.

Le frontend doit rester découplé du backend via API.

```text
React
 |
 v
HTTP API
 |
 v
FastAPI
```

---

# 6. Backend

FastAPI est la technologie API adoptée.

Responsabilités :

- endpoints ;
- validation ;
- routing ;
- gestion erreurs ;
- intégration services ;
- documentation OpenAPI ;
- health checks.

---

# 7. Validation

Pydantic peut être utilisé pour :

- request validation ;
- response models ;
- configuration models ;
- validation métier simple.

Exemple :

```text
Client Input
    |
    v
Pydantic Validation
    |
 +--+--+
 |     |
OK    INVALID
 |     |
 v     v
Process 4xx
```

---

# 8. Accès aux données

L'application utilise PostgreSQL pour les données relationnelles.

```text
Business API
     |
     v
Data Access Layer
     |
     v
PostgreSQL
```

Les responsabilités SQL ne doivent pas être dispersées arbitrairement dans toutes les couches applicatives.

---

# 9. Séparation OLTP / analytique

L'application peut consommer différents espaces logiques.

```text
Operational Request
      |
      v
OLTP Data

Analytical Request
      |
      v
Analytics / Warehouse
```

Les requêtes analytiques lourdes ne doivent pas perturber inutilement les opérations transactionnelles.

---

# 10. Intégration AI

L'application ne doit pas être fortement couplée à un modèle particulier.

Architecture cible :

```text
Business API
      |
      v
AI Integration Service
      |
      v
Internal AI Interface
      |
      +-----------+
      |           |
      v           v
Direct AI        RAG
      |           |
      +-----+-----+
            |
            v
          Ollama
            |
            v
           Qwen
```

---

# 11. Graceful degradation

Le principe est :

```text
AI unavailable
      |
      v
Core business functionality remains available
where possible
```

L'AI est une capacité d'amélioration sauf si le cas métier la rend explicitement critique.

---

# 12. Cas d'usage métier

Les cas d'usage doivent être formalisés autour d'actions utilisateur.

Exemples possibles :

```text
Search property information
View consolidated record
Analyse opportunity
Consult analytical indicators
Ask AI-assisted question
Analyse document
```

Les cas réellement implémentés devront être marqués comme tels.

---

# 13. User Story — exemple

```text
As a business user,
I want to search a property,
so that I can quickly access consolidated information.
```

Critères d'acceptation possibles :

```text
Given valid search criteria
When the user submits the search
Then matching results are returned
And invalid inputs are handled explicitly.
```

---

# 14. User Story — AI

```text
As a business user,
I want to ask a question about governed documents,
so that I can obtain contextual assistance.
```

Critères :

- seuls les documents autorisés sont utilisés ;
- la requête est tracée si nécessaire ;
- l'AI ne contourne pas les droits d'accès ;
- l'indisponibilité AI est gérée.

---

# 15. API-first

Les fonctionnalités métier doivent pouvoir être exposées via une API claire.

Exemple :

```text
GET /health
GET /properties
GET /properties/{id}
POST /search
POST /ai/query
```

Les endpoints réels seront déterminés par l'implémentation finale.

---

# 16. Contrat API

Un endpoint doit définir :

- méthode HTTP ;
- URI ;
- input ;
- output ;
- erreurs ;
- sécurité ;
- codes HTTP.

Exemple :

```text
POST /search

Input:
{
  "city": "Montpellier"
}

Output:
{
  "results": [...]
}
```

---

# 17. Gestion des erreurs

Les erreurs doivent être :

- explicites ;
- cohérentes ;
- sans fuite de données sensibles ;
- observables.

Exemple :

```text
400 Invalid request
401 Unauthenticated
403 Forbidden
404 Not found
409 Conflict
422 Validation error
500 Internal error
```

---

# 18. Health endpoints

Les services importants doivent fournir un mécanisme de health check.

Exemple :

```text
GET /health
```

Réponse :

```json
{
  "status": "ok"
}
```

Lorsque pertinent, on peut distinguer :

```text
/health/live
/health/ready
```

---

# 19. Configuration applicative

La configuration ne doit pas être codée en dur.

Sources possibles :

```text
Environment Variables
ConfigMaps
Secrets
```

Exemple :

```text
DB_HOST
DB_PORT
DB_NAME
AI_ENDPOINT
```

---

# 20. Secrets

Les secrets ne doivent pas apparaître :

- dans Git ;
- dans les logs ;
- dans les images ;
- dans la documentation publique.

État actuel :

```text
Kubernetes Secrets
GitLab Protected Variables
```

---

# 21. Authentification

L'architecture prévoit un mécanisme d'authentification adapté au niveau de maturité de l'application.

Keycloak reste une cible pour un IAM central.

```text
User
 |
 v
Authentication
 |
 v
Token
 |
 v
API
```

Il ne doit pas être présenté comme déjà implémenté si ce n'est pas le cas.

---

# 22. Autorisation

L'autorisation doit être appliquée côté backend.

```text
Authenticated
      |
      v
Authorized?
 +----+----+
 |         |
YES       NO
 |         |
 v         v
Process   403
```

Le frontend ne constitue pas une frontière de sécurité suffisante.

---

# 23. Observabilité applicative

Les services doivent progressivement fournir :

```text
Metrics
Logs
Traces
Health
```

Architecture :

```text
FastAPI
  |
  +--> Prometheus
  |
  +--> Loki
  |
  +--> OpenTelemetry
           |
           v
          Tempo
```

---

# 24. Logging

Les logs doivent être structurés lorsque pertinent.

Exemples de champs :

```text
timestamp
level
service
request_id
trace_id
message
```

Les logs ne doivent pas contenir :

- mots de passe ;
- tokens ;
- secrets ;
- documents sensibles complets.

---

# 25. Tracing

Le tracing permet de suivre :

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

Un `trace_id` facilite la corrélation entre services.

---

# 26. Maquettes

Les maquettes doivent représenter le parcours utilisateur avant ou pendant l'implémentation.

Exemples d'écrans :

```text
Login
Dashboard
Search
Property Details
Document Analysis
AI Assistant
Administration
```

Seules les vues réellement pertinentes au cas d'usage final doivent être produites.

---

# 27. Maquette — Dashboard

Une vue Dashboard peut présenter :

```text
+--------------------------------------+
| Dashboard                            |
+--------------------------------------+
| Search                               |
+--------------------------------------+
| KPI 1 | KPI 2 | KPI 3                |
+--------------------------------------+
| Recent items                         |
|                                      |
+--------------------------------------+
```

Ce schéma est illustratif et ne constitue pas encore une maquette finale.

---

# 28. Maquette — Recherche

```text
+--------------------------------------+
| Property Search                      |
+--------------------------------------+
| City:        [________________]       |
| Price Max:   [________________]       |
| Surface Min: [________________]       |
|                                      |
|             [ SEARCH ]               |
+--------------------------------------+
| Results                              |
|--------------------------------------|
| Result 1                             |
| Result 2                             |
| Result 3                             |
+--------------------------------------+
```

---

# 29. Maquette — Fiche détaillée

```text
+--------------------------------------+
| Property                             |
+--------------------------------------+
| Address                              |
| Type                                 |
| Surface                              |
| Price                                |
| Source                               |
+--------------------------------------+
| Analytics                            |
+--------------------------------------+
| Documents                            |
+--------------------------------------+
| AI Assistance                       |
+--------------------------------------+
```

---

# 30. Maquette — AI Assistant

```text
+--------------------------------------+
| AI Assistant                         |
+--------------------------------------+
| Question                             |
| [________________________________]   |
|                                      |
| [ ASK ]                              |
+--------------------------------------+
| Answer                               |
|                                      |
+--------------------------------------+
| Sources / References                 |
+--------------------------------------+
```

Les réponses AI doivent idéalement afficher les sources utilisées lorsqu'un processus RAG est impliqué.

---

# 31. Accessibilité des maquettes

Les maquettes doivent prévoir :

- navigation clavier ;
- ordre logique ;
- labels ;
- focus visible ;
- structure sémantique ;
- contraste ;
- messages d'erreur compréhensibles.

L'accessibilité doit être prise en compte avant la fin du développement.

---

# 32. Responsive design

L'interface doit rester utilisable sur différentes tailles d'écran lorsque requis.

Exemples :

```text
Desktop
Tablet
Mobile
```

Le besoin réel doit déterminer le niveau de support.

---

# 33. Flux utilisateur — recherche

```text
User
 |
 v
Search Page
 |
 v
Enter Criteria
 |
 v
Validate Input
 |
 v
API
 |
 v
Database
 |
 v
Results
 |
 v
Details
```

---

# 34. Flux utilisateur — AI

```text
User
 |
 v
AI Page
 |
 v
Enter Question
 |
 v
API
 |
 v
Authorization
 |
 v
AI Service
 |
 v
RAG / Ollama
 |
 v
Response
 |
 v
Display Sources
```

---

# 35. Architecture de déploiement applicatif

```text
GitLab
  |
  v
CI
  |
  v
Container Image
  |
  v
GitOps
  |
  v
Argo CD
  |
  v
Kubernetes
  |
  v
Ingress
  |
  v
Application
```

---

# 36. Packaging

L'application doit être conteneurisée.

Exemple :

```text
Dockerfile
```

responsable de :

- dépendances ;
- runtime ;
- application ;
- command.

---

# 37. Dépendances applicatives

Les dépendances doivent être explicites.

Exemple :

```text
requirements.txt
pyproject.toml
package.json
```

et doivent pouvoir être reproduites.

---

# 38. Database migration

Les évolutions de schéma applicatif doivent être versionnées.

Exemples :

```text
migration.sql
Alembic
```

selon le projet.

---

# 39. Testabilité

L'architecture doit permettre :

```text
Unit Test
Integration Test
API Test
Database Test
Security Test
Smoke Test
```

La séparation des couches améliore cette testabilité.

---

# 40. Stratégie de tests

```text
              E2E
             /   \
        Integration
          /       \
       Unit Tests
```

Les tests les plus nombreux doivent généralement rester rapides et ciblés.

---

# 41. Test API

Exemple :

```text
Given application is running
When GET /health is called
Then HTTP 200 is returned
And response status is "ok".
```

---

# 42. Test Data

```text
Given a valid entity exists
When the API requests it
Then the expected database record is returned.
```

---

# 43. Test AI

```text
Given Ollama is reachable
When a valid inference request is sent
Then a response is returned
Within the accepted timeout.
```

---

# 44. Test de dégradation AI

```text
Given AI service is unavailable
When a non-AI business feature is called
Then core application remains available.
```

si cette propriété est réellement implémentée.

---

# 45. Sécurité applicative

Les principaux contrôles comprennent :

- validation ;
- auth ;
- authorization ;
- secrets ;
- TLS ;
- safe errors ;
- dependency security ;
- secure logging.

Référence :

```text
../../../60-SECURITY/06-Application-Security.md
```

---

# 46. Patterns utilisés

Patterns pertinents possibles :

```text
Layered Architecture
Repository
Service Layer
Dependency Injection
API Gateway / AI Gateway target
GitOps
```

Les patterns doivent être justifiés par leur utilité.

Ils ne doivent pas être ajoutés uniquement pour augmenter la complexité.

---

# 47. Critères UX

L'expérience utilisateur doit favoriser :

- simplicité ;
- lisibilité ;
- feedback ;
- cohérence ;
- faible nombre d'étapes ;
- erreurs compréhensibles.

---

# 48. Critères de réussite applicatifs

Une fonctionnalité peut être considérée prête lorsqu'elle est :

```text
Implemented
+
Tested
+
Observable
+
Documented
+
Accessible where applicable
```

---

# 49. Preuves attendues

## Architecture réellement implémentée

Le backend du projet est organisé dans `src/api/`.

```text
Requête HTTP
     |
     v
Routes FastAPI / schémas Pydantic
     |
     v
Identité / rôle autorisé
     |
     v
Service métier
     |
     v
Repository / session
     |
     v
PostgreSQL
```

| Responsabilité | Implémentation depuis la racine du dépôt |
|---|---|
| Point d'entrée et intégration des routes | `src/api/main.py`, `src/api/api/v1/router.py` |
| Contrats d'entrée et de sortie | `src/api/schemas/` |
| Règles métier | `src/api/services/` |
| Accès aux données | `src/api/repositories/`, `src/api/db/` |
| Identité et rôles | `src/api/core/security.py`, `src/api/core/dependencies.py` |
| Métriques | `src/api/observability/metrics.py` |
| Vérification locale | `tests/backend/` et rapports BC03 / C6 |

Les modules métier couvrent clients, mandats, demandes/version, biens, présentations, recommandations et visites. Les services Python constituent les modules internes du backend ; leur séparation ne signifie pas qu'ils sont déployés comme microservices indépendants.

L'intégration actuelle du matching est déterministe. L'interface React, les écrans et l'assistant RAG restent des cibles lorsqu'aucune réalisation correspondante n'est fournie.

Références de validation :

```text
../../../60-SECURITY/RECOMMENDATION-AUDIT-RUNTIME-EVIDENCE.md
../C6-Tests-Executes/visite-audit-2026-09-09/README.md
```

Les preuves pertinentes peuvent inclure :

```text
Application architecture
PlantUML
API source code
OpenAPI
Screenshots
Mockups
Dockerfile
Kubernetes manifests
Tests
CI output
Runtime screenshots
```

---

# 50. Maquettes à produire

Ce dossier devra recevoir les maquettes réellement retenues.

Structure possible :

```text
01-login.*
02-dashboard.*
03-search.*
04-details.*
05-ai-assistant.*
```

Seulement les écrans réellement nécessaires doivent être créés.

---

# 51. Preuves runtime à consolider

Exemples :

```text
curl /health
curl API endpoint
Swagger / OpenAPI screenshot
Application screenshot
Kubernetes pod status
Ingress URL
Test result
```

---

# 52. Traceability

Le modèle cible est :

```text
Business Requirement
        |
        v
User Story
        |
        v
Screen / API
        |
        v
Implementation
        |
        v
Test
        |
        v
Evidence
```

---

# 53. Matrice fonction → composant

| Fonction | Composant |
|---|---|
| Recherche | API + PostgreSQL |
| Consultation | API |
| Analytics | PostgreSQL analytics |
| AI assistance | AI service |
| RAG | Retriever + Ollama |
| Authentication | Auth layer |
| Monitoring | Observability stack |

---

# 54. Matrice écran → API

Exemple cible :

| Écran | API |
|---|---|
| Dashboard | `/analytics/*` |
| Search | `/search` |
| Details | `/properties/{id}` |
| AI Assistant | `/ai/query` |
| Health | `/health` |

Ces routes illustrent les écrans cibles et ne constituent pas le contrat actuel de l'API. Les routes métier réalisées se trouvent sous `/api/v1`, notamment `/biens`, `/demandes`, `/mandats`, `/presentations` et `/visites`. Les recommandations utilisent `/api/v1/demande-versions/{id_demande_version}/recommendations`. Les sondes sont `/health` et `/ready`.

---

# 55. Statut actuel

| Élément | Statut |
|---|---|
| Architecture applicative | DOCUMENTÉE |
| Diagramme application | DISPONIBLE |
| Backend technology | FASTAPI / IMPLÉMENTÉ |
| Data integration | DOCUMENTÉE |
| AI integration | DOCUMENTÉE |
| Security architecture | DOCUMENTÉE |
| Observability | DOCUMENTÉE |
| User flows | BASELINE |
| Maquettes finales | À PRODUIRE |
| API métier finale | MODULES PRIORITAIRES IMPLÉMENTÉS / RECETTE COMPLÈTE À CONSOLIDER |
| Application runtime | À CONSOLIDER |
| Tests exécutés | TRAITÉS DANS C6 |

---

# 56. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Business Need
      |
      v
Use Case
      |
      v
Mockup / Flow
      |
      v
Application Architecture
      |
      v
API / Service
      |
      v
Runtime
      |
      v
Test
```

---

# 57. Conclusion

L'architecture applicative repose sur une séparation claire entre :

```text
Presentation
Business
Data
AI
Platform
```

et doit rester :

```text
Testable
Maintainable
Secure
Observable
Accessible
Deployable
```

Les maquettes doivent ensuite matérialiser le parcours utilisateur réel et fournir une preuve complémentaire de conception.

---

**BC03 / C1 — Architecture applicative & maquettes : DOCUMENTATION BASELINE COMPLETE**
