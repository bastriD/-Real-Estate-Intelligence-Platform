-- Read-only schema and live balance checks. Does not create financial records.
\set ON_ERROR_STOP on
BEGIN;
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM migration_control.schema_version WHERE version = '019') THEN
        RAISE EXCEPTION 'Migration 019 required';
    END IF;
    IF (SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal AND tgname IN
        ('guard_dossier_notarial', 'guard_mouvement_notarial', 'guard_notarial_payment', 'guard_notarial_sale')) <> 4 THEN
        RAISE EXCEPTION 'Notarial financial guards are missing';
    END IF;
    IF EXISTS (
        SELECT d.id_dossier_notarial FROM real_estate.dossier_notarial d
        LEFT JOIN real_estate.paiement p ON p.id_vente = d.id_vente
        LEFT JOIN real_estate.mouvement_notarial m USING (id_dossier_notarial)
        GROUP BY d.id_dossier_notarial, p.montant_honoraires
        HAVING coalesce(sum(m.montant) FILTER (WHERE m.nature = 'RECEPTION_ENTREPRISE'), 0)
             > coalesce(sum(m.montant) FILTER (WHERE m.nature = 'COLLECTE_NOTAIRE'), 0)
            OR sum(m.montant) FILTER (WHERE m.nature = 'COLLECTE_NOTAIRE') > p.montant_honoraires
    ) THEN RAISE EXCEPTION 'Notarial financial balances are inconsistent'; END IF;
    IF EXISTS (
        SELECT p.id_paiement FROM real_estate.paiement p
        JOIN real_estate.dossier_notarial d USING (id_vente)
        LEFT JOIN real_estate.mouvement_notarial m ON m.id_dossier_notarial = d.id_dossier_notarial
             AND m.nature = 'RECEPTION_ENTREPRISE'
        WHERE p.statut IN ('RECU', 'VERIFIE', 'PROGRAMME', 'PAYE')
        GROUP BY p.id_paiement
        HAVING sum(m.montant) IS DISTINCT FROM p.montant_honoraires
            OR max(m.date_operation) IS DISTINCT FROM p.date_reception_honoraires
    ) THEN RAISE EXCEPTION 'Company receipt is not justified by the ledger'; END IF;
END $$;
ROLLBACK;
