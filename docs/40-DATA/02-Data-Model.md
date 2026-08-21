# Data Model — Real Estate Intelligence Platform

**Version:** 2.0  
**Status:** Baseline aligned with StarterPack  
**Domain:** Real Estate Intelligence  
**Primary DBMS:** PostgreSQL  
**Methodology:** MERISE → MCD → MLD → MPD  
**Date de référence métier:** 25 July 2026

---

# 1. Purpose

This document defines the canonical data model of the Real Estate Intelligence Platform.

It provides the bridge between:

```text
Business Requirements
        |
        v
Legacy Database
        |
        v
MERISE MCD
        |
        v
MLD
        |
        v
PostgreSQL MPD
        |
        v
Application / Data / AI
```

The authoritative detailed models are maintained in:

```text
docs/evidence/05-BC05/C1-MCD-Migration-SQL/
```

including:

```text
MCD-MERISE-PROJET.md
MLD-PROJET.md
MPD-POSTGRESQL.md
```

---

# 2. Legacy Model

The inherited system contains only:

```text
secteurs
utilisateurs
mandats
```

This is intentional.

The inherited database represents the system to audit and migrate.

It must not be treated as the final target model.

---

# 3. Legacy Schema

Conceptually:

```text
SECTEURS
    |
    v
MANDATS
   / \
  /   \
 v     v
UTILISATEURS
 client/chasseur
 mixed together
```

The legacy `utilisateurs` relation contains both:

```text
CLIENT
```

and:

```text
CHASSEUR
```

records.

---

# 4. Legacy Problems

The main structural problems include:

```text
mixed business roles
free-text search criteria
no proper search version history
commission directly attached to user
missing properties
missing feedback model
missing payment lifecycle
missing analytics-oriented structure
```

These limitations directly affect:

- maintainability;
- scalability;
- analytics;
- AI readiness;
- traceability.

---

# 5. Target Canonical Model

The canonical target model consists of:

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

---

# 6. High-Level Model

```text
                     SECTEUR
                        ^
                        |
                        |
CLIENT -----------> MANDAT <----------- CHASSEUR
                       |
                       v
                    DEMANDE
                       |
                       v
                DEMANDE_VERSION
                  /          \
                 /            \
                v              v
        PRESENTATION       COMMENTAIRE
                \              /
                 \            /
                    -> BIEN <-
                        |
             +----------+----------+
             |                     |
             v                     v
           SOURCE               DOCUMENT


CHASSEUR
    |
    v
BAREME_COMMISSION


MANDAT
    |
    v
PAIEMENT
```

---

# 7. CLIENT

`CLIENT` represents the purchaser using the real-estate search service.

Main attributes:

```text
id_client
nom
prenom
email
telephone
ville
date_creation
statut
consentement_contact
```

A client may sign several mandates.

---

# 8. CHASSEUR

`CHASSEUR` represents a real-estate hunter responsible for client mandates.

Main attributes:

```text
id_chasseur
nom
prenom
email
telephone
date_entree
statut
```

Commission rules are deliberately not stored directly on this entity.

They belong to:

```text
BAREME_COMMISSION
```

---

# 9. Why CLIENT and CHASSEUR are separated

The inherited model stores both in:

```text
utilisateurs
```

with role-dependent columns.

The target model separates them because they represent distinct business concepts and have different attributes and responsibilities.

```text
LEGACY

UTILISATEURS
├── client
└── chasseur
```

becomes:

```text
TARGET

CLIENT

CHASSEUR
```

---

# 10. SECTEUR

`SECTEUR` represents a geographical search or operational zone.

Main attributes:

```text
id_secteur
pays
ville
quartier
code_postal
actif
```

The inherited sector information is preserved.

The model is extended to support international expansion.

---

# 11. Internationalization

The target architecture must not assume every location is French.

For example:

```text
code_postal
```

is represented as text rather than a numeric field.

This supports future coverage of:

```text
France
DROM
Spain
Germany
United Kingdom
Ireland
Benelux
Italy
Switzerland
```

---

# 12. MANDAT

`MANDAT` represents the legal search agreement between the client and the company.

Main attributes:

```text
id_mandat
reference_mandat
type_mandat
date_signature
mode_signature
date_debut
date_fin
statut
commentaire
id_client
id_chasseur
```

---

# 13. Mandate Type

The main values are:

```text
EXCLUSIF
NON_EXCLUSIF
```

This replaces an ambiguous purely technical representation with an explicit business concept.

---

# 14. Mandate Duration

The business rule is:

```text
date_fin
=
date_signature + 6 months
```

The implementation must preserve this rule unless a specifically documented renewal process modifies it.

---

# 15. Mandate Signature

The target model distinguishes:

```text
date_signature
```

and:

```text
mode_signature
```

Possible modes include:

```text
PAPIER
ELECTRONIQUE
AUTRE
INCONNU
```

`INCONNU` is necessary when migrating legacy data for which the original mode is unavailable.

---

# 16. MANDAT_SECTEUR

The inherited model effectively associates a mandate with one sector.

The target model allows:

```text
one mandate
      |
      v
multiple sectors
```

through:

```text
MANDAT_SECTEUR
```

This supports multi-area searches.

---

# 17. DEMANDE

`DEMANDE` represents the actual real-estate search.

It is intentionally distinct from:

```text
MANDAT
```

because:

```text
MANDAT
=
contract
```

while:

```text
DEMANDE
=
business search requirement
```

---

# 18. DEMANDE Main Attributes

```text
id_demande
reference_demande
date_creation
statut
id_mandat
```

A demand belongs to a mandate.

---

# 19. DEMANDE_VERSION

The search criteria evolve over time.

They must never simply overwrite the previous state.

Architecture:

```text
DEMANDE
   |
   +--> VERSION 1
   |
   +--> VERSION 2
   |
   +--> VERSION 3
```

---

# 20. Version Traceability

Each version records at least:

```text
numero_version
date_version
author
motif_modification
```

This allows the platform to answer:

```text
What changed?
When?
Who changed it?
Why?
```

---

# 21. Structured Search Criteria

The target demand version includes structured criteria such as:

```text
ville
code_postal
type_bien

budget_min
budget_max

surface_min

nb_pieces_min
nb_chambres_min

dpe_max

criteres_souhaites
```

---

# 22. Why structured criteria matter

The inherited system stores criteria in:

```text
mandats.description_recherche
```

as free text.

That makes:

- SQL filtering difficult;
- analytics unreliable;
- matching difficult;
- AI feature engineering inconsistent.

The target model converts search requirements into structured data.

---

# 23. Legacy Search Description

The original:

```text
description_recherche
```

must not simply be discarded.

It can be retained during migration as:

```text
description_recherche_legacy
```

so the migration remains auditable.

---

# 24. Demand Author Integrity

A version can be created by:

```text
CLIENT
CHASSEUR
SYSTEME
```

At physical level, the project uses explicit nullable references rather than an unsafe polymorphic foreign key.

Example:

```text
auteur_client_id
auteur_chasseur_id
auteur_systeme
```

with a constraint enforcing exactly one logical author.

---

# 25. Preferences

Flexible preferences such as:

```text
balcon
jardin
parking
ascenseur
terrasse
cave
vue
calme
lumineux
piscine
```

can initially be represented using:

```text
JSONB
```

in PostgreSQL.

This preserves flexibility while the structured core remains relational.

---

# 26. SOURCE

`SOURCE` describes where a property announcement originated.

Candidate source types:

```text
AGENCE
PARTICULIER
PLATEFORME
API
OPEN_DATA
MANUEL
AUTRE
```

---

# 27. BIEN

`BIEN` represents the canonical normalized property.

Main attributes:

```text
id_bien
reference_externe
type_bien
titre

adresse
code_postal
ville

latitude
longitude

prix
surface

nb_pieces
nb_chambres

dpe
description

date_publication
date_collecte

statut
id_source
```

---

# 28. BIEN is not RAW source data

External announcements may be inconsistent.

The canonical entity is populated only after normalization.

```text
CSV
JSON
API
 |
 v
RAW
 |
 v
STAGING
 |
 v
VALIDATION
 |
 v
BIEN
```

---

# 29. StarterPack Generated Data

The StarterPack generator produces linked synthetic datasets:

```text
recherches.csv
annonces.csv
json/annonce_XXXX.json
```

These are intended to simulate:

- heterogeneous sources;
- missing fields;
- renamed fields;
- multiple date formats;
- optional geolocation;
- structured search criteria.

They are not part of the inherited production database.

---

# 30. Generator → Target Mapping

```text
recherches.csv
      |
      v
DEMANDE
      |
      v
DEMANDE_VERSION
```

and:

```text
annonces.csv / JSON
      |
      v
RAW
      |
      v
STAGING
      |
      v
SOURCE + BIEN
```

---

# 31. PRESENTATION

`PRESENTATION` represents a property selected or proposed for a specific demand version.

Core relation:

```text
DEMANDE_VERSION
       |
       v
PRESENTATION
       |
       v
BIEN
```

---

# 32. PRESENTATION Attributes

```text
id_presentation
date_selection
date_presentation
score_matching
statut
id_demande_version
id_bien
```

---

# 33. Matching

The primary structured matching relationship is:

```text
DEMANDE_VERSION
        +
       BIEN
        |
        v
PRESENTATION
```

The matching system may add:

```text
score_matching
```

and eventually additional score components.

---

# 34. COMMENTAIRE

`COMMENTAIRE` represents feedback about a property within the context of a search.

This is different from `PRESENTATION`.

A presentation represents:

```text
system/business selection
```

while a comment represents:

```text
human feedback
```

---

# 35. COMMENTAIRE Context

A comment belongs to:

```text
DEMANDE_VERSION
+
BIEN
+
AUTHOR
```

Possible authors:

```text
CLIENT
CHASSEUR
```

---

# 36. Comment Decisions

Possible business decisions include:

```text
RETENIR
ECARTER
VISITER
REQUALIFIER
INFORMATION
```

These interactions may later contribute to AI-assisted requalification.

---

# 37. DOCUMENT

`DOCUMENT` represents metadata for files associated with a property.

Examples:

```text
PDF
photo
plan
diagnostic
brochure
audio
video
```

---

# 38. Binary Storage

The database stores metadata.

Actual binary files should normally live in object storage.

```text
PostgreSQL
    |
    +--> metadata

MinIO
    |
    +--> binary objects
```

---

# 39. AI Document Governance

Important fields include:

```text
classification
indexable_ia
```

`indexable_ia` defaults to:

```text
FALSE
```

so a stored document is not automatically eligible for AI indexing.

---

# 40. BAREME_COMMISSION

The commission model is separated from `CHASSEUR`.

A commission scale can vary:

```text
by hunter
by amount range
by period
```

---

# 41. BAREME_COMMISSION Attributes

```text
id_bareme
id_chasseur

montant_min
montant_max

taux_commission
montant_fixe

date_debut_validite
date_fin_validite

actif
```

---

# 42. Why commission history matters

The platform must be able to answer:

```text
Which commission rule applied
at the time of a historical transaction?
```

Therefore old commission scales are preserved instead of overwritten.

---

# 43. Commission Percentage

Physically, the commission is stored as a ratio.

Example:

```text
0.15
=
15 %
```

---

# 44. PAIEMENT

`PAIEMENT` represents the financial lifecycle after a successful transaction.

Main attributes:

```text
id_paiement
id_mandat
id_bareme

date_acte_authentique

montant_achat
montant_honoraires
montant_chasseur

date_reception_honoraires
date_paiement_chasseur

statut
```

---

# 45. Payment Lifecycle

Candidate statuses:

```text
ATTENDU
RECU
VERIFIE
PROGRAMME
PAYE
ANNULE
```

---

# 46. Commission Traceability

A payment can retain:

```text
id_bareme
```

to identify exactly which scale was used.

This prevents later barème changes from destroying historical traceability.

---

# 47. Hunter Performance

The business requires performance indicators based on information such as:

```text
mandate-to-purchase duration
exclusive mandate
successful transactions
number of mandates
number of visits
```

These indicators should generally be calculated in:

```text
warehouse
analytics
```

rather than stored as arbitrary mutable values in the OLTP model.

---

# 48. Future Entities

The full business journey may later require:

```text
VISITE
OFFRE
FACTURE
ACTE
NOTAIRE
RENOUVELLEMENT_MANDAT
```

They are valid future extensions.

They are not included in the minimum BC05 target schema until required by the executable application scope.

---

# 49. Why not model everything immediately

The project must avoid:

```text
over-engineering
```

The target model should support:

```text
required business needs
+
Data architecture
+
AI readiness
```

without attempting to implement the entire future enterprise in the first migration.

---

# 50. Referential Integrity

The target model relies on:

```text
PRIMARY KEY
FOREIGN KEY
UNIQUE
CHECK
NOT NULL
```

for core integrity.

Application validation complements database constraints but does not replace them.

---

# 51. Important Uniqueness Rules

Examples:

```text
CLIENT.email
```

```text
CHASSEUR.email
```

```text
MANDAT.reference_mandat
```

```text
DEMANDE_VERSION(
    id_demande,
    numero_version
)
```

```text
BIEN(
    id_source,
    reference_externe
)
```

```text
PRESENTATION(
    id_demande_version,
    id_bien
)
```

---

# 52. One Active Demand Version

The target database enforces:

```text
maximum one active version
per demand
```

through a PostgreSQL partial unique index.

---

# 53. Financial Types

Financial values use:

```text
NUMERIC
```

rather than floating-point types.

Examples:

```text
price
budget
commission
payment
```

---

# 54. Geographic Coordinates

Coordinates use bounded numeric fields.

```text
latitude
-90 .. 90
```

```text
longitude
-180 .. 180
```

PostGIS may be evaluated later if advanced geospatial processing is required.

---

# 55. DPE

Candidate values:

```text
A
B
C
D
E
F
G
```

Missing source information may remain:

```text
NULL
```

---

# 56. Data Lifecycle

Most business data should use status transitions rather than destructive deletion.

Examples:

```text
ACTIF
INACTIF
ARCHIVE
EXPIRE
TERMINE
ANNULE
```

---

# 57. Delete Strategy

Default:

```text
ON DELETE RESTRICT
```

for historical business entities.

This protects:

- contractual history;
- matching history;
- financial history;
- auditability.

---

# 58. Migration Strategy

The inherited schema is treated as an immutable migration source.

```text
"Fil_Rouge_Depart"
        |
        v
Migration
        |
        v
real_estate
```

The source schema must not be dropped by our migration.

---

# 59. Legacy User Migration

```text
utilisateurs
    |
    +-- role=client ----> CLIENT
    |
    +-- role=chasseur -> CHASSEUR
```

---

# 60. Legacy Sector Migration

```text
secteurs
   |
   v
SECTEUR
```

Existing rows default to:

```text
pays = France
```

---

# 61. Legacy Mandate Migration

```text
mandats
   |
   +--> MANDAT
   |
   +--> MANDAT_SECTEUR
   |
   +--> DEMANDE
   |
   +--> DEMANDE_VERSION 1
```

---

# 62. Legacy Exclusivity

```text
exclusif = TRUE
```

becomes:

```text
EXCLUSIF
```

and:

```text
exclusif = FALSE
```

becomes:

```text
NON_EXCLUSIF
```

---

# 63. Legacy Date Handling

Where the inherited model does not contain a distinct signature date, the migration may need to use:

```text
date_debut
```

as a documented migration assumption.

Such assumptions must be explicit.

---

# 64. Legacy Mode of Signature

The inherited database may not contain:

```text
mode_signature
```

Therefore the physical model supports:

```text
INCONNU
```

rather than fabricating a historical fact.

---

# 65. Initial Demand Migration

For every migrated mandate:

```text
MANDAT
   |
   v
DEMANDE
   |
   v
DEMANDE_VERSION 1
```

can be created.

The initial version can record:

```text
motif_modification
=
Migration depuis le SI hérité
```

with:

```text
auteur_systeme = TRUE
```

---

# 66. Legacy Commission Migration

The old:

```text
utilisateurs.taux_commission
```

can become an initial:

```text
BAREME_COMMISSION
```

for each hunter.

This does not recreate historical rules that were never stored.

That limitation must remain documented.

---

# 67. Data Platform Layers

The complete target Data architecture separates:

```text
real_estate
```

for canonical OLTP data,

```text
raw
```

for source preservation,

```text
staging
```

for cleaning and normalization,

```text
warehouse
```

for dimensional analytics,

and:

```text
analytics
```

for business-oriented models and KPI.

---

# 68. Data Flow

```text
Legacy Database
      |
      v
Migration
      |
      v
real_estate


Generated / External Sources
      |
      v
RAW
      |
      v
STAGING
      |
      v
real_estate
      |
      v
WAREHOUSE
      |
      v
ANALYTICS
```

---

# 69. Matching Data Flow

```text
DEMANDE_VERSION
        |
        +----------------+
                         |
                         v
                       MATCH
                         ^
                         |
                         |
                       BIEN
                         |
                         v
                  PRESENTATION
```

---

# 70. Feedback Loop

```text
PRESENTATION
      |
      v
CLIENT / CHASSEUR
      |
      v
COMMENTAIRE
      |
      v
Requalification / Analytics / Future AI
```

---

# 71. AI Data Minimization

The matching layer should consume:

```text
search criteria
property features
```

without automatically exposing:

```text
client email
phone
full identity
```

to an AI model.

---

# 72. AI Training

The certification project requires the design of the data structure and features needed by the AI/matching system.

Actual ML training may be performed as an implementation enhancement, but the canonical data model does not depend on a trained model existing.

---

# 73. OLAP Impact

The OLTP model is not the reporting model.

Data will later be transformed into dimensional structures such as:

```text
dimensions
facts
analytics views
```

The target OLTP normalization remains independent from the warehouse design.

---

# 74. 3V Impact

Future volumes include:

```text
thousands of mandates per week
```

and potentially:

```text
hundreds or thousands of properties
per search
```

This justifies capacity analysis but not premature distributed architecture.

---

# 75. Physical Target

The primary DBMS remains:

```text
PostgreSQL
```

because it supports:

```text
ACID
referential integrity
JSONB
analytics
indexing
extensions
mature tooling
```

---

# 76. Target PostgreSQL Schema

The canonical application tables live under:

```text
real_estate
```

Expected tables:

```text
bareme_commission
bien
chasseur
client
commentaire
demande
demande_version
document
mandat
mandat_secteur
paiement
presentation
secteur
source
```

---

# 77. Source of Truth

Detailed conceptual model:

```text
docs/evidence/05-BC05/C1-MCD-Migration-SQL/MCD-MERISE-PROJET.md
```

Detailed logical model:

```text
docs/evidence/05-BC05/C1-MCD-Migration-SQL/MLD-PROJET.md
```

Detailed physical model:

```text
docs/evidence/05-BC05/C1-MCD-Migration-SQL/MPD-POSTGRESQL.md
```

---

# 78. Model Governance

Any major structural change must follow:

```text
Requirement
   |
   v
MCD impact
   |
   v
MLD impact
   |
   v
MPD impact
   |
   v
Migration
   |
   v
Tests
```

---

# 79. ADR Requirement

A major architectural database change may require an ADR when it changes an architectural decision rather than only the implementation detail.

Examples:

```text
PostgreSQL -> another DBMS
```

```text
pgvector -> Qdrant
```

```text
single relational platform -> distributed storage architecture
```

---

# 80. Current Status

| Area | Status |
|---|---|
| Legacy model understood | COMPLETE |
| Target MCD | V2 COMPLETE |
| Target MLD | V2 COMPLETE |
| PostgreSQL MPD | V2 COMPLETE |
| Client/chasseur separation | COMPLETE |
| Structured demand | COMPLETE |
| Demand history | COMPLETE |
| Sector preservation | COMPLETE |
| Property model | COMPLETE |
| Comment model | COMPLETE |
| Matching relation | COMPLETE |
| Commission model | COMPLETE |
| Payment model | COMPLETE |
| Document extension | COMPLETE |
| Generator mapping | COMPLETE |
| Legacy migration design | COMPLETE |
| Runtime migration | PENDING |
| SQL execution evidence | PENDING |

---

# 81. Conclusion

The canonical model now reflects both the inherited system and the actual target business requirements.

The central transformation is:

```text
Legacy

SECTEURS
UTILISATEURS
MANDATS

        |
        v

Target

CLIENT
CHASSEUR
SECTEUR
MANDAT
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

This provides a stable foundation for:

```text
OLTP
OLAP
Data Quality
Analytics
Matching
AI
Governance
RGPD
```

while preserving a traceable migration path from the supplied StarterPack database.

---

**DATA MODEL V2 — ALIGNED WITH MCD / MLD / MPD V2**