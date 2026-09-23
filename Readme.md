# 🏠 Real Estate Intelligence Platform

An enterprise-grade **Data & AI platform for real-estate property search**, designed to support the complete journey between a property buyer and a real-estate hunter — from the initial search request to property matching, purchase, invoicing, remuneration and analytics.

The project combines **Software Engineering, Data Engineering, AI/MLOps, Data Governance, DevOps, Security and Observability** in a cloud-native architecture deployed on Kubernetes.

Developed as part of the **Diginamic Data & IA — RNCP40573** program.

---

## 🎯 Project Overview

Finding a property is more complex than simply filtering real-estate listings.

A buyer defines a project involving multiple criteria:

* location;
* budget;
* property type;
* surface;
* number of rooms and bedrooms;
* energy performance;
* personal preferences;
* additional flexible requirements.

A real-estate hunter then assists the buyer throughout the search and acquisition process.

The platform digitalizes and structures this complete workflow while providing a foundation for intelligent property recommendations and future AI-assisted services.

---

## 💼 Business Workflow

The platform models the complete real-estate hunting lifecycle:

```text
Buyer
  │
  ▼
Search Request
  │
  ▼
Hunter Assignment
  │
  ▼
Search Criteria Refinement
  │
  ▼
Search Mandate
  │
  ▼
Property Ingestion
  │
  ▼
Matching & Recommendations
  │
  ▼
Property Selection
  │
  ▼
Visits & Hunter Assessment
  │
  ▼
Purchase Offer
  │
  ▼
Seller Decision
  │
  ▼
Notarial Process
  │
  ▼
Authentic Deed & Sale
  │
  ▼
Company Fees
  │
  ▼
Client Invoice
  │
  ▼
Hunter Remuneration
  │
  ▼
Analytics & Performance
```

The system maintains traceability across this lifecycle so that important business decisions and state transitions remain auditable.

---

# ✨ Functional Scope

The project is based on the functional scenarios defined by the Fil Rouge StarterPack.

The functional specification currently contains **11 Gherkin feature files (`00–10`)**.

### Current Business Journey

| Area                | Capabilities                                                 |
| ------------------- | ------------------------------------------------------------ |
| Search request      | Creation and versioning of buyer requirements                |
| Hunter assignment   | Assignment, acceptance and refusal                           |
| Buyer account       | Identity and role-based access                               |
| Search mandate      | Exclusive/non-exclusive mandates and renewals                |
| Search criteria     | Structured and versioned property requirements               |
| Geographic search   | Sector-based search and targeting                            |
| Property ingestion  | Automated ingestion and transformation                       |
| Matching            | Property eligibility and deterministic ranking               |
| Recommendations     | Property selections associated with buyer searches           |
| Visits              | Property visit lifecycle                                     |
| Purchase offers     | Submission, revision, acceptance and refusal                 |
| Notarial workflow   | Notary, appointment, authentic deed and transaction tracking |
| Sale                | Final transaction recording                                  |
| Company fees        | Deterministic calculation and financial tracking             |
| Client invoicing    | Invoice lifecycle after transaction                          |
| Hunter remuneration | Commission calculation and invoice workflow                  |
| Audit               | Traceability of sensitive business operations                |

Some user-facing workflow elements are still being consolidated, particularly notifications, appointments, client feedback and richer property assessment workflows.

---

# 🤖 AI-Assisted Target Journey

The project distinguishes between the **current operational workflow** and the **future AI-assisted workflow**.

Future capabilities defined by the functional specification include:

### Buyer AI Assistance

* real-time project feasibility indicators;
* market-aware search refinement;
* personalized recommendations;
* learning from accepted and rejected properties;
* personalized post-purchase services.

### Real-Estate Hunter AI Assistance

* automated feasibility reports;
* assisted criteria refinement;
* property deduplication;
* intelligent ranking;
* negotiation-price estimation;
* learning from buyer feedback;
* assisted property-assessment writing;
* purchase-offer suggestions;
* automated document verification;
* mandate-renewal recommendations.

The architecture is intentionally designed so these capabilities can be progressively introduced without replacing deterministic business rules that require strict auditability.

---

# 🧠 Property Matching

The platform currently uses a **deterministic and explainable matching baseline**.

A buyer's search criteria are transformed into structured features and compared with available properties.

Current matching dimensions include:

| Feature            | Weight |
| ------------------ | -----: |
| Location           |    30% |
| Budget             |    30% |
| Property type      |    10% |
| Surface            |    10% |
| Rooms              |     7% |
| Bedrooms           |     7% |
| Energy performance |     6% |

Budget and geographical eligibility can also act as filtering constraints before ranking.

This baseline provides:

* reproducible recommendations;
* explainable scores;
* measurable evaluation;
* a reference against which future ML models can be compared.

The deterministic baseline is intentionally kept separate from future trained ML models.

---

# 🧪 Machine Learning & MLOps

The project includes an MLOps foundation built around **MLflow**.

It supports:

* experiment tracking;
* dataset evaluation;
* model/baseline comparison;
* metrics logging;
* artifact storage;
* reproducible experiments.

Synthetic labelled datasets are currently used to validate the matching and evaluation pipeline.

Synthetic evaluation results are treated as **technical validation**, not as evidence of real-world predictive performance.

Future work will introduce more representative datasets and compare trained models against the deterministic baseline before any production promotion.

---

# 🏗️ Architecture

The platform follows a modular, API-first and cloud-native architecture.

```text
                        Users / Applications
                                │
                                ▼
                         ┌─────────────┐
                         │   FastAPI   │
                         │ Business API│
                         └──────┬──────┘
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
                  ▼                           ▼
          Business Services            Matching Engine
                  │                           │
                  └─────────────┬─────────────┘
                                │
                                ▼
                         PostgreSQL OLTP
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
          Airflow            Warehouse        OpenMetadata
             │                  │                  │
             ▼                  ▼                  ▼
        Data Pipelines      Analytics        Governance
             │
             ▼
          MLflow
             │
             ▼
      ML / AI Experiments


        GitLab CI/CD → GitOps → Argo CD → Kubernetes

                         │
                         ▼
              Prometheus / Grafana
                Loki / Tempo / OTEL
```

---

# 🗄️ Data Architecture

The platform separates operational, ingestion and analytical responsibilities.

```text
External / Generated Sources
            │
            ▼
           RAW
            │
            ▼
         STAGING
            │
            ▼
      Operational Model
           OLTP
            │
            ▼
        Warehouse
            │
            ▼
         Analytics
            │
            ▼
      BI / AI / Reporting
```

Main logical data areas include:

* operational real-estate data;
* raw ingestion;
* staging transformations;
* analytical warehouse;
* analytics marts;
* migration tracking.

The **OLTP model remains the operational source of truth**, while the warehouse contains analytical representations of business events.

---

# 🔄 Versioned Search Requirements

Property searches evolve over time.

Instead of overwriting the original request, the platform keeps **versioned search requirements**.

This makes it possible to understand:

* what the buyer initially requested;
* how the search evolved;
* which criteria were changed;
* which version generated a recommendation;
* which properties were proposed under which requirements.

Structured geographical sectors are also attached to search versions.

This provides both business traceability and valuable historical data for future ML models.

---

# 🏘️ Property Data Pipeline

Property data is processed through an automated ingestion architecture.

```text
Property Sources
      │
      ▼
     RAW
      │
      ▼
   Validation
      │
      ▼
   STAGING
      │
      ▼
Normalization
      │
      ▼
     BIEN
      │
      ├────────► Matching
      │
      └────────► Warehouse
```

**Apache Airflow** orchestrates ingestion and transformation workflows.

The ingestion system also preserves lineage information required for Data Quality and governance.

---

# 💰 Mandates and Remuneration

The business model supports both:

* exclusive mandates;
* non-exclusive mandates.

Mandates have a contractual lifecycle and can be renewed while preserving their historical periods.

Hunter remuneration is calculated deterministically.

The calculation considers:

* right to remuneration;
* company fees;
* purchase amount bracket;
* mandate characteristics;
* hunter performance;
* seniority;
* historical performance indicators.

The calculation remains auditable and is frozen using the business conditions applicable at the authentic-deed date.

This ensures that historical remuneration remains reproducible even when future commission scales change.

---

# ⚖️ Notarial Transaction Workflow

The platform models the final real-estate transaction through an explicit notarial workflow.

```text
Accepted Offer
      │
      ▼
Notarial Dossier
      │
      ▼
Signing Appointment
      │
      ▼
Authentic Deed
      │
      ▼
Sale
      │
      ▼
Company Fees Collected
      │
      ▼
Company Receives Funds
```

A deliberate distinction is maintained between:

**fees collected by the notary on behalf of the company**

and

**funds actually received by the company**.

This allows the financial lifecycle to remain explicit and auditable.

---

# 📊 Analytics & Data Warehouse

Operational events are transformed into analytical models for:

* mandate analysis;
* hunter performance;
* search performance;
* recommendation analysis;
* transaction monitoring;
* financial analysis;
* notarial process analysis.

The warehouse is designed separately from the transactional model so operational and analytical workloads retain appropriate data grains.

---

# 🧹 Data Quality

Data Quality is treated as a platform capability rather than an isolated validation step.

Controls cover:

* completeness;
* consistency;
* validity;
* uniqueness;
* referential integrity;
* business-rule compliance;
* financial reconciliation;
* pipeline integrity;
* ML dataset quality.

Particular attention is given to:

* search geography;
* mandate validity;
* transaction chronology;
* notarial events;
* financial reconciliation;
* OLTP/warehouse reconciliation;
* AI dataset leakage.

---

# 🧭 Data Governance

**OpenMetadata** provides the governance foundation.

The governance architecture supports:

* technical metadata;
* ownership;
* lineage;
* business terminology;
* data discovery;
* Data Quality visibility;
* documentation of critical data assets.

Governance is progressively enriched as new operational, analytical and AI assets are introduced.

---

# 🔐 Security

Security is integrated into the application architecture.

Implemented controls include:

* authenticated application identities;
* password hashing with Argon2id;
* JWT authentication;
* role-based access control;
* resource ownership controls;
* audit logging;
* non-root application containers;
* secret separation from application source code.

Main application roles include:

```text
ADMIN
CHASSEUR
CLIENT
SERVICE
```

Sensitive business operations are designed to remain attributable and auditable.

---

# 📈 Observability

The platform integrates:

* **Prometheus** — metrics;
* **Grafana** — dashboards;
* **Loki** — logs;
* **Tempo** — distributed traces;
* **OpenTelemetry** — telemetry collection.

Application-specific metrics monitor areas such as:

* recommendation requests;
* matching latency;
* failures;
* eligible properties;
* selected properties;
* business workflow activity.

Observability configuration is deployed alongside the platform through GitOps.

---

# 🚀 DevOps & GitOps

The platform follows an automated delivery model.

```text
Developer
    │
    ▼
Git Repository
    │
    ▼
GitLab CI
    │
    ├── Tests
    ├── Validation
    ├── Security / Quality checks
    └── Container Build
              │
              ▼
        Container Registry
              │
              ▼
        GitOps Repository
              │
              ▼
           Argo CD
              │
              ▼
          Kubernetes
```

Permanent Kubernetes deployments are controlled through **GitOps** rather than manual cluster modifications.

---

# ☸️ Kubernetes Platform

The application runs on a highly available Kubernetes platform.

The platform hosts separate services for:

* application workloads;
* PostgreSQL;
* Airflow;
* MLflow;
* metadata governance;
* monitoring;
* logging;
* tracing;
* GitOps delivery.

The infrastructure is designed to demonstrate realistic platform-engineering practices while remaining suitable for a training and portfolio environment.

---

# ♻️ Business Continuity & Disaster Recovery

The project includes PCA/PRA practices covering:

* PostgreSQL backups;
* automated backup scheduling;
* recovery procedures;
* GitOps-based infrastructure reconstruction;
* recovery documentation;
* RPO/RTO analysis.

Backup availability alone is not considered sufficient: recovery procedures are part of the validation strategy.

---

# 🧰 Technology Stack

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL
* JWT
* Argon2id

### Data Engineering

* PostgreSQL
* Apache Airflow
* dbt
* MinIO

### AI / MLOps

* Python
* scikit-learn
* MLflow
* deterministic recommendation engine
* GPU-capable experimentation environment
* Ollama for future local LLM experimentation

### Data Governance

* OpenMetadata
* Data Quality controls
* lineage and metadata management

### DevOps / Platform

* Docker
* Kubernetes
* GitLab CI/CD
* GitLab Container Registry
* Argo CD
* GitOps

### Observability

* Prometheus
* Grafana
* Loki
* Tempo
* OpenTelemetry

---

# 📁 Repository Structure

```text
.
├── src/
│   ├── api/                  # FastAPI business application
│   └── ai/
│       └── matching/         # Matching and evaluation
│
├── database/
│   ├── migrations/           # Database evolution
│   └── tests/                # SQL validation
│
├── pipelines/
│   ├── airflow/              # Data orchestration
│   └── dbt/                  # Analytical transformations
│
├── governance/               # OpenMetadata / governance
├── observability/            # Metrics, dashboards and alerts
├── deploy/                   # Container and Kubernetes resources
├── scripts/                  # Automation and CI helpers
├── tests/                    # Automated test suites
├── docs/                     # Technical documentation
└── evidence/                 # Runtime / competency evidence
```

---

# 🧪 Testing Strategy

Testing covers several layers of the platform:

```text
Unit Tests
     │
     ▼
Service / Business Tests
     │
     ▼
API Tests
     │
     ▼
Database Tests
     │
     ▼
Data Pipeline Tests
     │
     ▼
AI / Matching Tests
     │
     ▼
Controlled End-to-End Validation
```

Runtime evidence is kept separate from automated unit-test evidence.

A passing test demonstrates the tested behaviour; it does not automatically prove the state of a live deployment.

---

# 🎓 RNCP40573

The project is designed to provide practical evidence across the **BC01–BC06 competency blocks**.

Evidence is based on actual project artifacts rather than technology names alone:

```text
Business Requirement
        │
        ▼
Architecture Decision
        │
        ▼
Implementation
        │
        ▼
Automated Test
        │
        ▼
Runtime Evidence
        │
        ▼
Documentation
        │
        ▼
RNCP Competency Evidence
```

This approach makes the project suitable both as an educational deliverable and as a professional technical portfolio.

--
