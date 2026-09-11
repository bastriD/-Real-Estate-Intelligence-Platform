import os
import sys
from datetime import datetime, timezone

import psycopg


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_connection():
    return psycopg.connect(
        host=env("POSTGRES_HOST"),
        port=int(env("POSTGRES_PORT")),
        dbname=env("POSTGRES_DB"),
        user=env("POSTGRES_USER"),
        password=env("POSTGRES_PASSWORD"),
        autocommit=False,
    )


def load_dim_source(cur):
    cur.execute("""
        INSERT INTO warehouse.dim_source (
            id_source_source,
            nom,
            type_source,
            url_base,
            actif,
            niveau_confiance,
            date_creation_source,
            valid_from,
            valid_to,
            is_current,
            dw_created_at,
            dw_updated_at
        )
        SELECT
            s.id_source,
            s.nom,
            s.type_source,
            s.url_base,
            s.actif,
            s.niveau_confiance,
            s.date_creation,
            CURRENT_TIMESTAMP,
            NULL,
            TRUE,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        FROM real_estate.source s
        WHERE NOT EXISTS (
            SELECT 1
            FROM warehouse.dim_source d
            WHERE d.id_source_source = s.id_source
              AND d.is_current = TRUE
        );
    """)


def load_dim_client(cur):
    cur.execute("""
        INSERT INTO warehouse.dim_client (
            id_client_source,
            ville,
            date_creation_source,
            statut,
            consentement_contact,
            dw_created_at,
            dw_updated_at
        )
        SELECT
            c.id_client,
            c.ville,
            c.date_creation,
            c.statut,
            c.consentement_contact,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        FROM real_estate.client c
        ON CONFLICT (id_client_source)
        DO UPDATE SET
            ville = EXCLUDED.ville,
            date_creation_source = EXCLUDED.date_creation_source,
            statut = EXCLUDED.statut,
            consentement_contact = EXCLUDED.consentement_contact,
            dw_updated_at = CURRENT_TIMESTAMP;
    """)


def load_dim_chasseur(cur):
    cur.execute("""
        INSERT INTO warehouse.dim_chasseur (
            id_chasseur_source,
            date_entree,
            statut,
            dw_created_at,
            dw_updated_at
        )
        SELECT
            c.id_chasseur,
            c.date_entree,
            c.statut,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        FROM real_estate.chasseur c
        ON CONFLICT (id_chasseur_source)
        DO UPDATE SET
            date_entree = EXCLUDED.date_entree,
            statut = EXCLUDED.statut,
            dw_updated_at = CURRENT_TIMESTAMP;
    """)


def load_dim_secteur(cur):
    cur.execute("""
        INSERT INTO warehouse.dim_secteur (
            id_secteur_source,
            pays,
            ville,
            quartier,
            code_postal,
            actif,
            dw_created_at,
            dw_updated_at
        )
        SELECT
            s.id_secteur,
            s.pays,
            s.ville,
            s.quartier,
            s.code_postal,
            s.actif,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        FROM real_estate.secteur s
        ON CONFLICT (id_secteur_source)
        DO UPDATE SET
            pays = EXCLUDED.pays,
            ville = EXCLUDED.ville,
            quartier = EXCLUDED.quartier,
            code_postal = EXCLUDED.code_postal,
            actif = EXCLUDED.actif,
            dw_updated_at = CURRENT_TIMESTAMP;
    """)


def load_dim_demande_version(cur):
    cur.execute("""
        INSERT INTO warehouse.dim_demande_version (
            id_demande_version_source,
            id_demande_source,
            numero_version,
            date_version,
            ville,
            code_postal,
            type_bien,
            budget_min,
            budget_max,
            surface_min,
            nb_pieces_min,
            nb_chambres_min,
            dpe_max,
            criteres_souhaites,
            active,
            auteur_type,
            dw_created_at,
            dw_updated_at
        )
        SELECT
            dv.id_demande_version,
            dv.id_demande,
            dv.numero_version,
            dv.date_version,
            dv.ville,
            dv.code_postal,
            dv.type_bien,
            dv.budget_min,
            dv.budget_max,
            dv.surface_min,
            dv.nb_pieces_min,
            dv.nb_chambres_min,
            dv.dpe_max,
            dv.criteres_souhaites,
            dv.active,
            CASE
                WHEN dv.auteur_client_id IS NOT NULL THEN 'CLIENT'
                WHEN dv.auteur_chasseur_id IS NOT NULL THEN 'CHASSEUR'
                WHEN dv.auteur_systeme = TRUE THEN 'SYSTEME'
                ELSE 'INCONNU'
            END,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        FROM real_estate.demande_version dv
        ON CONFLICT (id_demande_version_source)
        DO UPDATE SET
            id_demande_source = EXCLUDED.id_demande_source,
            numero_version = EXCLUDED.numero_version,
            date_version = EXCLUDED.date_version,
            ville = EXCLUDED.ville,
            code_postal = EXCLUDED.code_postal,
            type_bien = EXCLUDED.type_bien,
            budget_min = EXCLUDED.budget_min,
            budget_max = EXCLUDED.budget_max,
            surface_min = EXCLUDED.surface_min,
            nb_pieces_min = EXCLUDED.nb_pieces_min,
            nb_chambres_min = EXCLUDED.nb_chambres_min,
            dpe_max = EXCLUDED.dpe_max,
            criteres_souhaites = EXCLUDED.criteres_souhaites,
            active = EXCLUDED.active,
            auteur_type = EXCLUDED.auteur_type,
            dw_updated_at = CURRENT_TIMESTAMP;
    """)


def load_dim_bien(cur):
    cur.execute("""
        INSERT INTO warehouse.dim_bien (
            id_bien_source,
            id_source_source,
            reference_externe,
            titre,
            type_bien,
            adresse,
            latitude,
            longitude,
            dpe,
            statut,
            valid_from,
            valid_to,
            is_current,
            dw_created_at,
            dw_updated_at
        )
        SELECT
            b.id_bien,
            b.id_source,
            b.reference_externe,
            b.titre,
            b.type_bien,
            b.adresse,
            b.latitude,
            b.longitude,
            b.dpe,
            b.statut,
            COALESCE(b.date_collecte, CURRENT_TIMESTAMP),
            NULL,
            TRUE,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        FROM real_estate.bien b
        WHERE NOT EXISTS (
            SELECT 1
            FROM warehouse.dim_bien d
            WHERE d.id_source_source = b.id_source
              AND d.reference_externe = b.reference_externe
              AND d.is_current = TRUE
        );
    """)


def load_dim_localisation(cur):
    cur.execute("""
        INSERT INTO warehouse.dim_localisation (
            pays,
            code_postal,
            ville,
            region,
            departement_region,
            dw_created_at,
            dw_updated_at
        )
        SELECT DISTINCT
            'FRANCE',
            b.code_postal,
            b.ville,
            NULL,
            NULL,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        FROM real_estate.bien b
        WHERE b.ville IS NOT NULL
        ON CONFLICT (pays, code_postal, ville)
        DO NOTHING;
    """)


def load_fact_annonce(cur):
    cur.execute("""
        INSERT INTO warehouse.fact_annonce (
            bien_key,
            source_key,
            localisation_key,
            publication_date_key,
            collection_date_key,
            prix,
            surface,
            prix_m2,
            nb_pieces,
            nb_chambres,
            annonce_count,
            reference_externe,
            ingestion_batch,
            source_file,
            date_collecte_exacte,
            date_publication_exacte,
            dw_loaded_at
        )
        SELECT
            db.bien_key,
            ds.source_key,
            dl.localisation_key,
            TO_CHAR(b.date_publication::date, 'YYYYMMDD')::integer,
            TO_CHAR(b.date_collecte::date, 'YYYYMMDD')::integer,
            b.prix,
            b.surface,
            CASE
                WHEN b.surface > 0 THEN ROUND(b.prix / b.surface, 2)
                ELSE 0
            END,
            b.nb_pieces,
            b.nb_chambres,
            1,
            b.reference_externe,
            COALESCE(sa.ingestion_batch, 'UNKNOWN'),
            COALESCE(sa.source_file, 'UNKNOWN'),
            b.date_collecte,
            b.date_publication,
            CURRENT_TIMESTAMP
        FROM real_estate.bien b
        JOIN warehouse.dim_bien db
          ON db.id_source_source = b.id_source
         AND db.reference_externe = b.reference_externe
         AND db.is_current = TRUE
        JOIN warehouse.dim_source ds
          ON ds.id_source_source = b.id_source
         AND ds.is_current = TRUE
        JOIN warehouse.dim_localisation dl
          ON dl.pays = 'FRANCE'
         AND dl.ville = b.ville
         AND dl.code_postal IS NOT DISTINCT FROM b.code_postal
        LEFT JOIN staging.annonces sa
          ON sa.reference = b.reference_externe
        WHERE b.prix IS NOT NULL
          AND b.prix >= 0
          AND b.surface IS NOT NULL
          AND b.surface > 0
          AND b.date_publication IS NOT NULL
          AND b.date_collecte IS NOT NULL
        ON CONFLICT (
            source_key,
            reference_externe,
            ingestion_batch
        )
        DO NOTHING;
    """)


def load_fact_mandat(cur):
    cur.execute("""
        INSERT INTO warehouse.fact_mandat (
            id_mandat_source,
            reference_mandat,
            client_key,
            chasseur_key,
            date_signature_key,
            date_debut_key,
            date_fin_key,
            type_mandat,
            mode_signature,
            statut,
            est_exclusif,
            duree_jours,
            mandat_count,
            dw_loaded_at
        )
        SELECT
            m.id_mandat,
            m.reference_mandat,
            dc.client_key,
            dh.chasseur_key,
            TO_CHAR(m.date_signature, 'YYYYMMDD')::integer,
            TO_CHAR(m.date_debut, 'YYYYMMDD')::integer,
            TO_CHAR(m.date_fin, 'YYYYMMDD')::integer,
            m.type_mandat,
            m.mode_signature,
            m.statut,
            CASE
                WHEN UPPER(m.type_mandat) LIKE '%EXCLUSIF%'
                 AND UPPER(m.type_mandat) NOT LIKE '%NON%'
                    THEN TRUE
                ELSE FALSE
            END,
            (m.date_fin - m.date_debut),
            1,
            CURRENT_TIMESTAMP
        FROM real_estate.mandat m
        JOIN warehouse.dim_client dc
          ON dc.id_client_source = m.id_client
        JOIN warehouse.dim_chasseur dh
          ON dh.id_chasseur_source = m.id_chasseur
        ON CONFLICT (id_mandat_source)
        DO UPDATE SET
            reference_mandat = EXCLUDED.reference_mandat,
            client_key = EXCLUDED.client_key,
            chasseur_key = EXCLUDED.chasseur_key,
            date_signature_key = EXCLUDED.date_signature_key,
            date_debut_key = EXCLUDED.date_debut_key,
            date_fin_key = EXCLUDED.date_fin_key,
            type_mandat = EXCLUDED.type_mandat,
            mode_signature = EXCLUDED.mode_signature,
            statut = EXCLUDED.statut,
            est_exclusif = EXCLUDED.est_exclusif,
            duree_jours = EXCLUDED.duree_jours,
            dw_loaded_at = CURRENT_TIMESTAMP;
    """)
def load_fact_mandat_periode(cur):
    cur.execute("""
        INSERT INTO warehouse.fact_mandat_periode (
            id_mandat_periode_source,
            mandat_fact_key,
            numero_periode,
            type_periode,
            date_debut_key,
            date_fin_key,
            date_renouvellement_key,
            est_historique_legacy,
            duree_jours,
            periode_count,
            created_at_source,
            dw_loaded_at
        )
        SELECT
            mp.id_mandat_periode,
            fm.mandat_fact_key,
            mp.numero_periode,
            mp.type_periode,
            TO_CHAR(mp.date_debut, 'YYYYMMDD')::integer,
            TO_CHAR(mp.date_fin, 'YYYYMMDD')::integer,
            CASE
                WHEN mp.date_renouvellement IS NULL THEN NULL
                ELSE TO_CHAR(
                    mp.date_renouvellement,
                    'YYYYMMDD'
                )::integer
            END,
            mp.est_historique_legacy,
            (mp.date_fin - mp.date_debut),
            1,
            mp.created_at,
            CURRENT_TIMESTAMP
        FROM real_estate.mandat_periode mp
        JOIN warehouse.fact_mandat fm
          ON fm.id_mandat_source = mp.id_mandat
        ON CONFLICT (id_mandat_periode_source)
        DO UPDATE SET
            mandat_fact_key = EXCLUDED.mandat_fact_key,
            numero_periode = EXCLUDED.numero_periode,
            type_periode = EXCLUDED.type_periode,
            date_debut_key = EXCLUDED.date_debut_key,
            date_fin_key = EXCLUDED.date_fin_key,
            date_renouvellement_key =
                EXCLUDED.date_renouvellement_key,
            est_historique_legacy =
                EXCLUDED.est_historique_legacy,
            duree_jours = EXCLUDED.duree_jours,
            created_at_source = EXCLUDED.created_at_source,
            dw_loaded_at = CURRENT_TIMESTAMP;
    """)

def load_bridge_mandat_secteur(cur):
    cur.execute("""
        INSERT INTO warehouse.bridge_mandat_secteur (
            mandat_fact_key,
            secteur_key,
            dw_loaded_at
        )
        SELECT
            fm.mandat_fact_key,
            ds.secteur_key,
            CURRENT_TIMESTAMP
        FROM real_estate.mandat_secteur ms
        JOIN warehouse.fact_mandat fm
          ON fm.id_mandat_source = ms.id_mandat
        JOIN warehouse.dim_secteur ds
          ON ds.id_secteur_source = ms.id_secteur
        ON CONFLICT (
            mandat_fact_key,
            secteur_key
        )
        DO NOTHING;
    """)


def load_fact_presentation(cur):
    cur.execute("""
        INSERT INTO warehouse.fact_presentation (
            id_presentation_source,
            demande_version_key,
            bien_key,
            client_key,
            chasseur_key,
            date_selection_key,
            date_presentation_key,
            score_matching,
            statut,
            presentation_count,
            dw_loaded_at
        )
        SELECT
            p.id_presentation,
            ddv.demande_version_key,
            db.bien_key,
            COALESCE(dc.client_key, 0),
            COALESCE(dh.chasseur_key, 0),
            TO_CHAR(p.date_selection::date, 'YYYYMMDD')::integer,
            CASE
                WHEN p.date_presentation IS NULL THEN NULL
                ELSE TO_CHAR(p.date_presentation::date, 'YYYYMMDD')::integer
            END,
            p.score_matching,
            p.statut,
            1,
            CURRENT_TIMESTAMP
        FROM real_estate.presentation p
        JOIN real_estate.demande_version dv
          ON dv.id_demande_version = p.id_demande_version
        JOIN real_estate.demande d
          ON d.id_demande = dv.id_demande
        LEFT JOIN real_estate.mandat m
          ON m.id_mandat = d.id_mandat
        JOIN real_estate.bien b
          ON b.id_bien = p.id_bien
        JOIN warehouse.dim_demande_version ddv
          ON ddv.id_demande_version_source = p.id_demande_version
        JOIN warehouse.dim_bien db
          ON db.id_source_source = b.id_source
         AND db.reference_externe = b.reference_externe
         AND db.is_current = TRUE
        LEFT JOIN warehouse.dim_client dc
          ON dc.id_client_source = m.id_client
        LEFT JOIN warehouse.dim_chasseur dh
          ON dh.id_chasseur_source = m.id_chasseur
        ON CONFLICT (id_presentation_source)
        DO UPDATE SET
            demande_version_key = EXCLUDED.demande_version_key,
            bien_key = EXCLUDED.bien_key,
            client_key = EXCLUDED.client_key,
            chasseur_key = EXCLUDED.chasseur_key,
            date_selection_key = EXCLUDED.date_selection_key,
            date_presentation_key = EXCLUDED.date_presentation_key,
            score_matching = EXCLUDED.score_matching,
            statut = EXCLUDED.statut,
            dw_loaded_at = CURRENT_TIMESTAMP;
    """)


def load_fact_paiement(cur):
    cur.execute("""
        INSERT INTO warehouse.fact_paiement (
            id_paiement_source,
            id_bareme_source,
            mandat_fact_key,
            client_key,
            chasseur_key,
            date_acte_authentique_key,
            date_reception_honoraires_key,
            date_paiement_chasseur_key,
            montant_achat,
            montant_honoraires,
            montant_chasseur,
            statut,
            paiement_count,
            dw_loaded_at
        )
        SELECT
            p.id_paiement,
            p.id_bareme,
            fm.mandat_fact_key,
            dc.client_key,
            dh.chasseur_key,

            CASE
                WHEN p.date_acte_authentique IS NULL THEN NULL
                ELSE TO_CHAR(p.date_acte_authentique, 'YYYYMMDD')::integer
            END,

            CASE
                WHEN p.date_reception_honoraires IS NULL THEN NULL
                ELSE TO_CHAR(p.date_reception_honoraires, 'YYYYMMDD')::integer
            END,

            CASE
                WHEN p.date_paiement_chasseur IS NULL THEN NULL
                ELSE TO_CHAR(p.date_paiement_chasseur, 'YYYYMMDD')::integer
            END,

            p.montant_achat,
            p.montant_honoraires,
            p.montant_chasseur,
            p.statut,
            1,
            CURRENT_TIMESTAMP

        FROM real_estate.paiement p

        JOIN real_estate.mandat m
          ON m.id_mandat = p.id_mandat

        JOIN warehouse.fact_mandat fm
          ON fm.id_mandat_source = p.id_mandat

        JOIN warehouse.dim_client dc
          ON dc.id_client_source = m.id_client

        JOIN warehouse.dim_chasseur dh
          ON dh.id_chasseur_source = m.id_chasseur

        ON CONFLICT (id_paiement_source)
        DO UPDATE SET
            id_bareme_source = EXCLUDED.id_bareme_source,
            mandat_fact_key = EXCLUDED.mandat_fact_key,
            client_key = EXCLUDED.client_key,
            chasseur_key = EXCLUDED.chasseur_key,
            date_acte_authentique_key = EXCLUDED.date_acte_authentique_key,
            date_reception_honoraires_key = EXCLUDED.date_reception_honoraires_key,
            date_paiement_chasseur_key = EXCLUDED.date_paiement_chasseur_key,
            montant_achat = EXCLUDED.montant_achat,
            montant_honoraires = EXCLUDED.montant_honoraires,
            montant_chasseur = EXCLUDED.montant_chasseur,
            statut = EXCLUDED.statut,
            dw_loaded_at = CURRENT_TIMESTAMP;
    """)


def print_counts(cur):
    objects = [
        "dim_source",
        "dim_localisation",
        "dim_bien",
        "dim_client",
        "dim_chasseur",
        "dim_secteur",
        "dim_demande_version",
        "fact_annonce",
        "fact_mandat",
        "fact_mandat_periode",
        "bridge_mandat_secteur",
        "fact_presentation",
        "fact_paiement",
    ]

    print("\nWAREHOUSE COUNTS")
    print("=" * 60)

    for obj in objects:
        cur.execute(f"SELECT COUNT(*) FROM warehouse.{obj};")
        count = cur.fetchone()[0]
        print(f"{obj:28} {count}")

    print("=" * 60)


def main():
    started = datetime.now(timezone.utc)

    print("Starting OLTP -> Warehouse load")
    print(f"Started at: {started.isoformat()}")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                print("Loading dim_source...")
                load_dim_source(cur)

                print("Loading dim_localisation...")
                load_dim_localisation(cur)

                print("Loading dim_bien...")
                load_dim_bien(cur)

                print("Loading dim_client...")
                load_dim_client(cur)

                print("Loading dim_chasseur...")
                load_dim_chasseur(cur)

                print("Loading dim_secteur...")
                load_dim_secteur(cur)

                print("Loading dim_demande_version...")
                load_dim_demande_version(cur)

                print("Loading fact_annonce...")
                load_fact_annonce(cur)

                print("Loading fact_mandat...")
                load_fact_mandat(cur)
                
                print("Loading fact_mandat_periode...")
                load_fact_mandat_periode(cur)

                print("Loading bridge_mandat_secteur...")
                load_bridge_mandat_secteur(cur)

                print("Loading fact_presentation...")
                load_fact_presentation(cur)

                print("Loading fact_paiement...")
                load_fact_paiement(cur)

                print_counts(cur)

            conn.commit()

    except Exception as exc:
        print(f"ERROR: Warehouse load failed: {exc}", file=sys.stderr)
        raise

    finished = datetime.now(timezone.utc)

    print(f"Finished at: {finished.isoformat()}")
    print(f"Duration: {(finished - started).total_seconds():.2f}s")
    print("Warehouse load completed successfully.")


if __name__ == "__main__":
    main()