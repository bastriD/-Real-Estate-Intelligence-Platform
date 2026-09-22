"""One row per dossier; aggregate money before joining to avoid multiplication."""


def load_notarial_projection(cur):
    cur.execute("""
        INSERT INTO warehouse.fact_dossier_notarial (
            id_dossier_source, id_notaire_source, id_vente_source, acte_signe,
            honoraires_attendus, montant_collecte, montant_recu, derniere_reception
        )
        SELECT d.id_dossier_notarial, d.id_notaire, d.id_vente, d.id_vente IS NOT NULL,
               p.montant_honoraires, COALESCE(m.collecte, 0), COALESCE(m.recu, 0), m.derniere_reception
        FROM real_estate.dossier_notarial d
        LEFT JOIN real_estate.paiement p ON p.id_vente = d.id_vente
        LEFT JOIN (
            SELECT id_dossier_notarial,
                SUM(montant) FILTER (WHERE nature = 'COLLECTE_NOTAIRE') AS collecte,
                SUM(montant) FILTER (WHERE nature = 'RECEPTION_ENTREPRISE') AS recu,
                MAX(date_operation) FILTER (WHERE nature = 'RECEPTION_ENTREPRISE') AS derniere_reception
            FROM real_estate.mouvement_notarial GROUP BY id_dossier_notarial
        ) m USING (id_dossier_notarial)
        ON CONFLICT (id_dossier_source) DO UPDATE SET
            id_notaire_source = EXCLUDED.id_notaire_source,
            id_vente_source = EXCLUDED.id_vente_source,
            acte_signe = EXCLUDED.acte_signe,
            honoraires_attendus = EXCLUDED.honoraires_attendus,
            montant_collecte = EXCLUDED.montant_collecte,
            montant_recu = EXCLUDED.montant_recu,
            derniere_reception = EXCLUDED.derniere_reception,
            dw_updated_at = CURRENT_TIMESTAMP
    """)
