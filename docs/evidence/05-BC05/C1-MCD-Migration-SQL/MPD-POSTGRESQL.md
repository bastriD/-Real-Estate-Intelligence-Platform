# MPD PostgreSQL — Real Estate Intelligence Platform

**Projet :** PROJECT_FIL_ROUGE / CHASSE_IMMOBILIERE
**SGBD :** PostgreSQL 16
**Schéma OLTP :** `real_estate`
**Version documentaire :** 3.0
**Périmètre :** migrations `001` à `012`
**Source logique :** `MLD-PROJET.md` V3
**Statut :** aligné avec le schéma PostgreSQL déployé
**Dernière mise à jour :** 2026-09-15

---

# 1. Objectif

Ce document décrit le **Modèle Physique de Données PostgreSQL** actuellement déployé pour le domaine `real_estate`.

La chaîne de conception est :

```text id="ez4b1g"
Besoins métier
      |
      v
MCD V3
      |
      v
MLD V3
      |
      v
MPD PostgreSQL V3
      |
      v
Migrations SQL 001 -> 012
      |
      v
PostgreSQL runtime
```

Contrairement aux versions documentaires précédentes, ce document ne décrit pas un modèle cible hypothétique.

Il représente le schéma physique réellement observé dans PostgreSQL.

---

# 2. Runtime de référence

Le modèle est déployé dans :

```text id="pvbyjm"
PostgreSQL 16
Database : real_estate
Schema   : real_estate
```

Le schéma OLTP contient actuellement :

```text id="48w1dc"
23 tables
248 colonnes
```

Les migrations connues sont :

```text id="fz8a6h"
001_initial_schema.sql
002_migrate_legacy_data.sql
003_warehouse_schema.sql
004_add_visite_audit.sql
005_demande_pre_mandat.sql
006_auth_identity.sql
007_demande_chasseur_affectation.sql
008_mandat_lifecycle.sql
009_mandat_lifecycle_warehouse.sql
010_transaction_remuneration.sql
011_initial_remuneration_configuration.sql
012_chasseur_entry_date_backfill.sql
```

---

# 3. Inventaire physique

Les tables actuellement présentes dans `real_estate` sont :

```text id="k8q8nm"
audit_log
bareme_commission
bien
chasseur
client
commentaire
demande
demande_affectation
demande_version
document
mandat
mandat_periode
mandat_secteur
paiement
palier_performance
parametres_honoraires
parametres_remuneration
presentation
secteur
source
utilisateur
vente
visite
```

---

# 4. Convention de lecture

Les abréviations utilisées sont :

```text id="l5dwr1"
PK = Primary Key
FK = Foreign Key
UQ = Unique Constraint
CK = Check Constraint
NN = NOT NULL
```

Les colonnes marquées `NULL` sont physiquement optionnelles.

Les types présentés correspondent aux types observés dans PostgreSQL.

---

# 5. real_estate.client

```text id="xkzx52"
client
```

| Colonne              | Type PostgreSQL | Null | Défaut            |
| -------------------- | --------------- | ---- | ----------------- |
| id_client            | BIGINT          | NON  | —                 |
| nom                  | VARCHAR         | NON  | —                 |
| prenom               | VARCHAR         | OUI  | —                 |
| email                | VARCHAR         | NON  | —                 |
| telephone            | VARCHAR         | OUI  | —                 |
| ville                | VARCHAR         | OUI  | —                 |
| date_creation        | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |
| statut               | VARCHAR         | NON  | `'ACTIF'`         |
| consentement_contact | BOOLEAN         | NON  | `false`           |

Contraintes :

```text id="ugjtzx"
PK pk_client
    (id_client)

UQ uq_client_email
    (email)

CK ck_client_statut
    statut IN ('ACTIF', 'INACTIF', 'ARCHIVE')
```

---

# 6. real_estate.chasseur

| Colonne     | Type PostgreSQL | Null | Défaut    |
| ----------- | --------------- | ---- | --------- |
| id_chasseur | BIGINT          | NON  | —         |
| nom         | VARCHAR         | NON  | —         |
| prenom      | VARCHAR         | OUI  | —         |
| email       | VARCHAR         | NON  | —         |
| telephone   | VARCHAR         | OUI  | —         |
| date_entree | DATE            | OUI  | —         |
| statut      | VARCHAR         | NON  | `'ACTIF'` |

Contraintes :

```text id="mqlt8s"
PK pk_chasseur
    (id_chasseur)

UQ uq_chasseur_email
    (email)

CK ck_chasseur_statut
    statut IN ('ACTIF', 'INACTIF')
```

`date_entree` a été ajoutée au modèle de rémunération et complétée pour les données historiques par la migration 012 lorsque la donnée source le permettait selon la stratégie documentée.

---

# 7. real_estate.utilisateur

| Colonne            | Type PostgreSQL | Null | Défaut            |
| ------------------ | --------------- | ---- | ----------------- |
| id_utilisateur     | BIGINT          | NON  | —                 |
| email              | VARCHAR         | NON  | —                 |
| password_hash      | VARCHAR         | NON  | —                 |
| role               | VARCHAR         | NON  | —                 |
| actif              | BOOLEAN         | NON  | `true`            |
| id_client          | BIGINT          | OUI  | —                 |
| id_chasseur        | BIGINT          | OUI  | —                 |
| derniere_connexion | TIMESTAMPTZ     | OUI  | —                 |
| date_creation      | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |
| date_modification  | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |

Contraintes :

```text id="d8op1q"
PK utilisateur_pkey
    (id_utilisateur)

FK fk_utilisateur_client
    id_client
    -> real_estate.client(id_client)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT

FK fk_utilisateur_chasseur
    id_chasseur
    -> real_estate.chasseur(id_chasseur)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT
```

Rôles autorisés :

```text id="ol0rdk"
ADMIN
CLIENT
CHASSEUR
SERVICE
```

Contrainte d’identité :

```text id="ylqez9"
CLIENT
    => id_client IS NOT NULL
       AND id_chasseur IS NULL

CHASSEUR
    => id_chasseur IS NOT NULL
       AND id_client IS NULL

ADMIN / SERVICE
    => id_client IS NULL
       AND id_chasseur IS NULL
```

Autres contrôles :

```text id="akpclo"
email normalisé
présence de '@'
longueur email <= 255

password_hash non vide
longueur minimale physique >= 20
```

---

# 8. real_estate.secteur

| Colonne     | Type PostgreSQL | Null | Défaut     |
| ----------- | --------------- | ---- | ---------- |
| id_secteur  | BIGINT          | NON  | —          |
| pays        | VARCHAR         | NON  | `'France'` |
| ville       | VARCHAR         | NON  | —          |
| quartier    | VARCHAR         | OUI  | —          |
| code_postal | VARCHAR         | OUI  | —          |
| actif       | BOOLEAN         | NON  | `true`     |

Contraintes :

```text id="w8a9lq"
PK pk_secteur
    (id_secteur)

UQ uq_secteur_localisation
    (pays, ville, quartier, code_postal)
```

---

# 9. real_estate.mandat

| Colonne          | Type PostgreSQL | Null | Défaut    |
| ---------------- | --------------- | ---- | --------- |
| id_mandat        | BIGINT          | NON  | —         |
| reference_mandat | VARCHAR         | NON  | —         |
| type_mandat      | VARCHAR         | NON  | —         |
| date_signature   | DATE            | NON  | —         |
| mode_signature   | VARCHAR         | NON  | —         |
| date_debut       | DATE            | NON  | —         |
| date_fin         | DATE            | NON  | —         |
| statut           | VARCHAR         | NON  | `'ACTIF'` |
| commentaire      | TEXT            | OUI  | —         |
| id_client        | BIGINT          | NON  | —         |
| id_chasseur      | BIGINT          | NON  | —         |

Contraintes :

```text id="hwac8j"
PK pk_mandat
    (id_mandat)

UQ uq_mandat_reference
    (reference_mandat)

FK fk_mandat_client
    id_client
    -> real_estate.client(id_client)
    ON DELETE RESTRICT

FK fk_mandat_chasseur
    id_chasseur
    -> real_estate.chasseur(id_chasseur)
    ON DELETE RESTRICT
```

Types :

```text id="1i2ikv"
EXCLUSIF
NON_EXCLUSIF
```

Modes de signature :

```text id="o20a4g"
PAPIER
ELECTRONIQUE
AUTRE
INCONNU
```

Statuts :

```text id="j1fs51"
BROUILLON
ACTIF
SUSPENDU
TERMINE
EXPIRE
ANNULE
```

Contrainte temporelle :

```text id="qx0ohd"
date_fin >= date_debut
```

---

# 10. real_estate.mandat_secteur

| Colonne    | Type PostgreSQL | Null |
| ---------- | --------------- | ---- |
| id_mandat  | BIGINT          | NON  |
| id_secteur | BIGINT          | NON  |

Contraintes :

```text id="7rptwf"
PK pk_mandat_secteur
    (id_mandat, id_secteur)

FK fk_mandat_secteur_mandat
    id_mandat
    -> real_estate.mandat(id_mandat)
    ON DELETE CASCADE

FK fk_mandat_secteur_secteur
    id_secteur
    -> real_estate.secteur(id_secteur)
    ON DELETE RESTRICT
```

---

# 11. real_estate.mandat_periode

| Colonne               | Type PostgreSQL | Null | Défaut            |
| --------------------- | --------------- | ---- | ----------------- |
| id_mandat_periode     | BIGINT          | NON  | —                 |
| id_mandat             | BIGINT          | NON  | —                 |
| numero_periode        | INTEGER         | NON  | —                 |
| type_periode          | VARCHAR         | NON  | —                 |
| date_debut            | DATE            | NON  | —                 |
| date_fin              | DATE            | NON  | —                 |
| date_renouvellement   | DATE            | OUI  | —                 |
| commentaire           | TEXT            | OUI  | —                 |
| est_historique_legacy | BOOLEAN         | NON  | `false`           |
| created_at            | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |

Contraintes :

```text id="08r3h8"
PK pk_mandat_periode
    (id_mandat_periode)

UQ uq_mandat_periode_numero
    (id_mandat, numero_periode)

FK fk_mandat_periode_mandat
    id_mandat
    -> real_estate.mandat(id_mandat)
    ON DELETE CASCADE
```

Règles :

```text id="al5ovq"
numero_periode >= 1

date_fin >= date_debut
```

Types :

```text id="gwlf7d"
INITIAL
RENOUVELLEMENT
```

Durée contractuelle :

```text id="l61djf"
est_historique_legacy = TRUE

OR

date_fin =
(date_debut + INTERVAL '6 months')::date
```

Renouvellement :

```text id="wkt2fx"
INITIAL
    => date_renouvellement IS NULL

RENOUVELLEMENT
    => date_renouvellement IS NOT NULL
```

Cette contrainte matérialise physiquement le cycle contractuel de six mois.

---

# 12. real_estate.demande

| Colonne           | Type PostgreSQL | Null | Défaut            |
| ----------------- | --------------- | ---- | ----------------- |
| id_demande        | BIGINT          | NON  | —                 |
| reference_demande | VARCHAR         | OUI  | —                 |
| date_creation     | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |
| statut            | VARCHAR         | NON  | `'ACTIVE'`        |
| id_mandat         | BIGINT          | OUI  | —                 |
| origine           | VARCHAR         | NON  | `'API'`           |

Contraintes :

```text id="y5vdzc"
PK pk_demande
    (id_demande)

UQ uq_demande_reference
    (reference_demande)

FK fk_demande_mandat
    id_mandat
    -> real_estate.mandat(id_mandat)
    ON DELETE RESTRICT
```

Statuts :

```text id="x83dxn"
ACTIVE
SUSPENDUE
CLOTUREE
ANNULEE
```

Origines :

```text id="7jlv8w"
LEGACY
GENERATED
API
MANUEL
```

Règle de compatibilité legacy :

```text id="0z8shd"
origine <> 'LEGACY'
OR
id_mandat IS NOT NULL
```

Point physique important :

```text id="jj7vc7"
id_mandat BIGINT NULL
```

Le schéma supporte donc réellement la création d’une demande avant contractualisation.

---

# 13. real_estate.demande_affectation

| Colonne                    | Type PostgreSQL | Null | Défaut            |
| -------------------------- | --------------- | ---- | ----------------- |
| id_affectation             | BIGINT          | NON  | —                 |
| id_demande                 | BIGINT          | NON  | —                 |
| id_chasseur                | BIGINT          | NON  | —                 |
| statut                     | VARCHAR         | NON  | `'ASSIGNEE'`      |
| date_affectation           | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |
| date_decision              | TIMESTAMPTZ     | OUI  | —                 |
| id_utilisateur_affectation | BIGINT          | OUI  | —                 |
| id_utilisateur_decision    | BIGINT          | OUI  | —                 |
| motif_refus                | TEXT            | OUI  | —                 |

Contraintes :

```text id="nnsf5a"
PK pk_demande_affectation
    (id_affectation)

FK fk_demande_affectation_demande
    id_demande
    -> real_estate.demande(id_demande)
    ON DELETE RESTRICT

FK fk_demande_affectation_chasseur
    id_chasseur
    -> real_estate.chasseur(id_chasseur)
    ON DELETE RESTRICT

FK fk_demande_affectation_utilisateur_affectation
    id_utilisateur_affectation
    -> real_estate.utilisateur(id_utilisateur)
    ON DELETE RESTRICT

FK fk_demande_affectation_utilisateur_decision
    id_utilisateur_decision
    -> real_estate.utilisateur(id_utilisateur)
    ON DELETE RESTRICT
```

Statuts :

```text id="rdu17v"
ASSIGNEE
ACCEPTEE
REFUSEE
```

Règles :

```text id="4vzjv1"
date_decision IS NULL
OR
date_decision >= date_affectation
```

```text id="w38x64"
ASSIGNEE
    => date_decision IS NULL
       AND id_utilisateur_decision IS NULL

ACCEPTEE / REFUSEE
    => date_decision IS NOT NULL
```

```text id="wb5q9e"
statut <> 'REFUSEE'
    => motif_refus IS NULL
```

---

# 14. real_estate.demande_version

| Colonne                      | Type PostgreSQL | Null | Défaut            |
| ---------------------------- | --------------- | ---- | ----------------- |
| id_demande_version           | BIGINT          | NON  | —                 |
| numero_version               | INTEGER         | NON  | —                 |
| date_version                 | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |
| motif_modification           | TEXT            | NON  | —                 |
| ville                        | VARCHAR         | OUI  | —                 |
| code_postal                  | VARCHAR         | OUI  | —                 |
| type_bien                    | VARCHAR         | OUI  | —                 |
| budget_min                   | NUMERIC         | OUI  | —                 |
| budget_max                   | NUMERIC         | OUI  | —                 |
| surface_min                  | NUMERIC         | OUI  | —                 |
| nb_pieces_min                | INTEGER         | OUI  | —                 |
| nb_chambres_min              | INTEGER         | OUI  | —                 |
| dpe_max                      | CHAR            | OUI  | —                 |
| criteres_souhaites           | JSONB           | NON  | `'[]'::jsonb`     |
| description_recherche_legacy | TEXT            | OUI  | —                 |
| active                       | BOOLEAN         | NON  | `true`            |
| id_demande                   | BIGINT          | NON  | —                 |
| auteur_client_id             | BIGINT          | OUI  | —                 |
| auteur_chasseur_id           | BIGINT          | OUI  | —                 |
| auteur_systeme               | BOOLEAN         | NON  | `false`           |
| source_recherche_ref         | VARCHAR         | OUI  | —                 |
| ingestion_batch              | TEXT            | OUI  | —                 |

Contraintes :

```text id="z4rpp5"
PK pk_demande_version
    (id_demande_version)

UQ uq_demande_version_numero
    (id_demande, numero_version)

FK fk_demande_version_demande
    id_demande
    -> real_estate.demande(id_demande)
    ON DELETE RESTRICT

FK fk_demande_version_client
    auteur_client_id
    -> real_estate.client(id_client)
    ON DELETE RESTRICT

FK fk_demande_version_chasseur
    auteur_chasseur_id
    -> real_estate.chasseur(id_chasseur)
    ON DELETE RESTRICT
```

Règle d’auteur :

```text id="by7rrv"
(
    auteur_client_id IS NOT NULL
)
+
(
    auteur_chasseur_id IS NOT NULL
)
+
(
    auteur_systeme = TRUE
)
= 1
```

Ainsi exactement un auteur logique est autorisé.

Autres contrôles :

```text id="whtddn"
numero_version > 0

budget_min >= 0
budget_max >= 0

budget_min <= budget_max

surface_min >= 0

nb_pieces_min >= 0
nb_chambres_min >= 0

dpe_max IN ('A','B','C','D','E','F','G')
```

---

# 15. real_estate.source

| Colonne          | Type PostgreSQL | Null | Défaut            |
| ---------------- | --------------- | ---- | ----------------- |
| id_source        | BIGINT          | NON  | —                 |
| nom              | VARCHAR         | NON  | —                 |
| type_source      | VARCHAR         | NON  | —                 |
| url_base         | TEXT            | OUI  | —                 |
| actif            | BOOLEAN         | NON  | `true`            |
| niveau_confiance | VARCHAR         | OUI  | —                 |
| date_creation    | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |

Contraintes :

```text id="cb72tz"
PK pk_source
    (id_source)
```

Types :

```text id="xrcw92"
AGENCE
PARTICULIER
PLATEFORME
API
OPEN_DATA
MANUEL
AUTRE
```

Confiance :

```text id="x8f7eu"
FAIBLE
MOYEN
ELEVE
```

---

# 16. real_estate.bien

| Colonne           | Type PostgreSQL | Null | Défaut            |
| ----------------- | --------------- | ---- | ----------------- |
| id_bien           | BIGINT          | NON  | —                 |
| reference_externe | VARCHAR         | NON  | —                 |
| type_bien         | VARCHAR         | NON  | —                 |
| titre             | VARCHAR         | OUI  | —                 |
| adresse           | TEXT            | OUI  | —                 |
| code_postal       | VARCHAR         | OUI  | —                 |
| ville             | VARCHAR         | OUI  | —                 |
| latitude          | NUMERIC         | OUI  | —                 |
| longitude         | NUMERIC         | OUI  | —                 |
| prix              | NUMERIC         | OUI  | —                 |
| surface           | NUMERIC         | OUI  | —                 |
| nb_pieces         | INTEGER         | OUI  | —                 |
| nb_chambres       | INTEGER         | OUI  | —                 |
| dpe               | CHAR            | OUI  | —                 |
| description       | TEXT            | OUI  | —                 |
| date_publication  | TIMESTAMPTZ     | OUI  | —                 |
| date_collecte     | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |
| statut            | VARCHAR         | NON  | `'ACTIF'`         |
| id_source         | BIGINT          | NON  | —                 |

Contraintes :

```text id="51gf6k"
PK pk_bien
    (id_bien)

UQ uq_bien_source_reference
    (id_source, reference_externe)

FK fk_bien_source
    id_source
    -> real_estate.source(id_source)
    ON DELETE RESTRICT
```

Contrôles :

```text id="ns1epq"
prix IS NULL OR prix >= 0

surface IS NULL OR surface >= 0

nb_pieces IS NULL OR nb_pieces >= 0

nb_chambres IS NULL OR nb_chambres >= 0

latitude IS NULL
OR latitude BETWEEN -90 AND 90

longitude IS NULL
OR longitude BETWEEN -180 AND 180
```

DPE :

```text id="1w3n02"
A..G
```

Statuts :

```text id="jxbw21"
ACTIF
EXPIRE
VENDU
INDISPONIBLE
```

---

# 17. real_estate.presentation

| Colonne            | Type PostgreSQL | Null | Défaut            |
| ------------------ | --------------- | ---- | ----------------- |
| id_presentation    | BIGINT          | NON  | —                 |
| date_selection     | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |
| date_presentation  | TIMESTAMPTZ     | OUI  | —                 |
| score_matching     | NUMERIC         | OUI  | —                 |
| statut             | VARCHAR         | NON  | `'IDENTIFIE'`     |
| id_demande_version | BIGINT          | NON  | —                 |
| id_bien            | BIGINT          | NON  | —                 |

Contraintes :

```text id="0axmpd"
PK pk_presentation
    (id_presentation)

UQ uq_presentation_demande_bien
    (id_demande_version, id_bien)

FK fk_presentation_demande_version
    id_demande_version
    -> real_estate.demande_version(id_demande_version)
    ON DELETE RESTRICT

FK fk_presentation_bien
    id_bien
    -> real_estate.bien(id_bien)
    ON DELETE RESTRICT
```

Score :

```text id="ixw9fe"
score_matching IS NULL
OR
score_matching BETWEEN 0 AND 100
```

Statuts :

```text id="9wq25b"
IDENTIFIE
QUALIFIE
PRESENTE
REJETE
VISITE
RETENU
```

---

# 18. real_estate.commentaire

| Colonne            | Type PostgreSQL | Null | Défaut            |
| ------------------ | --------------- | ---- | ----------------- |
| id_commentaire     | BIGINT          | NON  | —                 |
| date_commentaire   | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |
| contenu            | TEXT            | NON  | —                 |
| priorite           | SMALLINT        | OUI  | —                 |
| decision           | VARCHAR         | OUI  | —                 |
| id_demande_version | BIGINT          | NON  | —                 |
| id_bien            | BIGINT          | NON  | —                 |
| auteur_client_id   | BIGINT          | OUI  | —                 |
| auteur_chasseur_id | BIGINT          | OUI  | —                 |

Contraintes :

```text id="lf8p5n"
PK pk_commentaire
    (id_commentaire)

FK fk_commentaire_demande_version
    -> real_estate.demande_version(id_demande_version)

FK fk_commentaire_bien
    -> real_estate.bien(id_bien)

FK fk_commentaire_client
    auteur_client_id
    -> real_estate.client(id_client)

FK fk_commentaire_chasseur
    auteur_chasseur_id
    -> real_estate.chasseur(id_chasseur)
```

Toutes les FK utilisent :

```text id="pcow5g"
ON DELETE RESTRICT
```

Exactement un auteur :

```text id="yjvl42"
(auteur_client_id IS NOT NULL)
+
(auteur_chasseur_id IS NOT NULL)
= 1
```

Priorité :

```text id="p8kshb"
1..5
```

Décisions :

```text id="c4e53f"
RETENIR
ECARTER
VISITER
REQUALIFIER
INFORMATION
```

---

# 19. real_estate.document

| Colonne         | Type PostgreSQL | Null | Défaut            |
| --------------- | --------------- | ---- | ----------------- |
| id_document     | BIGINT          | NON  | —                 |
| nom_fichier     | VARCHAR         | NON  | —                 |
| type_document   | VARCHAR         | OUI  | —                 |
| mime_type       | VARCHAR         | OUI  | —                 |
| chemin_stockage | TEXT            | NON  | —                 |
| checksum        | VARCHAR         | OUI  | —                 |
| date_ajout      | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |
| classification  | VARCHAR         | NON  | `'INTERNE'`       |
| indexable_ia    | BOOLEAN         | NON  | `false`           |
| id_bien         | BIGINT          | NON  | —                 |

Contraintes :

```text id="j39tdh"
PK pk_document
    (id_document)

FK fk_document_bien
    id_bien
    -> real_estate.bien(id_bien)
    ON DELETE RESTRICT
```

Classifications :

```text id="53tl9e"
PUBLIC
INTERNE
CONFIDENTIEL
RESTREINT
```

---

# 20. real_estate.visite

| Colonne         | Type PostgreSQL | Null | Défaut            |
| --------------- | --------------- | ---- | ----------------- |
| id_visite       | BIGINT          | NON  | —                 |
| date_visite     | TIMESTAMPTZ     | NON  | —                 |
| statut          | VARCHAR         | NON  | `'PLANIFIEE'`     |
| compte_rendu    | TEXT            | OUI  | —                 |
| note            | SMALLINT        | OUI  | —                 |
| photos          | JSONB           | NON  | `'[]'::jsonb`     |
| date_creation   | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |
| id_presentation | BIGINT          | NON  | —                 |

Contraintes :

```text id="66hyra"
PK pk_visite
    (id_visite)

FK fk_visite_presentation
    id_presentation
    -> real_estate.presentation(id_presentation)
    ON DELETE RESTRICT
```

Statuts :

```text id="7flz32"
PLANIFIEE
REALISEE
ANNULEE
REPORTEE
```

Note :

```text id="f5m1yw"
note IS NULL
OR
note BETWEEN 0 AND 5
```

Photos :

```text id="c9gzom"
jsonb_typeof(photos) = 'array'
```

---

# 21. real_estate.vente

| Colonne                  | Type PostgreSQL | Null | Défaut            |
| ------------------------ | --------------- | ---- | ----------------- |
| id_vente                 | BIGINT          | NON  | —                 |
| id_mandat                | BIGINT          | NON  | —                 |
| id_mandat_periode        | BIGINT          | OUI  | —                 |
| id_presentation          | BIGINT          | OUI  | —                 |
| id_bien                  | BIGINT          | OUI  | —                 |
| id_chasseur_beneficiaire | BIGINT          | OUI  | —                 |
| origine_vente            | VARCHAR         | NON  | —                 |
| date_acte_authentique    | DATE            | NON  | —                 |
| montant_achat            | NUMERIC         | NON  | —                 |
| date_creation            | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |

Contraintes :

```text id="6ggqxb"
PK pk_vente
    (id_vente)

FK fk_vente_mandat
    id_mandat
    -> real_estate.mandat(id_mandat)

FK fk_vente_mandat_periode
    id_mandat_periode
    -> real_estate.mandat_periode(id_mandat_periode)

FK fk_vente_presentation
    id_presentation
    -> real_estate.presentation(id_presentation)

FK fk_vente_bien
    id_bien
    -> real_estate.bien(id_bien)

FK fk_vente_chasseur_beneficiaire
    id_chasseur_beneficiaire
    -> real_estate.chasseur(id_chasseur)
```

Toutes ces FK utilisent :

```text id="d9a1vp"
ON DELETE RESTRICT
```

Origines :

```text id="a5hx3e"
CHASSEUR
CLIENT_SEUL
AUTRE_AGENCE
```

Montant :

```text id="h3jvz9"
montant_achat > 0
```

---

# 22. real_estate.parametres_honoraires

| Colonne                  | Type PostgreSQL | Null | Défaut            |
| ------------------------ | --------------- | ---- | ----------------- |
| id_parametres_honoraires | BIGINT          | NON  | —                 |
| date_debut_validite      | DATE            | NON  | —                 |
| date_fin_validite        | DATE            | OUI  | —                 |
| montant_fixe             | NUMERIC         | NON  | —                 |
| taux_pourcentage         | NUMERIC         | NON  | —                 |
| actif                    | BOOLEAN         | NON  | `true`            |
| date_creation            | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |

Contraintes :

```text id="s1l5iv"
PK pk_parametres_honoraires
    (id_parametres_honoraires)

montant_fixe >= 0

taux_pourcentage BETWEEN 0 AND 1

date_fin_validite IS NULL
OR
date_fin_validite >= date_debut_validite
```

---

# 23. real_estate.bareme_commission

| Colonne             | Type PostgreSQL | Null | Défaut         |
| ------------------- | --------------- | ---- | -------------- |
| id_bareme           | BIGINT          | NON  | —              |
| montant_min         | NUMERIC         | NON  | —              |
| montant_max         | NUMERIC         | OUI  | —              |
| taux_commission     | NUMERIC         | NON  | —              |
| montant_fixe        | NUMERIC         | NON  | `0`            |
| date_debut_validite | DATE            | NON  | —              |
| date_fin_validite   | DATE            | OUI  | —              |
| actif               | BOOLEAN         | NON  | `true`         |
| id_chasseur         | BIGINT          | OUI  | —              |
| statut_usage        | VARCHAR         | NON  | `'HISTORIQUE'` |

Contraintes :

```text id="a7s9ws"
PK pk_bareme_commission
    (id_bareme)

FK fk_bareme_commission_chasseur
    id_chasseur
    -> real_estate.chasseur(id_chasseur)
    ON DELETE RESTRICT
```

Contrôles :

```text id="kv40m1"
montant_min >= 0

montant_max IS NULL
OR
montant_max >= montant_min

taux_commission BETWEEN 0 AND 1

montant_fixe >= 0

date_fin_validite IS NULL
OR
date_fin_validite >= date_debut_validite
```

Statuts d’usage :

```text id="ly4qwp"
HISTORIQUE
APPROUVE
```

---

# 24. real_estate.parametres_remuneration

| Colonne                    | Type PostgreSQL | Null | Défaut            |
| -------------------------- | --------------- | ---- | ----------------- |
| id_parametres_remuneration | BIGINT          | NON  | —                 |
| date_debut_validite        | DATE            | NON  | —                 |
| date_fin_validite          | DATE            | OUI  | —                 |
| fenetre_mois               | INTEGER         | NON  | —                 |
| poids_delai                | NUMERIC         | NON  | —                 |
| poids_exclusivite          | NUMERIC         | NON  | —                 |
| poids_ventes               | NUMERIC         | NON  | —                 |
| poids_mandats              | NUMERIC         | NON  | —                 |
| poids_visites              | NUMERIC         | NON  | —                 |
| note_exclusif              | NUMERIC         | NON  | —                 |
| note_non_exclusif          | NUMERIC         | NON  | —                 |
| points_par_vente           | NUMERIC         | NON  | —                 |
| points_par_mandat          | NUMERIC         | NON  | —                 |
| taux_anciennete_par_annee  | NUMERIC         | NON  | —                 |
| plafond_anciennete         | NUMERIC         | NON  | —                 |
| score_pivot                | NUMERIC         | NON  | —                 |
| amplitude_performance      | NUMERIC         | NON  | —                 |
| taux_plancher              | NUMERIC         | NON  | —                 |
| taux_plafond               | NUMERIC         | NON  | —                 |
| actif                      | BOOLEAN         | NON  | `true`            |
| date_creation              | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |

Contraintes :

```text id="u99u81"
PK pk_parametres_remuneration
    (id_parametres_remuneration)
```

Fenêtre :

```text id="vky01e"
fenetre_mois > 0
```

Somme des poids :

```text id="n9l7n4"
poids_delai
+ poids_exclusivite
+ poids_ventes
+ poids_mandats
+ poids_visites
= 1.000000
```

Notes :

```text id="fvfrt9"
note_exclusif BETWEEN 0 AND 100
note_non_exclusif BETWEEN 0 AND 100
```

Points :

```text id="o0fhcv"
points_par_vente >= 0
points_par_mandat >= 0
```

Ancienneté :

```text id="q4a2pa"
taux_anciennete_par_annee >= 0

plafond_anciennete >= 0
AND
plafond_anciennete <= 1
```

Performance :

```text id="m9yfx5"
score_pivot BETWEEN 0 AND 100

amplitude_performance BETWEEN 0 AND 1
```

Bornes :

```text id="7czqyz"
taux_plancher >= 0

taux_plafond <= 1

taux_plancher <= taux_plafond
```

Validité :

```text id="s3ub1w"
date_fin_validite IS NULL
OR
date_fin_validite >= date_debut_validite
```

---

# 25. real_estate.palier_performance

| Colonne                    | Type PostgreSQL | Null | Défaut |
| -------------------------- | --------------- | ---- | ------ |
| id_palier_performance      | BIGINT          | NON  | —      |
| id_parametres_remuneration | BIGINT          | NON  | —      |
| critere                    | VARCHAR         | NON  | —      |
| ordre                      | INTEGER         | NON  | —      |
| borne_max                  | INTEGER         | OUI  | —      |
| note                       | NUMERIC         | NON  | —      |

Contraintes :

```text id="2c4j7j"
PK pk_palier_performance
    (id_palier_performance)

FK fk_palier_performance_parametres
    id_parametres_remuneration
    -> real_estate.parametres_remuneration(
        id_parametres_remuneration
    )
    ON DELETE RESTRICT

UQ uq_palier_performance_ordre
    (
        id_parametres_remuneration,
        critere,
        ordre
    )
```

Critères :

```text id="egnp3s"
DELAI_SEMAINES
VISITES
```

Contrôles :

```text id="6h2a91"
ordre >= 1

borne_max IS NULL
OR
borne_max >= 0

note BETWEEN 0 AND 100
```

---

# 26. real_estate.paiement

`paiement` est la table physique la plus importante du sous-domaine financier.

Elle conserve simultanément :

```text id="z61fqx"
références métier
+
montants
+
cycle financier
+
configuration utilisée
+
snapshot du calcul
```

## Colonnes

| Colonne                    | Type PostgreSQL | Null | Défaut      |
| -------------------------- | --------------- | ---- | ----------- |
| id_paiement                | BIGINT          | NON  | —           |
| date_acte_authentique      | DATE            | OUI  | —           |
| montant_achat              | NUMERIC         | OUI  | —           |
| montant_honoraires         | NUMERIC         | OUI  | —           |
| montant_chasseur           | NUMERIC         | OUI  | —           |
| date_reception_honoraires  | DATE            | OUI  | —           |
| date_paiement_chasseur     | DATE            | OUI  | —           |
| statut                     | VARCHAR         | NON  | `'ATTENDU'` |
| id_mandat                  | BIGINT          | NON  | —           |
| id_bareme                  | BIGINT          | OUI  | —           |
| id_vente                   | BIGINT          | OUI  | —           |
| id_chasseur_beneficiaire   | BIGINT          | OUI  | —           |
| id_parametres_honoraires   | BIGINT          | OUI  | —           |
| id_parametres_remuneration | BIGINT          | OUI  | —           |
| date_calcul                | TIMESTAMPTZ     | OUI  | —           |
| droit_remuneration         | BOOLEAN         | OUI  | —           |
| motif_refus                | VARCHAR         | OUI  | —           |
| semaines_mandat_acte       | INTEGER         | OUI  | —           |
| nb_visites_calcul          | INTEGER         | OUI  | —           |
| annees_anciennete_calcul   | INTEGER         | OUI  | —           |
| nb_ventes_fenetre          | INTEGER         | OUI  | —           |
| nb_mandats_fenetre         | INTEGER         | OUI  | —           |
| note_delai                 | NUMERIC         | OUI  | —           |
| note_exclusivite           | NUMERIC         | OUI  | —           |
| note_ventes                | NUMERIC         | OUI  | —           |
| note_mandats               | NUMERIC         | OUI  | —           |
| note_visites               | NUMERIC         | OUI  | —           |
| score_performance          | NUMERIC         | OUI  | —           |
| taux_base                  | NUMERIC         | OUI  | —           |
| majoration_anciennete      | NUMERIC         | OUI  | —           |
| modulation_performance     | NUMERIC         | OUI  | —           |
| taux_final                 | NUMERIC         | OUI  | —           |

---

# 27. Clés de paiement

```text id="4wrrxm"
PK pk_paiement
    (id_paiement)
```

Foreign Keys :

```text id="a1nt3p"
FK fk_paiement_mandat
    id_mandat
    -> real_estate.mandat(id_mandat)
    ON DELETE RESTRICT

FK fk_paiement_bareme
    id_bareme
    -> real_estate.bareme_commission(id_bareme)
    ON DELETE RESTRICT

FK fk_paiement_vente
    id_vente
    -> real_estate.vente(id_vente)
    ON DELETE RESTRICT

FK fk_paiement_chasseur_beneficiaire
    id_chasseur_beneficiaire
    -> real_estate.chasseur(id_chasseur)
    ON DELETE RESTRICT

FK fk_paiement_parametres_honoraires
    id_parametres_honoraires
    -> real_estate.parametres_honoraires(
        id_parametres_honoraires
    )
    ON DELETE RESTRICT

FK fk_paiement_parametres_remuneration
    id_parametres_remuneration
    -> real_estate.parametres_remuneration(
        id_parametres_remuneration
    )
    ON DELETE RESTRICT
```

---

# 28. Contraintes financières de paiement

Montants :

```text id="bf03vj"
montant_achat IS NULL
OR
montant_achat >= 0

montant_honoraires IS NULL
OR
montant_honoraires >= 0

montant_chasseur IS NULL
OR
montant_chasseur >= 0
```

Dates :

```text id="fjbc9j"
date_paiement_chasseur IS NULL

OR

date_reception_honoraires IS NULL

OR

date_paiement_chasseur >= date_reception_honoraires
```

---

# 29. Statut de paiement

Valeurs physiques autorisées :

```text id="a9al46"
ATTENDU
RECU
VERIFIE
PROGRAMME
PAYE
ANNULE
```

Le cycle nominal applicatif est :

```text id="sy8x21"
ATTENDU
   |
   v
RECU
   |
   v
VERIFIE
   |
   v
PROGRAMME
   |
   v
PAYE
```

La contrainte PostgreSQL garantit le domaine de valeurs.

Les transitions autorisées sont également contrôlées au niveau applicatif.

---

# 30. Éligibilité de paiement

Contrainte physique :

```text id="y3atn9"
droit_remuneration IS NULL

OR

(
    droit_remuneration = TRUE
    AND motif_refus IS NULL
)

OR

(
    droit_remuneration = FALSE
    AND motif_refus IS NOT NULL
)
```

Motifs autorisés :

```text id="87e7nt"
MANDAT_EXPIRE
HORS_DISPOSITIF
```

---

# 31. Compteurs du calcul

```text id="3ek4me"
nb_visites_calcul >= 0

annees_anciennete_calcul >= 0

nb_ventes_fenetre >= 0

nb_mandats_fenetre >= 0

semaines_mandat_acte >= 0
```

Ces contraintes s’appliquent lorsque les valeurs ne sont pas `NULL`.

---

# 32. Notes de performance

Les colonnes :

```text id="cuzbnk"
note_delai
note_exclusivite
note_ventes
note_mandats
note_visites
score_performance
```

respectent :

```text id="qzffip"
0 <= valeur <= 100
```

lorsqu’elles sont renseignées.

---

# 33. Taux du calcul

Contraintes :

```text id="5k2rra"
0 <= taux_base <= 1

0 <= majoration_anciennete <= 1

-1 <= modulation_performance <= 1

0 <= taux_final <= 1
```

Les valeurs sont conservées dans `paiement` afin de figer le calcul historique.

---

# 34. real_estate.audit_log

| Colonne         | Type PostgreSQL | Null | Défaut            |
| --------------- | --------------- | ---- | ----------------- |
| id_audit        | BIGINT          | NON  | —                 |
| date_evenement  | TIMESTAMPTZ     | NON  | CURRENT_TIMESTAMP |
| schema_name     | VARCHAR         | NON  | `'real_estate'`   |
| table_name      | VARCHAR         | NON  | —                 |
| operation       | VARCHAR         | NON  | —                 |
| record_id       | TEXT            | OUI  | —                 |
| utilisateur     | TEXT            | OUI  | —                 |
| ancienne_valeur | JSONB           | OUI  | —                 |
| nouvelle_valeur | JSONB           | OUI  | —                 |
| contexte        | JSONB           | NON  | `'{}'::jsonb`     |

Contraintes :

```text id="pmx9fk"
PK pk_audit_log
    (id_audit)

operation IN (
    'INSERT',
    'UPDATE',
    'DELETE'
)

jsonb_typeof(contexte) = 'object'
```

Le choix de :

```text id="rj9d1d"
table_name
+
record_id
```

permet un audit transverse sans créer une FK polymorphe impossible à garantir proprement avec le modèle relationnel classique.

---

# 35. Types PostgreSQL structurants

Le MPD utilise notamment :

```text id="5c7wwh"
BIGINT
INTEGER
SMALLINT
NUMERIC
BOOLEAN
DATE
TIMESTAMPTZ
VARCHAR
CHAR
TEXT
JSONB
```

---

# 36. Usage de JSONB

Le modèle utilise `JSONB` uniquement pour les données naturellement semi-structurées.

## DEMANDE_VERSION

```text id="lhh2rv"
criteres_souhaites JSONB
```

Collection de critères complémentaires.

## VISITE

```text id="q0yx0s"
photos JSONB
```

La base impose :

```text id="8x9vpy"
jsonb_typeof(photos) = 'array'
```

## AUDIT_LOG

```text id="wh99up"
ancienne_valeur JSONB
nouvelle_valeur JSONB
contexte JSONB
```

Ces données correspondent naturellement à des snapshots et métadonnées d’audit.

---

# 37. TIMESTAMPTZ

Les événements temporels techniques et métier nécessitant un instant absolu utilisent principalement :

```text id="fyzv4r"
TIMESTAMP WITH TIME ZONE
```

Exemples :

```text id="p85nr3"
date_creation
date_version
date_selection
date_visite
date_evenement
date_calcul
```

Les dates contractuelles ou comptables sans composante horaire utilisent :

```text id="i9txct"
DATE
```

Exemples :

```text id="k7e8kg"
date_signature
date_debut
date_fin
date_acte_authentique
date_reception_honoraires
date_paiement_chasseur
```

---

# 38. Politique référentielle

Le comportement dominant est :

```text id="k27qg5"
ON DELETE RESTRICT
```

Cela protège les historiques métier.

Les suppressions en cascade observées concernent :

```text id="cwxg4p"
MANDAT
    |
    +--> MANDAT_SECTEUR

MANDAT
    |
    +--> MANDAT_PERIODE
```

avec :

```text id="m1a8my"
ON DELETE CASCADE
```

La suppression d’un objet métier référencé par une transaction, une visite, un paiement ou un audit n’est donc pas implicitement propagée.

---

# 39. Graphe physique principal

```text id="ekpypv"
real_estate.client
      |
      +------------------------+
      |                        |
      v                        v
real_estate.demande       real_estate.mandat
      |                        |
      |                        +--> real_estate.mandat_periode
      |                        |
      |                        +--> real_estate.mandat_secteur
      |                                      |
      |                                      v
      |                              real_estate.secteur
      |
      +--> real_estate.demande_affectation
      |             |
      |             v
      |      real_estate.chasseur
      |
      v
real_estate.demande_version
      |
      +--> real_estate.presentation
      |             |
      |             +--> real_estate.bien
      |             |           |
      |             |           +--> real_estate.source
      |             |           |
      |             |           +--> real_estate.document
      |             |
      |             +--> real_estate.visite
      |
      +--> real_estate.commentaire
```

Transaction :

```text id="d1k4yz"
real_estate.mandat
        |
        +---------------------------+
        |                           |
real_estate.mandat_periode          |
                                    |
real_estate.presentation -----------+
                                    |
real_estate.bien -------------------+
                                    |
real_estate.chasseur ---------------+
                                    |
                                    v
                           real_estate.vente
                                    |
                                    v
                         real_estate.paiement
```

Configuration :

```text id="ffaqly"
real_estate.parametres_honoraires -----+
                                       |
real_estate.bareme_commission ----------+
                                       |
real_estate.parametres_remuneration ----+--> real_estate.paiement
              |
              v
real_estate.palier_performance
```

---

# 40. Matrice des clés étrangères

| Table enfant        | Colonne                    | Table parent            |
| ------------------- | -------------------------- | ----------------------- |
| utilisateur         | id_client                  | client                  |
| utilisateur         | id_chasseur                | chasseur                |
| mandat              | id_client                  | client                  |
| mandat              | id_chasseur                | chasseur                |
| mandat_secteur      | id_mandat                  | mandat                  |
| mandat_secteur      | id_secteur                 | secteur                 |
| mandat_periode      | id_mandat                  | mandat                  |
| demande             | id_mandat                  | mandat                  |
| demande_affectation | id_demande                 | demande                 |
| demande_affectation | id_chasseur                | chasseur                |
| demande_affectation | id_utilisateur_affectation | utilisateur             |
| demande_affectation | id_utilisateur_decision    | utilisateur             |
| demande_version     | id_demande                 | demande                 |
| demande_version     | auteur_client_id           | client                  |
| demande_version     | auteur_chasseur_id         | chasseur                |
| bien                | id_source                  | source                  |
| presentation        | id_demande_version         | demande_version         |
| presentation        | id_bien                    | bien                    |
| commentaire         | id_demande_version         | demande_version         |
| commentaire         | id_bien                    | bien                    |
| commentaire         | auteur_client_id           | client                  |
| commentaire         | auteur_chasseur_id         | chasseur                |
| document            | id_bien                    | bien                    |
| visite              | id_presentation            | presentation            |
| vente               | id_mandat                  | mandat                  |
| vente               | id_mandat_periode          | mandat_periode          |
| vente               | id_presentation            | presentation            |
| vente               | id_bien                    | bien                    |
| vente               | id_chasseur_beneficiaire   | chasseur                |
| bareme_commission   | id_chasseur                | chasseur                |
| palier_performance  | id_parametres_remuneration | parametres_remuneration |
| paiement            | id_mandat                  | mandat                  |
| paiement            | id_bareme                  | bareme_commission       |
| paiement            | id_vente                   | vente                   |
| paiement            | id_chasseur_beneficiaire   | chasseur                |
| paiement            | id_parametres_honoraires   | parametres_honoraires   |
| paiement            | id_parametres_remuneration | parametres_remuneration |

---

# 41. Contraintes UNIQUE structurantes

Le runtime contient notamment :

```text id="6cj4i4"
client(email)

chasseur(email)

bien(id_source, reference_externe)

demande(reference_demande)

demande_version(id_demande, numero_version)

mandat(reference_mandat)

mandat_periode(id_mandat, numero_periode)

mandat_secteur(id_mandat, id_secteur)

palier_performance(
    id_parametres_remuneration,
    critere,
    ordre
)

presentation(
    id_demande_version,
    id_bien
)

secteur(
    pays,
    ville,
    quartier,
    code_postal
)
```

---

# 42. Intégrité métier portée par PostgreSQL

Le MPD ne se limite pas aux PK/FK.

PostgreSQL protège également plusieurs invariants métier.

Exemples :

```text id="8sq8nw"
mandat.date_fin >= mandat.date_debut
```

```text id="w11ueq"
mandat_periode
=
6 mois
hors legacy explicitement identifié
```

```text id="1mt4bg"
demande legacy
=> mandat obligatoire
```

```text id="rldbgd"
demande_version
=> exactement un auteur
```

```text id="mrnzbk"
commentaire
=> exactement un auteur
```

```text id="1b4e1j"
vente.montant_achat > 0
```

```text id="n7m9em"
paiement
=> montants non négatifs
```

```text id="50wy4a"
paiement
=> notes entre 0 et 100
```

```text id="alxl7i"
parametres_remuneration
=> somme des poids = 1
```

Cette stratégie évite de dépendre uniquement du code applicatif pour protéger l’intégrité métier.

---

# 43. Calcul financier implémenté

Le modèle physique permet de conserver la chaîne :

```text id="0mkv3j"
VENTE
  |
  v
montant_achat
  |
  v
PARAMETRES_HONORAIRES
  |
  v
montant_honoraires
  |
  v
BAREME_COMMISSION
+
PARAMETRES_REMUNERATION
+
PALIER_PERFORMANCE
+
ancienneté
+
performance
  |
  v
taux_final
  |
  v
montant_chasseur
  |
  v
PAIEMENT
```

Le résultat n’est donc pas seulement calculé en mémoire.

Il est persisté avec les paramètres et indicateurs ayant conduit au résultat.

---

# 44. Exemple runtime contrôlé

Un scénario de validation E2E contrôlé a vérifié notamment :

```text id="4xk58z"
Mandat        : 17
Mandat période: 2
Demande ver.  : 137
Présentation  : 32
Bien          : 16025
Visite        : 6
Vente         : 3
Paiement      : 9
```

Montant d’achat :

```text id="1dp7y0"
300000.00 €
```

Honoraires entreprise :

```text id="ix1h3s"
10500.00 €
```

Taux final chasseur :

```text id="rrt2zu"
0.3752
=
37.52 %
```

Rémunération :

```text id="ofjhhj"
3939.60 €
```

Le paiement a parcouru :

```text id="em4p71"
ATTENDU
-> RECU
-> VERIFIE
-> PROGRAMME
-> PAYE
```

Ce scénario constitue une **preuve de validation contrôlée**, et non une transaction commerciale réelle.

---

# 45. Audit du scénario transactionnel

Les opérations sensibles du scénario contrôlé sont enregistrées dans `audit_log`.

La chaîne auditée comprend notamment :

```text id="yvvds5"
INSERT vente

INSERT calcul / paiement

UPDATE paiement
    ATTENDU -> RECU

UPDATE paiement
    RECU -> VERIFIE

UPDATE paiement
    VERIFIE -> PROGRAMME

UPDATE paiement
    PROGRAMME -> PAYE
```

Le MPD permet ainsi de relier :

```text id="iip2ky"
état métier
+
acteur
+
ancienne valeur
+
nouvelle valeur
+
contexte
```

---

# 46. Relation avec le Data Warehouse

Le schéma `real_estate` constitue la couche OLTP.

Il alimente notamment :

```text id="b96uwq"
warehouse.fact_mandat

warehouse.fact_mandat_periode

warehouse.fact_paiement

warehouse.fact_presentation

warehouse.fact_demande

warehouse.fact_matching
```

Exemple :

```text id="ckd59w"
real_estate.paiement
        |
        v
warehouse.fact_paiement
```

Le scénario contrôlé `paiement.id_paiement = 9` a été propagé dans `fact_paiement` via le pipeline Airflow normal.

---

# 47. OLTP != OLAP

Le schéma physique opérationnel conserve :

```text id="y90mcq"
état métier
relations transactionnelles
intégrité
audit
configuration
snapshots financiers
```

Le Data Warehouse conserve :

```text id="ow5ae6"
faits
dimensions
clés analytiques
agrégations
historique analytique
KPIs
```

Le modèle ne mélange donc pas les responsabilités OLTP et OLAP.

---

# 48. Sécurité physique et logique

Les informations d’authentification sont isolées dans :

```text id="bss9s8"
real_estate.utilisateur
```

Les mots de passe sont stockés sous forme de :

```text id="w1miy4"
password_hash
```

et non en clair.

Les identités métier restent dans :

```text id="47fyqy"
client
chasseur
```

Les contraintes physiques empêchent un utilisateur de représenter simultanément un client et un chasseur.

---

# 49. Données personnelles

Les tables principales contenant des informations personnelles ou potentiellement sensibles comprennent :

```text id="n7z7nl"
client
chasseur
utilisateur
commentaire
document
paiement
audit_log
```

Le modèle analytique ne doit pas recopier sans nécessité l’ensemble de ces attributs.

---

# 50. Migrations et évolution du MPD

L’évolution du modèle est incrémentale.

```text id="93h14s"
001
Initial schema

002
Legacy migration

003
Analytical warehouse

004
Visite + audit

005
Pre-mandate demand + lineage

006
Authentication identity

007
Demand / hunter assignment

008
Mandate lifecycle

009
Mandate lifecycle warehouse

010
Transaction + remuneration foundation

011
Approved remuneration configuration

012
Hunter entry-date backfill
```

Une évolution future du MPD doit passer par une nouvelle migration.

Les migrations existantes ne doivent pas être réécrites après leur application en environnement partagé.

---

# 51. Source de vérité

La hiérarchie utilisée pour ce MPD est :

```text id="y50pru"
1. PostgreSQL runtime
2. migrations SQL
3. tests SQL / applicatifs
4. code source
5. CI
6. GitOps
7. documentation
8. hypothèses
```

En cas de divergence entre une ancienne documentation et le runtime vérifié, le runtime déployé constitue la preuve physique prioritaire.

La documentation doit ensuite être réalignée.

---

# 52. Écarts corrigés par MPD V3

L’ancien `MPD-POSTGRESQL.md` ne constituait pas réellement un MPD.

Il décrivait encore un modèle logique V2 et annonçait :

```text id="u4l0ok"
READY FOR MPD POSTGRESQL V2
```

Le présent document corrige notamment :

```text id="dz4w2e"
types PostgreSQL réels
nullabilité réelle
defaults réels
PK réelles
FK réelles
CHECK réels
UNIQUE réels
JSONB réels
actions référentielles réelles
```

Il ajoute également les structures absentes de l’ancien modèle :

```text id="c8twjf"
audit_log
demande_affectation
mandat_periode
utilisateur
visite
vente
parametres_honoraires
parametres_remuneration
palier_performance
```

et met à jour :

```text id="i3cku4"
demande
demande_version
chasseur
bareme_commission
paiement
```

---

# 53. Concepts non présents physiquement

Les tables suivantes ne sont pas présentes dans le schéma `real_estate` actuellement vérifié :

```text id="0h9r1m"
offre
facture
notaire
renouvellement_mandat
```

Le renouvellement est représenté par :

```text id="q2t2yf"
real_estate.mandat_periode
```

avec :

```text id="ooc3oa"
type_periode = 'RENOUVELLEMENT'
```

L’acte authentique est actuellement porté par :

```text id="zsjq6p"
real_estate.vente.date_acte_authentique
```

---

# 54. Modèle physique synthétique

```text id="ydnhyn"
real_estate
|
+-- client
+-- chasseur
+-- utilisateur
|
+-- secteur
|
+-- mandat
|   +-- mandat_secteur
|   +-- mandat_periode
|
+-- demande
|   +-- demande_affectation
|   +-- demande_version
|
+-- source
+-- bien
|   +-- document
|
+-- presentation
|   +-- visite
|
+-- commentaire
|
+-- vente
|
+-- bareme_commission
+-- parametres_honoraires
+-- parametres_remuneration
|   +-- palier_performance
|
+-- paiement
|
+-- audit_log
```

---

# 55. Statut de validation

| Élément                 | Statut                     |
| ----------------------- | -------------------------- |
| MCD V3                  | COMPLETE                   |
| MLD V3                  | COMPLETE                   |
| 23 tables `real_estate` | RUNTIME VERIFIED           |
| 248 colonnes            | RUNTIME VERIFIED           |
| Types PostgreSQL        | RUNTIME VERIFIED           |
| Nullabilité             | RUNTIME VERIFIED           |
| Defaults                | RUNTIME VERIFIED           |
| PK                      | RUNTIME VERIFIED           |
| FK                      | RUNTIME VERIFIED           |
| UNIQUE                  | RUNTIME VERIFIED           |
| CHECK                   | RUNTIME VERIFIED           |
| Pre-mandate demand      | RUNTIME VERIFIED           |
| Auth identity           | RUNTIME VERIFIED           |
| Demand assignment       | RUNTIME VERIFIED           |
| Mandate lifecycle       | RUNTIME VERIFIED           |
| Six-month periods       | RUNTIME VERIFIED           |
| Visit                   | RUNTIME VERIFIED           |
| Sale                    | RUNTIME VERIFIED           |
| Remuneration foundation | RUNTIME VERIFIED           |
| Payment lifecycle       | RUNTIME VERIFIED           |
| Audit                   | RUNTIME VERIFIED           |
| Payment → warehouse     | RUNTIME VERIFIED           |
| Financial observability | RUNTIME VERIFIED           |
| MPD synchronization     | COMPLETE WITH THIS VERSION |

---

# 56. Conclusion

Le MPD V3 représente désormais le modèle PostgreSQL réellement utilisé par la plateforme.

La chaîne documentaire est alignée :

```text id="g25s8h"
MCD V3
   |
   v
MLD V3
   |
   v
MPD PostgreSQL V3
   |
   v
Migrations 001 -> 012
   |
   v
PostgreSQL 16
   |
   v
Runtime Kubernetes
```

Le modèle physique couvre désormais l’ensemble du parcours opérationnel principal :

```text id="c6sf1c"
CLIENT
  |
  v
DEMANDE
  |
  v
AFFECTATION
  |
  v
DEMANDE_VERSION
  |
  v
MATCHING / PRESENTATION
  |
  v
VISITE
  |
  v
VENTE
  |
  v
REMUNERATION
  |
  v
PAIEMENT
```

avec le contexte contractuel :

```text id="ue4aw3"
MANDAT
  |
  v
MANDAT_PERIODE
```

et les fonctions transverses :

```text id="j5kjrl"
UTILISATEUR
AUDIT_LOG
PARAMETRAGE FINANCIER
```

Les règles structurantes ne reposent pas uniquement sur l’application.

Elles sont également protégées par PostgreSQL grâce aux :

```text id="6r21y7"
PRIMARY KEY
FOREIGN KEY
UNIQUE
CHECK
NOT NULL
DEFAULT
```

Le MPD est ainsi cohérent avec les objectifs du projet :

```text id="o7dgnr"
intégrité
historisation
auditabilité
explicabilité
sécurité
traçabilité
analytics
observabilité
industrialisation
```

---

**MPD POSTGRESQL V3 — RUNTIME ALIGNED THROUGH MIGRATION 012**

**MCD V3 → MLD V3 → MPD V3 : SYNCHRONIZED**
