# BC03 — C7 — Qualité automatisée & CI

**Bloc de compétences :** BC03  
**Compétence :** C7 — Mettre en place un suivi automatisé de la qualité via l'intégration continue  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Pipeline modulaire et contrôles implémentés — preuves d'exécution à rattacher

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves démontrant que la qualité du projet peut être contrôlée automatiquement.

Le modèle cible est :

```text
Code Change
    |
    v
Git
    |
    v
Merge Request / Push
    |
    v
CI Pipeline
    |
    +----------------------+
    |          |           |
    v          v           v
Lint        Tests      Security Checks
    |          |           |
    +----------+-----------+
               |
               v
            Result
               |
       +-------+-------+
       |               |
      PASS            FAIL
       |               |
       v               v
Continue            Block / Fix
```

L'objectif est de détecter les défauts le plus tôt possible.

---

# 2. Sources de référence

Documents principaux :

```text
../../../70-DEVOPS/01-DevOps-Architecture.md
../../../70-DEVOPS/03-CI-CD-Architecture.md
../../../70-DEVOPS/06-Artifact-Management.md
../../../70-DEVOPS/07-Release-Management.md
```

Architecture GitOps :

```text
../../../70-DEVOPS/02-GitOps-Architecture.md
```

Sécurité :

```text
../../../60-SECURITY/06-Application-Security.md
../../../60-SECURITY/07-Container-Security.md
```

Observabilité :

```text
../../../90-OBSERVABILITY/
```

ADR :

```text
../../../98-ADR/ADR-0012-GitLab-CI-CD.md
```

---

# 3. Principe général

Le projet applique le principe :

```text
Quality
must be checked
before deployment
```

et non uniquement :

```text
after incident
```

La CI doit progressivement contrôler :

- code ;
- tests ;
- dépendances ;
- configuration ;
- sécurité ;
- artifacts ;
- policies.

---

# 4. GitLab CI

GitLab CI est la solution adoptée pour l'intégration continue.

Statut :

```text
ADOPTED
```

Composants :

```text
GitLab
GitLab Runner
.gitlab-ci.yml
```

---

# 5. Déclenchement

Une pipeline peut être déclenchée par :

```text
Push
Merge Request
Tag
Manual Trigger
Scheduled Pipeline
```

Le déclencheur doit correspondre au besoin réel.

---

# 6. Pipeline cible

Exemple logique :

```text
validate
   |
   v
test
   |
   v
security
   |
   v
build
   |
   v
package
   |
   v
publish
```

Le déploiement Kubernetes reste séparé via GitOps.

---

# 7. Séparation CI / CD

Le modèle du projet est :

```text
GitLab CI
=
Validate / Build / Publish

Argo CD
=
Deploy / Reconcile
```

Cette séparation évite que la CI devienne directement propriétaire de l'état runtime Kubernetes.

---

# 8. Exemple pipeline minimale

```yaml
stages:
  - validate
  - test
  - build

validate:
  stage: validate
  script:
    - echo "Validation"

test:
  stage: test
  script:
    - pytest

build:
  stage: build
  script:
    - docker build -t application:$CI_COMMIT_SHA .
```

Cet exemple est illustratif.

La pipeline réelle doit correspondre au repository final.

---

# 9. Validation syntaxique

Les fichiers de configuration doivent être validés avant déploiement.

Exemples :

```text
YAML
JSON
Dockerfile
Kubernetes manifests
Helm values
```

---

# 10. Linting Python

Un linter peut détecter :

- erreurs simples ;
- conventions ;
- imports inutiles ;
- problèmes de style.

Outils possibles :

```text
ruff
flake8
pylint
```

Le projet doit indiquer l'outil réellement adopté si un linter est utilisé.

---

# 11. Formatting

Un formatter peut standardiser le code.

Exemples :

```text
black
ruff format
```

Le formatting automatique réduit certaines différences inutiles dans les reviews.

---

# 12. Type Checking

Lorsque pertinent :

```text
mypy
pyright
```

peut améliorer la détection de certains problèmes.

Ce contrôle reste optionnel selon le code réel.

---

# 13. Tests unitaires

La CI doit pouvoir exécuter :

```bash
pytest
```

pour les projets Python concernés.

Résultat attendu :

```text
tests passed
```

et code de retour :

```text
0
```

---

# 14. Tests d'intégration

Des tests peuvent vérifier l'interaction avec :

- PostgreSQL ;
- Redis si utilisé ;
- API ;
- services internes.

Ils peuvent nécessiter des services CI dédiés.

---

# 15. Tests API

La CI peut exécuter des tests FastAPI.

Exemple :

```python
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
```

---

# 16. Tests Data

Pour dbt :

```bash
dbt test
```

ou :

```bash
dbt build
```

peut être intégré à une pipeline adaptée.

---

# 17. Tests SQL

La CI peut exécuter :

- migrations ;
- requêtes de validation ;
- tests d'intégrité ;
- tests de schéma.

---

# 18. Tests Data Quality

Le pipeline peut vérifier :

```text
Not Null
Uniqueness
Accepted Values
Relationships
Business Rules
```

---

# 19. Tests infrastructure

Les manifests Kubernetes peuvent être validés avant merge.

Contrôles possibles :

```text
kubectl dry-run
kubeconform
kubeval
helm lint
```

L'outil exact doit refléter l'implémentation réelle.

---

# 20. Helm validation

Exemple :

```bash
helm lint .
```

et éventuellement :

```bash
helm template .
```

pour examiner le rendu.

---

# 21. Docker build

La CI doit pouvoir construire une image de manière reproductible.

```text
Source
 |
 v
Docker Build
 |
 v
Container Image
```

---

# 22. Image tagging

Les tags doivent permettre la traçabilité.

Exemples :

```text
commit SHA
semantic version
release tag
```

Éviter de dépendre uniquement de :

```text
latest
```

pour la traçabilité.

---

# 23. Artifact traceability

Le modèle cible est :

```text
Git Commit
    |
    v
CI Pipeline
    |
    v
Artifact
    |
    v
Version / Tag
```

---

# 24. Container Registry

Les images produites peuvent être publiées dans un registry.

La preuve doit permettre d'identifier :

- image ;
- tag ;
- commit ;
- pipeline.

---

# 25. Security — secret scanning

La CI peut vérifier qu'aucun secret n'est commité.

Exemples d'outils :

```text
gitleaks
GitLab secret detection
trufflehog
```

Un seul outil correctement configuré peut suffire selon le scope.

---

# 26. Dependency scanning

Les dépendances peuvent contenir des vulnérabilités.

La CI peut contrôler :

```text
Python dependencies
Node dependencies
Container packages
```

---

# 27. SAST

Static Application Security Testing peut analyser le code.

Objectif :

```text
Find security weaknesses
before runtime
```

---

# 28. Container scanning

Une image construite peut être analysée pour rechercher :

- CVEs ;
- packages obsolètes ;
- vulnérabilités connues.

---

# 29. Policy validation

Governance as Code permet également de déplacer certains contrôles dans CI.

```text
Governance Definition
        |
        v
CI Validation
        |
   +----+----+
   |         |
 PASS       FAIL
```

---

# 30. Exemple Policy as Code

Une règle peut vérifier :

```text
Every critical workload
must define
resource requests
```

La CI peut alors rejeter un manifest ne respectant pas la règle.

---

# 31. Quality Gate

Le principe est :

```text
Tests Passed
+
Critical Validation Passed
+
Security Checks Passed
        |
        v
Eligible for Merge / Release
```

---

# 32. Merge Request

Une Merge Request permet de combiner :

```text
Human Review
+
Automated Validation
```

Les deux sont complémentaires.

---

# 33. Protected Branch

Les branches critiques peuvent être protégées afin d'éviter des changements directs non contrôlés.

---

# 34. Branch Strategy

Le projet doit utiliser une stratégie adaptée à sa taille.

Pour un projet simple :

```text
main
+
feature branches
```

peut suffire.

Il n'est pas nécessaire d'introduire un GitFlow complexe sans besoin.

---

# 35. Pipeline failure

Une pipeline en échec doit bloquer la progression lorsqu'elle échoue sur un contrôle obligatoire.

```text
FAIL
 |
 v
Fix
 |
 v
Commit
 |
 v
Rerun
```

---

# 36. Pipeline evidence

La preuve CI doit permettre d'identifier :

```text
Pipeline ID
Commit SHA
Branch
Jobs
Duration
Status
```

---

# 37. Test report

Les outils peuvent produire :

```text
JUnit XML
HTML report
coverage report
```

Ces rapports peuvent être archivés comme artifacts CI.

---

# 38. Code Coverage

La couverture peut aider à détecter les zones non testées.

Mais :

```text
100% Coverage
!=
100% Quality
```

La pertinence des tests reste plus importante que le chiffre seul.

---

# 39. Coverage threshold

Un seuil peut être utilisé si pertinent.

Exemple :

```text
coverage >= 80%
```

mais le seuil doit être justifié, pas choisi arbitrairement.

---

# 40. Quality metrics

Exemples :

```text
Tests Passed
Tests Failed
Coverage
Lint Errors
Security Findings
Build Duration
Image Size
```

---

# 41. CI performance

Une pipeline trop lente réduit l'efficacité.

Le projet peut surveiller :

```text
Pipeline Duration
Job Duration
Cache Hit
```

---

# 42. CI cache

Le cache peut accélérer :

- pip ;
- npm ;
- build dependencies.

Mais le cache doit pouvoir être invalidé correctement.

---

# 43. Parallel jobs

Certaines étapes indépendantes peuvent être parallélisées.

Exemple :

```text
lint --------+
             |
test --------+--> build
             |
security ----+
```

---

# 44. Fail fast

Les validations rapides peuvent être placées en début de pipeline.

Exemple :

```text
syntax
 |
 v
lint
 |
 v
tests
 |
 v
build
```

Éviter de construire une image coûteuse si le code échoue déjà au lint.

---

# 45. Deployment artifact

La CI doit produire un artifact identifiable.

Le modèle GitOps est ensuite :

```text
Artifact
   |
   v
Version referenced in GitOps
   |
   v
Argo CD
   |
   v
Kubernetes
```

---

# 46. GitOps repository update

La mise à jour d'image peut être :

```text
manual reviewed change
```

ou automatisée selon la maturité.

Elle doit rester traçable.

---

# 47. Argo CD validation

Après déploiement :

```text
Argo CD
 |
 v
Synced
+
Healthy
```

fournit une preuve complémentaire de CD.

---

# 48. Smoke tests

Après déploiement, un smoke test peut vérifier :

```text
health
basic API
critical dependency
```

---

# 49. Rollback

Une version défaillante doit pouvoir être corrigée par :

```text
Git revert
```

ou changement de version GitOps.

---

# 50. Database migration CI

Les migrations doivent être contrôlées.

Le pipeline peut vérifier :

- syntaxe ;
- ordre ;
- exécution sur base temporaire ;
- compatibilité.

---

# 51. Migration rollback

Toutes les migrations ne peuvent pas être annulées facilement.

Le projet doit donc privilégier :

```text
Backup
+
Forward Fix
+
Validated Migration
```

selon le contexte.

---

# 52. Data pipeline CI

Les repositories Data peuvent exécuter :

```text
dbt parse
dbt compile
dbt test
```

selon l'environnement disponible.

---

# 53. Airflow DAG validation

Une CI peut vérifier que les DAGs sont importables.

Exemples :

```text
Python syntax
Airflow DAG import
Unit tests
```

---

# 54. MLOps CI

Le code ML peut subir :

```text
unit tests
data schema checks
training smoke test
```

avant une exécution longue.

---

# 55. Model quality gate

Après training :

```text
Metric
 |
 v
Threshold
 |
 +---+---+
 |       |
PASS    FAIL
 |       |
 v       v
Candidate Reject
```

Le seuil doit être lié au cas d'usage.

---

# 56. Model promotion

La promotion doit rester distincte du simple training.

```text
Training
 |
 v
Evaluation
 |
 v
Approval
 |
 v
Promotion
```

---

# 57. AI prompt tests

Les prompts critiques peuvent être testés sur un dataset fixe.

Exemple :

```text
Prompt Version
+
Evaluation Dataset
+
Expected Criteria
```

---

# 58. RAG evaluation

Une CI ou pipeline dédiée peut mesurer :

```text
retrieval hit rate
answer relevance
source coverage
```

si RAG devient réellement implémenté.

---

# 59. Documentation CI

La documentation peut également être validée automatiquement.

Exemples :

```text
broken links
empty files
invalid ADR references
PlantUML syntax
```

Le projet a déjà exécuté manuellement plusieurs contrôles de ce type.

---

# 60. PlantUML validation

La CI peut rendre :

```text
*.puml
```

vers :

```text
*.svg
```

et échouer si un diagramme ne compile pas.

---

# 61. Diagram generation

Pipeline possible :

```text
PlantUML Source
      |
      v
CI
      |
      v
SVG
```

Cela industrialise le modèle Diagrams as Code.

---

# 62. Governance documentation checks

La CI peut vérifier :

- naming ;
- required metadata ;
- IDs ;
- duplicate IDs ;
- missing references.

---

# 63. ADR validation

Contrôles possibles :

```text
unique ADR number
required status
required title
valid references
```

---

# 64. Evidence generation

La CI elle-même devient une source de preuve.

```text
Commit
 |
 v
Pipeline
 |
 v
Test Result
 |
 v
Artifact
```

---

# 65. Quality loop

```text
Develop
  |
  v
Commit
  |
  v
CI
  |
  +--------+
  |        |
PASS      FAIL
  |        |
  v        v
Merge     Fix
  |
  v
Deploy
  |
  v
Observe
  |
  v
Improve
```

---

# 66. Shift Left

Le principe Shift Left consiste à détecter les défauts plus tôt.

```text
Design
 |
 v
Code
 |
 v
CI
 |
 v
Deployment
 |
 v
Runtime
```

Plus un défaut est détecté tôt, plus sa correction est généralement simple.

---

# 67. Shift Right

La qualité continue également après le déploiement.

```text
CI
 |
 v
Deployment
 |
 v
Observability
 |
 v
Runtime Feedback
```

CI et observabilité sont complémentaires.

---

# 68. CI et sécurité

Le pipeline peut devenir un point d'application de sécurité.

```text
Source
 |
 v
Security Checks
 |
 v
Artifact
```

mais ne remplace pas la sécurité runtime.

---

# 69. CI et gouvernance

La CI peut appliquer :

```text
Architecture Rules
Security Rules
Documentation Rules
Governance Rules
```

---

# 70. Governance as Code

Le modèle cible est :

```text
Governance Definition
        |
        v
Git
        |
        v
CI Validation
        |
        v
Applied State
        |
        v
Evidence
```

---

# 71. Environments

Les pipelines peuvent différencier :

```text
development
test
production-like
```

Les secrets et endpoints doivent rester adaptés à chaque environnement.

---

# 72. CI variables

Les secrets CI doivent utiliser des variables protégées plutôt que du plaintext.

---

# 73. Pipeline permissions

Le Runner doit disposer uniquement des permissions nécessaires.

Principe :

```text
Least Privilege
```

---

# 74. Runner isolation

Les runners doivent être considérés comme une partie sensible de la supply chain.

Ils peuvent accéder :

- code ;
- variables ;
- artifacts ;
- registry.

---

# 75. Artifact retention

Les artifacts CI ne doivent pas être conservés indéfiniment sans raison.

Une durée de rétention doit être définie selon :

- audit ;
- rollback ;
- coût ;
- preuve.

---

# 76. Image retention

Même principe pour les images :

```text
Active
Rollback
Retention
Cleanup
```

---

# 77. Eco-conception CI

Les pipelines doivent éviter :

- builds inutiles ;
- jobs dupliqués ;
- artifacts inutiles ;
- tests lourds sur chaque commit sans justification.

---

# 78. Example optimization

Avant :

```text
Every commit:
full integration
full image build
full AI training
```

Après :

```text
Commit:
lint + unit

Merge Request:
integration

Scheduled / explicit:
expensive ML training
```

---

# 79. Quality ownership

Les rôles concernés peuvent inclure :

```text
Developer
Platform
Data
AI
Security
Governance
```

La CI centralise certains contrôles, mais chaque domaine reste responsable de sa qualité.

---

# 80. Pipeline observability

Le projet peut suivre :

```text
Success rate
Failure rate
Duration
Flaky jobs
```

afin d'améliorer la CI elle-même.

---

# 81. Flaky tests

Un test instable doit être traité.

```text
Random PASS / FAIL
```

réduit la confiance dans la pipeline.

---

# 82. Manual jobs

Certaines opérations sensibles peuvent rester manuelles.

Exemple :

```text
production promotion
destructive migration
```

Un job manuel ne signifie pas absence d'automatisation ; il peut constituer un contrôle d'approbation.

---

# 83. Approval gates

Pour certaines étapes :

```text
Automated Validation
        |
        v
Human Approval
        |
        v
Promotion
```

peut être approprié.

---

# 84. CI evidence matrix

| Contrôle | Preuve |
|---|---|
| Lint | Job output |
| Unit tests | Test report |
| API tests | pytest report |
| dbt | dbt output |
| Build | Image artifact |
| Secret scan | Scanner report |
| Container scan | Security report |
| Policy | Validation output |
| PlantUML | Generated SVG |

---

# 85. Minimum viable CI

Pour le MVP, une pipeline convaincante doit au minimum pouvoir démontrer :

```text
Validate
+
Test
+
Build
```

et idéalement :

```text
Security Check
```

---

# 86. Pipeline cible application

```text
lint
  |
  v
unit-test
  |
  v
integration-test
  |
  v
security
  |
  v
build-image
  |
  v
publish
```

---

# 87. Pipeline cible Data

```text
syntax
 |
 v
dbt parse
 |
 v
dbt test
 |
 v
quality
```

---

# 88. Pipeline cible documentation

```text
markdown checks
 |
 v
ADR checks
 |
 v
PlantUML render
```

---

# 89. Pipeline cible Governance as Code

```text
schema validation
      |
      v
policy validation
      |
      v
apply / reconcile
```

---

# 90. Preuves existantes

## Pipeline actuelle du projet

La pipeline racine comporte les étapes :

```text
validate
    |
    v
database
    |
    v
build
    |
    v
deploy
```

Elle inclut les fichiers spécialisés de `.gitlab/ci/` pour la base, Airflow, les images Data, le warehouse, la gouvernance, OpenMetadata, l'observabilité, le backend, l'IA/MLOps et le PRA.

## Contrôle backend

Le job `backend:tests` installe `requirements-backend-test.txt` puis exécute :

```text
python -m pytest tests/backend tests/data tests/ai/test_candidate_availability.py -v --cov=src/api --cov-report=term-missing --cov-report=xml --cov-fail-under=80
```

Le rapport Cobertura `coverage.xml` est déclaré comme artifact GitLab, y compris en cas d'échec, avec une expiration de 30 jours. Les rapports locaux déjà disponibles sont référencés dans C6 ; ils prouvent une exécution locale de la sélection et non un succès du job distant.

## Séparation livraison et exécution

Le job PRA publie les manifestes dans le dépôt GitOps. Argo CD assure ensuite la réconciliation. Le succès de publication ne démontre pas à lui seul la réussite du CronJob ou la santé du service.

Sources depuis la racine :

```text
.gitlab-ci.yml
.gitlab/ci/backend-tests.yml
.gitlab/ci/backend.yml
.gitlab/ci/warehouse.yml
.gitlab/ci/governance.yml
.gitlab/ci/pra.yml
```

Preuves complémentaires :

```text
../C6-Tests-Executes/README.md
../../../60-SECURITY/RECOMMENDATION-AUDIT-RUNTIME-EVIDENCE.md
../../../PCA PRA/PCA-PRA-POSTGRESQL.md
```

Les contrôles SAST, DAST et scans d'images cités dans les exemples ne sont pas déclarés exécutés sans rapport correspondant.

| Élément | Statut |
|---|---|
| GitLab | OPÉRATIONNEL |
| GitLab Runner | OPÉRATIONNEL |
| CI/CD architecture | DOCUMENTÉE |
| GitOps | OPÉRATIONNEL |
| ADR CI/CD | DISPONIBLE |
| Automated tests in training projects | DÉJÀ PRATIQUÉS |
| Final project CI pipeline | CONFIGURATION MODULAIRE IMPLÉMENTÉE |
| Security CI | À CONSOLIDER |
| Quality reports | JUNIT / COUVERTURE LOCAUX DISPONIBLES EN C6 |
| Governance CI | CONFIGURATION PRÉSENTE / RÉSULTAT DISTANT À RATTACHER |

---

# 91. Preuves à produire

Ce dossier pourra recevoir :

```text
01-pipeline-success.txt
02-unit-test-report.xml
03-api-tests.txt
04-build-job.txt
05-security-scan.txt
06-policy-validation.txt
07-pipeline-screenshot.png
```

uniquement à partir de la pipeline réellement exécutée.

---

# 92. Exemple preuve

Une preuve CI solide contient :

```text
Repository
Commit SHA
Pipeline ID
Job
Command
Result
Timestamp
```

---

# 93. Ce qui ne constitue pas une preuve suffisante

```text
.gitlab-ci.yml exists
```

prouve seulement que la configuration existe.

Pour démontrer l'exécution :

```text
Pipeline Result
```

est nécessaire.

---

# 94. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Code Change
    |
    v
CI Trigger
    |
    v
Automated Checks
    |
    v
Pass / Fail
    |
    v
Artifact / Report
```

---

# 95. État actuel

```text
CI architecture              COMPLETE
GitLab Runner                OPERATIONAL
GitOps separation            COMPLETE
Quality controls             DOCUMENTED
Application CI               IMPLEMENTED / REMOTE RUN TO LINK
Automated test evidence      LOCAL REPORTS AVAILABLE
Security CI evidence         TO CONSOLIDATE
Governance CI evidence       TO CONSOLIDATE
Pipeline runtime proof       TO COMPLETE
```

---

# 96. Conclusion

La CI transforme les règles de qualité en contrôles répétables.

Le principe est :

```text
Quality Rule
    |
    v
Automation
    |
    v
Every Relevant Change
    |
    v
Consistent Result
```

La cible du projet est donc :

```text
Code
+
Tests
+
Security
+
Policy
+
Traceability
```

validés automatiquement avant que les changements ne deviennent l'état de référence.

---

**BC03 / C7 — Qualité automatisée & CI : DOCUMENTATION BASELINE COMPLETE**
