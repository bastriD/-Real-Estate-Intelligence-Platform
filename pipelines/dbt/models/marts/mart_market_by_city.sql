select
    dl.pays,
    dl.ville,
    dl.code_postal,

    count(*) as nb_annonces,

    round(avg(fa.prix), 2) as prix_moyen,

    round(min(fa.prix), 2) as prix_min,

    round(max(fa.prix), 2) as prix_max,

    round(avg(fa.surface), 2) as surface_moyenne,

    round(avg(fa.prix_m2), 2) as prix_m2_moyen,

    min(fa.date_publication_exacte) as premiere_publication,

    max(fa.date_publication_exacte) as derniere_publication

from {{ ref('stg_fact_annonce') }} as fa

join {{ source('warehouse', 'dim_localisation') }} as dl
  on dl.localisation_key = fa.localisation_key

group by
    dl.pays,
    dl.ville,
    dl.code_postal