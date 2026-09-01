# Labelled Dataset Strategy — Property Matching

**Version:** 1.0  
**Status:** Designed — Training Data Not Yet Sufficient  
**Project:** Enterprise Real Estate Intelligence Platform  
**Component:** AI / Matching / Supervised Learning Preparation  
**Last Updated:** 2026-09-01

---

# 1. Purpose

This document defines the labelled-data strategy for the future supervised property-matching capability of the Real Estate Intelligence Platform.

The platform already contains an implemented deterministic matching baseline.

The next Machine Learning requirement is not immediately to train a model, but to establish how real business interactions can become trustworthy labelled observations.

The objective is to define:

- the observation grain;
- feature sources;
- business outcome sources;
- positive and negative signals;
- leakage-prevention rules;
- dataset quality requirements;
- dataset lineage requirements;
- conditions that must be satisfied before supervised training is considered scientifically credible.

The strategy deliberately separates:

```text
Matching inputs
```

from:

```text
Matching outcomes
```

so that a future model learns from business results rather than from the output of the existing deterministic algorithm.

---

# 2. Current Matching Context

The current deterministic matching capability evaluates:

```text
DemandeVersion
       +
Bien
       ↓
Candidate Retrieval
       ↓
Feature Engineering
       ↓
Deterministic Score
       ↓
Ranked Candidates
```

This baseline is:

- implemented;
- unit tested;
- CI validated;
- Kubernetes runtime verified;
- tracked with MLflow;
- reproducible through GitLab CI traceability.

It provides the reference against which future learned models can be evaluated.

The deterministic baseline is not a trained Machine Learning model.

---

# 3. Supervised Learning Problem

A future supervised model must answer a question similar to:

> Given the customer's search requirements and the characteristics of a property, how likely is this property to produce a positive business outcome?

This requires two fundamentally different categories of information.

## 3.1 Predictive inputs

Information known when matching is performed.

Examples:

```text
requested city
requested postcode
requested property type
budget
minimum surface
minimum rooms
minimum bedrooms
maximum DPE
property price
property location
property type
property surface
property rooms
property bedrooms
property DPE
```

## 3.2 Outcomes

Information observed only after a property has been evaluated or presented.

Examples:

```text
presentation status
visit status
visit rating
customer decision
hunter decision
```

The model must learn relationships between the first category and the second.

Outcome information must not be included among predictive features.

---

# 4. Observation Grain

The canonical supervised-learning observation is:

```text
one row
=
one DemandeVersion
+
one Bien
```

The business key is therefore:

```text
(id_demande_version, id_bien)
```

This grain corresponds directly to the existing `presentation` uniqueness constraint:

```text
UNIQUE (id_demande_version, id_bien)
```

A conceptual training observation is:

```text
DemandeVersion 54
       +
Bien 13
       ↓
matching features
       +
business outcome
       ↓
one labelled observation
```

This grain is important because the same property may produce different outcomes for different customer requirements.

Likewise, different versions of the same demand represent different customer requirements and must remain separate observations.

---

# 5. Versioned Demand Integrity

Training observations must reference:

```text
id_demande_version
```

rather than only:

```text
id_demande
```

Search criteria are versioned and historical versions are preserved.

Therefore:

```text
Demande
   │
   ├── Version 1
   ├── Version 2
   └── Version N
```

must not be collapsed into a single mutable search state.

A historical property interaction must be evaluated using the exact demand version that existed when that interaction occurred.

This prevents future modifications to customer requirements from altering the meaning of historical training observations.

---

# 6. Feature Sources

The primary predictive data sources are:

```text
real_estate.demande_version
real_estate.bien
```

## 6.1 DemandeVersion features

Potential predictive fields include:

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
```

Additional structured criteria may be introduced later if they become sufficiently reliable.

## 6.2 Bien features

Potential property features include:

```text
ville
code_postal
type_bien
prix
surface
nb_pieces
nb_chambres
dpe
latitude
longitude
source
```

Feature selection must eventually be validated statistically and from a business perspective.

The existence of a database field alone does not automatically justify using it as a model feature.

---

# 7. Reusable Matching Features

The deterministic baseline already calculates explainable compatibility features:

```text
feature_location
feature_budget
feature_property_type
feature_surface
feature_rooms
feature_bedrooms
feature_dpe
```

These transformations may be reused as candidate features for future statistical models because they are derived from information available at matching time.

However, their usefulness must be evaluated rather than assumed.

A future training dataset may therefore contain both:

```text
raw demand/property attributes
```

and:

```text
derived compatibility features
```

provided they respect temporal and leakage constraints.

---

# 8. Outcome Sources

The current transactional schema provides three principal sources of business feedback:

```text
presentation
visite
commentaire
```

These represent different stages and strengths of business evidence.

---

# 9. Presentation Outcome

`real_estate.presentation` links:

```text
DemandeVersion
       +
Bien
```

and therefore naturally corresponds to the training observation grain.

Current allowed statuses are:

```text
IDENTIFIE
QUALIFIE
PRESENTE
REJETE
VISITE
RETENU
```

Conceptually, these represent progression through the matching lifecycle.

A possible interpretation is:

```text
IDENTIFIE
    ↓
QUALIFIE
    ↓
PRESENTE
    ↓
VISITE
    ↓
RETENU
```

with:

```text
REJETE
```

representing a negative branch.

These statuses are useful outcome signals.

They must not be used as predictive inputs when predicting the outcome of the same interaction.

---

# 10. Visit Outcome

`real_estate.visite` references:

```text
id_presentation
```

and therefore extends the same demand/property interaction.

Current visit statuses are:

```text
PLANIFIEE
REALISEE
ANNULEE
REPORTEE
```

A visit also supports:

```text
note = 0..5
```

A completed visit provides stronger downstream evidence than simple property identification or presentation.

A rating provides an additional graded satisfaction signal.

However, the meaning of cancelled or postponed visits must not automatically be interpreted as negative customer feedback.

For example:

```text
ANNULEE
```

could result from:

- customer rejection;
- seller unavailability;
- scheduling problems;
- administrative issues;
- external circumstances.

Therefore, ambiguous operational events must not automatically become negative labels.

---

# 11. Comment Outcome

`real_estate.commentaire` associates feedback directly with:

```text
id_demande_version
+
id_bien
```

and identifies the author as either:

```text
client
```

or:

```text
chasseur
```

Current decision values are:

```text
RETENIR
ECARTER
VISITER
REQUALIFIER
INFORMATION
```

These provide potentially valuable explicit business signals.

Strong candidate positive signals include:

```text
RETENIR
VISITER
```

A strong candidate negative signal is:

```text
ECARTER
```

The following are more ambiguous:

```text
REQUALIFIER
INFORMATION
```

They should not automatically be mapped to positive or negative classes without an explicit business rule.

The distinction between customer and hunter feedback should also be preserved.

A future model may need to distinguish:

```text
customer preference
```

from:

```text
professional hunter qualification
```

rather than treating both as identical evidence.

---

# 12. Outcome Strength

Not all events provide equally strong evidence.

The platform therefore treats business feedback as a hierarchy of signals rather than assuming that every event has equivalent meaning.

Conceptually:

```text
property identified
        ↓
property qualified
        ↓
property presented
        ↓
visit requested/planned
        ↓
visit completed
        ↓
positive visit rating
        ↓
property retained
```

Later-stage outcomes generally contain stronger information about actual customer compatibility.

This does not yet define the final ML target.

It defines the evidence from which future targets may be constructed.

---

# 13. Candidate Label Strategies

Several supervised-learning formulations are possible.

They should be evaluated once sufficient data exists.

## 13.1 Binary relevance

Example conceptual target:

```text
positive
negative
```

Possible positive evidence could eventually include:

```text
RETENU
VISITER
successful REALISEE visit with positive rating
```

Possible negative evidence could include:

```text
REJETE
ECARTER
```

This formulation is simple and suitable for an initial classification baseline.

## 13.2 Multi-class lifecycle prediction

A model could predict progression states such as:

```text
rejected
presented
visited
retained
```

This requires substantially more observations per class.

## 13.3 Ordinal relevance

Business outcomes could potentially be represented as increasing relevance levels.

For example:

```text
low relevance
medium relevance
high relevance
```

This approach requires explicit business validation of the ordering.

## 13.4 Ranking objective

Ultimately, property matching is naturally a ranking problem:

```text
for one DemandeVersion
rank candidate properties
```

A future learning-to-rank approach may therefore be appropriate.

However, ranking models require sufficient interaction data across many demands and candidate properties.

The project should begin with simpler statistical baselines before introducing unnecessary modelling complexity.

---

# 14. Final Label Not Yet Frozen

This document deliberately does not define a permanent mapping such as:

```text
RETENU = 1
REJETE = 0
```

as the final project target.

The available schema provides the necessary signals, but the exact target must be validated using:

- business meaning;
- event frequency;
- class distribution;
- label reliability;
- available sample size;
- modelling objective.

The target definition should therefore be versioned along with the future dataset-generation code.

---

# 15. Existing Runtime Observation

The current database contains one verified interaction chain:

```text
id_demande_version = 54
id_bien            = 13
id_presentation    = 19
```

Presentation:

```text
score_matching = 91.25
statut         = PRESENTE
date_selection = 2026-08-30
```

Visit:

```text
id_visite = 4
statut     = REALISEE
note       = 4
date       = 2026-09-02
```

Conceptually:

```text
DemandeVersion 54
       +
Bien 13
       ↓
Presentation 19
PRESENTE
       ↓
Visite 4
REALISEE
       ↓
Note 4/5
```

This demonstrates that the transactional schema can capture downstream matching feedback.

It does not provide enough observations to train a supervised model.

---

# 16. Current Label Distribution

The runtime database was inspected directly.

Current observed feedback distribution:

| Source | Value | Count |
|---|---|---:|
| presentation | PRESENTE | 1 |
| visite | REALISEE | 1 |
| visite_note | 4 | 1 |
| commentaire decision | none | 0 |

Therefore the available real interaction dataset currently contains:

```text
1 observed positive/progressing interaction
0 explicit negative interactions
```

This is insufficient for supervised-learning training and evaluation.

---

# 17. Why Training Is Currently Blocked

A supervised model requires variation in both inputs and outcomes.

The current dataset has:

```text
one interaction chain
```

and no meaningful negative class.

Training on this data would introduce several methodological problems:

- no statistically useful sample size;
- no meaningful class distribution;
- no reliable validation split;
- no independent test set;
- severe overfitting;
- meaningless accuracy/performance metrics;
- no evidence of generalization.

A technically successful call to:

```text
model.fit()
```

would therefore not constitute meaningful Machine Learning evidence.

The current state must be described as:

```text
schema ready
+
label strategy designed
+
business feedback collection possible
+
training data insufficient
```

rather than:

```text
ML training ready
```

---

# 18. Synthetic Labels

Synthetic labels may be used later for:

```text
pipeline testing
training-job validation
GPU validation
MLflow training integration
model packaging validation
CI/CD validation
```

but synthetic labels must always be explicitly identified as:

```text
synthetic
```

They must not be presented as evidence of real business predictive performance.

Metrics obtained from synthetic labels prove technical execution only.

They do not prove real-world model quality.

---

# 19. Baseline Score Leakage

`presentation.score_matching` contains a matching score generated by an existing matching process.

For the verified interaction:

```text
score_matching = 91.25
```

This field must not automatically become a predictive feature for a model intended to learn independently from business outcomes.

Using it as an input could create:

```text
baseline-output leakage
```

where the learned model primarily reproduces the existing matching algorithm.

Therefore:

```text
score_matching
```

should normally be preserved as:

```text
comparison metadata
```

rather than:

```text
training feature
```

when evaluating a new model against the deterministic baseline.

---

# 20. Target Leakage Prevention

Future dataset extraction must prevent information created after the matching decision from entering predictive features.

Examples of prohibited predictors for the same observation include:

```text
presentation.statut
visite.statut
visite.note
commentaire.decision
future comments
future customer actions
```

These fields may define or contribute to the label.

They must not simultaneously be used as predictive inputs.

The general temporal rule is:

> A model may only use information that would have been available at the time the matching decision was made.

---

# 21. Temporal Integrity

Dataset generation must preserve event chronology.

Conceptually:

```text
T0 — demand criteria exist
T0 — property characteristics known
T1 — matching performed
T2 — property presented
T3 — visit planned
T4 — visit completed
T5 — feedback received
```

Features should represent information available at or before:

```text
T1
```

Labels may be derived from:

```text
T2..T5
```

This prevents future information from leaking backwards into the model.

---

# 22. Duplicate Prevention

The canonical training grain is:

```text
(id_demande_version, id_bien)
```

A dataset-generation process must therefore avoid generating multiple independent training rows simply because multiple downstream events exist.

For example:

```text
one presentation
+
two comments
+
one visit
```

must not accidentally produce:

```text
three or four duplicated training observations
```

Outcome events should instead be aggregated to the canonical demand/property observation.

---

# 23. Multiple Visits

The schema permits multiple visits to reference the same presentation.

Future dataset extraction must therefore define deterministic aggregation rules.

Potential strategies include:

```text
latest completed visit
maximum rating
latest rating
aggregated visit history
```

The selected rule must be explicit and versioned.

No rule should be silently assumed.

---

# 24. Multiple Comments

Multiple comments may exist for the same:

```text
DemandeVersion + Bien
```

and may originate from different actors.

Future extraction must preserve:

```text
author type
timestamp
decision
priority
```

before deriving any aggregate label.

Conflicting decisions such as:

```text
client = ECARTER
hunter = RETENIR
```

must not be silently collapsed without a defined business rule.

---

# 25. Missing Outcomes Are Not Negative Labels

A property with no visit, comment or final decision must not automatically be labelled:

```text
negative
```

Absence of feedback may mean:

- the interaction has not yet progressed;
- feedback has not yet been entered;
- the property has not yet been reviewed;
- the business process remains open.

Therefore:

```text
no outcome
≠
negative outcome
```

Such observations may need to remain:

```text
unlabelled
```

until an explicit outcome or defined observation window exists.

---

# 26. Observation Window

A future production dataset will require an observation-window rule.

For example:

```text
matching time
      ↓
wait defined business period
      ↓
derive final outcome
```

Without such a rule, recently presented properties could incorrectly be treated as unsuccessful simply because their business lifecycle has not finished.

The exact duration must be determined from real business process data rather than arbitrarily fixed at this stage.

---

# 27. Dataset Quality Controls

Before supervised training, the generated dataset should validate at least:

```text
unique observation grain
valid foreign keys
valid demand versions
valid properties
feature completeness
label completeness
label distribution
class balance
temporal consistency
duplicate absence
outcome consistency
missing-value distribution
feature ranges
```

Additional checks should detect:

```text
future-data leakage
baseline-score leakage
impossible lifecycle sequences
conflicting labels
```

Dataset quality results should be retained as evidence.

---

# 28. Minimum Training Readiness

Training should not begin merely because more than one row exists.

Before claiming meaningful supervised-learning evaluation, the dataset should support:

- multiple independent demand versions;
- multiple properties;
- positive outcomes;
- negative outcomes;
- sufficient observations for train/validation/test separation;
- meaningful class distribution;
- representative feature variation;
- trustworthy temporal ordering.

The exact numerical minimum should be determined from the future dataset and modelling problem rather than invented prematurely.

---

# 29. Dataset Lineage

Future training datasets must be traceable.

The desired lineage is:

```text
PostgreSQL operational data
        ↓
versioned extraction code
        ↓
label derivation rules
        ↓
dataset quality validation
        ↓
dataset snapshot / identifier
        ↓
training run
        ↓
MLflow
```

The training run should eventually record information such as:

```text
dataset identifier
dataset extraction version
label strategy version
Git commit
GitLab pipeline
training parameters
model parameters
evaluation metrics
artifacts
```

This extends the GitLab-to-MLflow traceability already implemented for the deterministic baseline.

---

# 30. OpenMetadata Integration

The project's OpenMetadata platform can provide governance and lineage around the source data and future analytical/training datasets.

Relevant future responsibilities include:

- documenting source tables;
- ownership;
- glossary terms;
- data-layer classification;
- data-quality visibility;
- lineage;
- dataset discoverability.

MLflow and OpenMetadata serve different but complementary purposes:

```text
OpenMetadata
    ↓
data governance / lineage / quality

MLflow
    ↓
experiment / model / evaluation traceability
```

Neither should unnecessarily duplicate the responsibility of the other.

---

# 31. Dataset Extraction Component

The future implementation should introduce a dedicated extraction component under the AI matching domain.

Conceptually:

```text
src/ai/matching/
├── features.py
├── repository.py
├── evaluate.py
├── mlflow_tracking.py
├── run_evaluation.py
└── dataset.py
```

`dataset.py` should eventually be responsible for producing the canonical labelled observation structure.

It should not perform model training.

This maintains separation between:

```text
data preparation
```

and:

```text
model training
```

---

# 32. Proposed Dataset Structure

A future extracted dataset may conceptually contain fields such as:

```text
# Observation identity
id_demande_version
id_bien

# Demand attributes
demande_ville
demande_code_postal
demande_type_bien
budget_min
budget_max
surface_min
nb_pieces_min
nb_chambres_min
dpe_max

# Property attributes
bien_ville
bien_code_postal
bien_type_bien
prix
surface
nb_pieces
nb_chambres
dpe

# Derived matching features
feature_location
feature_budget
feature_property_type
feature_surface
feature_rooms
feature_bedrooms
feature_dpe

# Baseline comparison metadata
baseline_score

# Outcome evidence
presentation_statut
visite_statut
visite_note
commentaire_decision

# Derived supervised target
label

# Lineage
observation_timestamp
dataset_version
```

The final physical schema should be implemented only after the label contract is frozen.

---

# 33. Deterministic Baseline as Comparator

The deterministic matcher remains valuable after supervised ML is introduced.

Future evaluation should compare:

```text
Deterministic baseline
        VS
Statistical / ML baseline
```

using the same evaluation population whenever possible.

This enables a meaningful question:

> Does the learned model provide measurable value over the explainable deterministic approach?

A more complex model should not be promoted merely because it uses Machine Learning.

It should demonstrate measurable improvement under agreed business and technical criteria.

---

# 34. First Learned Model Strategy

When sufficient labelled observations exist, the first learned model should remain relatively simple.

A reasonable progression is:

```text
labelled dataset
      ↓
simple statistical analysis
      ↓
simple scikit-learn baseline
      ↓
MLflow evaluation
      ↓
compare with deterministic baseline
      ↓
only then consider more complex models
```

PyTorch/GPU training should be introduced when justified by:

- dataset size;
- modelling complexity;
- experimental evidence;
- project learning objectives.

The availability of a GPU alone is not sufficient justification for deep learning.

---

# 35. Current Maturity

| Capability | Status |
|---|---|
| Deterministic matching | IMPLEMENTED |
| Deterministic unit tests | VERIFIED |
| Runtime evaluation | VERIFIED |
| MLflow deterministic tracking | VERIFIED |
| GitLab/MLflow traceability | VERIFIED |
| Feedback schema | AVAILABLE |
| Presentation outcomes | AVAILABLE |
| Visit outcomes | AVAILABLE |
| Comment decisions | AVAILABLE |
| Label strategy | DESIGNED |
| Canonical observation grain | DEFINED |
| Leakage strategy | DEFINED |
| Dataset extraction code | NOT YET |
| Dataset DQ implementation | NOT YET |
| Sufficient real labels | NO |
| Supervised training ready | NO |
| Trained real-estate model | NO |

---

# 36. Immediate Next Implementation

The next implementation milestone is:

```text
src/ai/matching/dataset.py
```

Its first responsibility should be to extract and represent the canonical:

```text
DemandeVersion
+
Bien
+
outcome evidence
```

without training a model.

The initial implementation should prove that:

- demand/property observations join correctly;
- downstream outcome evidence can be aggregated;
- unlabeled observations remain distinguishable;
- no target leakage enters predictive features;
- the current single observed interaction is represented correctly.

Unit tests should validate these rules before any training pipeline is introduced.

---

# 37. Evidence Value

This strategy provides evidence that the AI implementation is not limited to invoking a Machine Learning library.

It demonstrates:

- business understanding;
- feature/target separation;
- historical version integrity;
- supervised-learning methodology;
- label engineering;
- leakage prevention;
- temporal reasoning;
- data-quality planning;
- experiment reproducibility;
- governance integration;
- justified control of model complexity.

This strengthens the project's AI/Big Data evidence while preserving methodological credibility.

---

# 38. Conclusion

The Real Estate Intelligence Platform contains the structural components required to collect meaningful matching feedback.

The canonical future supervised-learning observation is:

```text
one DemandeVersion
+
one Bien
+
predictive features
+
subsequent business outcome
```

The current database demonstrates that this lifecycle works through the verified chain:

```text
DemandeVersion 54
       +
Bien 13
       ↓
Presentation 19
PRESENTE
       ↓
Visite 4
REALISEE
       ↓
Note 4/5
```

However, one interaction and zero explicit negative examples are insufficient for credible supervised learning.

The correct current project state is therefore:

```text
Deterministic baseline
        VERIFIED
            ↓
MLOps tracking
        VERIFIED
            ↓
Label strategy
        DESIGNED
            ↓
Dataset extraction
        NEXT
            ↓
Feedback accumulation
            ↓
Statistically defensible ML training
```

The project will introduce learned matching only when the available data can support meaningful evaluation against the deterministic baseline.