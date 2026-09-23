# Real Estate Intelligence Platform

Enterprise Data & AI platform for a real-estate property-search company.

The project implements the business lifecycle of a real-estate hunter platform, from the initial client search request to property matching, visits, purchase offers, notarial transactions, invoicing, hunter remuneration, analytics and performance monitoring.

It was developed as part of the **Diginamic Data & IA — RNCP40573** program and combines application development, Data Engineering, Data Architecture, MLOps, Data Governance, Security, Observability, DevOps and GitOps within a Kubernetes-based platform.

The objective is not to demonstrate isolated technologies, but to build a coherent information system where business operations, data pipelines, analytical models, AI experiments and platform operations remain traceable and observable.

## Project scope

The platform addresses the complete property-search lifecycle:

```text
Client
  |
  v
Search Request
  |
  v
Hunter Assignment
  |
  v
Search Criteria Refinement
  |
  v
Mandate
  |
  v
Property Ingestion
  |
  v
Matching and Selection
  |
  v
Client Feedback
  |
  v
Visit and Hunter Assessment
  |
  v
Purchase Offer
  |
  v
Seller Decision
  |
  v
Notarial Process
  |
  v
Authentic Deed and Sale
  |
  v
Company Fees
  |
  v
Client Invoice
  |
  v
Hunter Remuneration
  |
  v
Performance and Analytics
```

The application is supported by a Data Platform responsible for ingestion, transformation, analytical modelling, Data Quality, metadata governance, ML experimentation and operational observability.

## Functional scope

The functional baseline contains 11 Gherkin feature files covering business rules and user journeys.

| ID | Area                                 | Scope     |
| -- | ------------------------------------ | --------- |
| 00 | Mandate and remuneration rules       | Current   |
| 01 | Client request and account           | Current   |
| 02 | Property search and visits           | Current   |
| 03 | Purchase offer and signature         | Current   |
| 04 | Hunter request handling              | Current   |
| 05 | Daily property selection             | Current   |
| 06 | Hunter assessment and purchase offer | Current   |
| 07 | Hunter remuneration and performance  | Current   |
| 08 | AI assistance for the client         | Future AI |
| 09 | AI assistance for the hunter         | Future AI |
| 10 | Hunter remuneration calculation      | Current   |

The current implementation concentrates on the deterministic operational workflow defined by `00–07` and `10`.

Features `08` and `09` define the future AI-assisted evolution of the platform and are deliberately separated from functionality already implemented and validated.

## Architecture

The platform follows an API-first, data-centric and cloud-native architecture.

```text
                             Users / API Clients
                                    |
                                    v
                            +---------------+
                            |    FastAPI    |
                            | Business API  |
                            +-------+-------+
                                    |
                    +---------------+---------------+
                    |                               |
                    v                               v
             Business Services              Matching Engine
                    |                               |
                    +---------------+---------------+
                                    |
                                    v
                            PostgreSQL OLTP
                                    |
             +----------------------+----------------------+
             |                      |                      |
             v                      v                      v
          Airflow                Warehouse             Audit
             |                      |
             v                      v
       Data Pipelines          dbt / Analytics
             |
             +----------------------+
             |
             v
       Data Quality / Lineage
             |
             v
         OpenMetadata


                  ML / AI Experimentation
                           |
                           v
                         MLflow
                           |
                           v
                         MinIO


                    Platform Delivery
                           |
              GitLab CI / Container Registry
                           |
                           v
                    GitOps Repository
                           |
                           v
                         Argo CD
                           |
                           v
                       Kubernetes


                       Observability
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      Prometheus          Loki             Tempo
          |                |                |
          +----------------+----------------+
                           |
                           v
                    OpenTelemetry
                           |
                           v
                        Grafana
```

The architecture separates four concerns:

* operational business processing;
* Data Engineering and analytics;
* AI/MLOps experimentation;
* platform engineering and operations.

PostgreSQL `real_estate` remains the operational source of truth. Warehouse and analytical models are derived from operational data and are not used to modify transactional business state.

## Application layer

The business application is implemented with:

* Python 3.12;
* FastAPI;
* Pydantic;
* SQLAlchemy;
* PostgreSQL;
* JWT authentication;
* Argon2id password hashing;
* Prometheus instrumentation.

The API covers the main business domains:

```text
Authentication
Clients
Search Requests
Hunter Assignments
Mandates
Properties
Recommendations
Presentations
Visits
Purchase Offers
Sales
Notarial Transactions
Client Invoices
Hunter Remuneration
Hunter Invoices
```

Application roles include:

```text
ADMIN
CHASSEUR
CLIENT
SERVICE
```

Authentication, role-based access control, resource ownership and audit logging are implemented at application level.

## Data architecture

The platform separates ingestion, operational and analytical data responsibilities.

```text
Data Sources
    |
    v
   RAW
    |
    v
 STAGING
    |
    v
Operational Model
    |
    +--------------------+
    |                    |
    v                    v
Matching             Warehouse
                         |
                         v
                      Analytics
                         |
                         v
                  Reporting / KPIs
```

The main logical schemas are:

```text
Fil_Rouge_Depart
raw
staging
real_estate
warehouse
analytics
migration_control
```

The `real_estate` schema contains the operational business model.

The `warehouse` and `analytics` layers provide analytical representations of operational events for reporting, performance analysis and future Data Science use cases.

## Versioned property search

A client's search criteria can evolve during the property-search process.

The platform therefore preserves versions of the search rather than overwriting the original request.

This provides traceability between:

```text
Search Request
      |
      v
Search Version
      |
      v
Structured Criteria
      |
      v
Target Sectors
      |
      v
Matching
      |
      v
Recommended Properties
```

Search criteria include budget, property type, surface, rooms, bedrooms, energy performance and geographical requirements.

Geographical targeting uses canonical sectors rather than deriving business geography only from postal codes.

This historical information also provides a foundation for future learning from search evolution and client decisions.

## Data ingestion

Apache Airflow orchestrates property-data ingestion.

The pipeline follows the general architecture:

```text
Source
  |
  v
RAW
  |
  v
Validation
  |
  v
STAGING
  |
  v
Normalization
  |
  v
Operational Property
  |
  +-----------------> Matching
  |
  +-----------------> Warehouse
```

The ingestion architecture preserves source lineage and geographical information through the transformation process.

Controlled synthetic data is used for development and validation. It must not be interpreted as real market data.

## Property matching

The current recommendation system uses a deterministic and explainable matching baseline.

Current dimensions are:

| Criterion          | Weight |
| ------------------ | -----: |
| Location           |    30% |
| Budget             |    30% |
| Property type      |    10% |
| Surface            |    10% |
| Rooms              |     7% |
| Bedrooms           |     7% |
| Energy performance |     6% |

Budget acts as a hard eligibility criterion.

Geographical filtering supports structured sector information.

The deterministic baseline provides a reproducible reference against which future Machine Learning approaches can be evaluated.

## MLflow and MLOps

MLflow provides experiment tracking for matching and future Machine Learning work.

The MLOps foundation supports:

* experiment tracking;
* parameters and metrics;
* dataset evaluation;
* baseline/model comparison;
* artifact management;
* reproducible experiments.

MinIO is used for artifact storage.

Synthetic labelled datasets are currently used to validate the matching and evaluation pipeline.

Results obtained from controlled synthetic datasets are treated as technical validation and not as evidence of real-world predictive performance.

A future trained model must demonstrate measurable improvement over the deterministic baseline before being considered for production use.

## Mandate lifecycle

The platform supports exclusive and non-exclusive mandates.

Mandates have an explicit contractual lifecycle:

```text
Mandate
   |
   v
Initial Period
   |
   +------> Expiration
   |
   +------> Renewal
                |
                v
          New Mandate Period
```

A standard mandate period lasts six months.

Historical periods are preserved for operational traceability and analytics.

## Offer and transaction lifecycle

The operational model supports purchase offers and their state transitions.

```text
Property Presentation
        |
        v
Purchase Offer
        |
        +--------> Refused
        |
        +--------> Revised
        |
        +--------> Accepted
                        |
                        v
                 Notarial Process
                        |
                        v
                 Authentic Deed
                        |
                        v
                       Sale
```

Offer revisions and decisions remain auditable.

## Notarial workflow

The notarial process is explicitly represented instead of being reduced to a sale date.

```text
Accepted Offer
      |
      v
Notarial Dossier
      |
      v
Signing Appointment
      |
      v
Authentic Deed
      |
      v
Sale
      |
      v
Notary Collects Company Fees
      |
      v
Company Receives Funds
```

The model deliberately distinguishes:

```text
COLLECTE_NOTAIRE
```

from:

```text
RECEPTION_ENTREPRISE
```

Collection by the notary on behalf of the company does not mean that the company has already received the funds.

This distinction allows financial state to remain explicit and auditable.

## Invoicing and hunter remuneration

After the transaction, the platform handles both client invoicing and hunter remuneration.

```text
Sale
  |
  v
Company Fees
  |
  v
Client Invoice
  |
  v
Company Receives Funds
  |
  v
Hunter Remuneration Eligibility
  |
  v
Hunter Invoice
  |
  v
Invoice Verification
  |
  v
Payment Scheduling
  |
  v
Payment
```

Hunter remuneration is calculated deterministically.

The calculation considers:

* entitlement to remuneration;
* company fees;
* purchase-price bracket;
* hunter-specific commission scale where applicable;
* seniority;
* performance indicators;
* minimum and maximum commission boundaries.

The remuneration base is the company's fees rather than the property purchase price.

Calculation inputs are frozen at the authentic-deed date so historical remuneration remains reproducible when commission scales or performance indicators subsequently change.

## Data Warehouse and analytics

Operational data is transformed into analytical models used to analyse:

* mandates;
* mandate periods;
* property searches;
* recommendations;
* transactions;
* notarial processes;
* payments;
* hunter performance.

The analytical layer is deliberately separated from the OLTP model.

Fact tables preserve explicit business grains, while dimensions provide reusable analytical context.

## Data Quality

Data Quality is integrated throughout the Data Platform.

Controls address:

* completeness;
* validity;
* consistency;
* uniqueness;
* referential integrity;
* business-rule compliance;
* financial reconciliation;
* pipeline integrity;
* analytical reconciliation;
* ML dataset quality.

Important project-specific controls include:

```text
Search criteria integrity
Sector consistency
Mandate chronology
Offer and transaction chronology
Notarial chronology
Company-fee reconciliation
Invoice/payment reconciliation
OLTP-to-Warehouse reconciliation
ML ground-truth isolation
```

Data Quality results are intended to become observable platform signals rather than remaining isolated test outputs.

## Data Governance

OpenMetadata provides the metadata and governance layer.

It is used to support:

* technical metadata;
* data discovery;
* ownership;
* lineage;
* business terminology;
* Data Quality visibility;
* documentation of critical data assets.

The objective is to maintain traceability from source data through ingestion, operational storage, warehouse transformations and analytical or AI consumption.

## Observability

Observability is a first-class architectural capability of the platform.

It covers both technical infrastructure and business/data workflows.

The stack includes:

| Component     | Responsibility                                |
| ------------- | --------------------------------------------- |
| Prometheus    | Metrics collection and time-series monitoring |
| Grafana       | Dashboards and operational visualization      |
| Loki          | Centralized logs                              |
| Promtail      | Log collection                                |
| Tempo         | Distributed tracing                           |
| OpenTelemetry | Telemetry instrumentation and collection      |
| Pushgateway   | Metrics from batch and short-lived workloads  |

The FastAPI backend exposes Prometheus metrics directly.

Business-oriented metrics currently cover the recommendation workflow, including:

```text
Recommendation request volume
Recommendation failures
Request duration
Eligible property counts
Selected property counts
Created presentations
Existing presentations
```

This allows monitoring to go beyond CPU and memory and provide visibility into actual application behaviour.

The observability architecture follows three principal signals:

```text
Metrics
   |
   +---- Prometheus
   |
   v
Grafana

Logs
   |
   +---- Promtail
   |
   v
Loki
   |
   v
Grafana

Traces
   |
   +---- OpenTelemetry
   |
   v
Tempo
   |
   v
Grafana
```

Data pipelines and batch processes can also expose operational metrics through Prometheus and Pushgateway.

The objective is to correlate:

```text
Infrastructure state
        +
Application behaviour
        +
Business metrics
        +
Data pipeline execution
```

within a common operational view.

Dashboards and observability configuration are managed as code and deployed through the platform delivery process.

## Security and auditability

Security is integrated into the application architecture.

Implemented controls include:

* authenticated application identities;
* Argon2id password hashing;
* JWT authentication;
* role-based authorization;
* resource ownership controls;
* business audit logging;
* non-root application containers;
* separation of secrets from source code.

Sensitive state transitions are designed to retain:

```text
Who
What
When
Business object
Previous state
New state
Context
```

This is particularly important for mandates, offers, notarial transactions, invoicing and payments.

## CI/CD and GitOps

The delivery architecture follows GitOps principles.

```text
Source Code
    |
    v
GitLab CI
    |
    +---- Tests
    |
    +---- Validation
    |
    +---- Container Build
    |
    v
Container Registry
    |
    v
GitOps Repository
    |
    v
Argo CD
    |
    v
Kubernetes
```

Git remains the source of truth for permanent platform changes.

Argo CD continuously reconciles the desired configuration with the Kubernetes environment.

## Business continuity

The platform includes continuity and disaster-recovery mechanisms covering:

* PostgreSQL backup;
* automated backup execution;
* restoration procedures;
* GitOps-based infrastructure reconstruction;
* RPO/RTO analysis;
* recovery documentation.

Recovery validation is considered part of the platform lifecycle; the existence of a backup alone is not considered sufficient evidence of recoverability.

## Technology stack

| Area                       | Technologies                          |
| -------------------------- | ------------------------------------- |
| Backend                    | Python, FastAPI, Pydantic, SQLAlchemy |
| Database                   | PostgreSQL                            |
| Data Engineering           | Airflow, dbt, MinIO                   |
| Matching / ML              | Python, scikit-learn, MLflow          |
| Governance                 | OpenMetadata                          |
| Containerization           | Docker                                |
| Orchestration              | Kubernetes                            |
| CI/CD                      | GitLab CI/CD                          |
| GitOps                     | Argo CD                               |
| Metrics                    | Prometheus                            |
| Dashboards                 | Grafana                               |
| Logging                    | Loki, Promtail                        |
| Tracing                    | Tempo, OpenTelemetry                  |
| Batch metrics              | Pushgateway                           |
| Local AI experimentation   | Ollama                                |
| Architecture documentation | PlantUML                              |

## Repository structure

```text
.
├── src/
│   ├── api/                  # FastAPI business application
│   └── ai/
│       └── matching/         # Matching and evaluation
│
├── database/
│   ├── migrations/           # Database evolution
│   └── tests/                # SQL and data validation
│
├── pipelines/
│   ├── airflow/              # Pipeline orchestration
│   └── dbt/                  # Analytical transformations
│
├── governance/               # Metadata and governance
├── observability/            # Metrics, dashboards and alerts
├── deploy/                   # Container and Kubernetes resources
├── scripts/                  # Automation and CI helpers
├── tests/                    # Automated tests
├── docs/                     # Project documentation
└── evidence/                 # Runtime and competency evidence
```

## Future AI capabilities

The functional specification separates current operational functionality from future AI assistance.

Future client-side capabilities include:

* search-project feasibility analysis;
* market-aware criteria refinement;
* preference learning;
* personalized recommendations;
* personalized post-purchase assistance.

Future hunter-side capabilities include:

* feasibility reports;
* assisted search refinement;
* property deduplication and ranking;
* negotiation estimation;
* learning from rejected properties;
* assisted assessment drafting;
* purchase-offer suggestions;
* automated document verification;
* mandate-renewal assistance.

These capabilities will be introduced progressively and evaluated against deterministic baselines.

AI is intended to assist the business workflow, not replace deterministic rules where reproducibility and auditability are required.

## Project status

The main platform foundations are operational:

```text
Business API
PostgreSQL OLTP
Versioned search model
Mandate lifecycle
Property ingestion
Deterministic matching
MLflow experimentation
Offer lifecycle
Notarial workflow
Client invoicing
Hunter remuneration
Data Warehouse
Data Quality
OpenMetadata
Security / RBAC / Audit
Observability
CI/CD
GitOps
Kubernetes
PCA / PRA
```

Current work focuses on completing and validating the remaining functional scenarios before expanding the future AI layer.

Priority areas include:

1. completion of the hunter payment and performance lifecycle;
2. complete functional coverage of the current User Stories;
3. notification and appointment workflows;
4. richer client feedback and property prioritisation;
5. hunter property assessments;
6. OLTP/Warehouse reconciliation;
7. Data Quality and governance consolidation;
8. final security and recovery evidence;
9. future AI and ML experimentation.

## RNCP40573

The project is developed as part of the Diginamic Data & IA curriculum and is designed to provide practical evidence across **BC01–BC06**.

Evidence is maintained through the complete engineering chain:

```text
Business Requirement
        |
        v
Architecture Decision
        |
        v
Implementation
        |
        v
Automated Test
        |
        v
Runtime Evidence
        |
        v
Documentation
        |
        v
Competency Evidence
```

The objective is to demonstrate competencies through implemented and validated engineering work rather than through the presence of technologies alone.

## Documentation

Detailed technical documentation is maintained under `docs/`.

It covers:

```text
Business requirements
Application architecture
Infrastructure architecture
Data architecture
Data Quality
Data Governance
AI and MLOps
Security
Observability
DevOps and GitOps
PCA / PRA
Architecture Decision Records
RNCP competency evidence
```

The README presents the overall project.

Detailed implementation decisions, operational procedures and runtime evidence remain in their respective technical documents.
