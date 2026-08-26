select
    date_trunc(
        'day',
        fa.date_collecte_exacte
    )::date as date_collecte,

    count(*) as nb_annonces,

    count(distinct fa.reference_externe) as nb_biens_uniques,

    round(avg(fa.prix), 2) as prix_moyen,

    round(
        percentile_cont(0.5)
        within group (order by fa.prix)::numeric,
        2
    ) as prix_median,

    round(avg(fa.prix_m2), 2) as prix_m2_moyen,

    round(
        percentile_cont(0.5)
        within group (order by fa.prix_m2)::numeric,
        2
    ) as prix_m2_median,

    round(avg(fa.surface), 2) as surface_moyenne,

    count(distinct fa.ingestion_batch) as nb_batches

from {{ ref('stg_fact_annonce') }} as fa

where fa.date_collecte_exacte is not null

group by
    date_trunc(
        'day',
        fa.date_collecte_exacte
    )::date

order by
    date_collecte