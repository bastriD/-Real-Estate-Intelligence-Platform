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

The project separates application runtime, deterministic AI/MLOps runtime and future training dependencies.

The current dependency chain is:

```text
requirements-backend.txt
        │
        ▼
requirements-ai.txt
        │
        ▼
requirements-ai-mlops.txt
        │
        ▼
requirements-ai-training.txt
```

## 17.1 Backend dependencies

`requirements-backend.txt` contains the application runtime stack, including:

- FastAPI;
- Uvicorn;
- Pydantic;
- SQLAlchemy;
- Psycopg;
- Prometheus client;
- backend testing/runtime dependencies.

These dependencies are sufficient for the application/API layer.

## 17.2 Deterministic AI dependencies

`requirements-ai.txt` extends the backend runtime with the libraries required by the deterministic matching implementation:

- Pandas;
- NumPy.

The deterministic matching implementation therefore remains lightweight and does not require a Machine Learning framework.

## 17.3 MLOps dependencies

`requirements-ai-mlops.txt` extends the deterministic AI runtime with:

- MLflow.

This dependency layer supports:

- experiment tracking;
- parameters;
- metrics;
- tags;
- evaluation artifacts;
- execution traceability.

MLflow is deliberately separated from the normal backend image.

## 17.4 Training dependencies

`requirements-ai-training.txt` extends the MLOps environment with training-oriented dependencies such as:

- scikit-learn;
- PyTorch.

These dependencies remain reserved for future model-training workloads.

They are not required by the current deterministic matcher.

This separation avoids packaging large ML and GPU-oriented dependencies into workloads that do not need them.

The resulting architecture is:

```text
Backend runtime
      │
      ▼
Deterministic AI runtime
      │
      ▼
MLOps evaluation runtime
      │
      ▼
Future ML training runtime
```

This dependency layering also provides clearer container responsibility and reduces unnecessary runtime complexity.

---

# 18. CI and Runtime Separation

AI and MLOps responsibilities are separated across dedicated GitLab CI definitions.

The principal CI responsibilities are:

```text
.gitlab/ci/ai.yml
        │
        ▼
Deterministic AI validation

.gitlab/ci/ai-mlops.yml
        │
        ├── build dedicated AI/MLOps image
        │
        └── trigger ephemeral evaluation Job

.gitlab/ci/backend-tests.yml
        │
        ▼
Backend/API validation

.gitlab/ci/backend.yml
        │
        ▼
Backend image + permanent GitOps publication
```

## 18.1 Deterministic AI validation

`ai.yml` validates:

- AI dependencies;
- Python syntax;
- matching modules;
- repository extraction;
- evaluation orchestration;
- AI unit tests.

The validated deterministic matching test suite contains:

```text
11 / 11 passing tests
```

## 18.2 AI/MLOps image build

`ai-mlops.yml` builds a dedicated image from:

```text
deploy/docker/Dockerfile.ai-mlops
```

The image contains:

```text
deterministic matching
+
PostgreSQL client library
+
Pandas / NumPy
+
MLflow client
```

Training dependencies are deliberately excluded.

The validated immutable image used for the final traceability execution was:

```text
gitlab.local:4567/root/chasse_immobiliere/ai-mlops:1e347521
```

## 18.3 Ephemeral evaluation execution

The deterministic evaluation is not a permanent application workload.

It therefore does not require:

```text
Deployment
Service
Ingress
Argo CD Application
```

Instead, GitLab CI triggers an ephemeral Kubernetes Job:

```text
GitLab CI
    │
    ▼
Shell Runner
    │
    ▼
kubectl
    │
    ▼
Kubernetes Job
real-estate-matching-evaluation
```

This distinction is intentional.

Permanent application resources continue to use the project's GitOps/Argo CD deployment model.

Ephemeral evaluation workloads are explicitly triggered by GitLab CI.

---

# 19. Backend and MLOps Deployment Responsibilities

The deterministic matching source code is reusable by both the application runtime and the dedicated evaluation runtime.

Two different execution paths therefore exist.

## 19.1 Permanent backend path

The permanent application deployment remains:

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
        ↓
real-estate-backend
```

The backend deployment has previously been verified:

```text
Application: real-estate-backend
Sync:        Synced
Health:      Healthy
```

The deterministic matching modules were also verified inside the deployed backend runtime.

## 19.2 Ephemeral MLOps evaluation path

The MLOps evaluation follows a different execution path:

```text
Git commit
    ↓
GitLab Pipeline
    ↓
ai-mlops:build-image
    ↓
GitLab Container Registry
    ↓
immutable ai-mlops image
    ↓
ai-mlops:evaluate
    ↓
GitLab shell runner
    ↓
Kubernetes Job
    ↓
PostgreSQL + MLflow
    ↓
Job Complete
```

The evaluation Job is intentionally ephemeral.

No permanent service is exposed for it.

This preserves a clean separation between:

```text
application serving
```

and:

```text
batch evaluation / MLOps execution
```

---

# 20. Kubernetes MLOps Runtime Verification

The dedicated evaluation workload is defined by:

```text
deploy/mlops/matching-evaluation-job.yaml
```

The Job runs in:

```text
namespace: real-estate
```

with the name:

```text
real-estate-matching-evaluation
```

The validated execution used:

```text
Image:
gitlab.local:4567/root/chasse_immobiliere/ai-mlops:1e347521
```

Final Kubernetes state:

```text
Job:
real-estate-matching-evaluation

Status:
Complete

Completions:
1/1

Pod:
Completed

Node:
k8s-wk-03
```

The execution completed successfully in approximately seven seconds.

The Job consumed:

```text
PostgreSQL
real-estate-postgresql.real-estate.svc.cluster.local

MLflow
mlflow-tracking.mlflow.svc.cluster.local:5000
```

PostgreSQL credentials were supplied through the existing Kubernetes Secret:

```text
real-estate-postgresql-secret
```

The GitLab Registry pull secret used was:

```text
gitlab-registry-auth
```

No database credentials are hardcoded in the Job manifest.

---

# 21. MLflow Experiment Tracking

The deterministic baseline is now tracked in MLflow.

Experiment:

```text
real-estate-deterministic-matching
```

Experiment ID:

```text
3
```

Final validated run:

```text
Run name:
matching-baseline-dv-54

Run ID:
594285bb07c54a348ee73d80d440d57b

Status:
Finished
```

The tracked run corresponds to:

```text
DemandeVersion 54
```

and was executed against the project's generated/synthetic property dataset.

This does not represent a trained model.

The run is explicitly tagged as:

```text
model_family = deterministic
model_type = weighted-rule-baseline
business_use_case = property-matching
data_type = generated-synthetic-project-data
training_required = false
evaluation_type = deterministic-baseline
model_registry_enabled = false
```

This distinction prevents the deterministic algorithm from being incorrectly presented as a trained Machine Learning model.

---

# 22. MLflow Parameters and Metrics

The search criteria used during evaluation are persisted as MLflow parameters.

For DemandeVersion 54:

```text
ville             = Nantes
code_postal       = 44000
type_bien         = APPARTEMENT
budget_min        = 300000
budget_max        = 410000
surface_min       = 70
nb_pieces_min     = 3
nb_chambres_min   = 2
dpe_max           = D
```

The evaluation produced the following tracked metrics:

| Metric | Value |
|---|---:|
| `properties_loaded` | 800 |
| `candidates_after_filtering` | 721 |
| `top_matching_score` | 90.00 |
| `mean_matching_score` | 72.42 |
| `median_matching_score` | 70.97 |

These metrics demonstrate that MLflow tracks the actual deterministic evaluation output rather than merely recording execution status.

The top score remains consistent with the previously validated explainability case:

```text
90.00
```

The missing 10 points correspond to the property-type mismatch between the requested:

```text
APPARTEMENT
```

and the highest-ranked:

```text
Maison
```

while property type carries 10% of the deterministic score.

---

# 23. MLflow Evaluation Artifacts

The evaluation runtime generates and stores two artifacts:

```text
evaluation/
├── ranked_candidates.csv
└── evaluation_metadata.json
```

## 23.1 Ranked candidates

`ranked_candidates.csv` contains the evaluated property candidates and their matching results.

The first ranked candidate in the validated execution was:

```text
reference_externe: AN-90NQYQAU
ville:             Nantes
code_postal:       44000
type_bien:         Maison
prix:              303316
surface:           275
nb_pieces:         5
nb_chambres:       2
matching_score:    90.00
```

The artifact provides a reproducible record of the ranking produced during a specific evaluation run.

## 23.2 Evaluation metadata

`evaluation_metadata.json` records execution context including:

```text
run_id
timestamp_utc
experiment_name
tracking_uri
id_demande_version
properties_loaded
candidates_after_filtering
top_matching_score
baseline_type
data_type
model_training
model_registry
GitLab traceability
```

For the validated execution, the metadata explicitly identifies:

```text
baseline_type:
deterministic-weighted-rules

data_type:
generated-synthetic-project-data

model_training:
false

model_registry:
false
```

The artifact is therefore self-describing and preserves the methodological status of the evaluation.

---

# 24. GitLab-to-MLflow Traceability

The evaluation pipeline now provides explicit source-code and CI traceability.

GitLab predefined CI metadata is injected into the Kubernetes Job and then persisted as MLflow tags.

The implemented lineage is:

```text
GitLab predefined variables
        ↓
ai-mlops:evaluate
        ↓
rendered Kubernetes Job
        ↓
Pod environment
        ↓
run_evaluation.py
        ↓
MLflow tags
        ↓
evaluation_metadata.json
```

The final validated run recorded:

```text
git_commit_sha:
1e3475211bd86bf248e9f0d7b60bac89e6864cc6

git_commit_short_sha:
1e347521

git_branch:
main

git_ref_name:
main

git_repository:
https://gitlab.local/root/chasse_immobiliere

git_project_path:
root/chasse_immobiliere

git_pipeline_id:
1248

git_job_id:
12368

git_job_name:
ai-mlops:evaluate
```

Pipeline and Job URLs are also persisted.

This establishes a direct traceability chain:

```text
Git commit 1e347521
        ↓
GitLab Pipeline 1248
        ↓
Immutable image ai-mlops:1e347521
        ↓
GitLab Job 12368
        ↓
Kubernetes evaluation Job
        ↓
DemandeVersion 54
        ↓
Deterministic matching evaluation
        ↓
MLflow Run 594285bb07c54a348ee73d80d440d57b
        ├── parameters
        ├── metrics
        ├── traceability tags
        ├── evaluation_metadata.json
        └── ranked_candidates.csv
```

This provides reproducibility and auditability across source code, CI/CD, container runtime, data evaluation and MLOps tracking.

MLflow also attempts automatic Git discovery inside the evaluation container.

Because the lightweight runtime image does not include the Git executable, MLflow emits a Git-discovery warning.

This warning does not affect evaluation or tracking.

The project deliberately uses explicit GitLab CI metadata instead of adding Git solely for automatic discovery.

---

# 25. Current Maturity

The deterministic matching and MLOps baseline has reached the following maturity:

| State | Status |
|---|---|
| Designed | YES |
| Implemented | YES |
| Unit Tested | YES |
| CI Verified | YES |
| Backend Container Packaged | YES |
| Backend GitOps Published | YES |
| Backend Argo CD Synced | YES |
| Backend Kubernetes Runtime Verified | YES |
| Dedicated AI/MLOps Image Built | YES |
| Immutable AI/MLOps Image Published | YES |
| Kubernetes Evaluation Job Verified | YES |
| Generated/Synthetic Dataset Verified | YES |
| MLflow Experiment Tracked | YES |
| MLflow Parameters Verified | YES |
| MLflow Metrics Verified | YES |
| MLflow Artifacts Verified | YES |
| Git Commit Traceability Verified | YES |
| GitLab Pipeline Traceability Verified | YES |
| GitLab Job Traceability Verified | YES |
| Production Data Verified | NO |
| Supervised ML Trained | NO |
| GPU Training Verified | NO |
| ML Model Registered | NO |
| ML Model Production Serving | NO |

The distinction between these states is intentional.

The project now has an operational deterministic AI/MLOps baseline, but it does not falsely claim that a statistically validated learned model exists.

---

# 26. Current Limitations

The current baseline retains several known limitations.

## 26.1 Synthetic source data

Properties are generated for project validation rather than collected from a live real-estate source.

The evaluation therefore proves software behavior against the deployed project dataset, not real-world market performance.

## 26.2 Sparse search criteria

Many existing demand versions do not contain the complete target feature set.

The current scoring implementation therefore handles missing optional criteria without automatically penalizing candidates.

## 26.3 Geographic coverage

The generated property dataset does not cover every city represented by active search requests.

A zero-candidate result can therefore represent a source-data coverage limitation rather than a matching algorithm failure.

## 26.4 Limited business feedback

The platform currently contains insufficient presentation, visit and customer feedback for credible supervised-learning evaluation.

## 26.5 Hand-defined weights

The deterministic weights represent explicit business-oriented rules.

They have not been learned from historical outcomes.

## 26.6 No trained model

No supervised model is currently presented as production-ready.

This is deliberate.

Introducing a learned model before sufficient labels exist would produce technically executable training but scientifically weak business evidence.

## 26.7 MLflow Git auto-discovery warning

The dedicated AI/MLOps image does not contain the Git executable.

MLflow therefore cannot perform automatic repository discovery from inside the container.

This does not affect traceability because Git commit, repository, pipeline and job information are explicitly supplied by GitLab CI and persisted in MLflow.

---

# 27. Next Evolution

The deterministic matching + MLOps baseline is now complete.

The next AI milestones are:

```text
1. Preserve deterministic baseline evidence

2. Define the labelled-data strategy

3. Define business outcomes and target labels

4. Establish rules for presentation / visit / feedback collection

5. Build a training dataset when sufficient observations exist

6. Establish a first statistical / ML baseline

7. Compare learned performance against the deterministic baseline

8. Introduce PyTorch / GPU training where technically and scientifically justified

9. Track training experiments with MLflow

10. Introduce Model Registry only for actual trained model versions

11. Define model promotion criteria

12. Expose selected inference through FastAPI

13. Add inference observability

14. Deploy permanent serving components through GitOps / Argo CD

15. Introduce RAG separately after matching is stable
```

The immediate next methodological task is therefore not GPU training.

It is:

```text
define how future business interactions become trustworthy labelled data
```

The deterministic baseline remains the reference against which future learned approaches can be evaluated.

---

# 28. Evidence Summary

Evidence available for the deterministic matching and MLOps baseline now includes:

- feature-engineering source code;
- PostgreSQL matching extraction;
- reusable evaluation orchestration;
- 11 passing AI unit tests;
- GitLab deterministic AI validation;
- dedicated MLOps dependency layer;
- dedicated AI/MLOps Docker image;
- immutable AI/MLOps image publication;
- GitLab-triggered Kubernetes evaluation Job;
- successful Kubernetes Job completion;
- PostgreSQL runtime integration;
- MLflow runtime integration;
- MLflow experiment creation;
- MLflow run completion;
- MLflow parameter tracking;
- MLflow metric tracking;
- ranked-candidate artifact;
- evaluation metadata artifact;
- Git commit traceability;
- Git branch/ref traceability;
- GitLab repository traceability;
- GitLab pipeline traceability;
- GitLab job traceability;
- immutable image-to-commit correspondence;
- DV54 exact-postcode execution;
- DV54 feature-level explainability;
- DV12 postcode-fallback execution;
- explicit generated/synthetic-data classification;
- explicit distinction between deterministic matching and trained Machine Learning.

Key final runtime evidence:

```text
Git commit:
1e3475211bd86bf248e9f0d7b60bac89e6864cc6

Immutable image:
ai-mlops:1e347521

GitLab pipeline:
1248

GitLab job:
12368

Kubernetes Job:
real-estate-matching-evaluation

Kubernetes status:
Complete 1/1

MLflow experiment:
real-estate-deterministic-matching

MLflow run:
594285bb07c54a348ee73d80d440d57b

DemandeVersion:
54

Properties loaded:
800

Candidates:
721

Top score:
90.00

Mean score:
72.42

Median score:
70.97
```

Screenshots and terminal captures can be stored separately in the project evidence documentation for jury presentation.

---

# 29. Conclusion

The Real Estate Intelligence Platform now contains an operational and evidenced deterministic property-matching baseline with an associated MLOps evaluation path.

The matching capability is:

- explainable;
- reproducible;
- unit tested;
- CI validated;
- containerized;
- Kubernetes runtime verified;
- evaluated against generated project data;
- tracked through MLflow;
- associated with evaluation metrics;
- associated with reproducible artifacts;
- traceable to an immutable Git commit;
- traceable to its GitLab pipeline and job.

The implementation deliberately separates:

```text
permanent application serving
```

from:

```text
ephemeral AI/MLOps evaluation
```

and separates:

```text
deterministic business intelligence
```

from:

```text
statistically validated learned intelligence
```

The project therefore has a defensible baseline for future Machine Learning work without overstating the maturity or statistical validity of the current dataset.

The next AI phase should focus on transforming future business feedback into a governed and trustworthy labelled dataset before introducing supervised model training.