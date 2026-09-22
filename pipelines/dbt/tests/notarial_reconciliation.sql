select id_dossier_source
from {{ ref('stg_dossier_notarial') }}
where montant_recu < 0 or montant_collecte < montant_recu
   or montant_collecte > honoraires_attendus
   or (not acte_signe and (montant_collecte <> 0 or montant_recu <> 0))
