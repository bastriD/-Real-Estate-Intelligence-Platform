"""Current property geography and versioned search-sector alternatives."""


def load_sector_projection(cur):
    # Call after dim_bien, dim_secteur and dim_demande_version. Refresh unknown
    # mappings too, so migration 017's invalidation reaches analytics.
    cur.execute("""
        UPDATE warehouse.dim_bien db
        SET secteur_key = COALESCE(ds.secteur_key, 0), dw_updated_at = CURRENT_TIMESTAMP
        FROM real_estate.bien b
        LEFT JOIN warehouse.dim_secteur ds ON ds.id_secteur_source = b.id_secteur
        WHERE db.id_bien_source = b.id_bien AND db.is_current = TRUE
          AND db.secteur_key IS DISTINCT FROM COALESCE(ds.secteur_key, 0)
    """)
    cur.execute("""
        DELETE FROM warehouse.bridge_demande_version_secteur target
        WHERE NOT EXISTS (
            SELECT 1 FROM real_estate.demande_version_secteur link
            JOIN warehouse.dim_demande_version dv
              ON dv.id_demande_version_source = link.id_demande_version
            JOIN warehouse.dim_secteur ds ON ds.id_secteur_source = link.id_secteur
            WHERE target.demande_version_key = dv.demande_version_key
              AND target.secteur_key = ds.secteur_key
        )
    """)
    cur.execute("""
        INSERT INTO warehouse.bridge_demande_version_secteur (demande_version_key, secteur_key)
        SELECT dv.demande_version_key, ds.secteur_key
        FROM real_estate.demande_version_secteur link
        JOIN warehouse.dim_demande_version dv
          ON dv.id_demande_version_source = link.id_demande_version
        JOIN warehouse.dim_secteur ds ON ds.id_secteur_source = link.id_secteur
        ON CONFLICT DO NOTHING
    """)
