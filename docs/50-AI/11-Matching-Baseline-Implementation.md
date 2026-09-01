# Deterministic Property Matching Baseline — Implementation

**Version:** 1.0  
**Status:** Implemented and Runtime Verified  
**Project:** Enterprise Real Estate Intelligence Platform  
**Component:** AI / Property Matching  
**Last Updated:** 2026-09-01

---

# 1. Purpose

This document describes the implementation and validation of the first property matching capability of the Real Estate Intelligence Platform.

The objective of this component is to rank available properties against a versioned customer search request (`demande_version`) using deterministic and explainable business rules.

This implementation deliberately precedes supervised Machine Learning.

The current transactional dataset contains insufficient real business feedback to train and evaluate a statistically credible supervised model. A deterministic baseline therefore provides:

- an immediately usable matching capability;
- an explainable reference algorithm;
- reusable feature engineering;
- a candidate retrieval strategy;
- a baseline against which future ML models can be compared;
- a mechanism for generating future matching observations and feedback;
- a reproducible evaluation path.

The deterministic matcher is not presented as a trained Machine Learning model.

---

# 2. Business Context

The platform manages real-estate search requests through:

```text
Client
  ↓
Mandat
  ↓
Demande
  ↓
DemandeVersion
```

Search criteria are stored in immutable, versioned `demande_version` records.

A property matching operation compares one specific `DemandeVersion` with properties stored in:

```text
real_estate.bien
```

This preserves an important business rule:

> A matching result must be evaluated against the exact version of the customer's requirements that existed at the time of evaluation.

This avoids silently evaluating historical results against subsequently modified search criteria.

---

# 3. Current Matching Architecture

The implemented flow is:

```text
PostgreSQL
    │
    ▼
DemandeVersion + Bien
    │
    ▼
Candidate Retrieval
    │
    ▼
Feature Engineering
    │
    ▼
Deterministic Weighted Scoring
    │
    ▼
Ranked Properties
    │
    ▼
Evaluation Result
```

The implementation currently consists of:

```text
src/ai/matching/
├── features.py
├── repository.py
└── evaluate.py
```

Responsibilities are separated between data access, feature/scoring logic and evaluation orchestration.

---

# 4. Repository Layer

File:

```text
src/ai/matching/repository.py
```

The repository layer retrieves matching inputs from PostgreSQL.

Implemented functions include:

```text
load_demande_version()
load_candidate_biens()
load_matching_input()
```

## 4.1 DemandeVersion retrieval

`load_demande_version()` retrieves the search criteria associated with a specific version identifier.

The retrieved fields include:

- version identifier;
- version number;
- version date;
- city;
- postcode;
- property type;
- minimum budget;
- maximum budget;
- minimum surface;
- minimum number of rooms;
- minimum number of bedrooms;
- maximum DPE;
- desired criteria;
- active state;
- parent demand identifier.

## 4.2 Property candidate retrieval

`load_candidate_biens()` retrieves properties from:

```text
real_estate.bien
```

Candidate retrieval begins with the requested city.

This prevents the scoring layer from unnecessarily evaluating the complete property dataset.

The repository currently uses direct Psycopg database access for the matching workload.

---

# 5. Candidate Filtering Strategy

Candidate filtering is implemented in:

```text
src/ai/matching/features.py
```

The filtering process follows three main rules.

## 5.1 City

The requested city is a hard candidate criterion.

Only properties belonging to the requested city proceed to subsequent matching operations.

## 5.2 Postcode

The requested postcode uses a conditional strategy.

```text
Requested postcode
       │
       ▼
Do exact-postcode candidates exist?
       │
   ┌───┴────┐
   │        │
  YES       NO
   │        │
   ▼        ▼
Use exact   Keep city-level
postcode    candidates
```

This avoids returning an empty result simply because the source dataset does not contain the exact requested postcode while still containing properties in the requested city.

## 5.3 Maximum budget

`budget_max` is applied as a hard candidate filter.

Properties above the customer's maximum budget are excluded from the ranked candidate set.

---

# 6. Feature Engineering

After candidate filtering, the matcher calculates explainable matching features.

Current features are:

```text
feature_location
feature_budget
feature_property_type
feature_surface
feature_rooms
feature_bedrooms
feature_dpe
```

Each feature represents one interpretable component of the business matching decision.

Missing optional search criteria do not automatically penalize a property.

This is particularly important with the current project dataset because many historical/generated search requests contain only a subset of the complete target criteria.

---

# 7. Matching Weights

The deterministic V1 scoring weights are:

| Feature | Weight |
|---|---:|
| Location | 30% |
| Budget | 30% |
| Property type | 10% |
| Surface | 10% |
| Rooms | 7% |
| Bedrooms | 7% |
| DPE | 6% |
| **Total** | **100%** |

The final score is normalized to:

```text
0 – 100
```

and rounded to two decimal places.

Results are returned in descending matching-score order.

---

# 8. Hard Filters vs Soft Criteria

The current baseline deliberately distinguishes candidate retrieval from ranking.

## Hard candidate constraints

Currently:

- city;
- exact postcode when exact-postcode candidates exist;
- maximum budget.

## Soft scoring criteria

Currently:

- property type;
- minimum budget relationship;
- minimum surface;
- minimum rooms;
- minimum bedrooms;
- DPE.

This distinction allows the matcher to preserve potentially useful candidates while ranking them according to preference compatibility.

Whether additional criteria such as property type should eventually become hard constraints remains a business decision and can be evaluated using future feedback.

The V1 algorithm should therefore be treated as a measurable baseline rather than as a final immutable business policy.

---

# 9. Evaluation Orchestration

File:

```text
src/ai/matching/evaluate.py
```

The evaluation layer provides:

```text
evaluate_demande_version()
```

It orchestrates:

```text
load matching input
        ↓
convert demand criteria
        ↓
build matching features
        ↓
compute matching score
        ↓
return ranked evaluation result
```

The returned result includes:

- `id_demande_version`;
- demand criteria;
- number of properties initially loaded;
- number of candidates remaining after filtering;
- ranked property DataFrame.

This removes the need to reproduce the matching procedure manually and provides a reusable entry point for later:

- API integration;
- evaluation jobs;
- MLflow tracking;
- model comparison;
- observability.

---

# 10. Unit Test Validation

The AI matching test suite currently contains:

```text
tests/ai/test_matching_features.py
tests/ai/test_matching_repository.py
tests/ai/test_matching_evaluate.py
```

The complete AI test suite was executed successfully:

```text
11 passed
```

Validated behaviors include:

- exact postcode preference;
- city fallback when exact postcode does not exist;
- maximum budget hard filtering;
- handling of absent optional criteria;
- score bounded between 0 and 100;
- demand retrieval;
- missing demand handling;
- property DataFrame retrieval;
- city requirement;
- combined matching input retrieval;
- evaluation orchestration.

At this milestone:

```text
11 / 11 AI tests passed
```

---

# 11. Runtime Validation — DemandeVersion 54

The deterministic matcher was executed inside the deployed Kubernetes backend against the project's generated PostgreSQL dataset.

DemandeVersion:

```text
54
```

Criteria:

```text
City:           Nantes
Postcode:       44000
Property type:  APPARTEMENT
Budget min:     300000
Budget max:     410000
Surface min:    70
Rooms min:      3
Bedrooms min:   2
DPE max:        D
```

Runtime result:

```text
Properties loaded:           800
Candidates after filtering:  721
Top score:                   90.0
Top property:                AN-90NQYQAU
```

The exact requested postcode existed in the source dataset, therefore exact-postcode matching was used.

---

# 12. Explainability Validation — DemandeVersion 54

The top candidates for DemandeVersion 54 obtained a score of:

```text
90.00
```

rather than `100.00`.

Feature inspection demonstrated why.

The highest-ranked properties satisfied:

```text
Location       = 1
Budget         = 1
Surface        = 1
Rooms          = 1
Bedrooms       = 1
DPE            = 1
Property type  = 0
```

The request required:

```text
APPARTEMENT
```

while the highest-ranked properties were:

```text
Maison
```

Since property type represents 10% of the score:

```text
100 - 10 = 90
```

The resulting score is therefore directly explainable from the configured business weights.

A candidate priced slightly below the preferred minimum budget also demonstrated partial budget scoring:

```text
Price:           294261
Budget min:      300000
feature_budget:  0.98087
Final score:     89.43
```

This validation demonstrates that the deterministic score can be decomposed and explained criterion by criterion.

---

# 13. Runtime Validation — DemandeVersion 12

A second runtime case was used specifically to validate postcode fallback.

DemandeVersion:

```text
12
```

Requested location:

```text
City:      Nantes
Postcode:  44200
```

Maximum budget:

```text
480000
```

Runtime result:

```text
Properties loaded:           800
Candidates after filtering:  776
Top score:                   100.0
```

The generated source dataset contained Nantes properties under postcode:

```text
44000
```

but no exact `44200` candidates.

The matcher therefore retained Nantes city-level candidates instead of returning an empty result.

This runtime case validates the fallback branch of the candidate retrieval algorithm.

---

# 14. Dataset Limitation

The current property dataset is generated/synthetic project data.

It must not be described as:

- production data;
- live real-estate market data;
- externally collected current market data;
- statistically representative market data.

The runtime validation proves that the software operates correctly against the deployed project dataset.

It does **not** prove real-world predictive performance.

---

# 15. Current Supervised Learning Limitation

The transactional schema is structurally capable of capturing future matching feedback through entities such as:

```text
presentation
visite
commentaire
```

However, the current project database contains very little actual feedback.

At the time of this implementation, the observed feedback included only approximately:

```text
Presentation PRESENTE: 1
Visite REALISEE:       1
Visite with note:      1
```

This is insufficient for credible supervised Machine Learning training and evaluation.

Training a model now and presenting its metrics as meaningful business performance would therefore be misleading.

---

# 16. Why Deterministic Matching Comes First

The deterministic baseline solves several problems before Machine Learning is introduced.

It provides:

1. a working business capability;
2. explainable decisions;
3. candidate retrieval;
4. reusable feature engineering;
5. testable business rules;
6. an evaluation entry point;
7. a future baseline for model comparison.

The intended evolution is:

```text
Deterministic baseline
        ↓
Matching observations
        ↓
Business feedback
        ↓
Labelled dataset
        ↓
ML baseline
        ↓
Model evaluation
        ↓
Compare ML vs deterministic baseline
        ↓
Promotion decision
```

A learned model should only replace or complement the deterministic baseline when evidence demonstrates that it provides measurable value.

---

# 17. Dependency Architecture

The project separates backend, AI runtime and training dependencies.

```text
requirements-backend.txt
        │
        ▼
requirements-ai.txt
        │
        ▼
requirements-ai-training.txt
```

## Backend dependencies

Contain the application/runtime stack such as:

- FastAPI;
- SQLAlchemy;
- Psycopg;
- Pydantic;
- Prometheus client;
- testing/runtime dependencies.

## AI runtime dependencies

`requirements-ai.txt` extends the backend dependencies with lightweight matching requirements such as:

- Pandas;
- NumPy.

## AI training dependencies

`requirements-ai-training.txt` is reserved for training-related tooling such as:

- scikit-learn;
- MLflow;
- PyTorch.

Training dependencies are intentionally excluded from the backend container.

This avoids packaging large ML/GPU dependencies into an API image that does not require them.

---

# 18. CI Separation

AI validation has a dedicated GitLab CI definition:

```text
.gitlab/ci/ai.yml
```

Its current responsibility includes:

- dependency validation;
- AI source validation;
- Python syntax validation;
- runtime dependency imports;
- AI module imports;
- AI unit tests.

Backend image publication remains separate.

This establishes a clearer responsibility boundary:

```text
ai.yml
    ↓
AI matching validation

backend-tests.yml
    ↓
Backend/API validation

backend.yml
    ↓
Backend image
    ↓
GitOps publication
    ↓
Argo CD
    ↓
Kubernetes
```

A dedicated training pipeline can be introduced later without coupling GPU/model-training dependencies to the backend CI path.

---

# 19. Container and GitOps Deployment

The deterministic AI matching implementation is packaged inside the backend runtime image.

Validated immutable image for this milestone:

```text
gitlab.local:4567/root/chasse_immobiliere/backend:0899e76b
```

The deployment path remained:

```text
Windows development repository
        ↓
GitLab
        ↓
GitLab CI
        ↓
GitLab Container Registry
        ↓
lab-gitops
        ↓
Argo CD
        ↓
Kubernetes
```

Argo CD validation:

```text
Application: real-estate-backend
Sync:        Synced
Health:      Healthy
```

The Kubernetes deployment was verified using image:

```text
backend:0899e76b
```

The running container was also verified to contain:

```text
/app/src/ai/matching/evaluate.py
/app/src/ai/matching/features.py
/app/src/ai/matching/repository.py
```

---

# 20. Runtime Evaluation Verification

The reusable `evaluate_demande_version()` function was executed directly inside the deployed Kubernetes backend against PostgreSQL.

For DemandeVersion 54:

```text
DemandeVersion:              54
Properties loaded:           800
Candidates after filtering:  721
Top score:                   90.0
Top property:                AN-90NQYQAU
```

This confirms that the reusable evaluation layer behaves consistently with the previously validated lower-level feature and repository components.

---

# 21. Current Maturity

The deterministic matching baseline has reached the following maturity:

| State | Status |
|---|---|
| Designed | YES |
| Implemented | YES |
| Unit Tested | YES |
| CI Verified | YES |
| Container Packaged | YES |
| GitOps Published | YES |
| Argo CD Synced | YES |
| Kubernetes Runtime Verified | YES |
| Generated/Synthetic Dataset Verified | YES |
| Production Data Verified | NO |
| MLflow Experiment Tracked | NOT YET |
| Supervised ML Trained | NOT YET |
| GPU Training Verified | NOT YET |
| ML Model Production Serving | NOT YET |

The distinction between these states is intentional.

Architectural capability must not be confused with implemented application capability.

---

# 22. Current Limitations

The current V1 baseline has several known limitations.

## Synthetic source data

Properties are generated for project validation rather than collected from a live real-estate source.

## Sparse search criteria

Many existing demand versions do not contain the complete target feature set.

## Geographic coverage

The generated property dataset does not cover every city represented by active search requests.

A zero-candidate result can therefore represent a source-data coverage limitation rather than a matching algorithm failure.

## Limited business feedback

There is insufficient presentation/visit/customer feedback for credible supervised learning.

## Hand-defined weights

Current weights are business-oriented deterministic parameters.

They have not been learned from historical outcomes.

## No MLflow experiment yet

The deterministic baseline has not yet been registered as an MLflow experiment/run.

---

# 23. Next Evolution

The next AI milestones are:

```text
1. Preserve deterministic evaluation evidence
2. Track deterministic baseline with MLflow
3. Define labelled-data strategy
4. Build training dataset when sufficient labels exist
5. Establish first statistical/ML baseline
6. Evaluate learned model against deterministic baseline
7. Introduce PyTorch/GPU training where justified
8. Version and govern models with MLflow
9. Expose selected inference through FastAPI
10. Add inference observability
11. Deploy through GitOps
12. Introduce RAG separately after matching is stable
```

Machine Learning is therefore an evolution of the current baseline, not a replacement introduced without measurable evidence.

---

# 24. Evidence Summary

Evidence available for this implementation includes:

- source code for feature engineering;
- source code for PostgreSQL matching extraction;
- reusable evaluation orchestration;
- 11 passing AI unit tests;
- GitLab AI validation pipeline;
- successful backend image publication;
- immutable container image;
- successful GitOps publication;
- Argo CD `Synced / Healthy`;
- Kubernetes runtime image verification;
- runtime module verification;
- DV54 exact-postcode execution;
- DV54 feature-level explainability;
- DV12 postcode-fallback execution;
- generated/synthetic data limitation explicitly documented.

Screenshots and terminal captures may be stored separately under the project evidence documentation.

---

# 25. Conclusion

The Real Estate Intelligence Platform now contains an implemented deterministic property matching baseline.

The baseline is:

- explainable;
- reproducible;
- unit tested;
- CI validated;
- containerized;
- GitOps deployed;
- runtime verified;
- validated against the project's generated dataset.

It establishes the technical and methodological foundation required for the next MLOps and Machine Learning phases.

Most importantly, the implementation maintains a clear distinction between:

```text
working deterministic intelligence
```

and:

```text
statistically validated learned intelligence
```

This distinction allows future ML models to be evaluated objectively rather than being introduced solely for technological demonstration.