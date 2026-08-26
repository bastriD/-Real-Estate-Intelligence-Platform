select
    ds.nom as source_nom,
    ds.type_source,

    count(*) as nb_annonces,

    count(distinct fa.reference_externe) as nb_biens_uniques,

    count(distinct fa.ingestion_batch) as nb_batches,

    round(avg(fa.prix), 2) as prix_moyen,

    round(
        percentile_cont(0.5) within group (order by fa.prix)::numeric,
        2
    ) as prix_median,

    round(avg(fa.prix_m2), 2) as prix_m2_moyen,

    round(avg(fa.surface), 2) as surface_moyenne,

    min(fa.date_collecte_exacte) as premiere_collecte,

    max(fa.date_collecte_exacte) as derniere_collecte

from {{ ref('stg_fact_annonce') }} as fa

join {{ source('warehouse', 'dim_source') }} as ds
  on ds.source_key = fa.source_key
 and ds.is_current = true

group by
    ds.nom,
    ds.type_source