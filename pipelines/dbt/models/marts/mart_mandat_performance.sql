select
    fm.statut,
    fm.type_mandat,
    fm.est_exclusif,

    count(*) as nb_mandats,

    count(distinct fm.client_key) as nb_clients,

    count(distinct fm.chasseur_key) as nb_chasseurs,

    round(avg(fm.duree_jours), 2) as duree_moyenne_jours,

    min(fm.duree_jours) as duree_min_jours,

    max(fm.duree_jours) as duree_max_jours

from {{ source('warehouse', 'fact_mandat') }} as fm

group by
    fm.statut,
    fm.type_mandat,
    fm.est_exclusif