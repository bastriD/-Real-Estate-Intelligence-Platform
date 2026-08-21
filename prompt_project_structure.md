# PROJECT MIGRATION PROMPT — DATABASE IMPLEMENTATION

## Project

**Real Estate Intelligence Platform / Chasse Immobilière**

This conversation is dedicated specifically to:

> **DATABASE IMPLEMENTATION, MIGRATION, VALIDATION AND DATA ENGINEERING**

The documentation/design phase has already been completed in another conversation.

Do **not** restart the documentation work unless implementation discovers a genuine inconsistency requiring an architectural decision.

---

# 1. Current Project Status

The documentation baseline is considered:

```text
V2
REVIEWED
CONSISTENT
FROZEN FOR IMPLEMENTATION
```

Repository-wide checks have already been performed:

```text
No empty Markdown files
No broken internal Markdown links
No problematic stale legacy-table references detected
```

The next phase is implementation.

---

# 2. Repository

Project repository:

```text
chasse_immobiliere/
```

Current structure:

```text
.
├── .gitlab/
│   └── ci/
│
├── database/
│   ├── migrations/
│   ├── olap/
│   ├── oltp/
│   ├── seeds/
│   └── tests/
│
├── deploy/
│   ├── docker/
│   ├── helm/
│   └── kubernetes/
│
├── docs/
│   ├── 00-FOUNDATION/
│   ├── 10-BUSINESS/
│   ├── 20-APPLICATION/
│   ├── 30-INFRASTRUCTURE/
│   ├── 40-DATA/
│   ├── 50-AI/
│   ├── 60-SECURITY/
│   ├── 70-DEVOPS/
│   ├── 80-OPERATIONS/
│   ├── 90-OBSERVABILITY/
│   ├── 95-GOVERNANCE/
│   ├── 98-ADR/
│   ├── 99-DIAGRAMS/
│   └── evidence/
│
├── ml/
│   ├── evaluation/
│   ├── features/
│   ├── models/
│   └── training/
│
├── pipelines/
│   ├── airflow/
│   └── dbt/
│
├── scripts/
│
├── src/
│   ├── ai/
│   ├── api/
│   ├── domain/
│   └── services/
│
└── tests/
    ├── e2e/
    ├── integration/
    ├── security/
    └── unit/
```

---

# 3. Official StarterPack

The Diginamic StarterPack is maintained in a **separate repository**.

It is not the working project repository.

Official source:

```text
https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack
```

The StarterPack has been updated by Diginamic.

Important additions include:

```text
outils/Readme.md
outils/generer_annonces.py
```

The generator is relevant for producing synthetic announcement/search data and for:

```text
migration testing
ETL testing
volume testing
ML technical validation
performance testing
```

Do not modify the StarterPack repository as if it were the project.

Use it as:

```text
SOURCE / REFERENCE / LEGACY INPUT
```

while:

```text
chasse_immobiliere
```

is the implementation repository.

---

# 4. Architecture Principle

We distinguish:

```text
OFFICIAL STARTERPACK / LEGACY
            |
            v
      MIGRATION / ETL
            |
            v
PROJECT TARGET DATA MODEL V2
```

Never silently replace the V2 target model with the StarterPack schema.

The StarterPack represents input/reference data.

The project V2 model represents the target architecture.

---

# 5. Target Data Model V2

The approved business model contains:

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

This model is the implementation target.

---

# 6. Important Modeling Decisions

## DEMANDE and DEMANDE_VERSION

A search is separated into:

```text
DEMANDE
   |
   +--> DEMANDE_VERSION 1
   +--> DEMANDE_VERSION 2
   +--> DEMANDE_VERSION N
```

This provides search-criteria historization.

Do not collapse these back into one table without an explicit architectural decision.

---

## SECTEUR

Sector management is modeled explicitly.

Relationship:

```text
MANDAT
   |
   v
MANDAT_SECTEUR
   |
   v
SECTEUR
```

---

## Financial Model

The V2 model introduces:

```text
BAREME_COMMISSION
PAIEMENT
```

These are intentional.

Financial data must remain separated from AI/matching services unless required.

---

## Matching

`PRESENTATION` represents the relationship between:

```text
DEMANDE_VERSION
+
BIEN
```

and contains the matching result/business presentation information.

Current decision:

```text
DO NOT immediately add
model_name
model_version
```

to `PRESENTATION`.

For now ML traceability can use:

```text
MLflow
logs
request_id
API response
```

If implementation demonstrates the need for persisted scoring traceability, evaluate a dedicated entity such as:

```text
MATCHING_EXECUTION
```

rather than automatically overloading `PRESENTATION`.

---

# 7. Documentation Sources of Truth

Before implementing database structures, consult the existing project documentation.

Particularly:

```text
docs/40-DATA/
```

and:

```text
docs/evidence/05-BC05/C1-MCD-Migration-SQL/
```

The evidence directory contains the validated:

```text
MCD
MLD
MPD
migration design
```

Do not invent a different database architecture without first identifying a contradiction.

---

# 8. Documentation vs Implementation

Keep them separated.

Documentation:

```text
docs/
```

Executable database implementation:

```text
database/
```

Do NOT place executable SQL inside evidence folders as the canonical runtime implementation.

Evidence documents may reference runtime files.

The runtime files themselves belong under:

```text
database/
```

---

# 9. Database Implementation Structure

Use:

```text
database/
├── migrations/
├── oltp/
├── olap/
├── seeds/
└── tests/
```

Responsibilities:

```text
migrations/
    schema evolution and migration scripts

oltp/
    operational database objects

olap/
    warehouse / analytical objects

seeds/
    controlled development/test datasets

tests/
    SQL validation and data-quality tests
```

---

# 10. First Implementation Objective

Start with:

```text
database/migrations/001_initial_schema.sql
```

The implementation chain is:

```text
MCD V2
   |
   v
MLD V2
   |
   v
MPD PostgreSQL V2
   |
   v
001_initial_schema.sql
   |
   v
PostgreSQL execution
   |
   v
schema validation
   |
   v
constraints validation
```

Do not start OLAP, ML or API work before the OLTP foundation is validated.

---

# 11. Migration Strategy

After the target schema exists:

```text
Legacy StarterPack
       |
       v
Inspect Source
       |
       v
Mapping
       |
       v
Transform
       |
       v
Load V2
       |
       v
Validate
```

We need explicit source → target mappings.

Example conceptually:

```text
legacy client
    |
    v
CLIENT

legacy search
    |
    +--> DEMANDE
    |
    +--> DEMANDE_VERSION
```

Never guess mappings when the source schema can be inspected.

---

# 12. Migration Quality

Migration must verify:

```text
row counts
nullability
foreign keys
duplicates
invalid references
business constraints
financial consistency
```

Where useful, produce reconciliation queries.

---

# 13. PostgreSQL

The target database is PostgreSQL.

Use PostgreSQL-native design where appropriate:

```text
IDENTITY
TIMESTAMP / TIMESTAMPTZ
NUMERIC
BOOLEAN
CHECK
UNIQUE
FOREIGN KEY
INDEX
```

Avoid database-specific syntax from another engine unless migration explicitly requires it.

---

# 14. Constraints

Prefer database-enforced integrity.

Use appropriately:

```text
PRIMARY KEY
FOREIGN KEY
NOT NULL
UNIQUE
CHECK
```

Do not move every business invariant exclusively into application code.

---

# 15. Migration Safety

Migration scripts must be understandable and controlled.

Before destructive operations:

```text
inspect
backup
validate
```

Do not issue destructive SQL casually.

For destructive commands, explain exactly what will be affected before execution.

---

# 16. SQL Style

Use explicit schemas where relevant.

Prefer:

```sql
CREATE TABLE real_estate.client (
    ...
);
```

over relying implicitly on:

```text
search_path
```

for critical objects.

Use consistent naming:

```text
snake_case
lowercase
```

---

# 17. Synthetic Data

The updated StarterPack generator can be used to produce controlled synthetic datasets.

Synthetic data is useful for:

```text
development
migration
performance testing
ETL
ML training pipeline validation
```

Do not claim synthetic-data ML metrics represent real-world business performance.

---

# 18. Future Data Architecture

After OLTP implementation is validated, the planned progression is:

```text
OLTP
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

Then:

```text
dbt
Airflow
OpenMetadata
Data Quality
```

---

# 19. Future ML Extension

The project deliberately goes beyond the minimum certification requirement.

Planned matching evolution:

```text
Structured Filtering
        |
        v
Rule-Based Baseline
        |
        v
Logistic Regression
        |
        v
Random Forest
        |
        v
Model Comparison
        |
        v
MLflow
        |
        v
Model Registry
        |
        v
FastAPI Serving
```

This is a project extension, not something to remove because it exceeds the minimum requirement.

---

# 20. Future Semantic AI

Local Ollama may later provide:

```text
criteria extraction
semantic preference analysis
match explanation
document summarization
RAG
```

But:

```text
LLM != primary structured matching engine
```

Structured constraints belong first in:

```text
SQL
Python
ML
```

---

# 21. Local-First AI

The project follows:

```text
LOCAL-FIRST AI
```

External AI is an explicitly governed exception.

Local AI infrastructure includes Ollama on the controlled GPU environment.

---

# 22. MLflow

Future model experiments will track:

```text
parameters
features
dataset reference
metrics
artifacts
Git SHA
model version
```

Do not invent metrics before real execution.

Until measured:

```text
TBD
```

---

# 23. CI/CD

There should be one root:

```text
.gitlab-ci.yml
```

with modular pipeline definitions under:

```text
.gitlab/ci/
```

Do not create independent `.gitlab-ci.yml` files throughout every folder unless there is a justified architecture change.

---

# 24. GitOps

Future deployment flow:

```text
Git
 |
 v
GitLab CI
 |
 v
Container Registry
 |
 v
GitOps desired state
 |
 v
Argo CD
 |
 v
Kubernetes
```

---

# 25. Infrastructure

The existing homelab/platform should be reused where appropriate.

Relevant capabilities already available include:

```text
Kubernetes
Argo CD
Airflow
MLflow
MinIO
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
OpenMetadata
Ollama
```

Do not unnecessarily redesign the physical infrastructure during database implementation.

---

# 26. Evidence Strategy

Implementation produces evidence.

Do not invent evidence before execution.

Examples:

```text
SQL output
migration result
row counts
constraint tests
query plans
screenshots
CI output
Airflow run
MLflow run
Grafana metrics
```

Then documentation can reference those artifacts.

The direction is:

```text
IMPLEMENT
   |
   v
TEST
   |
   v
CAPTURE EVIDENCE
   |
   v
UPDATE DOCUMENTATION IF NECESSARY
```

not:

```text
invent documentation evidence
before implementation
```

---

# 27. Working Method

Work strictly step by step.

Do NOT give me ten implementation steps and expect me to execute them all.

Give:

```text
STEP 1
```

with the complete command/script required.

Then wait for my:

```text
output
```

or:

```text
YES
```

before proceeding to:

```text
STEP 2
```

If a command fails:

```text
STOP
analyse the actual output
fix that problem
```

before continuing.

---

# 28. Scripts

When asking me to create a file, always provide the **complete file content**, not fragments such as:

```text
add this below...
replace these three lines...
```

unless we are intentionally making a very small patch.

For important files such as:

```text
SQL migrations
Docker Compose
Dockerfile
GitLab CI
Python
Airflow DAG
dbt configuration
Kubernetes manifests
```

prefer the complete file.

---

# 29. Verification

Never assume a command worked.

After creating something, verify it.

Example:

```text
CREATE FILE
   |
   v
CHECK FILE
   |
   v
EXECUTE
   |
   v
CHECK RESULT
```

---

# 30. No Fabricated State

Never say:

```text
migration succeeded
tests passed
database contains X rows
model achieved X%
deployment is healthy
```

unless the runtime output demonstrates it.

Use:

```text
PLANNED
PENDING
TBD
```

where appropriate.

---

# 31. Architectural Changes

If implementation exposes a conflict with the frozen documentation:

STOP.

Explain:

```text
Current documented decision
Actual implementation problem
Possible alternatives
Recommended change
Impact
```

Then wait for approval before modifying the architecture.

---

# 32. Do Not Reopen Documentation Unnecessarily

The documentation phase has already been extensive.

Do not repeatedly propose:

```text
rewrite README
rewrite architecture
rewrite evidence
rewrite BC05
```

unless implementation reveals a real reason.

Our focus in this conversation is:

```text
BUILD THE PROJECT.
```

---

# 33. Immediate Starting Point

We are currently exactly here:

```text
DOCUMENTATION V2
      |
      | COMPLETE
      v
========================
IMPLEMENTATION BOUNDARY
========================
      |
      v
POSTGRESQL TARGET SCHEMA
      |
      v
001_initial_schema.sql
```

Before writing SQL, first inspect the existing V2 MPD documentation and confirm the exact tables, columns, PKs, FKs, UNIQUE constraints and CHECK constraints that must be implemented.

Then proceed step by step.

---

# 34. First Task

Start by reviewing the existing V2 database design from the project files.

Do **not** generate `001_initial_schema.sql` from assumptions.

First tell me which project files you need me to provide/upload if they are not already available in this Project conversation.

Once the V2 MPD is confirmed, we will create:

```text
database/migrations/001_initial_schema.sql
```

and begin the real database implementation.