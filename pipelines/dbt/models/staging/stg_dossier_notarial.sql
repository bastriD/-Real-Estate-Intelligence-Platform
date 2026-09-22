select id_dossier_source, id_notaire_source, id_vente_source, acte_signe,
       honoraires_attendus, montant_collecte, montant_recu, derniere_reception,
       dw_updated_at
from {{ source('warehouse', 'fact_dossier_notarial') }}
