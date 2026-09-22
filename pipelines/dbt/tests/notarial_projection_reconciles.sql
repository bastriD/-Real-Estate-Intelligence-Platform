with movements as (
    select id_dossier_notarial,
        sum(montant) filter (where nature = 'COLLECTE_NOTAIRE') as collecte,
        sum(montant) filter (where nature = 'RECEPTION_ENTREPRISE') as recu,
        max(date_operation) filter (where nature = 'RECEPTION_ENTREPRISE') as derniere_reception
    from {{ source('real_estate_oltp', 'mouvement_notarial') }}
    group by id_dossier_notarial
), expected as (
    select d.id_dossier_notarial as id_dossier_source, d.id_notaire as id_notaire_source,
        d.id_vente as id_vente_source, d.id_vente is not null as acte_signe,
        p.montant_honoraires as honoraires_attendus,
        coalesce(m.collecte, 0) as montant_collecte, coalesce(m.recu, 0) as montant_recu,
        m.derniere_reception
    from {{ source('real_estate_oltp', 'dossier_notarial') }} d
    left join {{ source('real_estate_oltp', 'paiement') }} p on p.id_vente = d.id_vente
    left join movements m using (id_dossier_notarial)
), actual as (
    select id_dossier_source, id_notaire_source, id_vente_source, acte_signe,
        honoraires_attendus, montant_collecte, montant_recu, derniere_reception
    from {{ ref('stg_dossier_notarial') }}
), missing_or_changed as (
    select * from expected except select * from actual
), extra_or_changed as (
    select * from actual except select * from expected
)
select * from missing_or_changed
union all
select * from extra_or_changed
