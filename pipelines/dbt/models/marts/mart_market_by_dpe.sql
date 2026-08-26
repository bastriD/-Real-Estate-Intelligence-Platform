select
    db.dpe,

    count(*) as nb_annonces,

    count(distinct fa.reference_externe) as nb_biens_uniques,

    round(avg(fa.prix), 2) as prix_moyen,

    round(
        percentile_cont(0.5) within group (order by fa.prix)::numeric,
        2
    ) as prix_median,

    round(avg(fa.prix_m2), 2) as prix_m2_moyen,

    round(avg(fa.surface), 2) as surface_moyenne,

    round(avg(fa.nb_pieces), 2) as nb_pieces_moyen,

    round(avg(fa.nb_chambres), 2) as nb_chambres_moyen,

    min(fa.date_publication_exacte) as premiere_publication,

    max(fa.date_publication_exacte) as derniere_publication

from {{ ref('stg_fact_annonce') }} as fa

join {{ ref('stg_dim_bien') }} as db
  on db.bien_key = fa.bien_key
 and db.is_current = true

where db.dpe is not null

group by
    db.dpe