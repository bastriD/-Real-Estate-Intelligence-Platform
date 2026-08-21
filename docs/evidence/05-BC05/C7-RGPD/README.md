# BC05 — C7 — RGPD

**Bloc de compétences :** BC05  
**Compétence :** C7 — Intégrer les exigences RGPD dans la conception, le traitement et l'exploitation des données  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Version :** 1.0  
**Statut :** Baseline documentaire — preuves opérationnelles à consolider

---

# 1. Objectif

Ce dossier démontre que la protection des données personnelles est intégrée à l'architecture Data et AI du projet.

Le RGPD n'est pas traité comme un document isolé ajouté après l'implémentation.

Le cycle attendu est :

```text
Data
 |
 v
Purpose
 |
 v
Legal Basis
 |
 v
Collection
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

L'objectif est de pouvoir répondre à :

```text
What personal data is processed?
Why?
Where?
By whom?
For how long?
With what controls?
Can it be deleted or corrected?
```

---

# 2. Source principale

Le livrable principal existant est :

```text
REGISTRE-RGPD.md
```

Ce document doit rester la source de vérité pour le registre des traitements.

Le présent dossier sert à relier ce registre aux composants techniques du projet.

---

# 3. Documents complémentaires

Références Data :

```text
../../../40-DATA/04-Data-Governance.md
../../../40-DATA/09-Data-Lifecycle.md
../../../40-DATA/10-Data-Security.md
```

Références Security :

```text
../../../60-SECURITY/01-Security-Architecture.md
../../../60-SECURITY/02-Identity-and-Access-Management.md
../../../60-SECURITY/04-Secret-Management.md
../../../60-SECURITY/06-Application-Security.md
```

Références AI :

```text
../../../50-AI/07-AI-Governance.md
../../../50-AI/08-AI-Security.md
```

Modèle Data :

```text
../C1-MCD-Migration-SQL/MCD-MERISE-PROJET.md
../C1-MCD-Migration-SQL/MLD-PROJET.md
../C1-MCD-Migration-SQL/MPD-POSTGRESQL.md
```

---

# 4. Données personnelles du projet

Les principales données personnelles peuvent être présentes dans :

```text
CLIENT
CHASSEUR
MANDAT
PRESENTATION
DOCUMENT
```

---

# 5. CLIENT

Données personnelles possibles :

```text
nom
prenom
email
telephone
```

Potentiellement :

```text
commentaires
preferences
feedback
```

selon l'application réellement implémentée.

---

# 6. CHASSEUR

Données personnelles possibles :

```text
nom
prenom
email
telephone
```

Ces données sont principalement nécessaires à l'organisation et à l'attribution des mandats.

---

# 7. MANDAT

Le mandat peut indirectement relier :

```text
CLIENT
```

à :

```text
criteria
business history
status
```

Même si certaines colonnes ne contiennent pas directement de nom, l'ensemble peut rester rattachable à une personne.

---

# 8. PRESENTATION

Les champs tels que :

```text
feedback_client
commentaire_chasseur
```

peuvent contenir des données personnelles ou des informations sensibles saisies en texte libre.

Ils doivent donc être traités avec attention.

---

# 9. DOCUMENT

Les documents peuvent contenir des informations personnelles supplémentaires.

Exemples :

```text
name
address
contact information
contractual information
financial information
diagnostic or legal documents
```

La simple présence d'un fichier dans le stockage ne signifie pas qu'il peut être librement exploité par l'IA.

---

# 10. Catégories de données

Le projet doit pouvoir distinguer :

```text
Identification Data
Contact Data
Business Data
Search Preferences
Contractual Data
Documents
Technical Data
Logs
AI Interaction Data
```

---

# 11. Finalité

Chaque traitement doit avoir une finalité explicite.

Exemples :

```text
Manage real-estate search mandate
Search matching properties
Communicate with client
Generate business analysis
Improve service quality
Operate platform
```

Une donnée ne doit pas être collectée sans objectif identifié.

---

# 12. Limitation de finalité

Une donnée collectée pour :

```text
real-estate search
```

ne doit pas être réutilisée arbitrairement pour :

```text
marketing
AI training
third-party enrichment
```

sans analyse appropriée.

---

# 13. Base légale

Le registre RGPD doit préciser la base légale applicable à chaque traitement.

Exemples possibles selon le traitement :

```text
Contract
Legal Obligation
Legitimate Interest
Consent
```

La base légale exacte doit rester celle du registre et du contexte réel.

---

# 14. Minimisation

Principe :

```text
Collect only what is necessary
```

Exemple :

un modèle de matching n'a généralement pas besoin de :

```text
client email
client phone
full identity
```

pour calculer un score immobilier.

---

# 15. Matching et minimisation

Le flux préféré est :

```text
CLIENT
  |
  v
Relevant Search Criteria
  |
  v
Matching Engine
```

et non :

```text
Entire Client Record
  |
  v
AI Model
```

---

# 16. Données d'entraînement

Un dataset ML ne doit contenir que les informations nécessaires.

Les données directement identifiantes doivent être évitées si elles n'apportent aucune valeur au modèle.

---

# 17. Pseudonymisation

Pour certains traitements analytiques ou ML, l'identifiant métier peut être remplacé par un identifiant technique.

Exemple :

```text
client_id = 42
```

sans transférer :

```text
name
email
phone
```

dans le dataset.

---

# 18. Anonymisation

Si les données peuvent être véritablement anonymisées, elles peuvent être utilisées pour certains usages sans conserver la possibilité d'identifier une personne.

Mais :

```text
Pseudonymized
!=
Anonymous
```

La pseudonymisation reste généralement soumise au RGPD.

---

# 19. OLTP

Le schéma :

```text
real_estate
```

contient les données opérationnelles.

L'accès doit être limité selon le rôle.

---

# 20. OLAP

Lors du chargement vers :

```text
warehouse
analytics
```

les colonnes personnelles doivent être examinées.

Il ne faut pas recopier automatiquement toutes les colonnes OLTP.

---

# 21. Exemple minimisation OLAP

Au lieu de :

```text
dim_client
├── name
├── firstname
├── email
├── phone
├── address
```

si ces informations ne sont pas nécessaires, préférer :

```text
dim_client
├── client_key
├── source_client_id
└── status
```

---

# 22. Analytics

Un dashboard métier doit utiliser autant que possible des informations :

```text
aggregated
minimized
non-identifying
```

si l'identification individuelle n'est pas nécessaire.

---

# 23. Data Warehouse et duplication

La duplication OLTP → OLAP augmente la surface de traitement.

Chaque duplication doit donc répondre à :

```text
Why is this field copied?
```

---

# 24. AI

Les workflows AI augmentent les risques liés à :

- duplication ;
- prompts ;
- embeddings ;
- caches ;
- logs ;
- external APIs ;
- model training.

Ils nécessitent une analyse spécifique.

---

# 25. IA locale

Le traitement local constitue un mécanisme important de maîtrise.

```text
Private Data
    |
    v
Local Infrastructure
    |
    v
Ollama / Model
```

Cela réduit les transferts vers des fournisseurs externes.

---

# 26. IA externe

Si une API AI externe est utilisée :

```text
Data
 |
 v
Classification
 |
 v
External Transfer Allowed?
 |
 +----+----+
 |         |
NO        YES
 |         |
 v         v
Local    Controlled External Use
```

L'utilisation externe doit être explicitement gouvernée.

---

# 27. Prompt Data

Un prompt peut contenir des données personnelles.

Il doit donc être traité comme une donnée soumise aux mêmes exigences de :

```text
access
logging
retention
security
```

---

# 28. Logs AI

À éviter :

```text
log full prompts
log full documents
log full personal records
```

sauf besoin clairement justifié et protégé.

---

# 29. Embeddings

Un embedding peut révéler indirectement des informations sur le contenu source.

Il ne doit donc pas être considéré automatiquement comme anonyme.

---

# 30. Vector Database

Les vecteurs doivent respecter :

```text
authorization
retention
deletion
classification
```

comme les documents sources.

---

# 31. RAG

Le modèle correct est :

```text
Authenticated User
        |
        v
Authorization
        |
        v
Allowed Documents
        |
        v
Retrieval
        |
        v
LLM
```

---

# 32. RAG interdit

À éviter :

```text
User
 |
 v
Search across all embeddings
 |
 v
LLM
```

puis demander au LLM de ne pas révéler les documents interdits.

Le contrôle doit être appliqué avant le contenu génératif.

---

# 33. indexable_ia

Le modèle prévoit :

```text
document.indexable_ia
```

Ce champ permet de distinguer :

```text
stored document
```

de :

```text
document eligible for AI indexing
```

Il ne remplace pas la gestion des permissions.

---

# 34. Classification document

Le MPD prévoit :

```text
PUBLIC
INTERNE
CONFIDENTIEL
RESTREINT
```

Cette classification peut influencer :

```text
AI eligibility
access
sharing
retention
```

---

# 35. Droits des personnes

Selon le traitement, il faut pouvoir prendre en compte les droits applicables :

```text
Access
Rectification
Erasure
Restriction
Objection
Portability
```

dans les limites et conditions prévues par le RGPD.

---

# 36. Droit d'accès

Le système doit permettre d'identifier les données détenues concernant une personne lorsque nécessaire.

Le MCD et la traçabilité des relations contribuent à cette capacité.

---

# 37. Rectification

Certaines données doivent pouvoir être corrigées.

Exemples :

```text
email
telephone
search criteria
```

L'historique métier doit cependant être conservé lorsque cela est légalement ou fonctionnellement nécessaire.

---

# 38. Effacement

Le droit à l'effacement ne signifie pas nécessairement :

```text
DELETE everything immediately
```

dans tous les cas.

Il faut tenir compte :

- obligations légales ;
- contrats ;
- historique nécessaire ;
- sauvegardes ;
- délais techniques.

---

# 39. Erasure Workflow

Architecture logique :

```text
Request
 |
 v
Identity Verification
 |
 v
Scope Identification
 |
 v
Legal / Retention Check
 |
 v
Delete / Anonymize
 |
 v
Verify
 |
 v
Evidence
```

---

# 40. Data Lineage et effacement

La capacité à supprimer correctement des données nécessite de connaître :

```text
OLTP
Staging
Warehouse
Analytics
Documents
Vectors
Logs
Backups
```

où elles peuvent avoir été propagées.

---

# 41. OpenMetadata

OpenMetadata peut contribuer à identifier :

```text
data assets
owners
lineage
classifications
```

Cela facilite l'analyse d'impact.

---

# 42. Conservation

Les données ne doivent pas être conservées indéfiniment sans justification.

Les principales catégories à gérer sont :

```text
Operational Data
Analytics
Documents
Logs
Traces
Metrics
ML Datasets
Model Artifacts
Backups
AI Inputs / Outputs
```

---

# 43. Politique de rétention

Chaque catégorie importante doit avoir :

```text
Purpose
Retention Duration
Deletion / Archive Rule
Owner
```

La durée exacte doit provenir du registre et des obligations applicables.

---

# 44. Logs

Les logs opérationnels doivent disposer d'une durée de conservation maîtrisée.

Loki ne doit pas devenir une archive infinie de données potentiellement personnelles.

---

# 45. Traces

Les traces peuvent contenir :

```text
URL
parameters
identifiers
service metadata
```

Elles doivent également être analysées sous l'angle RGPD.

---

# 46. Metrics

Les métriques devraient idéalement éviter les labels à forte cardinalité contenant des identifiants personnels.

À éviter :

```text
client_email="..."
```

comme label Prometheus.

---

# 47. Backups

Une donnée supprimée de la base active peut rester temporairement dans un backup.

La stratégie doit définir comment gérer cette situation selon :

- politique de rétention ;
- restaurations ;
- exigences réglementaires.

---

# 48. Restore

Une restauration ancienne peut réintroduire une donnée supprimée.

Le PRA doit donc prévoir une procédure de réconciliation lorsque nécessaire.

---

# 49. Sécurité

Le RGPD exige des mesures de sécurité adaptées.

Le projet utilise ou prévoit notamment :

```text
RBAC
TLS
Secrets Management
Network Controls
Application Authorization
Monitoring
Backup
```

---

# 50. Confidentialité

Les données ne doivent être accessibles qu'aux personnes et services autorisés.

---

# 51. Intégrité

Les mécanismes :

```text
PK
FK
CHECK
UNIQUE
Data Quality
Checksums
```

contribuent à protéger l'intégrité.

---

# 52. Disponibilité

La disponibilité est également une dimension de la protection des données.

Les mécanismes incluent :

```text
Backup
Restore
PRA
High Availability
Monitoring
```

---

# 53. Encryption in Transit

Les communications sensibles doivent utiliser :

```text
TLS
```

lorsque applicable.

---

# 54. Encryption at Rest

Le besoin de chiffrement au repos doit être évalué pour :

```text
PostgreSQL
MinIO
Backups
Host storage
```

selon le niveau de sensibilité.

---

# 55. Secrets

Les credentials ne doivent pas apparaître dans :

```text
Git
code
documentation
container images
logs
```

---

# 56. Access Control

Le contrôle d'accès doit exister à plusieurs niveaux :

```text
Application
Database
Kubernetes
Object Storage
Metadata Platform
AI Services
```

---

# 57. Least Privilege

Les services doivent utiliser uniquement les permissions nécessaires.

Exemple :

```text
analytics service
```

n'a pas nécessairement besoin de modifier :

```text
client
```

dans OLTP.

---

# 58. Audit

Les actions sensibles peuvent nécessiter une traçabilité.

Exemples :

```text
admin access
data export
data deletion
permission change
model promotion
```

---

# 59. Breach Management

Un incident impliquant des données personnelles doit pouvoir être identifié et analysé.

Processus :

```text
Detection
 |
 v
Containment
 |
 v
Impact Analysis
 |
 v
Decision / Notification Process
 |
 v
Remediation
```

Les obligations exactes doivent être gérées selon le cadre applicable.

---

# 60. Privacy by Design

Le projet applique :

```text
Privacy
before
implementation completion
```

Exemples :

```text
data minimization in MCD
document classification
AI local-first
controlled logging
warehouse minimization
```

---

# 61. Privacy by Default

Les valeurs par défaut doivent éviter l'exposition inutile.

Exemple :

```text
indexable_ia = FALSE
```

est préférable à :

```text
indexable_ia = TRUE
```

pour tous les documents par défaut.

---

# 62. Exemple MPD

Le MPD prévoit :

```sql
indexable_ia BOOLEAN NOT NULL DEFAULT FALSE
```

Cela matérialise un choix Privacy/Security by Default.

---

# 63. Consentement

Le MCD contient :

```text
consentement_contact
```

Il faut toutefois éviter de traiter un simple booléen comme preuve universelle de tout consentement RGPD.

Un consentement valide dépend notamment :

- finalité ;
- information ;
- liberté ;
- traçabilité ;
- retrait.

---

# 64. Marketing

Un consentement de contact métier ne doit pas être réutilisé automatiquement comme consentement :

```text
marketing
AI training
external sharing
```

---

# 65. Data Processing Inventory

Le registre doit identifier chaque traitement important.

Exemples :

```text
Client management
Mandate management
Property matching
Analytics
AI-assisted matching
Document processing
Monitoring
Backup
```

---

# 66. Sous-traitants

Si des services externes sont utilisés, ils doivent être identifiés lorsque pertinent.

Exemples possibles :

```text
cloud provider
external AI provider
email provider
storage provider
```

Dans la plateforme locale, une grande partie du traitement reste interne.

---

# 67. Transferts

Un transfert vers une API externe doit être distingué du traitement local.

```text
Local:
Data stays within controlled platform

External:
Data leaves controlled boundary
```

---

# 68. Souveraineté

La souveraineté n'est pas strictement identique au RGPD, mais les deux se rejoignent sur :

```text
control
location
provider dependency
data transfer
```

La souveraineté détaillée est traitée dans :

```text
../C8-Souverainete-Securite-IA/
```

---

# 69. Données de test

Les environnements de test doivent privilégier :

```text
synthetic
anonymized
pseudonymized
```

datasets lorsque possible.

---

# 70. Synthetic Data

La génération de données synthétiques pour :

```text
benchmark
OLAP
ML training demo
```

permet de limiter l'utilisation inutile de données personnelles réelles.

---

# 71. ML Dataset

Le dataset final doit disposer d'une description.

Exemple :

```text
dataset name
purpose
source
columns
personal-data status
retention
version
```

---

# 72. Dataset Card

Une fiche dataset peut compléter la Model Card.

Elle permet de documenter :

```text
origin
schema
quality
bias
privacy
limitations
```

---

# 73. AI Training

Avant entraînement :

```text
Dataset
 |
 v
Personal Data?
 |
 +----+----+
 |         |
NO        YES
 |         |
 v         v
Train   Need Assessment
```

---

# 74. Feature Selection

Une feature ne doit pas être retenue uniquement parce qu'elle améliore la métrique.

Il faut vérifier :

```text
Is it necessary?
Is it lawful?
Can it introduce bias?
Does it expose identity?
```

---

# 75. Automated Decision

Le programme de matching est conçu principalement comme :

```text
Decision Support
```

avec validation humaine.

Cela doit être clairement présenté dans la documentation.

---

# 76. Profilage

Si une fonctionnalité évolue vers une prise de décision entièrement automatisée produisant des effets significatifs, une analyse supplémentaire sera nécessaire.

Le projet MVP ne doit pas être présenté comme tel si ce n'est pas le cas.

---

# 77. Human-in-the-loop

Architecture :

```text
Model
 |
 v
Recommendation
 |
 v
Chasseur
 |
 v
Business Decision
```

Cette séparation constitue également un mécanisme de gouvernance.

---

# 78. Data Subject Request Evidence

Une preuve future peut être un scénario technique démontrant :

```text
find client
find mandates
find request versions
find presentations
identify related data
```

sans nécessairement utiliser de vraies données personnelles.

---

# 79. Example SQL inventory

Une future procédure peut utiliser des requêtes telles que :

```sql
SELECT *
FROM real_estate.client
WHERE id_client = :id;
```

puis suivre les relations.

La procédure finale doit être testée avec des données synthétiques.

---

# 80. Deletion Test

Une preuve intéressante peut être :

```text
Create synthetic person
      |
      v
Create related data
      |
      v
Execute deletion/anonymization workflow
      |
      v
Verify remaining data
```

---

# 81. Retention Test

Un autre scénario peut vérifier qu'une règle de purge sélectionne correctement les données dépassant la rétention.

---

# 82. AI Data Leakage Test

Une future preuve sécurité/RGPD peut vérifier qu'une requête AI ne retourne pas des documents appartenant à un utilisateur non autorisé.

---

# 83. Logging Test

Vérifier qu'une requête métier ne fait pas apparaître :

```text
email
phone
token
password
```

dans les logs lorsque ces informations ne sont pas nécessaires.

---

# 84. OpenMetadata Evidence

Une preuve peut montrer :

```text
PII classification
owner
description
lineage
```

sur une table contenant des données personnelles.

---

# 85. Evidence Directory

Le dossier pourra plus tard contenir :

```text
C7-RGPD/
│
├── README.md
├── processing-map.md
├── data-classification.md
├── retention-matrix.md
├── erasure-procedure.md
├── tests/
│   ├── erasure-test.txt
│   ├── logging-test.txt
│   └── ai-access-test.txt
└── evidence/
    └── ...
```

Seulement après implémentation réelle.

---

# 86. Matrice données

| Entité | Données personnelles | Besoin principal |
|---|---|---|
| CLIENT | Oui | Gestion client |
| CHASSEUR | Oui | Organisation |
| MANDAT | Indirectes | Relation contractuelle |
| DEMANDE_VERSION | Potentiellement | Recherche immobilière |
| BIEN | Généralement non | Bien immobilier |
| PRESENTATION | Potentiellement | Matching / feedback |
| DOCUMENT | Potentiellement élevé | Information associée |
| SOURCE | Généralement non | Provenance |

---

# 87. Matrice traitement

| Traitement | Données | Finalité |
|---|---|---|
| Client management | CLIENT | Gestion relation |
| Mandate | CLIENT + MANDAT | Exécution mission |
| Matching | DEMANDE + BIEN | Trouver biens |
| Analytics | données minimisées | Pilotage |
| ML | features sélectionnées | Amélioration matching |
| RAG | documents autorisés | Assistance |
| Monitoring | données techniques | Exploitation |
| Backup | données système | Continuité |

---

# 88. Matrice localisation

| Donnée | Stockage cible |
|---|---|
| Client operational data | PostgreSQL |
| Property data | PostgreSQL |
| Document metadata | PostgreSQL |
| Documents | MinIO |
| Warehouse data | PostgreSQL |
| ML metadata | MLflow DB |
| ML artifacts | MinIO |
| Embeddings future | pgvector/Qdrant |
| Logs | Loki |
| Metrics | Prometheus |
| Traces | Tempo |

---

# 89. Matrice contrôle

| Risque | Contrôle |
|---|---|
| Excess data collection | Minimization |
| Unauthorized access | RBAC |
| Data interception | TLS |
| Credential leak | Secret management |
| AI external leakage | Local-first |
| RAG leakage | Authorization before retrieval |
| Infinite retention | Lifecycle rules |
| Log exposure | Secure logging |
| Backup exposure | Protected backups |

---

# 90. Preuves finales attendues

Pour démontrer cette compétence :

```text
RGPD register
+
Data mapping
+
MCD classification
+
Security controls
+
Retention rules
+
AI data-flow analysis
+
At least one executed compliance-oriented test
```

---

# 91. Ce qui ne suffit pas

Les affirmations suivantes ne suffisent pas seules :

```text
"We comply with GDPR."

"We use local AI."

"We have a consent checkbox."

"We encrypt traffic."

"We have a privacy policy."
```

La conformité doit être reliée aux traitements réellement implémentés.

---

# 92. Traceability

Le modèle attendu est :

```text
Processing
   |
   v
Personal Data
   |
   v
Purpose / Legal Basis
   |
   v
Technical Component
   |
   v
Control
   |
   v
Evidence
```

---

# 93. Exemple

```text
Property Matching
      |
      v
Client Search Criteria
      |
      v
Contract / appropriate basis
      |
      v
PostgreSQL + Matching Service
      |
      v
Minimized feature set
      |
      v
Access / processing evidence
```

---

# 94. Relation C1

Le MCD identifie les lieux de stockage et les relations entre les données.

---

# 95. Relation C3

Le Data Warehouse doit éviter de recopier inutilement des données personnelles.

---

# 96. Relation C5

Le matching doit utiliser uniquement les features nécessaires.

---

# 97. Relation C6

Le programme IA doit contrôler :

```text
inputs
logs
datasets
artifacts
external communications
```

---

# 98. Relation C8

C8 approfondit la protection spécifique des traitements IA et les enjeux de souveraineté.

---

# 99. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Personal Data
      |
      v
Purpose
      |
      v
Storage / Processing
      |
      v
Security & Privacy Controls
      |
      v
Retention / Rights
      |
      v
Technical Evidence
```

---

# 100. Statut actuel

| Élément | Statut |
|---|---|
| RGPD register | EXISTANT |
| Personal data inventory | BASELINE DÉFINIE |
| Data minimization | DOCUMENTÉE |
| OLTP privacy | DOCUMENTÉE |
| OLAP minimization | DOCUMENTÉE |
| AI privacy | DOCUMENTÉE |
| RAG authorization | DOCUMENTÉE |
| Local AI strategy | DOCUMENTÉE |
| Retention principles | DOCUMENTÉS |
| Rights workflow | DOCUMENTÉ |
| Security controls | DOCUMENTÉS |
| Runtime classifications | À CONSOLIDER |
| Retention implementation | À PRODUIRE |
| Erasure test | À PRODUIRE |
| AI access test | À PRODUIRE |
| Compliance evidence | À PRODUIRE |

---

# 101. Conclusion

Le RGPD est intégré au projet selon une logique :

```text
Privacy by Design
+
Privacy by Default
+
Data Minimization
+
Controlled Access
+
Lifecycle Management
+
Local-first AI
+
Traceability
```

Le système doit conserver uniquement les données nécessaires, limiter leur propagation et appliquer les mêmes principes aux bases de données, analytics, documents, logs et traitements IA.

Les preuves finales devront être issues de l'implémentation réelle et de tests exécutés.

---

**BC05 / C7 — RGPD — DOCUMENTATION BASELINE COMPLETE**