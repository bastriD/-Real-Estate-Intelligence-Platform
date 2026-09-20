#!/bin/sh
# warehouse:validate / script. Sourced by GitLab; run from the project checkout.

test -f database/migrations/003_warehouse_schema.sql
grep -q "CREATE SCHEMA IF NOT EXISTS warehouse;" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.dim_date" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.dim_source" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.dim_localisation" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.dim_bien" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.dim_client" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.dim_chasseur" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.dim_secteur" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.dim_demande_version" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.fact_annonce" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.fact_mandat" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.fact_presentation" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.fact_paiement" database/migrations/003_warehouse_schema.sql
grep -q "warehouse.bridge_mandat_secteur" database/migrations/003_warehouse_schema.sql
grep -q "^BEGIN;" database/migrations/003_warehouse_schema.sql
grep -q "^COMMIT;" database/migrations/003_warehouse_schema.sql
