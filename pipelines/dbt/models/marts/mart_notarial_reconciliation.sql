-- Agency fees only. Not purchase prices and not remuneration of the notary.
select count(*) as dossiers_total,
       count(*) filter (where acte_signe) as actes_signes,
       count(*) filter (where acte_signe and honoraires_attendus is null) as paiements_a_calculer,
       coalesce(sum(montant_collecte), 0) as honoraires_collectes,
       coalesce(sum(montant_recu), 0) as honoraires_recus,
       coalesce(sum(montant_collecte - montant_recu), 0) as solde_chez_notaire,
       max(dw_updated_at) as derniere_actualisation
from {{ ref('stg_dossier_notarial') }}
