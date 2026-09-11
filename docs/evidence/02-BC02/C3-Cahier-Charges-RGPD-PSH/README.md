# BC02 — C3 — Cahier des charges, RGPD et accessibilité PSH

**Bloc de compétences :** BC02  
**Compétence :** C3 — Formaliser les exigences fonctionnelles, techniques, réglementaires et d'accessibilité  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Baseline documentaire — preuves de conformité à consolider

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves démontrant que les exigences du projet sont formalisées avant et pendant leur implémentation.

Il couvre trois dimensions principales :

```text
Requirements
     |
     +------------------+
     |                  |
     v                  v
Technical           Regulatory
Requirements        Requirements
     |                  |
     |              +---+---+
     |              |       |
     v              v       v
Architecture       RGPD   Accessibility
```

Le cahier des charges doit permettre de relier :

```text
Business Need
      |
      v
Requirement
      |
      v
Architecture
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

# 2. Documents de référence

Les documents principaux sont :

```text
CAHIER-DES-CHARGES-TECHNIQUE.md
REGISTRE-RGPD.md
```

Ces intitulés désignent les livrables du projet Fil Rouge. Leurs fichiers autonomes ne sont pas présents dans la copie locale consultée ; leur emplacement final reste à rattacher.

Ils doivent rester les sources de vérité correspondantes.

Ce dossier `evidence/` ne les remplace pas.

---

# 3. Sources architecturales complémentaires

Les exigences techniques sont également reliées à :

```text
../../../00-FOUNDATION/02-Project-Vision.md
../../../00-FOUNDATION/03-Business-Objectives.md
../../../00-FOUNDATION/04-Architecture-Decisions.md
../../../00-FOUNDATION/05-Technology-Stack.md

../../../20-APPLICATION/01-Application-Architecture.md
../../../30-INFRASTRUCTURE/
../../../40-DATA/
../../../50-AI/
../../../60-SECURITY/
../../../70-DEVOPS/
../../../80-OPERATIONS/
../../../90-OBSERVABILITY/
../../../95-GOVERNANCE/
```

---

# 4. Catégories d'exigences

Les exigences du projet sont réparties en plusieurs catégories.

```text
REQ-BUS   Business
REQ-FUN   Functional
REQ-APP   Application
REQ-DATA  Data
REQ-AI    Artificial Intelligence
REQ-INF   Infrastructure
REQ-SEC   Security
REQ-OPS   Operations
REQ-OBS   Observability
REQ-GOV   Governance
REQ-RGPD  Data Protection
REQ-ACC   Accessibility
REQ-ECO   Eco-design
```

Cette classification permet une meilleure traçabilité.

---

# 5. Exigences métier

La plateforme doit soutenir les activités métier en améliorant :

- centralisation ;
- recherche ;
- traitement de données ;
- automatisation ;
- analyse ;
- traçabilité ;
- exploitation de l'IA ;
- qualité de l'information.

Les technologies ne constituent pas elles-mêmes les exigences métier.

Exemple :

```text
Incorrect:

REQ-BUS-001
Use Kubernetes
```

Kubernetes est une réponse technique.

L'exigence métier doit plutôt exprimer le résultat recherché.

```text
REQ-BUS-001
The platform must provide reliable and reproducible
access to the required business services.
```

---

# 6. Exigences fonctionnelles

Les principales familles fonctionnelles sont :

```text
Data acquisition
Data management
Data transformation
Search
Analytics
Business API
Document processing
AI assistance
Model lifecycle
Metadata management
Administration
```

Les exigences détaillées dépendent des cas d'usage réellement implémentés.

---

# 7. Exigences applicatives

Les applications doivent, selon leur rôle :

- exposer des interfaces définies ;
- valider leurs entrées ;
- gérer les erreurs ;
- fournir des health checks ;
- produire des logs exploitables ;
- exposer des métriques lorsque pertinent ;
- respecter les contrôles d'accès ;
- être déployables de manière reproductible.

Architecture :

```text
Client
  |
  v
Ingress
  |
  v
API / Application
  |
  +--------+
  |        |
  v        v
Data      AI
```

---

# 8. Exigences Data

La Data Platform doit permettre :

- ingestion ;
- stockage ;
- transformation ;
- validation ;
- historisation lorsque nécessaire ;
- analytics ;
- metadata ;
- lineage ;
- Data Quality ;
- gouvernance.

Architecture logique :

```text
SOURCE
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
```

---

# 9. Exigences de qualité Data

La qualité doit pouvoir être vérifiée automatiquement.

Exemples :

```text
Not Null
Uniqueness
Referential Integrity
Accepted Values
Freshness
Row Counts
Business Rules
```

Les contrôles doivent produire des résultats vérifiables.

---

# 10. Exigences AI / ML

La plateforme AI doit permettre selon les cas d'usage :

- training ;
- experiment tracking ;
- evaluation ;
- model versioning ;
- artifact management ;
- inference ;
- monitoring ;
- governance.

Séparation :

```text
Airflow
=
Workflow Orchestration

MLflow
=
ML Lifecycle

Ollama
=
Local LLM Inference
```

---

# 11. Exigences de souveraineté AI

Le traitement local est privilégié lorsque des données sensibles ou internes sont utilisées.

Principe :

```text
Local AI
=
DEFAULT

External AI
=
GOVERNED EXCEPTION
```

Une utilisation externe doit prendre en compte :

- nature des données ;
- confidentialité ;
- base légale lorsque applicable ;
- politique de sécurité ;
- fournisseur ;
- conservation ;
- transfert éventuel ;
- traçabilité.

---

# 12. Exigences infrastructure

La plateforme doit être :

- reproductible ;
- observable ;
- récupérable ;
- documentée ;
- compatible avec les ressources disponibles.

La cible actuelle repose principalement sur :

```text
Physical Infrastructure
        |
        v
Proxmox
        |
        v
Virtual Machines
        |
        v
Kubernetes
```

---

# 13. Exigences Kubernetes

Les workloads doivent respecter autant que possible :

- namespaces ;
- resource requests ;
- resource limits ;
- health probes ;
- configuration externalisée ;
- secrets séparés ;
- RBAC ;
- TLS ;
- observabilité ;
- déploiement déclaratif.

---

# 14. Exigences GitOps

Le desired state doit être versionné.

```text
Git
 |
 v
Review / Validation
 |
 v
Argo CD
 |
 v
Kubernetes
```

Les modifications manuelles doivent rester exceptionnelles et ne doivent pas devenir une source de configuration permanente.

---

# 15. Exigences sécurité

Les exigences de sécurité comprennent notamment :

```text
Authentication
Authorization
Least Privilege
Secrets Management
Encryption
TLS
Network Security
Container Security
Kubernetes Security
Auditability
Monitoring
Backup
Recovery
```

Références :

```text
../../../60-SECURITY/
```

---

# 16. Exigences de gestion des secrets

État actuel :

```text
Kubernetes Secrets
GitLab protected variables
```

État cible possible :

```text
HashiCorp Vault
```

Vault reste une cible et ne doit pas être présenté comme une dépendance déjà adoptée.

---

# 17. Exigences d'identité

État cible possible :

```text
Keycloak
```

Les besoins concernés sont :

- centralisation des identités ;
- SSO ;
- OpenID Connect ;
- OAuth2 ;
- gestion des rôles.

Keycloak reste une technologie cible jusqu'à son adoption et son implémentation effectives.

---

# 18. Exigences d'observabilité

Les services critiques doivent être observables à travers :

```text
Metrics
Logs
Traces
Health
```

Stack actuelle :

```text
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
Alertmanager
```

---

# 19. Exigences de continuité

La plateforme doit disposer de mécanismes permettant :

- sauvegarde ;
- restauration ;
- reconstruction ;
- validation de reprise.

Principe :

```text
Backup
  |
  v
Restore
  |
  v
Validation
  |
  v
Evidence
```

Un backup sans test de restauration ne constitue pas une preuve suffisante de recoverability.

---

# 20. RGPD — objectif

Le RGPD doit être intégré au projet comme une exigence d'architecture et non comme une documentation ajoutée uniquement en fin de projet.

Le cycle recherché est :

```text
Personal Data
      |
      v
Purpose
      |
      v
Legal Basis
      |
      v
Processing
      |
      v
Protection
      |
      v
Retention
      |
      v
Deletion
```

---

# 21. Registre RGPD

Le projet possède un registre dédié :

```text
REGISTRE-RGPD.md
```

Le registre doit permettre d'identifier, lorsque applicable :

- traitement ;
- finalité ;
- catégories de données ;
- personnes concernées ;
- base légale ;
- destinataires ;
- durée de conservation ;
- mesures de sécurité ;
- transferts ;
- responsables.

---

# 22. Minimisation des données

Principe :

```text
Collect Everything
      X

Collect What Is Necessary
      ✓
```

Une donnée ne doit être collectée que si elle répond à une finalité identifiée.

---

# 23. Limitation de finalité

Les données collectées pour un objectif ne doivent pas être réutilisées arbitrairement.

Chaque traitement doit être relié à une finalité.

```text
Data
 |
 v
Defined Purpose
```

---

# 24. Durée de conservation

Les données ne doivent pas être conservées indéfiniment sans justification.

Le projet doit pouvoir distinguer :

```text
Operational Retention
Legal Retention
Analytics Retention
Backup Retention
Log Retention
AI / ML Data Retention
```

---

# 25. Droits des personnes

Lorsque le traitement contient des données personnelles, l'architecture doit permettre de prendre en compte les droits applicables, notamment selon le contexte :

- accès ;
- rectification ;
- effacement ;
- limitation ;
- opposition ;
- portabilité lorsque applicable.

L'implémentation dépend du type de traitement.

---

# 26. Sécurité des données personnelles

Les mesures pertinentes peuvent comprendre :

```text
RBAC
TLS
Secrets
Audit Logs
Network Controls
Backup
Access Control
Pseudonymisation
Anonymisation
```

La mesure réellement utilisée doit être démontrée.

---

# 27. Données et IA

L'utilisation de données personnelles dans des workflows AI nécessite une attention supplémentaire.

Avant utilisation :

```text
Dataset
  |
  v
Contains Personal Data?
  |
 +------+------+
 |             |
NO            YES
 |             |
 v             v
Proceed     RGPD Analysis
                 |
                 v
           AI Governance
```

---

# 28. RAG et confidentialité

Un système RAG ne doit pas rendre accessible un document simplement parce qu'il est présent dans l'index.

Le modèle de sécurité doit être :

```text
User
 |
 v
Authorization
 |
 v
Permitted Documents
 |
 v
Retrieval
 |
 v
LLM
```

et non :

```text
User
 |
 v
All Vector Data
```

---

# 29. Accessibilité — objectif

L'accessibilité doit permettre aux personnes en situation de handicap d'utiliser les interfaces et livrables concernés.

Les catégories à considérer incluent notamment :

- handicap visuel ;
- handicap auditif ;
- handicap moteur ;
- handicap cognitif.

---

# 30. Accessibilité des interfaces

Lorsqu'une interface web est développée, les points à prendre en compte comprennent notamment :

- navigation clavier ;
- focus visible ;
- labels ;
- structure sémantique ;
- alternatives textuelles ;
- contraste suffisant ;
- formulaires compréhensibles ;
- messages d'erreur exploitables ;
- absence de dépendance exclusive à la couleur ;
- zoom ;
- responsive design.

---

# 31. Navigation clavier

Les fonctionnalités essentielles doivent pouvoir être utilisées sans dépendance exclusive à la souris.

Exemples :

```text
TAB
SHIFT + TAB
ENTER
SPACE
ESC
```

selon le composant.

---

# 32. HTML sémantique

Préférer :

```html
<button>Search</button>
```

à un élément générique simulant un bouton sans sémantique appropriée.

La sémantique native facilite :

- navigation clavier ;
- technologies d'assistance ;
- maintenance.

---

# 33. Formulaires

Chaque champ doit avoir une identification compréhensible.

Exemple :

```html
<label for="city">Ville</label>
<input id="city" name="city" type="text">
```

Les erreurs doivent être explicites et ne pas dépendre uniquement d'une couleur.

---

# 34. Images et diagrammes

Les images informatives doivent disposer d'une alternative ou d'une explication textuelle appropriée lorsque nécessaire.

Les diagrammes d'architecture possèdent déjà une documentation textuelle associée dans le projet.

Cela facilite leur compréhension même lorsque le rendu graphique n'est pas directement exploitable.

---

# 35. Documents techniques

L'accessibilité concerne également la documentation.

Les documents doivent privilégier :

- titres structurés ;
- tableaux compréhensibles ;
- texte explicite ;
- code correctement délimité ;
- langage cohérent ;
- hiérarchie logique.

Markdown facilite cette structuration.

---

# 36. Tests d'accessibilité

Les preuves pourront comprendre :

```text
Keyboard navigation test
Semantic HTML review
Form label review
Contrast test
Responsive test
Accessibility audit
```

Les tests doivent être exécutés sur l'interface réellement développée.

Ils ne doivent pas être déclarés réussis avant exécution.

---

# 37. Exigences d'éco-conception

Même si l'éco-conception possède son propre livrable, elle constitue également une exigence non fonctionnelle.

Principes :

- éviter les traitements inutiles ;
- limiter la rétention inutile ;
- choisir des modèles AI adaptés ;
- contrôler les ressources ;
- limiter les logs inutiles ;
- éviter les technologies sans besoin ;
- réutiliser l'infrastructure existante lorsque pertinent.

---

# 38. Traçabilité des exigences

Le modèle cible est :

```text
Requirement
    |
    v
Architecture Component
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

Exemple :

```text
REQ-OBS-001
Service must expose metrics
        |
        v
Prometheus instrumentation
        |
        v
Prometheus target
        |
        v
Query / Dashboard
        |
        v
Evidence
```

---

# 39. Exemple RGPD

```text
REQ-RGPD-001

Personal data must have a defined retention policy.
```

Traçabilité :

```text
REQ-RGPD-001
      |
      v
REGISTRE-RGPD
      |
      v
Retention Rule
      |
      v
Implementation
      |
      v
Verification
```

---

# 40. Exemple sécurité

```text
REQ-SEC-001

External application traffic must use TLS.
```

Traçabilité :

```text
REQ-SEC-001
      |
      v
cert-manager
      |
      v
Ingress TLS
      |
      v
HTTPS Test
      |
      v
Evidence
```

---

# 41. Exemple accessibilité

```text
REQ-ACC-001

Primary application functions must be keyboard accessible.
```

Traçabilité :

```text
REQ-ACC-001
      |
      v
Accessible UI Implementation
      |
      v
Keyboard Test
      |
      v
Evidence
```

---

# 42. Matrice synthétique

| Domaine | Exigence principale | Réponse |
|---|---|---|
| Business | Centralisation | Enterprise Platform |
| Application | Services structurés | API architecture |
| Data | Pipeline gouverné | PostgreSQL + Airflow + dbt |
| Metadata | Catalogue / lineage | OpenMetadata |
| AI | IA gouvernée | MLflow + Ollama |
| Sovereignty | Traitement local | Local-first AI |
| Infrastructure | Orchestration | Kubernetes |
| Deployment | Reproductibilité | GitOps |
| Security | Contrôle d'accès | RBAC / TLS / Secrets |
| Observability | Metrics/logs/traces | Observability stack |
| Recovery | Restauration | Backup / DR |
| RGPD | Protection données | Register + controls |
| Accessibility | Usage PSH | Accessible UI requirements |
| Eco-design | Ressources maîtrisées | Capacity / lifecycle controls |

---

# 43. Preuves existantes

## Traçabilité vers les réalisations

| Exigence | Réponse actuelle | Preuve |
|---|---|---|
| Identifier l'acteur | Compte `utilisateur`, JWT et vérification du compte actif | Documentation sécurité applicative |
| Contrôler les rôles | Dépendances `require_roles` dans les routes métier | `src/api/core/dependencies.py` et tests RBAC |
| Tracer les opérations | Audit des présentations, recommandations et visites | Rapport runtime des recommandations et tests Visite |
| Maintenir la qualité Data | Contrôles SQL par couche et tests dbt | Architecture Data implémentée |
| Permettre la reprise | Sauvegarde externe et restauration isolée | Rapport PRA PostgreSQL |

Références :

```text
../../../60-SECURITY/SECURITY-RBAC-AUDIT-IMPLEMENTATION-EVIDENCE.md
../../../60-SECURITY/RECOMMENDATION-AUDIT-RUNTIME-EVIDENCE.md
../../../40-DATA/ARCHITECTURE-DATA-IMPLEMENTEE.md
../../../PCA PRA/PCA-PRA-POSTGRESQL.md
../../03-BC03/C6-Tests-Executes/visite-audit-2026-09-09/README.md
```

L'accès par rôle ne couvre pas encore tous les contrôles de propriété des ressources. Les droits des personnes, la rétention et l'accessibilité restent à démontrer pour leur périmètre propre.

Les preuves documentaires comprennent :

```text
Architecture documentation
Security documentation
Data Governance
Data Security
AI Governance
AI Security
Risk Management
Backup / DR
Technology Decisions
ADR
REGISTRE-RGPD
CAHIER-DES-CHARGES-TECHNIQUE
```

---

# 44. Preuves à consolider

Les preuves techniques devront notamment couvrir :

```text
TLS
RBAC
Secrets
Data Quality
Data lineage
Retention
Backup / Restore
Application tests
Accessibility tests
AI security
```

Le statut doit refléter la réalité :

```text
DOCUMENTED
IMPLEMENTED
TESTED
EVIDENCED
```

Ces statuts ne sont pas équivalents.

---

# 45. Critères d'acceptation du cahier des charges

Une exigence est suffisamment définie lorsqu'elle est :

- compréhensible ;
- non ambiguë ;
- justifiée ;
- testable ;
- traçable ;
- liée à un besoin.

Le cycle complet est :

```text
Defined
  |
  v
Implemented
  |
  v
Tested
  |
  v
Evidenced
```

---

# 46. État actuel

| Domaine | Statut |
|---|---|
| Cahier des charges technique | EXIGENCES DOCUMENTÉES / FICHIER AUTONOME À RATTACHER |
| Architecture requirements | DOCUMENTÉS |
| Data requirements | DOCUMENTÉS |
| AI requirements | DOCUMENTÉS |
| Security requirements | DOCUMENTÉS |
| Observability requirements | DOCUMENTÉS |
| RGPD register | RÉFÉRENCÉ / FICHIER AUTONOME À RATTACHER |
| Data security | DOCUMENTÉE |
| AI sovereignty | DOCUMENTÉE |
| Accessibility requirements | BASELINE DOCUMENTÉE |
| Accessibility implementation | À ÉVALUER SUR L'APPLICATION |
| Accessibility tests | À EXÉCUTER |
| RGPD runtime evidence | À CONSOLIDER |
| Requirement → Test traceability | PARTIELLE — SÉCURITÉ, AUDIT ET DATA RÉFÉRENCÉS |

---

# 47. Points de vigilance

Le projet ne doit pas confondre :

```text
Documented Requirement
```

avec :

```text
Implemented Requirement
```

ni :

```text
Implemented
```

avec :

```text
Tested and Evidenced
```

Pour la soutenance, les affirmations doivent correspondre à l'état réel.

---

# 48. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Need
 |
 v
Requirement
 |
 +-------------+
 |             |
 v             v
Technical    Regulatory
 |             |
 |        +----+----+
 |        |         |
 v        v         v
Impl.    RGPD   Accessibility
 |        |         |
 +--------+---------+
          |
          v
         Test
          |
          v
       Evidence
```

---

# 49. Conclusion

Le cahier des charges ne constitue pas uniquement une liste de fonctionnalités.

Il définit les conditions dans lesquelles la solution doit être :

```text
Functional
Secure
Governed
Observable
Recoverable
Compliant
Accessible
Maintainable
```

Le RGPD et l'accessibilité font partie des exigences du système et doivent être reliés à l'implémentation et aux tests.

---

**BC02 / C3 — Cahier des charges, RGPD et accessibilité PSH : DOCUMENTATION BASELINE COMPLETE**
