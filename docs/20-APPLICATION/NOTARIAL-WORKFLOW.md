# Notary: authentic deed and agency fee collection

The implemented flow is accepted offer -> notarial appointment -> signed deed ->
agency fees collected by the notary -> actual company receipt -> existing client
invoice -> existing hunter invoice, verification and remuneration controls.
The application records documentary evidence of the notary's actions; it does
not itself produce or electronically authenticate an authentic deed.

## Operational API

All routes below require the existing ADMIN role. A notary is a business entity,
not a new login role. Neither clients nor hunters can read notarial contacts,
deed references or transfer details through these routes.

1. `POST /api/v1/notaires` with `nom`, `office`, `email`.
2. `POST /api/v1/notaires/dossiers` with `id_notaire`, `id_offre` and timezone-aware
   `date_rendez_vous`. The offer must be accepted and attached to a mandate.
3. `POST /api/v1/notaires/dossiers/{id}/signature` with `date_acte_authentique`,
   `montant_achat`, `reference_acte`, `reference_document`. The final sale price
   is explicitly recorded; it is not silently copied from the accepted offer.
   This creates the existing `vente` and links the dossier in one transaction.
   Existing mandate-period and hunter-beneficiary calculation still applies.
4. Use `POST /api/v1/remunerations/ventes/{id_vente}/calcul` to establish
   its `paiement` snapshot and expected agency fees. Calculation is distinct from
   authorization or payment to the hunter.
5. `POST /api/v1/notaires/dossiers/{id}/mouvements` with `nature`, `montant`,
   `date_operation`, `reference`. Nature is `COLLECTE_NOTAIRE` for collection or
   `RECEPTION_ENTREPRISE` for actual company receipt, not a promised transfer.
6. Continue the existing client-invoice and hunter-invoice workflows.

Read the notary list at `GET /api/v1/notaires`, the dossier at
`GET /api/v1/notaires/dossiers/{id}`, and movements at its `/mouvements` route.
Document references identify evidence held in the existing document/archive
process; this API does not upload or inspect deed documents.

## Financial guarantees and boundaries

Amounts use the existing `paiement.montant_honoraires` accounting basis (the client
invoice currently records HT). This does not add VAT, transfer banking, purchase
price settlement to the seller, or the notary's own remuneration.

Collections and receipts can be partial. Cumulative company receipts cannot
exceed collections, and collections cannot exceed expected agency fees.
Collection and partial receipt leave payment at ATTENDU. The final receipt sets
RECU and the actual receipt completion date atomically. Direct payment transition
cannot bypass reconciliation for a notarial dossier. Company and hunter invoice
rules, including conformity before hunter payment, remain active.

Movements are chronological and append-only. Repeating a reference with identical
content returns the original movement; conflicting content is rejected. Payment
row locks serialize concurrent financial changes. Signed dossiers and financial
bases after collection are protected by database triggers. New dossiers must be
created before the completed sale; legacy sales are not retroactively assigned
invented notaries or evidence and keep their previous receipt workflow.

There is no API for refunds, financial corrections, dossier cancellation or
rescheduling yet. Do not simulate a correction by deleting a movement; a future
correction workflow must preserve the ledger and reconcile downstream invoices.

## Deployment order

1. Apply manual `database:migrate-019` after migration 018. Existing rows are
   preserved; no synthetic sales, notaries or receipts are seeded.
2. Deploy the backend and data-pipeline images. Migration 019 must precede them:
   payment guards and warehouse loading now reference its new tables.
3. Run the warehouse loader, then dbt models/tests. The warehouse fact has one
   row per dossier; money is aggregated before joining to prevent double counts.
4. Refresh OpenMetadata discovery/dbt ingestion, apply governance, then publish
   the existing Grafana dashboard. The three new panels show agency collection,
   company receipts and funds still held by notaries, from the warehouse snapshot.
5. Run manual `database:test-notarial` for installed guards and live balance
   reconciliation. Exercise accepted offer -> signature -> collection -> partial
   receipt -> full receipt -> invoicing in a test environment on the trusted runner.

Offline automated tests cover service rules, API permissions, payment bypass
prevention, schemas and CI/reporting contracts. They do not establish PostgreSQL
trigger/concurrency behavior or a successful live deployment. Commit, push and
trusted-runner/runtime verification remain with the user.
