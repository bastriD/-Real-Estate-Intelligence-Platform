-- Return discrepancies, including removed links and newly unmapped properties.
with expected as (
    select dv.demande_version_key, ds.secteur_key
    from {{ source('real_estate_oltp', 'demande_version_secteur') }} link
    join {{ source('warehouse', 'dim_demande_version') }} dv
      on dv.id_demande_version_source = link.id_demande_version
    join {{ source('warehouse', 'dim_secteur') }} ds
      on ds.id_secteur_source = link.id_secteur
), missing as (
    select * from expected
    except
    select * from {{ ref('stg_demande_version_secteur') }}
), extra as (
    select * from {{ ref('stg_demande_version_secteur') }}
    except
    select * from expected
)
select 'missing search sector' as discrepancy, demande_version_key as entity_key from missing
union all
select 'extra search sector', demande_version_key from extra
union all
select 'property sector', db.bien_key
from {{ ref('stg_dim_bien') }} db
join {{ source('real_estate_oltp', 'bien') }} b on b.id_bien = db.id_bien_source
left join {{ source('warehouse', 'dim_secteur') }} ds on ds.id_secteur_source = b.id_secteur
where db.is_current and db.secteur_key is distinct from coalesce(ds.secteur_key, 0)
