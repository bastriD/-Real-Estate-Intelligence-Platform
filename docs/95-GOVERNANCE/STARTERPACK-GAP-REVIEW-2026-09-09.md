# Professor's StarterPack update — gap review

Review date: 9 September 2026. Local application commit: `d43ea13`.

## What actually changed

The public repository was downloaded with its history. Its current HEAD is `902207e3c72fe5c806f639020e00558d0f592a26` (7 September 2026).

The substantive addition is commit [069bb50](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/commit/069bb507ebb08da062d410c4caf01b7a5b0bfd59): a remuneration specification, associated Gherkin scenarios, and updated indexes. The subsequent commit formats tables. The preceding functional addition was the Gherkin/course material on 25 August. The September change does not replace the overall assignment or introduce a new infrastructure requirement.

Pinned primary sources:

- [Remuneration rules and reference Python implementation](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/blob/902207e3c72fe5c806f639020e00558d0f592a26/documents%20utiles/REGLES-CALCUL-REMUNERATION.md).
- [Remuneration scenarios](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/blob/902207e3c72fe5c806f639020e00558d0f592a26/user-stories/10_calcul_remuneration_chasseur.feature).
- [Assignment](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/blob/902207e3c72fe5c806f639020e00558d0f592a26/Readme.md).
- [Evaluation grid](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/blob/902207e3c72fe5c806f639020e00558d0f592a26/documents%20utiles/GRILLE-EVALUATION.md).

## Verdict

The new remuneration requirements are only partially represented in our data model and are not implemented as a business workflow. Existing matching, MLOps, and infrastructure work does not cover this gap. Extend the current application and model rather than rebuild the platform.

The professor distinguishes business obligations from proposed parameter values. Example fees, weights, time windows, modulation percentages, and bounds must be documented as project decisions, not presented as immutable client requirements. Gherkin is a working specification; the repository explicitly says it is not itself an official deliverable.

## Implementation comparison

Paths below are relative to the project root.

| Area | What we have | Missing or insufficient | Priority |
|---|---|---|---|
| Calculation service | No remuneration-related Python service or tests found under `src/` and `tests/` | Deterministic eligibility, fee base, performance, rate selection, modulation, and rounding workflow | P1 |
| Fee parameters | `bareme_commission.montant_fixe` and stored `paiement.montant_honoraires` | A separately dated company-fee parameter model; the hunter commission rate is not the company fee percentage | P1 |
| Commission grids | Price bounds, validity dates, hunter FK, and ratio constraints in migration 001 | `id_chasseur NOT NULL` prevents the proposed default grid; no applicable-grid selection service or overlap protection. Decide default/override and interval semantics | P1 |
| Eligibility | Mandate type, dates, hunter and client exist | Transaction origin, explicit beneficiary, denied-right reason, and one-beneficiary-per-sale enforcement are not represented as a complete workflow | P1 |
| Mandate validity | Date fields and date-order validation | Six calendar months and traceable renewal are not enforced by current schema/API validation. Migration 001 explicitly defers the rule | P1 |
| Performance inputs | Hunter entry date, mandates, visits, and some payment dates/amounts exist | Reliable completed-sale identity and attribution, relevant-visit counting, historical aggregates, and the five-factor remuneration score. `mart_mandat_performance.sql` only aggregates mandate counts and durations | P1 |
| Historical calculation | Payment stores purchase price, fees, hunter amount, and a grid FK | Frozen score, component notes/inputs, base rate, modulations, final rate, calculation date, beneficiary, and parameter provenance; no application mechanism enforcing immutability | P1 |
| Payment lifecycle | Status vocabulary and receipt/payment dates in the database | No payment API/service, invoice linkage/verification workflow, notification implementation, or post-payment performance update found | P1 |
| Restricted access | Identity roles and admin protection for clients | Remuneration access for the concerned hunter and authorized manager, including cross-owner tests. Manager authority needs an explicit model or documented mapping | P1 |
| Acceptance tests | Backend and AI suites exist | No remuneration suite. Add rule cases, rounding boundaries, historical-rate changes, duplicate calculation/payment, expiry, and unauthorized access | P1 |
| Analytics/governance | Warehouse payment fact, loader, and metadata descriptions | Propagate the final model changes into warehouse/dbt and governance; distinguish historical payment facts from recomputed current performance | P2 |

Relevant local evidence:

- `database/migrations/001_initial_schema.sql`: chasseur at line 60, mandat at 164, commission grid at 755, payment at 813.
- `src/api/schemas/mandat.py` and `src/api/services/mandat.py`: date validation and current mandate workflow.
- `src/api/api/v1/router.py`: no remuneration, payment, or commission-grid router.
- `database/olap/load_warehouse.py`: payment loading.
- `pipelines/dbt/models/marts/mart_mandat_performance.sql`: current analytical scope.
- `database/migrations/006_auth_identity.sql`: ADMIN, CLIENT, CHASSEUR, SERVICE identity roles.

## Migration issue to resolve before enabling calculations

`database/migrations/002_migrate_legacy_data.sql`, lines 627–670, assumes legacy commission values are percentages, divides them by 100, and creates active, unbounded hunter grids. `database/tests/002_legacy_migration.sql` verifies this numerical conversion.

The new teaching material explicitly calls out ambiguity in the legacy rate's meaning. Numerical conversion preserves a number; it does not validate its business interpretation. Preserve the source data and document this anomaly. Before using these rows for remuneration, distinguish migrated historical values from approved operational grids. Use a new migration and an explicit decision rather than rewriting applied migration history or silently replacing old rates with the professor's examples.

## Specification points requiring an explicit interpretation

These are source ambiguities or implementation decisions, not reasons to postpone the whole project:

1. **Expired example mandate.** The positive worked example and end-to-end scenario use signature 14 November 2025 and deed 30 July 2026. Initial six-month validity ends 14 May 2026. A renewal must be explicit to make the positive payment consistent with the eligibility rule. Preserve the original signature date for the intended elapsed-time calculation if that is the selected interpretation.
2. **Expiry and lower performance.** The scenario requires expiry without sale to lower performance. The proposed positive mandate-count component and unchanged sale count do not guarantee that decline. Define the event/recalculation semantics with the professor; do not silently invent a sixth criterion.
3. **Money interval boundaries.** Examples such as 199999 followed by 200000 leave fractional-euro gaps if copied as inclusive bounds. Use a documented interval convention and test values such as 199999.99, exact thresholds, and overlapping validity periods.
4. **Business decisions.** Record the source document's D1–D9 choices, including compensation outside the agency, aggregation window, default-grid precedence, parameter ownership, and approval responsibilities. Keep example numeric values configurable.

Under the professor's example parameters and an explicitly valid/renewed mandate, the worked case expects company fees of EUR 13,500, a score of 73.5, a final rate of 46.16%, and hunter remuneration of EUR 6,231.60. This is a future acceptance target, not a test passed by our project.

## Delivery sequence

1. Add a concise remuneration decision record and requirement-to-test mapping; identify unresolved source ambiguities separately.
2. Extend the MCD/MLD and add the next migration for transaction attribution, parameter versions, default/individual grids, and immutable calculation details. Preserve existing data.
3. Implement a pure Decimal-based calculation module and automated rule tests. The professor provides a reference implementation, but its presence in teaching material is not evidence that our project implements or passes it.
4. Integrate database lookups, aggregation, authorized API operations, and atomic/idempotent persistence; complete mandate-renewal semantics.
5. Add payment/invoice transitions and performance refresh; update analytics and governance where affected.
6. Execute unit and database-backed acceptance tests and attach results to BC02/BC05 design evidence and BC03 execution evidence.

## Scope correction to the previous alignment review

The official assignment prioritizes BC05 with BC01/BC02/BC03. Model training is not required, and the existing website and business client are outside implementation scope; backend/API work, design mockups, and accessibility recommendations remain relevant. More MLOps or a new frontend should therefore not displace remuneration and the required concise deliverables. See the pinned assignment and evaluation grid above.

The previous review remains useful for security and evidence gaps, but its baseline was our own documentation. This review adds the professor's actual September delta. It is a source-code/schema comparison, not a live database or CI execution audit. No application code, database, or deployment was changed.
