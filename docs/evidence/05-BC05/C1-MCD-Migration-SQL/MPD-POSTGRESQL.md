# MPD PostgreSQL — Real Estate Intelligence Platform

**Projet :** Real Estate Intelligence Platform  
**Méthode :** MERISE  
**Version :** 1.0  
**Statut :** Baseline physique  
**Source :**
- `MCD-MERISE-PROJET.md`
- `MLD-PROJET.md`

---

# 1. Objectif

Le Modèle Physique de Données traduit le MLD en structures directement implémentables dans PostgreSQL.

Le chemin complet est :

```text
MCD
 |
 v
MLD
 |
 v
MPD PostgreSQL
 |
 v
migration.sql
 |
 v
PostgreSQL
 |
 v
Validation
```

Le MPD définit :

- les noms de tables ;
- les noms de colonnes ;
- les types PostgreSQL ;
- les clés primaires ;
- les clés étrangères ;
- les contraintes ;
- les index ;
- les valeurs par défaut ;
- les règles d'intégrité.

---

# 2. Convention de nommage

Le projet utilise :

```text
snake_case
```

pour :

- tables ;
- colonnes ;
- contraintes ;
- index.

Les tables utilisent des noms au singulier.

Exemples :

```text
client
mandat
demande_version
bien
presentation
```

---

# 3. Stratégie d'identifiants

Pour le MVP, les identifiants utilisent :

```text
BIGINT GENERATED ALWAYS AS IDENTITY
```

Exemple :

```sql
id_client BIGINT GENERATED ALWAYS AS IDENTITY
```

Avantages :

- simple ;
- natif PostgreSQL ;
- lisible ;
- performant ;
- adapté au périmètre actuel.

---

# 4. Schéma PostgreSQL

Le modèle métier sera isolé dans un schéma dédié :

```text
real_estate
```

Création :

```sql
CREATE SCHEMA IF NOT EXISTS real_estate;
```

Les tables deviennent :

```text
real_estate.client
real_estate.chasseur
real_estate.mandat
real_estate.demande_version
real_estate.source
real_estate.bien
real_estate.presentation
real_estate.document
```

---

# 5. Table client

```sql
CREATE TABLE real_estate.client (
    id_client BIGINT GENERATED ALWAYS AS IDENTITY,
    nom VARCHAR(120) NOT NULL,
    prenom VARCHAR(120),
    email VARCHAR(255) NOT NULL,
    telephone VARCHAR(40),
    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',
    consentement_contact BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_client
        PRIMARY KEY (id_client),

    CONSTRAINT uq_client_email
        UNIQUE (email),

    CONSTRAINT ck_client_statut
        CHECK (statut IN ('ACTIF', 'INACTIF', 'ARCHIVE'))
);
```

---

# 6. Justification client

## email

```text
VARCHAR(255)
```

car l'adresse email reste une chaîne de longueur raisonnable.

Elle est unique dans le MVP.

## consentement_contact

```text
BOOLEAN
```

permet de distinguer explicitement :

```text
true
false
```

sans utiliser des valeurs textuelles.

---

# 7. Table chasseur

```sql
CREATE TABLE real_estate.chasseur (
    id_chasseur BIGINT GENERATED ALWAYS AS IDENTITY,
    nom VARCHAR(120) NOT NULL,
    prenom VARCHAR(120),
    email VARCHAR(255) NOT NULL,
    telephone VARCHAR(40),
    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',
    date_entree DATE,

    CONSTRAINT pk_chasseur
        PRIMARY KEY (id_chasseur),

    CONSTRAINT uq_chasseur_email
        UNIQUE (email),

    CONSTRAINT ck_chasseur_statut
        CHECK (statut IN ('ACTIF', 'INACTIF'))
);
```

---

# 8. Table source

```sql
CREATE TABLE real_estate.source (
    id_source BIGINT GENERATED ALWAYS AS IDENTITY,
    nom VARCHAR(150) NOT NULL,
    type_source VARCHAR(40) NOT NULL,
    url_base TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    niveau_confiance VARCHAR(20),
    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_source
        PRIMARY KEY (id_source),

    CONSTRAINT ck_source_type
        CHECK (
            type_source IN (
                'PORTAIL',
                'AGENCE',
                'API',
                'MANUEL',
                'PARTENAIRE',
                'OPEN_DATA'
            )
        ),

    CONSTRAINT ck_source_confiance
        CHECK (
            niveau_confiance IS NULL
            OR niveau_confiance IN ('FAIBLE', 'MOYEN', 'ELEVE')
        )
);
```

---

# 9. Table mandat

```sql
CREATE TABLE real_estate.mandat (
    id_mandat BIGINT GENERATED ALWAYS AS IDENTITY,
    reference_mandat VARCHAR(80) NOT NULL,
    date_signature DATE,
    date_debut DATE,
    date_fin DATE,
    statut VARCHAR(20) NOT NULL DEFAULT 'BROUILLON',
    budget_min NUMERIC(12,2),
    budget_max NUMERIC(12,2),
    commentaire TEXT,

    id_client BIGINT NOT NULL,
    id_chasseur BIGINT NOT NULL,

    CONSTRAINT pk_mandat
        PRIMARY KEY (id_mandat),

    CONSTRAINT uq_mandat_reference
        UNIQUE (reference_mandat),

    CONSTRAINT fk_mandat_client
        FOREIGN KEY (id_client)
        REFERENCES real_estate.client(id_client)
        ON DELETE RESTRICT,

    CONSTRAINT fk_mandat_chasseur
        FOREIGN KEY (id_chasseur)
        REFERENCES real_estate.chasseur(id_chasseur)
        ON DELETE RESTRICT,

    CONSTRAINT ck_mandat_statut
        CHECK (
            statut IN (
                'BROUILLON',
                'ACTIF',
                'SUSPENDU',
                'TERMINE',
                'ANNULE'
            )
        ),

    CONSTRAINT ck_mandat_budget_min
        CHECK (budget_min IS NULL OR budget_min >= 0),

    CONSTRAINT ck_mandat_budget_max
        CHECK (budget_max IS NULL OR budget_max >= 0),

    CONSTRAINT ck_mandat_budget_range
        CHECK (
            budget_min IS NULL
            OR budget_max IS NULL
            OR budget_min <= budget_max
        ),

    CONSTRAINT ck_mandat_dates
        CHECK (
            date_fin IS NULL
            OR date_debut IS NULL
            OR date_fin >= date_debut
        )
);
```

---

# 10. Table demande_version

```sql
CREATE TABLE real_estate.demande_version (
    id_demande_version BIGINT GENERATED ALWAYS AS IDENTITY,
    numero_version INTEGER NOT NULL,
    date_version TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    type_bien VARCHAR(40),
    localisation VARCHAR(255),
    budget_min NUMERIC(12,2),
    budget_max NUMERIC(12,2),
    surface_min NUMERIC(10,2),
    nb_pieces_min INTEGER,
    nb_chambres_min INTEGER,
    exterieur_requis BOOLEAN NOT NULL DEFAULT FALSE,
    parking_requis BOOLEAN NOT NULL DEFAULT FALSE,
    ascenseur_requis BOOLEAN NOT NULL DEFAULT FALSE,
    commentaire TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,

    id_mandat BIGINT NOT NULL,

    CONSTRAINT pk_demande_version
        PRIMARY KEY (id_demande_version),

    CONSTRAINT fk_demande_version_mandat
        FOREIGN KEY (id_mandat)
        REFERENCES real_estate.mandat(id_mandat)
        ON DELETE RESTRICT,

    CONSTRAINT uq_demande_version_numero
        UNIQUE (id_mandat, numero_version),

    CONSTRAINT ck_demande_version_numero
        CHECK (numero_version > 0),

    CONSTRAINT ck_demande_version_budget_min
        CHECK (budget_min IS NULL OR budget_min >= 0),

    CONSTRAINT ck_demande_version_budget_max
        CHECK (budget_max IS NULL OR budget_max >= 0),

    CONSTRAINT ck_demande_version_budget_range
        CHECK (
            budget_min IS NULL
            OR budget_max IS NULL
            OR budget_min <= budget_max
        ),

    CONSTRAINT ck_demande_version_surface
        CHECK (surface_min IS NULL OR surface_min >= 0),

    CONSTRAINT ck_demande_version_pieces
        CHECK (nb_pieces_min IS NULL OR nb_pieces_min >= 0),

    CONSTRAINT ck_demande_version_chambres
        CHECK (nb_chambres_min IS NULL OR nb_chambres_min >= 0)
);
```

---

# 11. Version active unique

PostgreSQL permet un index unique partiel.

```sql
CREATE UNIQUE INDEX uq_demande_version_active
ON real_estate.demande_version(id_mandat)
WHERE active = TRUE;
```

Cela garantit :

```text
Maximum one active request version
per mandate
```

tout en autorisant plusieurs anciennes versions :

```text
active = false
```

---

# 12. Table bien

```sql
CREATE TABLE real_estate.bien (
    id_bien BIGINT GENERATED ALWAYS AS IDENTITY,
    reference_externe VARCHAR(150) NOT NULL,
    titre VARCHAR(255),
    type_bien VARCHAR(40) NOT NULL,
    adresse TEXT,
    code_postal VARCHAR(20),
    ville VARCHAR(120),
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    prix NUMERIC(12,2),
    surface NUMERIC(10,2),
    nb_pieces INTEGER,
    nb_chambres INTEGER,
    etage INTEGER,
    ascenseur BOOLEAN,
    parking BOOLEAN,
    balcon BOOLEAN,
    terrasse BOOLEAN,
    jardin BOOLEAN,
    description TEXT,
    date_publication TIMESTAMPTZ,
    date_collecte TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',

    id_source BIGINT NOT NULL,

    CONSTRAINT pk_bien
        PRIMARY KEY (id_bien),

    CONSTRAINT fk_bien_source
        FOREIGN KEY (id_source)
        REFERENCES real_estate.source(id_source)
        ON DELETE RESTRICT,

    CONSTRAINT uq_bien_source_reference
        UNIQUE (id_source, reference_externe),

    CONSTRAINT ck_bien_prix
        CHECK (prix IS NULL OR prix >= 0),

    CONSTRAINT ck_bien_surface
        CHECK (surface IS NULL OR surface >= 0),

    CONSTRAINT ck_bien_pieces
        CHECK (nb_pieces IS NULL OR nb_pieces >= 0),

    CONSTRAINT ck_bien_chambres
        CHECK (nb_chambres IS NULL OR nb_chambres >= 0),

    CONSTRAINT ck_bien_latitude
        CHECK (
            latitude IS NULL
            OR latitude BETWEEN -90 AND 90
        ),

    CONSTRAINT ck_bien_longitude
        CHECK (
            longitude IS NULL
            OR longitude BETWEEN -180 AND 180
        ),

    CONSTRAINT ck_bien_statut
        CHECK (
            statut IN (
                'ACTIF',
                'EXPIRE',
                'VENDU',
                'INDISPONIBLE'
            )
        )
);
```

---

# 13. Pourquoi NUMERIC pour prix

Le prix utilise :

```text
NUMERIC(12,2)
```

et non :

```text
FLOAT
```

afin d'éviter les problèmes de représentation approximative pour des montants financiers.

---

# 14. Pourquoi latitude / longitude séparées

Le MVP ne nécessite pas encore PostGIS.

On utilise :

```text
latitude
longitude
```

avec des contraintes de plage.

Si le projet nécessite ensuite :

- distance ;
- polygones ;
- recherche géospatiale avancée ;

PostGIS pourra être évalué via ADR.

---

# 15. Table presentation

```sql
CREATE TABLE real_estate.presentation (
    id_presentation BIGINT GENERATED ALWAYS AS IDENTITY,
    date_selection TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_presentation TIMESTAMPTZ,
    score_matching NUMERIC(5,2),
    score_budget NUMERIC(5,2),
    score_localisation NUMERIC(5,2),
    score_surface NUMERIC(5,2),
    score_criteres NUMERIC(5,2),
    statut VARCHAR(20) NOT NULL DEFAULT 'IDENTIFIE',
    motif_rejet TEXT,
    commentaire_chasseur TEXT,
    feedback_client TEXT,

    id_demande_version BIGINT NOT NULL,
    id_bien BIGINT NOT NULL,

    CONSTRAINT pk_presentation
        PRIMARY KEY (id_presentation),

    CONSTRAINT fk_presentation_demande_version
        FOREIGN KEY (id_demande_version)
        REFERENCES real_estate.demande_version(id_demande_version)
        ON DELETE RESTRICT,

    CONSTRAINT fk_presentation_bien
        FOREIGN KEY (id_bien)
        REFERENCES real_estate.bien(id_bien)
        ON DELETE RESTRICT,

    CONSTRAINT uq_presentation_demande_bien
        UNIQUE (id_demande_version, id_bien),

    CONSTRAINT ck_presentation_score_matching
        CHECK (
            score_matching IS NULL
            OR score_matching BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_presentation_score_budget
        CHECK (
            score_budget IS NULL
            OR score_budget BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_presentation_score_localisation
        CHECK (
            score_localisation IS NULL
            OR score_localisation BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_presentation_score_surface
        CHECK (
            score_surface IS NULL
            OR score_surface BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_presentation_score_criteres
        CHECK (
            score_criteres IS NULL
            OR score_criteres BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_presentation_statut
        CHECK (
            statut IN (
                'IDENTIFIE',
                'QUALIFIE',
                'PRESENTE',
                'REJETE',
                'VISITE',
                'RETENU'
            )
        )
);
```

---

# 16. Table document

```sql
CREATE TABLE real_estate.document (
    id_document BIGINT GENERATED ALWAYS AS IDENTITY,
    nom_fichier VARCHAR(255) NOT NULL,
    type_document VARCHAR(60),
    mime_type VARCHAR(120),
    chemin_stockage TEXT NOT NULL,
    checksum VARCHAR(128),
    date_ajout TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    classification VARCHAR(20) NOT NULL DEFAULT 'INTERNE',
    indexable_ia BOOLEAN NOT NULL DEFAULT FALSE,

    id_bien BIGINT NOT NULL,

    CONSTRAINT pk_document
        PRIMARY KEY (id_document),

    CONSTRAINT fk_document_bien
        FOREIGN KEY (id_bien)
        REFERENCES real_estate.bien(id_bien)
        ON DELETE RESTRICT,

    CONSTRAINT ck_document_classification
        CHECK (
            classification IN (
                'PUBLIC',
                'INTERNE',
                'CONFIDENTIEL',
                'RESTREINT'
            )
        )
);
```

---

# 17. Index techniques minimum

Les foreign keys ne créent pas automatiquement tous les index utiles côté PostgreSQL.

Les index candidats retenus pour le MVP sont :

```sql
CREATE INDEX idx_mandat_id_client
ON real_estate.mandat(id_client);

CREATE INDEX idx_mandat_id_chasseur
ON real_estate.mandat(id_chasseur);

CREATE INDEX idx_demande_version_id_mandat
ON real_estate.demande_version(id_mandat);

CREATE INDEX idx_bien_id_source
ON real_estate.bien(id_source);

CREATE INDEX idx_presentation_id_demande_version
ON real_estate.presentation(id_demande_version);

CREATE INDEX idx_presentation_id_bien
ON real_estate.presentation(id_bien);

CREATE INDEX idx_document_id_bien
ON real_estate.document(id_bien);
```

---

# 18. Index métier candidats

Les recherches immobilières peuvent utiliser :

```text
ville
type_bien
prix
surface
```

Candidats :

```sql
CREATE INDEX idx_bien_ville
ON real_estate.bien(ville);

CREATE INDEX idx_bien_type
ON real_estate.bien(type_bien);
```

Cependant, les index :

```text
prix
surface
composite indexes
```

seront ajoutés après mesure avec :

```sql
EXPLAIN ANALYZE
```

dans BC05 / C2.

---

# 19. Pourquoi ne pas indexer toutes les colonnes

Chaque index :

- consomme du disque ;
- consomme de la mémoire ;
- ralentit les écritures ;
- doit être maintenu.

Le projet applique :

```text
Query
 |
 v
Measure
 |
 v
Index
```

et non :

```text
Index Everything
```

---

# 20. Index actif de demande

Le partial index :

```sql
CREATE UNIQUE INDEX uq_demande_version_active
ON real_estate.demande_version(id_mandat)
WHERE active = TRUE;
```

a deux rôles :

```text
Integrity
+
Performance
```

---

# 21. Recherche immobilière cible

Exemple de requête fréquente :

```sql
SELECT
    id_bien,
    titre,
    ville,
    prix,
    surface,
    nb_pieces
FROM real_estate.bien
WHERE statut = 'ACTIF'
  AND ville = 'Montpellier'
  AND prix <= 350000
  AND surface >= 70;
```

Cette requête sera utilisée plus tard comme candidat pour l'étude d'optimisation.

---

# 22. Index composite candidat

Après mesure, un index possible pourrait être :

```sql
CREATE INDEX idx_bien_search
ON real_estate.bien(ville, statut, prix, surface);
```

Mais cet index **n'est pas encore adopté**.

Il doit être justifié par :

```text
EXPLAIN ANALYZE before
vs
EXPLAIN ANALYZE after
```

---

# 23. Search normalization

Les valeurs telles que :

```text
Montpellier
MONTPELLIER
montpellier
```

peuvent poser problème.

Une stratégie future peut utiliser :

```sql
LOWER(ville)
```

ou une normalisation à l'ingestion.

Le MPD initial ne crée pas encore d'index fonctionnel.

---

# 24. Timestamps

Le projet utilise :

```text
TIMESTAMPTZ
```

pour les événements nécessitant un instant précis.

Exemples :

```text
date_creation
date_version
date_collecte
date_selection
date_ajout
```

---

# 25. DATE

Les dates purement métier peuvent rester :

```text
DATE
```

Exemples :

```text
date_signature
date_debut
date_fin
date_entree
```

---

# 26. Nullability — scores

Les scores de présentation sont :

```text
NULL
```

avant exécution du matching.

Après matching, ils peuvent être renseignés.

Cela distingue :

```text
not calculated
```

de :

```text
score = 0
```

---

# 27. Nullability — données BIEN

Certaines sources peuvent ne pas fournir toutes les informations.

Exemple :

```text
latitude
longitude
surface
nb_chambres
```

peuvent être null.

Cela reflète la qualité réelle des sources.

---

# 28. Données personnelles

Les colonnes suivantes sont particulièrement sensibles :

```text
client.nom
client.prenom
client.email
client.telephone

chasseur.nom
chasseur.prenom
chasseur.email
chasseur.telephone

presentation.feedback_client
presentation.commentaire_chasseur
```

Ces éléments devront être classifiés dans OpenMetadata.

---

# 29. RAG / documents

Le MPD stocke :

```text
metadata document
```

mais pas nécessairement :

```text
file binary
```

Le fichier peut être stocké dans :

```text
MinIO / Object Storage
```

avec :

```text
chemin_stockage
```

comme référence.

---

# 30. Séparation metadata / binary

Architecture :

```text
PostgreSQL
   |
   +--> Document metadata

Object Storage
   |
   +--> Binary content
```

Cette séparation évite de transformer PostgreSQL en stockage binaire général sans nécessité.

---

# 31. Checksum

Le `checksum` permet éventuellement :

- détection de corruption ;
- détection de doublons ;
- validation d'intégrité.

Le format exact dépendra de l'algorithme retenu.

---

# 32. Search Vector future

Une évolution RAG peut nécessiter :

```text
embedding
```

Le MPD métier initial ne stocke pas encore les vecteurs.

Les candidats restent :

```text
pgvector
Qdrant
```

Ils seront ajoutés seulement après décision.

---

# 33. Audit fields

Le MPD initial conserve uniquement les timestamps métier nécessaires.

Une évolution peut ajouter :

```text
updated_at
created_by
updated_by
```

si les exigences d'audit l'imposent.

---

# 34. Soft Delete

Le modèle préfère actuellement les statuts métier :

```text
ACTIF
INACTIF
ARCHIVE
ANNULE
EXPIRE
```

plutôt qu'un :

```text
deleted = true
```

générique.

---

# 35. ON DELETE

Le choix principal est :

```text
ON DELETE RESTRICT
```

afin d'éviter la destruction accidentelle de l'historique.

La suppression métier normale doit être gérée par :

```text
status
```

---

# 36. Transactions

Les opérations multi-tables importantes doivent pouvoir utiliser une transaction.

Exemple :

```text
Create mandate
+
Create first request version
```

dans une même unité logique.

---

# 37. Exemple transaction métier

```sql
BEGIN;

INSERT INTO real_estate.mandat (...);

INSERT INTO real_estate.demande_version (...);

COMMIT;
```

Le code applicatif devra récupérer correctement l'identifiant du mandat.

---

# 38. Isolation

PostgreSQL utilise par défaut :

```text
READ COMMITTED
```

Cela est suffisant pour le MVP sauf besoin concurrent spécifique.

---

# 39. Database roles — cible

Une évolution peut introduire :

```text
real_estate_app
real_estate_readonly
real_estate_etl
real_estate_admin
```

selon les responsabilités.

---

# 40. Least privilege

Exemple :

```text
Application account
```

ne doit pas nécessairement disposer de :

```text
DROP TABLE
CREATE ROLE
SUPERUSER
```

---

# 41. Search Path

L'application peut utiliser explicitement :

```text
real_estate.table
```

afin d'éviter les ambiguïtés de `search_path`.

---

# 42. Migration order

Le futur `migration.sql` doit utiliser l'ordre :

```text
CREATE SCHEMA

CLIENT
CHASSEUR
SOURCE

MANDAT

DEMANDE_VERSION

BIEN

PRESENTATION

DOCUMENT

INDEXES
```

---

# 43. Transaction migration

Le script initial utilisera :

```sql
BEGIN;
...
COMMIT;
```

afin de garantir une migration atomique si toutes les instructions sont transactionnelles.

---

# 44. Comments PostgreSQL

Nous pourrons également ajouter :

```sql
COMMENT ON TABLE ...
COMMENT ON COLUMN ...
```

pour améliorer la documentation technique.

Ce n'est pas obligatoire pour la migration V1.

---

# 45. Validation MPD

Le MPD doit être validé à plusieurs niveaux :

```text
Syntax
Schema
Constraints
Foreign Keys
Business Rules
Sample Inserts
Invalid Inserts
```

---

# 46. Validation schema

Après migration :

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'real_estate'
ORDER BY table_name;
```

Résultat attendu :

```text
bien
chasseur
client
demande_version
document
mandat
presentation
source
```

---

# 47. Validation PK / FK

Les contraintes peuvent être vérifiées via :

```sql
SELECT
    conname,
    contype,
    conrelid::regclass
FROM pg_constraint
WHERE connamespace = 'real_estate'::regnamespace
ORDER BY conrelid::regclass::text, conname;
```

---

# 48. Validation indexes

```sql
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'real_estate'
ORDER BY tablename, indexname;
```

---

# 49. Validation version active

Le test doit montrer que deux versions actives du même mandat sont interdites.

```text
Version 1 active = true
Version 2 active = true
```

Résultat attendu :

```text
UNIQUE violation
```

---

# 50. Validation presentation duplicate

Pour un même couple :

```text
demande_version + bien
```

une seconde présentation doit être rejetée.

---

# 51. Validation score

Test :

```text
score_matching = 120
```

Résultat attendu :

```text
CHECK constraint violation
```

---

# 52. Validation budget

Test :

```text
budget_min = 400000
budget_max = 300000
```

Résultat :

```text
CHECK constraint violation
```

---

# 53. Validation coordinate

Test :

```text
latitude = 190
```

Résultat :

```text
CHECK constraint violation
```

---

# 54. Dataset de démonstration

La migration initiale ne doit pas mélanger :

```text
schema creation
```

et :

```text
business demo data
```

La structure recommandée est :

```text
migration.sql
seed.sql
tests.sql
```

---

# 55. migration.sql

Responsable de :

```text
Schema
Tables
Constraints
Indexes
```

---

# 56. seed.sql

Responsable de données de démonstration.

Exemple :

```text
1 client
1 chasseur
1 mandat
2 versions de demande
1 source
several properties
presentations
documents
```

---

# 57. tests.sql

Responsable des contrôles SQL démontrables.

Exemples :

```text
schema checks
row counts
business queries
```

Les tests invalides provoquant volontairement des erreurs peuvent être exécutés séparément.

---

# 58. MPD résumé

```text
real_estate
│
├── client
├── chasseur
├── source
├── mandat
├── demande_version
├── bien
├── presentation
└── document
```

---

# 59. Dépendances

```text
client
   |
   v
mandat
   ^
   |
chasseur


mandat
   |
   v
demande_version


source
  |
  v
bien


demande_version
      |
      v
presentation
      ^
      |
     bien


bien
 |
 v
document
```

---

# 60. Critère de réussite

Le MPD est valide si :

```text
MCD business semantics preserved
+
MLD relationships preserved
+
PostgreSQL constraints enforce key rules
+
schema remains usable by application
```

---

# 61. Statut

| Élément | Statut |
|---|---|
| PostgreSQL schema | DEFINED |
| Tables | DEFINED |
| PK | DEFINED |
| FK | DEFINED |
| CHECK | DEFINED |
| UNIQUE | DEFINED |
| Partial unique index | DEFINED |
| Basic FK indexes | DEFINED |
| Search index candidates | IDENTIFIED |
| Data types | DEFINED |
| RGPD considerations | DOCUMENTED |
| RAG document support | DOCUMENTED |
| migration.sql | NEXT |
| seed.sql | AFTER MIGRATION |
| SQL validation | AFTER EXECUTION |

---

# 62. Conclusion

Le MPD PostgreSQL traduit le MLD en huit tables métier dans le schéma :

```text
real_estate
```

avec :

```text
referential integrity
business constraints
history preservation
matching traceability
document governance
```

La structure est maintenant suffisamment détaillée pour produire un `migration.sql` exécutable sans inventer de nouvelles règles métier.

---

**MPD PostgreSQL V1 — READY FOR MIGRATION.SQL**