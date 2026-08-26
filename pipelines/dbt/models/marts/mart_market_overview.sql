select
    count(*) as total_annonces,

    count(distinct fa.reference_externe) as total_biens_uniques,

    count(distinct fa.ingestion_batch) as total_batches,

    round(avg(fa.prix), 2) as prix_moyen,

    round(
        percentile_cont(0.5) within group (order by fa.prix)::numeric,
        2
    ) as prix_median,

    round(min(fa.prix), 2) as prix_min,

    round(max(fa.prix), 2) as prix_max,

    round(avg(fa.surface), 2) as surface_moyenne,

    round(
        percentile_cont(0.5) within group (order by fa.surface)::numeric,
        2
    ) as surface_mediane,

    round(avg(fa.prix_m2), 2) as prix_m2_moyen,

    round(
        percentile_cont(0.5) within group (order by fa.prix_m2)::numeric,
        2
    ) as prix_m2_median,

    round(avg(fa.nb_pieces), 2) as nb_pieces_moyen,

    round(avg(fa.nb_chambres), 2) as nb_chambres_moyen,

    min(fa.date_publication_exacte) as premiere_publication,

    max(fa.date_publication_exacte) as derniere_publication,

    max(fa.date_collecte_exacte) as derniere_collecte

from {{ ref('stg_fact_annonce') }} as fa