# Real Estate Governance-as-Code

Configuration preflight and KPI semantics: [validation guide](docs/VALIDATION.md).

Sector ingestion metadata and dashboard alignment are documented in
[Sector governance and observability](../docs/40-DATA/SECTOR-GOVERNANCE-OBSERVABILITY.md).

## Enterprise Real Estate Intelligence Platform

**Project:** Chasse Immobilière — Diginamic Fil Rouge  
**Component:** Data Governance  
**Implementation:** OpenMetadata + Python + GitLab CI + Kubernetes + Argo CD  
**Governance model:** Governance-as-Code  
**Version:** 1.0.0

---

# 1. Purpose

This directory implements the Governance-as-Code layer of the Chasse Immobilière data platform.

The objective is to make data governance:

- versioned;
- reproducible;
- automated;
- auditable;
- reviewable through Git;
- deployable through the existing CI/CD and GitOps platform;
- integrated with OpenMetadata.

Governance is therefore not configured exclusively through the OpenMetadata graphical interface.

Governance definitions are stored as code in the project repository and applied automatically to OpenMetadata through its REST API.

The governance layer complements the existing technical data platform:

```text
External / Generated Sources
            |
            v
           RAW
            |
            v
         STAGING
            |
            v
           OLTP
       real_estate
            |
            v
        WAREHOUSE
            |
            v
           dbt
            |
            v
        ANALYTICS
            |
            v
      OpenMetadata
            |
            v
   Governance-as-Code
```

---

# 2. Governance Objectives

The governance implementation addresses several concerns of the project.

## 2.1 Business semantics

Business concepts must have a shared and documented meaning.

Examples:

```text
Client
Prospect
Chasseur
Mandat
Demande
Version de demande
Bien
Annonce
Secteur
Présentation
Visite
Honoraires
Commission
Paiement
Performance chasseur
```

These concepts are represented in an OpenMetadata business glossary.

---

## 2.2 Data ownership

Every important dataset must have an accountable owner.

The project separates:

```text
Technical identity
        ≠
Data ownership
        ≠
Business ownership
```

For example:

```text
real_estate_user
```

is a PostgreSQL technical account.

It must not automatically become the business owner of the data.

---

## 2.3 Data classification

Datasets and columns can contain different categories of information:

```text
Public
Internal
Confidential
Restricted

Personal Data
Direct Identifier
Indirect Identifier
Financial Data

Raw
Staging
OLTP
Warehouse
Analytics
```

These classifications allow the platform to document how data should be handled.

---

## 2.4 RGPD / Privacy

The real-estate platform manipulates personal information such as:

- identity;
- email;
- telephone;
- customer information;
- budgets;
- transactions;
- financial information;
- search criteria.

Governance provides metadata allowing these elements to be identified and protected.

Governance-as-Code supports the RGPD strategy but does not replace the project's dedicated RGPD processing register.

---

## 2.5 Data Quality

Data quality controls already exist in the operational pipeline.

Governance does not duplicate them.

Instead, it connects quality concepts and metadata to the assets already validated by:

```text
Airflow
SQL validation
dbt tests
```

---

## 2.6 Lineage

OpenMetadata already receives lineage information from PostgreSQL and dbt ingestion.

Governance verifies expected lineage relationships but does not recreate them.

---

## 2.7 AI readiness

Future AI components must not receive unrestricted access to production customer data.

Governance identifies datasets that may require:

- pseudonymisation;
- masking;
- restricted access;
- read-only access;
- exclusion from AI;
- human validation.

This prepares the platform for future matching, recommendation and AI-assisted real-estate services.

---

# 3. Scope

Governance-as-Code manages:

```text
Business glossary
Classifications
Tags
Privacy metadata
Sensitivity metadata
Ownership
Data Quality metadata
Lineage requirements
Governance policies
```

It does NOT:

```text
Create PostgreSQL tables
Modify database schemas
Load business data
Transform source records
Replace Airflow
Replace dbt
Recreate OpenMetadata lineage
Delete existing metadata
Store secrets
```

Governance operates on metadata.

---

# 4. Existing Data Platform

Governance is implemented on top of the existing Real Estate data architecture.

The validated data flow is:

```text
Generated Real Estate Data
          |
          v
     raw.annonces
          |
          v
   staging.annonces
          |
          v
   real_estate.bien
          |
          v
 warehouse.fact_annonce
          |
          v
 analytics.stg_fact_annonce
          |
          v
 analytics.mart_market_by_city
```

The complete orchestration chain is managed by Airflow:

```text
generate_source_data
        |
        v
load_raw
        |
        v
validate_raw
        |
        v
transform_staging
        |
        v
validate_staging
        |
        v
load_oltp
        |
        v
validate_oltp
        |
        v
load_warehouse
        |
        v
validate_warehouse
        |
        v
dbt_run
        |
        v
dbt_test
```

The current dbt validation result is:

```text
PASS=19
WARN=0
ERROR=0
SKIP=0
TOTAL=19
```

OpenMetadata then catalogs the PostgreSQL and dbt assets.

---

# 5. Architecture

The Governance-as-Code architecture follows the existing deployment model of the project.

```text
Developer Workstation
Windows / VS Code
        |
        v
chasse_immobiliere Git repository
        |
        v
governance/
        |
        +--------------------------------+
        |                                |
        v                                v
JSON Governance Definitions        Python Governance Engine
        |                                |
        +---------------+----------------+
                        |
                        v
                   Docker Image
                        |
                        v
                     GitLab
                        |
                        v
              GitLab Container Registry
                        |
                        v
                    lab-gitops
                        |
                        v
                     Argo CD
                        |
                        v
                Kubernetes Cluster
                        |
                        v
              Governance Kubernetes Job
                        |
                        v
                 OpenMetadata REST API
                        |
                        v
                   OpenMetadata
```

The Windows workstation does not need direct Kubernetes administration for normal deployment.

The deployment path remains:

```text
Git
 ↓
GitLab CI
 ↓
Container Registry
 ↓
GitOps
 ↓
Argo CD
 ↓
Kubernetes
```

---

# 6. Directory Structure

```text
governance/
│
├── .gitignore
├── apply-governance.sh
├── Dockerfile
├── README.md
├── requirements.txt
│
├── docs/
│   └── governance-config.json
│
├── glossary/
│   └── real_estate_glossary.json
│
├── k8s/
│
├── ownership/
│   └── real_estate_ownership.json
│
├── quality/
│   └── real_estate_quality.json
│
├── scripts/
│   └── main.py
│
└── tagging/
    └── real_estate_tags.json
```

---

# 7. Component Responsibilities

## 7.1 `docs/governance-config.json`

Central governance configuration.

It defines:

```text
Project identity
OpenMetadata configuration
Enabled governance modules
Governed schemas
Protected schemas
Governance policies
```

Governed schemas:

```text
real_estate
warehouse
analytics
```

Protected/technical schemas:

```text
raw
staging
migration_control
Fil_Rouge_Depart
```

The distinction is intentional.

The trusted business and analytical layers receive business governance while ingestion, migration and legacy layers remain identifiable as technical processing layers.

---

# 8. Business Glossary

Configuration:

```text
glossary/real_estate_glossary.json
```

OpenMetadata glossary:

```text
RealEstateBusinessGlossary
```

The glossary establishes a common vocabulary between:

```text
Business
Data Engineering
Analytics
Data Science
AI
Governance
Architecture
```

Defined concepts include:

```text
Client
Prospect
Chasseur
Mandat
MandatExclusif
MandatNonExclusif
Demande
VersionDemande
Bien
Annonce
Source
Secteur
Presentation
Visite
Commentaire
Prix
PrixM2
Surface
DPE
Honoraires
Commission
BaremeCommission
Paiement
PerformanceChasseur
IngestionBatch
SourceFile
DataQuality
OLTP
Warehouse
Analytics
```

The glossary therefore provides the semantic layer above the physical database.

Example:

```text
Business concept
      |
      v
     Bien
      |
      v
real_estate.bien
      |
      v
warehouse dimensions/facts
      |
      v
analytics models
```

---

# 9. Data Classification

Configuration:

```text
tagging/real_estate_tags.json
```

Five classification families are defined.

---

## 9.1 Data Sensitivity

```text
RealEstateDataSensitivity
```

Tags:

```text
Public
Internal
Confidential
Restricted
```

These tags describe the level of protection required by an asset.

---

## 9.2 Privacy

```text
RealEstatePrivacy
```

Tags:

```text
PersonalData
DirectIdentifier
IndirectIdentifier
FinancialData
RequiresPseudonymisation
AIRestricted
```

Example future classification:

```text
client.email
       |
       +--> PersonalData
       |
       +--> DirectIdentifier
       |
       +--> RequiresPseudonymisation
       |
       +--> AIRestricted
```

This classification will support RGPD and controlled AI access.

---

## 9.3 Data Layer

```text
RealEstateDataLayer
```

Tags:

```text
Legacy
Raw
Staging
OLTP
Warehouse
Analytics
```

This allows OpenMetadata assets to expose their architectural role.

Example:

```text
Fil_Rouge_Depart.*
        |
        v
      Legacy

raw.*
        |
        v
       Raw

staging.*
        |
        v
     Staging

real_estate.*
        |
        v
      OLTP

warehouse.*
        |
        v
    Warehouse

analytics.*
        |
        v
    Analytics
```

---

## 9.4 Data Quality

```text
RealEstateDataQuality
```

Tags:

```text
QualityControlled
CriticalDataset
SourceOfTruth
DerivedData
```

Examples:

```text
real_estate.bien
    |
    +--> QualityControlled
    +--> CriticalDataset
    +--> SourceOfTruth
```

and:

```text
analytics.mart_market_by_city
    |
    +--> QualityControlled
    +--> CriticalDataset
    +--> DerivedData
```

---

## 9.5 Technical Metadata

```text
RealEstateTechnicalMetadata
```

Tags:

```text
LineageMetadata
IngestionMetadata
AuditMetadata
```

These distinguish technical traceability information from business information.

---

# 10. Ownership Model

Configuration:

```text
ownership/real_estate_ownership.json
```

Three governance teams are defined.

```text
RealEstateBusiness
RealEstateDataTeam
RealEstateAnalytics
```

Responsibility model:

```text
                    OpenMetadata
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
RealEstateBusiness  RealEstateDataTeam  RealEstateAnalytics
        |                |                |
        v                v                v
 Business OLTP       Data Platform      Analytics
    assets           + Warehouse       + marts
```

---

## 10.1 Business Ownership

Examples:

```text
client
chasseur
secteur
mandat
mandat_secteur
demande
demande_version
bien
commentaire
document
paiement
presentation
visite
```

Owner:

```text
RealEstateBusiness
```

---

## 10.2 Data Platform Ownership

Examples:

```text
source
audit_log
warehouse.*
```

Owner:

```text
RealEstateDataTeam
```

---

## 10.3 Analytics Ownership

```text
analytics.*
```

Owner:

```text
RealEstateAnalytics
```

---

# 11. Technical Accounts Are Not Business Owners

The PostgreSQL application account:

```text
real_estate_user
```

exists for technical database authentication.

It does not represent:

```text
Data Owner
Business Owner
Data Steward
Business Team
```

Governance therefore explicitly separates authentication identity from organizational accountability.

This avoids the incorrect model:

```text
Database login
      =
Business owner
```

The correct model is:

```text
Database login
      |
      v
Technical authentication


OpenMetadata Team
      |
      v
Governance accountability
```

---

# 12. Data Quality Governance

Configuration:

```text
quality/real_estate_quality.json
```

The quality framework is:

```text
RealEstateDataQuality
```

Quality controls are divided according to the architecture.

---

## 12.1 RAW Quality

```text
raw
 |
 v
validate_raw
```

Purpose:

- verify expected datasets;
- verify expected columns;
- verify structural validity;
- prevent obviously invalid ingestion from progressing.

---

## 12.2 STAGING Quality

```text
staging
   |
   v
validate_staging
```

Important controls include:

```text
reference required
type_bien required
ville required
code_postal required
prix required
surface required
date_publication required

prix > 0
surface > 0

reference uniqueness
quality_valid validation
```

---

## 12.3 OLTP Quality

```text
real_estate
     |
     v
validate_oltp
```

Controls include:

```text
Referential integrity
External property reference uniqueness
Required business relationships
STAGING → BIEN reconciliation
Duplicate detection
```

The validated generated dataset contained:

```text
2000 staging valid rows
2000 distinct references
2000 matched biens
0 unmatched rows
```

---

## 12.4 Warehouse Quality

```text
warehouse
    |
    v
validate_warehouse
```

Controls include:

```text
Expected dimensions
Expected fact tables
Dimension keys
Fact/dimension relationships
Loaded volumes
```

---

## 12.5 dbt Quality

```text
analytics
    |
    v
dbt test
```

Current validated result:

```text
19 tests
19 passed
0 warnings
0 errors
0 skipped
```

Governance records that these assets are quality controlled.

It does not claim that OpenMetadata itself executed the dbt tests.

---

# 13. Data Quality Architecture

The complete relationship is:

```text
Data
 |
 v
Airflow pipeline
 |
 v
SQL validation
 |
 v
dbt validation
 |
 v
Validated dataset
 |
 v
OpenMetadata ingestion
 |
 v
Governance metadata
```

Therefore:

```text
Execution evidence
       +
Metadata evidence
       =
Governed quality
```

---

# 14. Lineage

OpenMetadata lineage is populated separately from Governance-as-Code.

The currently validated analytical lineage includes:

```text
warehouse.fact_annonce
          |
          v
analytics.stg_fact_annonce
          |
          v
analytics.mart_market_by_city
```

Additional upstream dependency:

```text
warehouse.dim_localisation
          |
          v
analytics.mart_market_by_city
```

Column-level lineage has also been validated for the analytical chain.

Example:

```text
warehouse.fact_annonce.id_bien
              |
              v
analytics.stg_fact_annonce.id_bien
              |
              v
analytics.mart_market_by_city
```

Governance verifies expected relationships.

It does not recreate lineage already managed through ingestion.

---

# 15. Why Lineage Is Not Created Here

There must be a clear separation of responsibilities.

```text
PostgreSQL ingestion
        |
        +--> schemas
        +--> tables
        +--> columns

dbt ingestion
        |
        +--> dbt models
        +--> SQL
        +--> table lineage
        +--> column lineage

Governance-as-Code
        |
        +--> semantics
        +--> classifications
        +--> ownership
        +--> governance metadata
        +--> expected lineage validation
```

This avoids having several systems attempting to manage the same metadata relationship.

---

# 16. Governance Engine

Main implementation:

```text
scripts/main.py
```

The Python governance engine performs the following sequence:

```text
START
  |
  v
Load governance-config.json
  |
  v
Read OM_URL
  |
  v
Read OM_JWT_TOKEN
  |
  v
Validate OpenMetadata connectivity
  |
  v
Apply Business Glossary
  |
  v
Apply Glossary Terms
  |
  v
Apply Classifications
  |
  v
Apply Tags
  |
  v
Create / reuse Teams
  |
  v
Apply Ownership
  |
  v
Apply Data Quality metadata
  |
  v
Verify expected lineage
  |
  v
END
```

---

# 17. OpenMetadata Communication

The governance engine communicates with:

```text
OpenMetadata REST API
```

using:

```text
HTTP GET
HTTP PUT
HTTP POST
HTTP PATCH
```

Operations include:

```text
Lookup existing entities
Create/update governance entities
Create teams when absent
Patch ownership
Patch tags
Read lineage
```

The database itself is not modified.

---

# 18. Idempotency

Governance execution must be repeatable.

Running the same governance version multiple times should converge toward the same desired state.

The implementation therefore:

- searches for existing teams;
- reuses existing teams;
- creates or updates governance entities;
- checks existing ownership;
- preserves existing tags;
- adds missing required tags;
- does not delete unrelated metadata;
- does not recreate database assets;
- does not modify source data.

Desired behaviour:

```text
Run #1
   |
   v
Governance state v1

Run #2
   |
   v
Governance state v1

Run #3
   |
   v
Governance state v1
```

rather than:

```text
Run #1 → duplicates
Run #2 → more duplicates
Run #3 → inconsistent metadata
```

---

# 19. Runtime Configuration

The container requires:

```text
OM_URL
OM_JWT_TOKEN
```

`OM_URL` identifies the OpenMetadata API endpoint.

Example inside the Kubernetes network:

```text
http://openmetadata:8585/api
```

The exact service endpoint must correspond to the deployed OpenMetadata service.

`OM_JWT_TOKEN` contains the authentication token used by the governance automation.

---

# 20. Secret Management

The JWT token must never be stored directly in:

```text
main.py
Dockerfile
JSON files
README.md
Git repository
GitOps manifests
```

The target Kubernetes secret is:

```text
om-admin-token
```

Expected key:

```text
jwtToken
```

Runtime injection:

```text
Kubernetes Secret
       |
       v
om-admin-token
       |
       v
jwtToken
       |
       v
OM_JWT_TOKEN
       |
       v
Governance container
       |
       v
OpenMetadata
```

---

# 21. Container

The governance image is defined by:

```text
Dockerfile
```

Base image:

```text
python:3.12-slim
```

Python dependencies:

```text
requests==2.32.3
PyYAML==6.0.2
```

The image contains:

```text
/app
 |
 +-- docs/
 +-- glossary/
 +-- ownership/
 +-- quality/
 +-- scripts/
 +-- tagging/
 |
 +-- requirements.txt
 +-- apply-governance.sh
```

The container does not need a PostgreSQL client because governance communicates with OpenMetadata rather than directly modifying PostgreSQL.

---

# 22. Container Entrypoint

Entrypoint:

```text
apply-governance.sh
```

The script:

1. validates `OM_URL`;
2. validates `OM_JWT_TOKEN`;
3. starts the Python governance engine;
4. fails the container if governance application fails.

Execution:

```text
Container start
      |
      v
apply-governance.sh
      |
      +--> OM_URL present?
      |
      +--> OM_JWT_TOKEN present?
      |
      v
python3 /app/scripts/main.py
      |
      v
OpenMetadata API
```

The token itself is never printed.

---

# 23. Deployment Strategy

Governance follows the same engineering principles as the rest of the platform.

The target workflow is:

```text
Developer
   |
   v
Git commit
   |
   v
GitLab
   |
   v
CI pipeline
   |
   v
Build governance image
   |
   v
GitLab Container Registry
   |
   v
Update GitOps configuration
   |
   v
lab-gitops
   |
   v
Argo CD
   |
   v
Kubernetes
   |
   v
Governance Job
   |
   v
OpenMetadata
```

---

# 24. GitOps Principle

Permanent Kubernetes configuration belongs in:

```text
lab-gitops
```

The application repository contains:

```text
governance source code
governance definitions
Dockerfile
documentation
```

The GitOps repository contains:

```text
Kubernetes manifests
image references
runtime configuration
deployment state
```

Argo CD reconciles the Kubernetes cluster with Git.

Therefore:

```text
Git = desired state
Kubernetes = runtime state
```

Manual cluster changes should not become the permanent deployment method.

---

# 25. OpenMetadata Dependency Order

Governance must run only after the relevant metadata assets exist.

Correct logical order:

```text
PostgreSQL objects
       |
       v
dbt models
       |
       v
PostgreSQL metadata ingestion
       |
       v
dbt metadata ingestion
       |
       v
OpenMetadata assets
       |
       v
OpenMetadata lineage
       |
       v
Governance-as-Code
```

If governance executes before metadata ingestion, some ownership/tagging targets may not yet exist.

The governance engine therefore warns about missing targets rather than altering the database.

---

# 26. Governance Principles

## 26.1 Least Privilege

Automation receives only the permissions required to manage the relevant metadata.

---

## 26.2 Privacy by Design

Personal information is identified and protected as part of system design rather than after deployment.

---

## 26.3 Separation of Responsibilities

Technical database identities and organizational ownership are different concepts.

---

## 26.4 Traceability

Governance changes are version controlled.

```text
Governance change
      |
      v
Git commit
      |
      v
Review
      |
      v
CI/CD
      |
      v
OpenMetadata
```

---

## 26.5 Automation First

Repeatable governance operations should be automated rather than manually reproduced through the UI.

---

## 26.6 No Source Mutation

Governance manages metadata.

It must not mutate operational business records.

---

## 26.7 No Destructive Governance by Default

The initial implementation does not automatically delete existing OpenMetadata:

```text
tags
glossary entities
owners
lineage
assets
```

This reduces the risk of destructive metadata operations.

---

# 27. RGPD Integration

The project handles personally identifiable information.

Governance classifications include:

```text
RealEstatePrivacy.PersonalData
RealEstatePrivacy.DirectIdentifier
RealEstatePrivacy.IndirectIdentifier
RealEstatePrivacy.FinancialData
RealEstatePrivacy.RequiresPseudonymisation
RealEstatePrivacy.AIRestricted
```

Example:

```text
Operational customer data
          |
          v
Privacy classification
          |
          +--> personal?
          |
          +--> direct identifier?
          |
          +--> financial?
          |
          +--> AI restricted?
          |
          v
Protection policy
```

Governance-as-Code supports privacy-by-design.

However, it does not replace the dedicated project RGPD register.

That register must still document:

```text
Processing activity
Purpose
Legal basis
Categories of data
Recipients
Retention period
Security measures
Data subject rights
```

---

# 28. AI Sovereignty and Security

The future architecture includes AI-assisted capabilities.

Possible use cases include:

```text
Property/request matching
Search feasibility scoring
Recommendation
Request refinement
Property ranking
Assistance to hunters
AI hunter
```

The unsafe architecture would be:

```text
Production OLTP
      |
      v
External LLM
```

This must be avoided for unrestricted personal data.

Preferred architecture:

```text
OLTP
 |
 v
Controlled transformation
 |
 v
Warehouse
 |
 v
Analytics
 |
 v
Governance controls
 |
 +--> remove unnecessary PII
 |
 +--> pseudonymise identifiers
 |
 +--> enforce read-only access
 |
 +--> restrict sensitive attributes
 |
 v
AI Feature Layer
 |
 v
AI / ML service
```

This supports:

```text
Data minimisation
Privacy by design
Least privilege
Pseudonymisation
Controlled exposure
Traceability
```

---

# 29. Data Governance and AI

Governance is important for future model training and inference because the model must know which information can legitimately be consumed.

Conceptually:

```text
Demande
   +
Bien
   +
Market information
   +
User interaction
        |
        v
Governed datasets
        |
        v
Feature engineering
        |
        v
Matching model
        |
        +--> relevance score
        +--> feasibility score
        +--> ranking
```

Personal identifiers should normally not become matching features simply because they exist in the operational database.

---

# 30. Governance and the Data Lifecycle

The complete governed lifecycle becomes:

```text
SOURCE
   |
   v
RAW
   |
   | ingestion metadata
   v
STAGING
   |
   | quality validation
   v
OLTP
   |
   | business ownership
   | glossary
   | privacy
   v
WAREHOUSE
   |
   | data ownership
   | analytical preparation
   v
ANALYTICS
   |
   | analytics ownership
   | quality
   | lineage
   v
AI / BI / Decision Support
```

Governance therefore accompanies the data throughout its lifecycle rather than being a separate isolated component.

---

# 31. Governance and Data Quality Are Different

Data quality answers:

```text
Is the data correct?
Is it complete?
Is it valid?
Is it unique?
Is it consistent?
```

Governance answers:

```text
What does this data mean?
Who owns it?
How sensitive is it?
Who may use it?
Where did it come from?
Is it suitable for AI?
What controls apply to it?
```

Together:

```text
Data Quality
      +
Governance
      +
Lineage
      =
Trusted Data Platform
```

---

# 32. Governance and OpenMetadata

OpenMetadata acts as the central metadata catalog.

It provides visibility over:

```text
Databases
Schemas
Tables
Columns
dbt models
Descriptions
Owners
Tags
Glossary
Lineage
Data Quality metadata
```

Governance-as-Code makes the governance configuration reproducible.

Therefore:

```text
OpenMetadata
      =
Governance runtime/catalog

Git
      =
Governance source of truth
```

---

# 33. Current Governance Assets

The following governance definitions are currently maintained as code:

```text
docs/governance-config.json

glossary/real_estate_glossary.json

tagging/real_estate_tags.json

ownership/real_estate_ownership.json

quality/real_estate_quality.json

scripts/main.py

apply-governance.sh

Dockerfile

requirements.txt
```

---

# 34. Security Rules

The following rules are mandatory for this module.

## Never commit

```text
JWT tokens
Passwords
API secrets
Database passwords
Private keys
.env files containing secrets
```

## Never expose

```text
OM_JWT_TOKEN
```

in logs.

## Never use

the PostgreSQL application account as a substitute for governance ownership.

## Never give

an AI unrestricted direct access to production personal data.

## Never modify

source business data from the governance job.

---

# 35. Failure Behaviour

The governance engine distinguishes between fatal errors and missing metadata targets.

Fatal examples:

```text
OM_URL missing
OM_JWT_TOKEN missing
OpenMetadata unreachable
Authentication failure
Invalid governance configuration
Invalid API operation
```

These must fail the governance job.

Missing target example:

```text
A configured table has not yet been ingested into OpenMetadata.
```

The engine can log a warning so the issue can be investigated without modifying the underlying database.

---

# 36. Observability

The governance container writes structured execution information to stdout.

Example logical sequence:

```text
Governance configuration loaded
Connected to OpenMetadata

Step 1/4
Applying business glossary

Step 2/4
Applying classifications and tags

Step 3/4
Applying ownership

Step 4/4
Applying Data Quality governance

Governance-as-Code execution completed successfully
```

These logs become accessible through Kubernetes job logs.

---

# 37. Validation Strategy

A successful deployment must eventually verify the following.

## Glossary

OpenMetadata contains:

```text
RealEstateBusinessGlossary
```

with the expected business terms.

## Classifications

OpenMetadata contains:

```text
RealEstateDataSensitivity
RealEstatePrivacy
RealEstateDataLayer
RealEstateDataQuality
RealEstateTechnicalMetadata
```

## Ownership

Relevant assets show the expected teams.

## Quality

Critical datasets show the expected Data Quality tags.

## Lineage

Expected analytical lineage remains visible.

## Idempotency

A second governance execution must not create uncontrolled duplicates or destroy existing metadata.

---

# 38. Expected Final State

Once the complete governance deployment is operational:

```text
                        REAL ESTATE DATA PLATFORM

                                  |
              +-------------------+-------------------+
              |                                       |
              v                                       v
          DATA PLANE                           GOVERNANCE PLANE
              |                                       |
              v                                       v
            RAW                                  Glossary
              |                                       |
              v                                       v
          STAGING                               Classification
              |                                       |
              v                                       v
            OLTP                                  Ownership
              |                                       |
              v                                       v
         WAREHOUSE                               Privacy/RGPD
              |                                       |
              v                                       v
          ANALYTICS                              Data Quality
              |                                       |
              +-------------------+-------------------+
                                  |
                                  v
                            OpenMetadata
                                  |
                                  v
                         Trusted Data Catalog
                                  |
                     +------------+------------+
                     |                         |
                     v                         v
                    BI                     AI / ML
```

---

# 39. Relation to the Diginamic Fil Rouge

Governance-as-Code is an engineering implementation that strengthens several mandatory project concerns.

It provides technical evidence for:

```text
Data quality
Data traceability
Privacy by design
Data security
Data ownership
AI data protection
Architecture documentation
Reproducibility
```

It particularly strengthens the project's BC05 data and AI architecture work.

However, Governance-as-Code does not replace mandatory written deliverables such as:

```text
RGPD register
Eco-design note
Accessibility recommendations
AI sovereignty/security note
Architecture decision matrix
3V dimensioning
PCA/PRA
Project framing
```

Those remain separate project deliverables.

---

# 40. Why Governance-as-Code Was Chosen

Manual governance through a graphical interface would technically work but creates several problems:

```text
No reproducibility
Difficult auditing
Configuration drift
Manual errors
Poor environment portability
No code review
Weak traceability
```

Governance-as-Code provides:

```text
Version control
Repeatability
Automation
Review
Auditability
Git history
Deployment consistency
Infrastructure integration
```

It therefore follows the same philosophy already used by the infrastructure:

```text
Infrastructure-as-Code
        +
GitOps
        +
Data pipelines as code
        +
dbt models as code
        +
Governance-as-Code
```

---

# 41. Architectural Decision

The project deliberately separates responsibilities.

```text
Airflow
    =
Pipeline orchestration

PostgreSQL
    =
Operational and analytical data storage

dbt
    =
Analytical transformations and tests

OpenMetadata
    =
Metadata catalog and lineage platform

Governance-as-Code
    =
Declarative governance configuration

GitLab CI
    =
Build and automation

GitOps / Argo CD
    =
Kubernetes desired-state deployment
```

No single component is expected to perform every responsibility.

This reduces coupling and makes the architecture easier to maintain and defend.

---

# 42. Governance Evolution

The initial implementation establishes the governance foundation.

Future improvements may include:

```text
Column-level PII tagging
Automatic glossary-term association
Automated schema-layer tagging
Data retention policies
Data domains
Data products
Data contracts
OpenMetadata policies
Fine-grained access controls
Automated quality result publication
Governance compliance reports
AI feature governance
Data masking policies
Pseudonymisation pipelines
```

These extensions should build on the current structure rather than replace it.

---

# 43. Current Implementation Status

Implemented in repository:

```text
[OK] Governance directory structure
[OK] Python dependencies
[OK] Central governance configuration
[OK] Business glossary definitions
[OK] Classification definitions
[OK] Privacy classification
[OK] Data sensitivity classification
[OK] Data-layer classification
[OK] Data Quality governance definition
[OK] Ownership model
[OK] Python governance engine
[OK] Container entrypoint
[OK] Dockerfile
[OK] Secret-safe .gitignore
[OK] Governance documentation
```

Still to implement/test:

```text
[ ] Kubernetes governance Job
[ ] GitLab CI image build
[ ] GitLab Registry publication
[ ] GitOps deployment
[ ] Kubernetes Secret integration
[ ] First OpenMetadata apply
[ ] Runtime validation
[ ] Idempotency test
[ ] OpenMetadata UI verification
[ ] Final governance evidence
```

---

# 44. Next Deployment Stage

The next technical stage is:

```text
governance source
      |
      v
Docker image
      |
      v
GitLab Registry
      |
      v
Kubernetes Job manifest
      |
      v
lab-gitops
      |
      v
Argo CD
      |
      v
openmetadata namespace
      |
      v
OpenMetadata API
      |
      v
Governance applied
```

The Kubernetes manifest must reference:

```text
OM_URL
OM_JWT_TOKEN
```

with the JWT token obtained from the Kubernetes Secret rather than embedded in Git.

---

# 45. Final Governance Principle

The platform follows one central principle:

> **Business data is managed in the data platform; knowledge about that data is governed in OpenMetadata; the desired governance state is maintained in Git.**

This gives the project three complementary sources of truth:

```text
PostgreSQL
    |
    +--> Data truth

OpenMetadata
    |
    +--> Metadata and governance truth

Git
    |
    +--> Configuration and desired-state truth
```

Together they provide a reproducible and auditable foundation for analytics, future AI capabilities and enterprise data governance.
