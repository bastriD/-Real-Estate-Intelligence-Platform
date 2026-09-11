# BC05 — C7 — RGPD

**Bloc de compétences :** BC05  
**Compétence :** Intégrer les exigences RGPD dans la conception, le traitement et l'exploitation des données  
**Projet :** Real Estate Intelligence Platform  
**Version :** 2.0  
**Statut :** Baseline documentaire alignée avec le Data Model V2 — preuves runtime à produire

---

# 1. Objectif

Ce dossier démontre que la protection des données personnelles est intégrée à l'architecture Data et IA du projet.

Le RGPD est traité selon une logique :

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
Deletion / Anonymization
```

Le système doit pouvoir répondre à :

```text
What personal data is processed?
Why?
Where?
By whom?
For how long?
With which technical controls?
Can it be corrected, exported or deleted?
```

---

# 2. Source de vérité RGPD

Le registre principal reste :

```text
REGISTRE-RGPD.md
```

Le fichier autonome n'est pas présent dans la copie locale consultée. Son rattachement et sa validation restent à compléter. Ce dossier ne remplace pas le registre.

Il relie les traitements RGPD :

```text
business
```

aux composants :

```text
database
analytics
AI
logs
documents
backups
```

---

# 3. Data Model V2 concerné

Le modèle métier cible contient :

```text
CLIENT
CHASSEUR
SECTEUR
MANDAT
MANDAT_SECTEUR
DEMANDE
DEMANDE_VERSION
SOURCE
BIEN
PRESENTATION
COMMENTAIRE
DOCUMENT
BAREME_COMMISSION
PAIEMENT
```

Toutes les entités ne contiennent pas directement des données personnelles, mais certaines peuvent être rattachées indirectement à une personne.

---

# 4. CLIENT

Données personnelles principales :

```text
nom
prenom
email
telephone
ville
consentement_contact
```

Le client est directement identifiable.

---

# 5. CHASSEUR

Données personnelles :

```text
nom
prenom
email
telephone
date_entree
```

Ces informations sont nécessaires à l'organisation interne et à l'exécution des mandats.

---

# 6. MANDAT

`MANDAT` relie :

```text
CLIENT
+
CHASSEUR
```

à un contrat.

Il contient donc des informations indirectement personnelles même si certaines colonnes sont purement métier.

---

# 7. DEMANDE

`DEMANDE` représente une recherche immobilière.

Elle est rattachée à :

```text
MANDAT
```

et donc indirectement à un client.

---

# 8. DEMANDE_VERSION

Les critères peuvent contenir :

```text
budget
location
property type
surface
rooms
preferences
```

Ces informations ne sont pas nécessairement identifiantes isolément, mais peuvent être rattachées à une personne via le mandat.

---

# 9. COMMENTAIRE

`COMMENTAIRE` est particulièrement sensible car il peut contenir du texte libre.

Exemples :

```text
client feedback
hunter notes
preferences
reasons for rejection
```

Le texte libre peut contenir des données personnelles supplémentaires non prévues dans le schéma.

---

# 10. PRESENTATION

`PRESENTATION` relie :

```text
DEMANDE_VERSION
+
BIEN
```

et peut donc faire partie de l'historique comportemental d'un client.

---

# 11. PAIEMENT

`PAIEMENT` contient des données financières liées à un mandat.

Exemples :

```text
montant_achat
montant_honoraires
montant_chasseur
dates de paiement
```

Ces données doivent être protégées avec un niveau de confidentialité élevé.

---

# 12. BAREME_COMMISSION

`BAREME_COMMISSION` est lié à :

```text
CHASSEUR
```

et contient des données de rémunération.

Il doit être traité comme une information interne sensible.

---

# 13. DOCUMENT

Les documents peuvent contenir :

```text
contracts
property diagnostics
photos
legal documents
financial information
personal information
```

La présence d'un document dans MinIO ou PostgreSQL ne signifie pas automatiquement qu'il peut être utilisé par l'IA.

---

# 14. SECTEUR

`SECTEUR` n'est généralement pas une donnée personnelle.

Cependant, lorsqu'un secteur est combiné avec une recherche très spécifique, il peut contribuer à réidentifier indirectement un client.

---

# 15. SOURCE / BIEN

Les données de biens et de sources sont généralement des données métier.

Néanmoins :

```text
contact seller
private owner information
```

provenant de certaines annonces peuvent devenir des données personnelles.

La normalisation doit donc distinguer :

```text
property metadata
```

de :

```text
personal contact data
```

---

# 16. Catégories de données

Le projet distingue :

```text
Identity Data
Contact Data
Contractual Data
Search Preferences
Financial Data
Property Data
Operational Metadata
Documents
AI Inputs / Outputs
Logs / Traces
```

---

# 17. Finalité

Chaque traitement doit avoir une finalité claire.

Exemples :

```text
manage client relationship
execute mandate
search properties
calculate commissions
manage payments
provide analytics
assist property matching
operate platform
```

---

# 18. Limitation de finalité

Une donnée collectée pour :

```text
property search
```

ne doit pas être réutilisée arbitrairement pour :

```text
marketing
external AI training
third-party profiling
```

sans analyse spécifique.

---

# 19. Minimisation

Principe :

```text
Collect only what is necessary.
Process only what is necessary.
Expose only what is necessary.
```

---

# 20. Exemple Matching

Le matching nécessite :

```text
budget
location
surface
rooms
preferences
property features
```

Il ne nécessite généralement pas :

```text
client email
client phone
full client identity
```

---

# 21. AI Data Flow

Préférer :

```text
CLIENT
   |
   v
DEMANDE_VERSION
   |
   v
Relevant Features
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

# 22. Pseudonymisation

Les datasets analytiques et ML peuvent utiliser :

```text
technical identifiers
```

au lieu de :

```text
names
emails
phones
```

---

# 23. Anonymisation

Important :

```text
Pseudonymized
!=
Anonymous
```

La pseudonymisation réduit le risque mais ne sort généralement pas les données du périmètre RGPD.

---

# 24. StarterPack Generated Data

Le générateur StarterPack produit :

```text
synthetic searches
synthetic announcements
```

Ces données sont particulièrement utiles pour :

```text
development
benchmark
ETL testing
ML technical validation
```

sans utiliser inutilement de vraies données personnelles.

---

# 25. Données synthétiques

Lorsqu'elles sont réellement synthétiques et non dérivées de personnes identifiables, elles réduisent fortement les risques de confidentialité.

Elles doivent cependant être clairement identifiées comme :

```text
synthetic test data
```

---

# 26. Environnements de développement

Les environnements :

```text
development
test
CI
benchmark
```

doivent privilégier :

```text
synthetic
anonymized
pseudonymized
```

datasets.

---

# 27. Production Data

Les données réelles ne doivent pas être copiées vers un environnement de développement sans justification et protection adéquate.

---

# 28. OLTP

Le schéma :

```text
real_estate
```

contient les données opérationnelles.

L'accès doit être limité par :

```text
application role
database role
least privilege
```

---

# 29. RAW

La zone RAW peut contenir des données sources potentiellement sensibles.

Elle doit être considérée comme :

```text
trusted infrastructure
but untrusted data content
```

---

# 30. STAGING

STAGING ne doit pas devenir une zone de duplication permanente.

Les données doivent y être conservées uniquement selon le besoin technique.

---

# 31. OLAP

Lors du passage vers :

```text
warehouse
analytics
```

les colonnes personnelles doivent être minimisées.

---

# 32. Exemple dim_client

Éviter si inutile :

```text
dim_client
├── nom
├── prenom
├── email
├── telephone
```

Préférer :

```text
dim_client
├── client_key
├── status
└── city / analytical segment
```

si cela suffit.

---

# 33. PAIEMENT dans OLAP

Les données financières peuvent être agrégées.

Exemple :

```text
fact_payment
```

peut contenir :

```text
purchase_amount
company_fee
hunter_payment
```

sans exposer directement les données d'identité du client.

---

# 34. Analytics

Les dashboards doivent privilégier :

```text
aggregated information
```

lorsque le détail individuel n'est pas nécessaire.

---

# 35. ML Training

Notre extension ML utilise des features minimisées.

Le dataset d'entraînement devrait éviter les identifiants directs.

---

# 36. ML Labels

Les labels peuvent provenir de :

```text
PRESENTATION
COMMENTAIRE
```

sans nécessiter de stocker :

```text
name
email
phone
```

dans le dataset.

---

# 37. MLflow

MLflow peut contenir :

```text
parameters
metrics
artifacts
dataset references
```

Les artifacts ne doivent pas intégrer involontairement des données personnelles inutiles.

---

# 38. Model Artifacts

Un modèle entraîné peut parfois mémoriser ou révéler certaines informations selon l'algorithme et les données.

Le dataset doit donc être minimisé avant entraînement.

---

# 39. Dataset Card

Chaque dataset ML important devra documenter :

```text
source
purpose
personal data
features
retention
limitations
```

---

# 40. Model Card

La Model Card doit inclure :

```text
privacy considerations
```

et les limites d'usage.

---

# 41. Ollama Local

Le projet privilégie :

```text
local inference
```

via Ollama pour les traitements internes lorsque pertinent.

Cela permet de limiter les transferts externes.

---

# 42. Local Does Not Remove GDPR

Même en local, il faut gérer :

```text
access
purpose
retention
security
logging
```

---

# 43. External AI

Une API externe doit être traitée comme :

```text
external data transfer / processing dependency
```

et non comme un composant transparent.

---

# 44. Prompt Data

Les prompts peuvent contenir des données personnelles.

Ils doivent respecter :

```text
minimization
access control
retention
logging policy
```

---

# 45. Prompt Logging

Éviter par défaut :

```text
full private prompts
```

dans les logs standards.

---

# 46. RAG

Architecture cible :

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

# 47. Authorization Before Retrieval

Principe :

```text
AUTHORIZATION
BEFORE
RETRIEVAL
```

Le LLM ne doit jamais servir de mécanisme de contrôle d'accès.

---

# 48. Document Classification

Les documents utilisent :

```text
PUBLIC
INTERNE
CONFIDENTIEL
RESTREINT
```

---

# 49. indexable_ia

Par défaut :

```text
FALSE
```

Cela matérialise :

```text
Privacy by Default
```

---

# 50. Embeddings

Un embedding ne doit pas être automatiquement considéré comme anonyme.

Il peut conserver une représentation du contenu source.

---

# 51. Vector Database

Les mêmes règles s'appliquent à :

```text
pgvector
Qdrant
```

concernant :

```text
access
retention
deletion
classification
```

---

# 52. Droit d'accès

Le système doit permettre d'identifier les données d'une personne dans :

```text
CLIENT
MANDAT
DEMANDE
PRESENTATION
COMMENTAIRE
PAIEMENT
DOCUMENT
```

selon les relations.

---

# 53. Rectification

Exemples :

```text
email
phone
search criteria
```

doivent pouvoir être corrigés selon les règles métier applicables.

---

# 54. Historisation vs rectification

La rectification ne signifie pas que tout historique doit être détruit.

Exemple :

```text
DEMANDE_VERSION
```

conserve volontairement l'historique des changements.

---

# 55. Effacement

L'effacement doit considérer :

```text
active database
warehouse
documents
vectors
logs
backups
```

---

# 56. Erasure Workflow

```text
Request
 |
 v
Identity Verification
 |
 v
Data Inventory
 |
 v
Retention / Legal Check
 |
 v
Delete / Anonymize
 |
 v
Verification
 |
 v
Evidence
```

---

# 57. Data Lineage

Une bonne traçabilité permet d'identifier :

```text
where personal data has propagated
```

par exemple :

```text
OLTP
 |
 v
STAGING
 |
 v
WAREHOUSE
```

---

# 58. OpenMetadata

OpenMetadata peut aider à documenter :

```text
PII classification
ownership
lineage
data assets
```

---

# 59. Conservation

Les catégories suivantes nécessitent des règles de rétention :

```text
client data
mandates
payments
comments
documents
raw files
warehouse data
logs
traces
ML datasets
model artifacts
backups
AI prompts
AI outputs
```

---

# 60. Retention Matrix

Chaque catégorie doit avoir :

```text
purpose
retention period
owner
deletion method
```

Les durées exactes doivent rester alignées avec le registre RGPD et les obligations métier.

---

# 61. PAIEMENT Retention

Les données financières peuvent être soumises à des obligations légales de conservation différentes des données de matching.

La politique finale doit donc distinguer les catégories.

---

# 62. Logs

Loki ne doit pas devenir :

```text
permanent personal-data archive
```

---

# 63. Metrics

Éviter les labels tels que :

```text
client_email
client_phone
```

dans Prometheus.

---

# 64. Traces

Les traces peuvent contenir :

```text
URL parameters
IDs
request metadata
```

Elles doivent être configurées avec prudence.

---

# 65. Backups

Une donnée supprimée de la base active peut rester temporairement dans :

```text
backup
```

La politique doit expliquer cette situation.

---

# 66. Restore Risk

Une restauration peut réintroduire des données supprimées.

La procédure PRA doit prévoir une réconciliation lorsque nécessaire.

---

# 67. Confidentiality

Contrôles principaux :

```text
RBAC
database roles
application authorization
network controls
secret management
```

---

# 68. Integrity

Le modèle V2 utilise :

```text
PK
FK
UNIQUE
CHECK
NOT NULL
```

pour protéger l'intégrité.

---

# 69. Financial Integrity

Les données :

```text
BAREME_COMMISSION
PAIEMENT
```

nécessitent une intégrité particulièrement forte.

---

# 70. Availability

La protection des données inclut également :

```text
backup
restore
PRA
monitoring
```

---

# 71. Encryption in Transit

Les flux sensibles doivent utiliser :

```text
TLS
```

lorsque pertinent.

---

# 72. Encryption at Rest

À évaluer pour :

```text
PostgreSQL storage
MinIO
backups
host disks
```

selon la sensibilité et l'architecture.

---

# 73. Secrets

Aucun secret dans :

```text
Git
source code
documentation
container image
logs
```

---

# 74. Least Privilege

Exemple :

```text
Matching Service
```

doit pouvoir lire :

```text
DEMANDE_VERSION
BIEN
```

sans nécessairement pouvoir modifier :

```text
PAIEMENT
```

---

# 75. Financial Access

L'accès aux :

```text
BAREME_COMMISSION
PAIEMENT
```

doit être plus restrictif que l'accès à un catalogue de biens.

---

# 76. Audit

Actions sensibles candidates :

```text
client export
data deletion
financial modification
permission change
model promotion
document indexing
```

---

# 77. Privacy by Design

Exemples déjà intégrés dans le design :

```text
CLIENT separated from matching features
document classification
indexable_ia default FALSE
warehouse minimization
local-first AI
synthetic test data
```

---

# 78. Privacy by Default

Le comportement par défaut doit réduire l'exposition.

Exemple :

```text
document AI indexing
=
disabled
```

jusqu'à autorisation.

---

# 79. Consent

Le champ :

```text
consentement_contact
```

ne doit pas être interprété comme autorisation universelle pour :

```text
marketing
AI training
external sharing
```

---

# 80. Automated Decision Making

Le matching reste principalement :

```text
Decision Support
```

et non :

```text
fully autonomous consequential decision
```

---

# 81. Human in the Loop

```text
Matching
   |
   v
Recommendation
   |
   v
Hunter / Client
   |
   v
Decision
```

---

# 82. AI Features

Les features doivent rester :

```text
business relevant
```

et éviter les variables inutiles ou pouvant introduire des biais injustifiés.

---

# 83. Testing Strategy

Les preuves RGPD ne doivent pas être uniquement documentaires.

Des tests techniques seront produits.

---

# 84. Erasure Test

Scénario :

```text
Create synthetic client
      |
      v
Create related records
      |
      v
Execute deletion/anonymization procedure
      |
      v
Verify result
```

---

# 85. Logging Test

Vérifier que :

```text
email
phone
token
password
```

ne sont pas exposés inutilement.

---

# 86. AI Access Test

Vérifier qu'un utilisateur non autorisé ne peut pas récupérer un document restreint via l'IA.

---

# 87. Financial Access Test

Vérifier qu'un rôle non autorisé ne peut pas accéder aux paiements ou barèmes de commission.

---

# 88. Evidence Runtime

## Contrôles déjà reliés à l'implémentation

| Traitement / donnée | Contrôle actuel | Limite |
|---|---|---|
| Identités applicatives | Mot de passe haché, JWT, compte actif et rôles | Ne démontre pas tous les droits par propriétaire |
| Recommandations / présentations | Acteur et contexte dans `audit_log` | Rétention et accès au journal à documenter |
| Visites | Snapshots et acteur dans l'audit des mutations | Persistance runtime propre à Visite à consolider |
| Dataset ML | Features explicites et labels issus de la provenance synthétique | Traçabilité synthétique différente d'un feedback client réel |
| Sauvegardes | Stockage MinIO externe avec identité dédiée et test de restauration | Rétention / ILM et traitement des suppressions à formaliser |

Sources :

```text
../../../60-SECURITY/SECURITY-RBAC-AUDIT-IMPLEMENTATION-EVIDENCE.md
../../../60-SECURITY/RECOMMENDATION-AUDIT-RUNTIME-EVIDENCE.md
../../../PCA PRA/PCA-PRA-POSTGRESQL.md
../../03-BC03/C6-Tests-Executes/visite-audit-2026-09-09/README.md
../../../../src/ai/matching/training_dataset.py
```

L'email de l'acteur et les snapshots d'audit sont eux-mêmes des données à gouverner. Les preuves de soutenance doivent utiliser des données de test et masquer les secrets.

La présence de contrôles techniques n'établit pas à elle seule la conformité globale. Le registre final, les durées de conservation et l'exécution des droits restent à justifier dans leur périmètre. Les contrôles RAG restent associés à une extension future.

Les futures preuves peuvent inclure :

```text
SQL role test
API authorization test
erasure test
log inspection
OpenMetadata classification
RAG authorization test
```

---

# 89. Data Classification Matrix

| Entité | Personal Data | Sensitivity |
|---|---|---|
| CLIENT | Oui | Élevée |
| CHASSEUR | Oui | Élevée |
| SECTEUR | Non / indirect | Faible |
| MANDAT | Indirecte | Élevée |
| DEMANDE | Indirecte | Élevée |
| DEMANDE_VERSION | Indirecte | Élevée |
| BIEN | Généralement non | Faible/modérée |
| PRESENTATION | Indirecte | Modérée |
| COMMENTAIRE | Oui possible | Élevée |
| DOCUMENT | Oui possible | Très élevée |
| BAREME_COMMISSION | Chasseur | Élevée |
| PAIEMENT | Oui / financier | Très élevée |

---

# 90. Processing Matrix

| Traitement | Données |
|---|---|
| Client management | CLIENT |
| Mandate management | CLIENT + CHASSEUR + MANDAT |
| Property search | DEMANDE_VERSION + BIEN |
| Matching | DEMANDE_VERSION + BIEN |
| Feedback | COMMENTAIRE |
| Financial management | PAIEMENT + BAREME |
| Analytics | Minimized operational data |
| ML | Minimized features |
| RAG | Authorized documents |
| Monitoring | Technical metadata |

---

# 91. Storage Matrix

| Data | Target |
|---|---|
| Operational data | PostgreSQL |
| Generated RAW | PostgreSQL / MinIO depending format |
| Documents | MinIO |
| Document metadata | PostgreSQL |
| Warehouse | PostgreSQL |
| ML metadata | MLflow |
| ML artifacts | MinIO |
| Embeddings | pgvector / Qdrant candidate |
| Logs | Loki |
| Metrics | Prometheus |
| Traces | Tempo |

---

# 92. Current Status

| Élément | Statut |
|---|---|
| RGPD register | RÉFÉRENCÉ / FICHIER AUTONOME À RATTACHER |
| V2 personal-data mapping | UPDATED |
| Payment/commission privacy | ADDED |
| Data minimization | UPDATED |
| Generated synthetic-data strategy | ADDED |
| OLTP privacy | DEFINED |
| OLAP privacy | DEFINED |
| ML privacy | DEFINED |
| RAG privacy | DEFINED |
| Local AI | DEFINED |
| Rights workflow | DEFINED |
| Retention principles | DEFINED |
| Runtime tests | AUTH / AUDIT PARTIELLEMENT DOCUMENTÉS ; DROITS ET RÉTENTION À VALIDER |

---

# 93. Conclusion

L'architecture V2 applique :

```text
Privacy by Design
+
Privacy by Default
+
Data Minimization
+
Synthetic Test Data
+
Least Privilege
+
Controlled AI Access
+
Lifecycle Management
+
Traceability
```

Les nouvelles entités :

```text
BAREME_COMMISSION
PAIEMENT
COMMENTAIRE
```

augmentent la nécessité de contrôler les accès et la confidentialité.

Le système doit donc protéger non seulement les données d'identité, mais également :

```text
search behavior
feedback
financial information
documents
AI context
```

Les preuves finales devront provenir de tests exécutés sur l'implémentation réelle.

---

**BC05 / C7 — RGPD V2 — ALIGNED WITH TARGET DATA MODEL**
