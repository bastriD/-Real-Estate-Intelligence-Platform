# MPD PostgreSQL — Real Estate Intelligence Platform

**Projet :** Real Estate Intelligence Platform  
**Méthode :** MERISE  
**Version :** 2.0  
**Statut :** Baseline physique corrigée  
**Sources :**
- `MCD-MERISE-PROJET.md` V2
- `MLD-PROJET.md` V2

---

# 1. Objectif

Le Modèle Physique de Données traduit le MLD V2 en structures PostgreSQL directement implémentables.

Chaîne :

```text
Legacy Fixtures
      |
      v
MCD V2
      |
      v
MLD V2
      |
      v
MPD PostgreSQL V2
      |
      v
migration.sql
      |
      v
PostgreSQL
```

Le MPD définit :

- schémas PostgreSQL ;
- tables ;
- colonnes ;
- types ;
- clés primaires ;
- clés étrangères ;
- contraintes ;
- index ;
- règles temporelles ;
- stratégie d'historisation ;
- stratégie de migration.

---

# 2. Schémas PostgreSQL

Le modèle cible sera séparé logiquement.

```text
legacy
real_estate
raw
staging
warehouse
analytics
```

Pour la première migration métier, la priorité est :

```text
real_estate
```

Les données héritées restent dans leur schéma d'origine :

```text
"Fil_Rouge_Depart"
```

---

# 3. Schéma métier cible

```sql
CREATE SCHEMA IF NOT EXISTS real_estate;
```

Les principales tables seront :

```text
real_estate.client
real_estate.chasseur
real_estate.secteur
real_estate.mandat
real_estate.mandat_secteur
real_estate.demande
real_estate.demande_version
real_estate.source
real_estate.bien
real_estate.presentation
real_estate.commentaire
real_estate.document
real_estate.bareme_commission
real_estate.paiement
```

---

# 4. Convention de nommage

Tables :

```text
snake_case
singular
```

Colonnes :

```text
snake_case
```

Contraintes :

```text
pk_<table>
fk_<table>_<reference>
uq_<table>_<columns>
ck_<table>_<rule>
```

Index :

```text
idx_<table>_<columns>
```

---

# 5. Identifiants

Les identifiants utilisent :

```text
BIGINT GENERATED ALWAYS AS IDENTITY
```

Exemple :

```sql
id_client BIGINT GENERATED ALWAYS AS IDENTITY
```

---

# 6. Table client

```sql
CREATE TABLE real_estate.client (
    id_client BIGINT GENERATED ALWAYS AS IDENTITY,

    nom VARCHAR(120) NOT NULL,
    prenom VARCHAR(120),

    email VARCHAR(255) NOT NULL,
    telephone VARCHAR(40),

    ville VARCHAR(120),

    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',

    consentement_contact BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_client
        PRIMARY KEY (id_client),

    CONSTRAINT uq_client_email
        UNIQUE (email),

    CONSTRAINT ck_client_statut
        CHECK (
            statut IN (
                'ACTIF',
                'INACTIF',
                'ARCHIVE'
            )
        )
);
```

---

# 7. Table chasseur

```sql
CREATE TABLE real_estate.chasseur (
    id_chasseur BIGINT GENERATED ALWAYS AS IDENTITY,

    nom VARCHAR(120) NOT NULL,
    prenom VARCHAR(120),

    email VARCHAR(255) NOT NULL,
    telephone VARCHAR(40),

    date_entree DATE,

    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',

    CONSTRAINT pk_chasseur
        PRIMARY KEY (id_chasseur),

    CONSTRAINT uq_chasseur_email
        UNIQUE (email),

    CONSTRAINT ck_chasseur_statut
        CHECK (
            statut IN (
                'ACTIF',
                'INACTIF'
            )
        )
);
```

---

# 8. Table secteur

```sql
CREATE TABLE real_estate.secteur (
    id_secteur BIGINT GENERATED ALWAYS AS IDENTITY,

    pays VARCHAR(100) NOT NULL DEFAULT 'France',

    ville VARCHAR(120) NOT NULL,
    quartier VARCHAR(150),
    code_postal VARCHAR(20),

    actif BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT pk_secteur
        PRIMARY KEY (id_secteur),

    CONSTRAINT uq_secteur_localisation
        UNIQUE (
            pays,
            ville,
            quartier,
            code_postal
        )
);
```

---

# 9. Internationalisation

Le champ :

```text
code_postal
```

reste :

```text
VARCHAR(20)
```

et non :

```text
INTEGER
```

afin de supporter plusieurs pays.

---

# 10. Table mandat

```sql
CREATE TABLE real_estate.mandat (
    id_mandat BIGINT GENERATED ALWAYS AS IDENTITY,

    reference_mandat VARCHAR(80) NOT NULL,

    type_mandat VARCHAR(20) NOT NULL,

    date_signature DATE NOT NULL,
    mode_signature VARCHAR(30) NOT NULL,

    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,

    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',

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

    CONSTRAINT ck_mandat_type
        CHECK (
            type_mandat IN (
                'EXCLUSIF',
                'NON_EXCLUSIF'
            )
        ),

    CONSTRAINT ck_mandat_mode_signature
        CHECK (
            mode_signature IN (
                'PAPIER',
                'ELECTRONIQUE',
                'AUTRE'
            )
        ),

    CONSTRAINT ck_mandat_statut
        CHECK (
            statut IN (
                'BROUILLON',
                'ACTIF',
                'SUSPENDU',
                'TERMINE',
                'EXPIRE',
                'ANNULE'
            )
        ),

    CONSTRAINT ck_mandat_dates
        CHECK (
            date_fin >= date_debut
        )
);
```

---

# 11. Règle six mois

La règle métier impose :

```text
date_fin = date_signature + 6 mois
```

Cette règle doit être contrôlée.

En PostgreSQL :

```sql
CONSTRAINT ck_mandat_duree
CHECK (
    date_fin = (date_signature + INTERVAL '6 months')::date
)
```

Cette contrainte peut être adoptée si le processus métier confirme qu'un mandat initial doit toujours avoir exactement six mois.

---

# 12. Renouvellement mandat

Le renouvellement ne doit pas écraser arbitrairement l'historique.

Deux stratégies sont possibles :

```text
A. nouveau mandat
```

ou :

```text
B. table renouvellement_mandat
```

Pour le MVP, un nouveau mandat référencé peut être utilisé si nécessaire.

---

# 13. Table mandat_secteur

```sql
CREATE TABLE real_estate.mandat_secteur (
    id_mandat BIGINT NOT NULL,
    id_secteur BIGINT NOT NULL,

    CONSTRAINT pk_mandat_secteur
        PRIMARY KEY (
            id_mandat,
            id_secteur
        ),

    CONSTRAINT fk_mandat_secteur_mandat
        FOREIGN KEY (id_mandat)
        REFERENCES real_estate.mandat(id_mandat)
        ON DELETE CASCADE,

    CONSTRAINT fk_mandat_secteur_secteur
        FOREIGN KEY (id_secteur)
        REFERENCES real_estate.secteur(id_secteur)
        ON DELETE RESTRICT
);
```

---

# 14. Pourquoi table associative

Le système hérité possède :

```text
1 mandat -> 1 secteur
```

Le modèle cible autorise :

```text
1 mandat -> plusieurs secteurs
```

ce qui est plus cohérent avec les recherches multi-zones.

---

# 15. Table demande

```sql
CREATE TABLE real_estate.demande (
    id_demande BIGINT GENERATED ALWAYS AS IDENTITY,

    reference_demande VARCHAR(80),

    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    id_mandat BIGINT NOT NULL,

    CONSTRAINT pk_demande
        PRIMARY KEY (id_demande),

    CONSTRAINT uq_demande_reference
        UNIQUE (reference_demande),

    CONSTRAINT fk_demande_mandat
        FOREIGN KEY (id_mandat)
        REFERENCES real_estate.mandat(id_mandat)
        ON DELETE RESTRICT,

    CONSTRAINT ck_demande_statut
        CHECK (
            statut IN (
                'ACTIVE',
                'SUSPENDUE',
                'CLOTUREE',
                'ANNULEE'
            )
        )
);
```

---

# 16. Référence demande

`reference_demande` permet notamment de conserver la référence produite par le générateur StarterPack :

```text
REC-XXXXXXXX
```

si elle est utilisée comme donnée de test.

---

# 17. Stratégie auteur — décision MPD

Nous évitons une colonne polymorphe :

```text
auteur_type
auteur_id
```

car PostgreSQL ne peut pas garantir une vraie FK vers plusieurs tables.

Nous retenons :

```text
auteur_client_id
auteur_chasseur_id
auteur_systeme
```

avec contrainte garantissant un seul auteur logique.

---

# 18. Table demande_version

```sql
CREATE TABLE real_estate.demande_version (
    id_demande_version BIGINT GENERATED ALWAYS AS IDENTITY,

    numero_version INTEGER NOT NULL,

    date_version TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    motif_modification TEXT NOT NULL,

    ville VARCHAR(120),
    code_postal VARCHAR(20),
    type_bien VARCHAR(50),

    budget_min NUMERIC(12,2),
    budget_max NUMERIC(12,2),

    surface_min NUMERIC(10,2),

    nb_pieces_min INTEGER,
    nb_chambres_min INTEGER,

    dpe_max CHAR(1),

    criteres_souhaites JSONB NOT NULL DEFAULT '[]'::jsonb,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    id_demande BIGINT NOT NULL,

    auteur_client_id BIGINT,
    auteur_chasseur_id BIGINT,
    auteur_systeme BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_demande_version
        PRIMARY KEY (id_demande_version),

    CONSTRAINT fk_demande_version_demande
        FOREIGN KEY (id_demande)
        REFERENCES real_estate.demande(id_demande)
        ON DELETE RESTRICT,

    CONSTRAINT fk_demande_version_client
        FOREIGN KEY (auteur_client_id)
        REFERENCES real_estate.client(id_client)
        ON DELETE RESTRICT,

    CONSTRAINT fk_demande_version_chasseur
        FOREIGN KEY (auteur_chasseur_id)
        REFERENCES real_estate.chasseur(id_chasseur)
        ON DELETE RESTRICT,

    CONSTRAINT uq_demande_version_numero
        UNIQUE (
            id_demande,
            numero_version
        ),

    CONSTRAINT ck_demande_version_numero
        CHECK (
            numero_version > 0
        ),

    CONSTRAINT ck_demande_version_auteur
        CHECK (
            (
                CASE
                    WHEN auteur_client_id IS NOT NULL THEN 1
                    ELSE 0
                END
            )
            +
            (
                CASE
                    WHEN auteur_chasseur_id IS NOT NULL THEN 1
                    ELSE 0
                END
            )
            +
            (
                CASE
                    WHEN auteur_systeme THEN 1
                    ELSE 0
                END
            )
            = 1
        ),

    CONSTRAINT ck_demande_version_budget_min
        CHECK (
            budget_min IS NULL
            OR budget_min >= 0
        ),

    CONSTRAINT ck_demande_version_budget_max
        CHECK (
            budget_max IS NULL
            OR budget_max >= 0
        ),

    CONSTRAINT ck_demande_version_budget_range
        CHECK (
            budget_min IS NULL
            OR budget_max IS NULL
            OR budget_min <= budget_max
        ),

    CONSTRAINT ck_demande_version_surface
        CHECK (
            surface_min IS NULL
            OR surface_min >= 0
        ),

    CONSTRAINT ck_demande_version_pieces
        CHECK (
            nb_pieces_min IS NULL
            OR nb_pieces_min >= 0
        ),

    CONSTRAINT ck_demande_version_chambres
        CHECK (
            nb_chambres_min IS NULL
            OR nb_chambres_min >= 0
        ),

    CONSTRAINT ck_demande_version_dpe
        CHECK (
            dpe_max IS NULL
            OR dpe_max IN (
                'A','B','C','D','E','F','G'
            )
        )
);
```

---

# 19. Pourquoi JSONB pour criteres_souhaites

Le générateur StarterPack produit une liste variable de critères tels que :

```text
balcon
jardin
parking
ascenseur
terrasse
cave
vue
calme
lumineux
piscine
```

Pour la première version, `JSONB` fournit :

- flexibilité ;
- compatibilité avec les données générées ;
- conservation de la variété ;
- interrogation possible.

Une normalisation future vers une table dédiée reste possible.

---

# 20. Une seule version active

```sql
CREATE UNIQUE INDEX uq_demande_version_active
ON real_estate.demande_version(id_demande)
WHERE active = TRUE;
```

Cette règle garantit :

```text
maximum one active version
per demande
```

---

# 21. Table source

```sql
CREATE TABLE real_estate.source (
    id_source BIGINT GENERATED ALWAYS AS IDENTITY,

    nom VARCHAR(150) NOT NULL,
    type_source VARCHAR(40) NOT NULL,

    url_base TEXT,

    actif BOOLEAN NOT NULL DEFAULT TRUE,

    niveau_confiance VARCHAR(20),

    date_creation TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_source
        PRIMARY KEY (id_source),

    CONSTRAINT ck_source_type
        CHECK (
            type_source IN (
                'AGENCE',
                'PARTICULIER',
                'PLATEFORME',
                'API',
                'OPEN_DATA',
                'MANUEL',
                'AUTRE'
            )
        ),

    CONSTRAINT ck_source_confiance
        CHECK (
            niveau_confiance IS NULL
            OR niveau_confiance IN (
                'FAIBLE',
                'MOYEN',
                'ELEVE'
            )
        )
);
```

---

# 22. Table bien

```sql
CREATE TABLE real_estate.bien (
    id_bien BIGINT GENERATED ALWAYS AS IDENTITY,

    reference_externe VARCHAR(150) NOT NULL,

    type_bien VARCHAR(50) NOT NULL,
    titre VARCHAR(255),

    adresse TEXT,
    code_postal VARCHAR(20),
    ville VARCHAR(120),

    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),

    prix NUMERIC(12,2),
    surface NUMERIC(10,2),

    nb_pieces INTEGER,
    nb_chambres INTEGER,

    dpe CHAR(1),

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
        UNIQUE (
            id_source,
            reference_externe
        ),

    CONSTRAINT ck_bien_prix
        CHECK (
            prix IS NULL
            OR prix >= 0
        ),

    CONSTRAINT ck_bien_surface
        CHECK (
            surface IS NULL
            OR surface >= 0
        ),

    CONSTRAINT ck_bien_pieces
        CHECK (
            nb_pieces IS NULL
            OR nb_pieces >= 0
        ),

    CONSTRAINT ck_bien_chambres
        CHECK (
            nb_chambres IS NULL
            OR nb_chambres >= 0
        ),

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

    CONSTRAINT ck_bien_dpe
        CHECK (
            dpe IS NULL
            OR dpe IN (
                'A','B','C','D','E','F','G'
            )
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

# 23. RAW vs BIEN

Les annonces générées ne sont pas nécessairement directement compatibles avec `bien`.

Elles passent par :

```text
raw
 |
 v
staging
 |
 v
normalization
 |
 v
real_estate.bien
```

---

# 24. Table presentation

```sql
CREATE TABLE real_estate.presentation (
    id_presentation BIGINT GENERATED ALWAYS AS IDENTITY,

    date_selection TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    date_presentation TIMESTAMPTZ,

    score_matching NUMERIC(5,2),

    statut VARCHAR(20) NOT NULL DEFAULT 'IDENTIFIE',

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
        UNIQUE (
            id_demande_version,
            id_bien
        ),

    CONSTRAINT ck_presentation_score
        CHECK (
            score_matching IS NULL
            OR score_matching BETWEEN 0 AND 100
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

# 25. Auteur commentaire — même stratégie

Comme pour `demande_version`, nous utilisons :

```text
auteur_client_id
auteur_chasseur_id
```

et une contrainte garantissant un auteur unique.

---

# 26. Table commentaire

```sql
CREATE TABLE real_estate.commentaire (
    id_commentaire BIGINT GENERATED ALWAYS AS IDENTITY,

    date_commentaire TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    contenu TEXT NOT NULL,

    priorite SMALLINT,

    decision VARCHAR(20),

    id_demande_version BIGINT NOT NULL,
    id_bien BIGINT NOT NULL,

    auteur_client_id BIGINT,
    auteur_chasseur_id BIGINT,

    CONSTRAINT pk_commentaire
        PRIMARY KEY (id_commentaire),

    CONSTRAINT fk_commentaire_demande_version
        FOREIGN KEY (id_demande_version)
        REFERENCES real_estate.demande_version(id_demande_version)
        ON DELETE RESTRICT,

    CONSTRAINT fk_commentaire_bien
        FOREIGN KEY (id_bien)
        REFERENCES real_estate.bien(id_bien)
        ON DELETE RESTRICT,

    CONSTRAINT fk_commentaire_client
        FOREIGN KEY (auteur_client_id)
        REFERENCES real_estate.client(id_client)
        ON DELETE RESTRICT,

    CONSTRAINT fk_commentaire_chasseur
        FOREIGN KEY (auteur_chasseur_id)
        REFERENCES real_estate.chasseur(id_chasseur)
        ON DELETE RESTRICT,

    CONSTRAINT ck_commentaire_auteur
        CHECK (
            (
                CASE
                    WHEN auteur_client_id IS NOT NULL THEN 1
                    ELSE 0
                END
            )
            +
            (
                CASE
                    WHEN auteur_chasseur_id IS NOT NULL THEN 1
                    ELSE 0
                END
            )
            = 1
        ),

    CONSTRAINT ck_commentaire_priorite
        CHECK (
            priorite IS NULL
            OR priorite BETWEEN 1 AND 5
        ),

    CONSTRAINT ck_commentaire_decision
        CHECK (
            decision IS NULL
            OR decision IN (
                'RETENIR',
                'ECARTER',
                'VISITER',
                'REQUALIFIER',
                'INFORMATION'
            )
        )
);
```

---

# 27. Table document

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

# 28. Table bareme_commission

```sql
CREATE TABLE real_estate.bareme_commission (
    id_bareme BIGINT GENERATED ALWAYS AS IDENTITY,

    montant_min NUMERIC(12,2) NOT NULL,
    montant_max NUMERIC(12,2),

    taux_commission NUMERIC(7,4) NOT NULL,

    montant_fixe NUMERIC(12,2) NOT NULL DEFAULT 0,

    date_debut_validite DATE NOT NULL,
    date_fin_validite DATE,

    actif BOOLEAN NOT NULL DEFAULT TRUE,

    id_chasseur BIGINT NOT NULL,

    CONSTRAINT pk_bareme_commission
        PRIMARY KEY (id_bareme),

    CONSTRAINT fk_bareme_commission_chasseur
        FOREIGN KEY (id_chasseur)
        REFERENCES real_estate.chasseur(id_chasseur)
        ON DELETE RESTRICT,

    CONSTRAINT ck_bareme_montant_min
        CHECK (
            montant_min >= 0
        ),

    CONSTRAINT ck_bareme_montant_max
        CHECK (
            montant_max IS NULL
            OR montant_max >= montant_min
        ),

    CONSTRAINT ck_bareme_taux
        CHECK (
            taux_commission >= 0
            AND taux_commission <= 1
        ),

    CONSTRAINT ck_bareme_montant_fixe
        CHECK (
            montant_fixe >= 0
        ),

    CONSTRAINT ck_bareme_dates
        CHECK (
            date_fin_validite IS NULL
            OR date_fin_validite >= date_debut_validite
        )
);
```

---

# 29. Stockage taux commission

Le taux sera stocké comme ratio.

Exemple :

```text
0.1500
=
15 %
```

et non :

```text
15
```

Cela évite les ambiguïtés.

---

# 30. Tranches ouvertes

`montant_max = NULL` signifie :

```text
pas de borne supérieure
```

Exemple :

```text
500000 -> NULL
```

signifie :

```text
>= 500000
```

---

# 31. Chevauchement de barèmes

Une simple contrainte `CHECK` ne peut pas facilement empêcher tous les chevauchements temporels + montants.

Cette règle peut nécessiter :

- trigger ;
- exclusion constraint ;
- validation applicative.

Pour le MVP, nous documentons la règle et la testerons explicitement.

---

# 32. Table paiement

```sql
CREATE TABLE real_estate.paiement (
    id_paiement BIGINT GENERATED ALWAYS AS IDENTITY,

    date_acte_authentique DATE,

    montant_achat NUMERIC(12,2),

    montant_honoraires NUMERIC(12,2),

    montant_chasseur NUMERIC(12,2),

    date_reception_honoraires DATE,
    date_paiement_chasseur DATE,

    statut VARCHAR(20) NOT NULL DEFAULT 'ATTENDU',

    id_mandat BIGINT NOT NULL,

    id_bareme BIGINT,

    CONSTRAINT pk_paiement
        PRIMARY KEY (id_paiement),

    CONSTRAINT fk_paiement_mandat
        FOREIGN KEY (id_mandat)
        REFERENCES real_estate.mandat(id_mandat)
        ON DELETE RESTRICT,

    CONSTRAINT fk_paiement_bareme
        FOREIGN KEY (id_bareme)
        REFERENCES real_estate.bareme_commission(id_bareme)
        ON DELETE RESTRICT,

    CONSTRAINT ck_paiement_montant_achat
        CHECK (
            montant_achat IS NULL
            OR montant_achat >= 0
        ),

    CONSTRAINT ck_paiement_honoraires
        CHECK (
            montant_honoraires IS NULL
            OR montant_honoraires >= 0
        ),

    CONSTRAINT ck_paiement_chasseur
        CHECK (
            montant_chasseur IS NULL
            OR montant_chasseur >= 0
        ),

    CONSTRAINT ck_paiement_statut
        CHECK (
            statut IN (
                'ATTENDU',
                'RECU',
                'VERIFIE',
                'PROGRAMME',
                'PAYE',
                'ANNULE'
            )
        ),

    CONSTRAINT ck_paiement_dates
        CHECK (
            date_paiement_chasseur IS NULL
            OR date_reception_honoraires IS NULL
            OR date_paiement_chasseur >= date_reception_honoraires
        )
);
```

---

# 33. Pourquoi id_bareme est conservé

Même si le barème peut être retrouvé par date, le paiement conserve explicitement :

```text
id_bareme
```

pour assurer la traçabilité du calcul historique.

---

# 34. Index clés étrangères

```sql
CREATE INDEX idx_mandat_id_client
ON real_estate.mandat(id_client);

CREATE INDEX idx_mandat_id_chasseur
ON real_estate.mandat(id_chasseur);

CREATE INDEX idx_mandat_secteur_id_secteur
ON real_estate.mandat_secteur(id_secteur);

CREATE INDEX idx_demande_id_mandat
ON real_estate.demande(id_mandat);

CREATE INDEX idx_demande_version_id_demande
ON real_estate.demande_version(id_demande);

CREATE INDEX idx_bien_id_source
ON real_estate.bien(id_source);

CREATE INDEX idx_presentation_id_demande_version
ON real_estate.presentation(id_demande_version);

CREATE INDEX idx_presentation_id_bien
ON real_estate.presentation(id_bien);

CREATE INDEX idx_commentaire_id_demande_version
ON real_estate.commentaire(id_demande_version);

CREATE INDEX idx_commentaire_id_bien
ON real_estate.commentaire(id_bien);

CREATE INDEX idx_document_id_bien
ON real_estate.document(id_bien);

CREATE INDEX idx_bareme_id_chasseur
ON real_estate.bareme_commission(id_chasseur);

CREATE INDEX idx_paiement_id_mandat
ON real_estate.paiement(id_mandat);
```

---

# 35. Index de recherche immobilière

Index initiaux :

```sql
CREATE INDEX idx_bien_ville
ON real_estate.bien(ville);

CREATE INDEX idx_bien_type_bien
ON real_estate.bien(type_bien);
```

Les index :

```text
prix
surface
composites
```

seront ajoutés uniquement après benchmark `EXPLAIN ANALYZE`.

---

# 36. Index demandes

```sql
CREATE INDEX idx_demande_version_ville
ON real_estate.demande_version(ville);

CREATE INDEX idx_demande_version_type_bien
ON real_estate.demande_version(type_bien);
```

Ils sont candidats utiles pour les workflows de matching.

---

# 37. JSONB index

Si les critères JSONB sont interrogés régulièrement, un index GIN pourra être évalué :

```sql
CREATE INDEX idx_demande_version_criteres_gin
ON real_estate.demande_version
USING GIN (criteres_souhaites);
```

Il n'est pas obligatoire dans la migration initiale.

---

# 38. Ordre de création

```text
1. schema real_estate

2. client
3. chasseur
4. secteur
5. source

6. mandat
7. mandat_secteur

8. demande
9. demande_version

10. bien

11. presentation
12. commentaire
13. document

14. bareme_commission
15. paiement

16. indexes
```

---

# 39. Migration source

La base héritée reste :

```text
"Fil_Rouge_Depart"
```

avec :

```text
secteurs
utilisateurs
mandats
```

La migration cible ne doit pas effectuer :

```text
DROP
```

sur ce schéma.

---

# 40. Migration client

Concept :

```sql
INSERT INTO real_estate.client (...)
SELECT ...
FROM "Fil_Rouge_Depart".utilisateurs
WHERE role = 'client';
```

---

# 41. Migration chasseur

```sql
INSERT INTO real_estate.chasseur (...)
SELECT ...
FROM "Fil_Rouge_Depart".utilisateurs
WHERE role = 'chasseur';
```

---

# 42. Migration secteurs

```text
legacy secteurs
      |
      v
real_estate.secteur
```

avec :

```text
pays = France
```

par défaut pour les données existantes.

---

# 43. Migration mandat

Les mandats hérités sont transformés vers :

```text
real_estate.mandat
```

en conservant les relations :

```text
client
chasseur
secteur
```

---

# 44. Exclusivité

Le champ hérité :

```text
exclusif BOOLEAN
```

est converti vers :

```text
type_mandat
```

avec :

```text
TRUE
 -> EXCLUSIF

FALSE
 -> NON_EXCLUSIF
```

---

# 45. Date signature héritée

Le schéma hérité ne contient pas forcément toutes les informations nécessaires au nouveau modèle.

Lorsque `date_signature` n'existe pas explicitement, il faudra décider si :

```text
date_debut
```

peut être utilisée comme hypothèse de migration.

Cette hypothèse devra être documentée.

---

# 46. mode_signature héritée

Cette donnée n'existe pas forcément dans l'ancien schéma.

Elle ne doit pas être inventée comme une donnée réelle.

Options :

```text
INCONNU
```

ou valeur nullable pendant migration.

Le MPD final d'implémentation pourra donc autoriser temporairement :

```text
mode_signature = 'INCONNU'
```

---

# 47. Ajustement recommandé

La contrainte `mode_signature` doit accepter :

```text
INCONNU
```

pour permettre la migration fidèle de données héritées.

Valeurs :

```text
PAPIER
ELECTRONIQUE
AUTRE
INCONNU
```

---

# 48. date_fin héritée

Si la règle métier est :

```text
6 mois
```

alors :

```text
date_fin = date_debut + 6 mois
```

peut être dérivée lors de la migration si `date_debut` correspond bien au début contractuel.

Cette transformation doit être explicitement documentée.

---

# 49. Migration demande

Chaque mandat hérité produit :

```text
1 DEMANDE
```

initiale.

---

# 50. Migration première version

Chaque demande initiale produit :

```text
DEMANDE_VERSION 1
```

avec :

```text
date_version = migration timestamp
motif_modification = 'Migration depuis le SI hérité'
auteur_systeme = TRUE
```

---

# 51. description_recherche

Le champ :

```text
mandats.description_recherche
```

ne doit pas être perdu.

Une colonne temporaire ou complémentaire peut être conservée dans la première version.

Option recommandée :

ajouter :

```text
description_recherche_legacy TEXT
```

dans `demande_version`.

---

# 52. Ajustement demande_version

Ajouter :

```sql
description_recherche_legacy TEXT
```

permet :

- conservation ;
- audit ;
- transformation future ;
- comparaison avec critères structurés.

---

# 53. Extraction structurée

Le texte historique peut ensuite être traité :

```text
manual extraction
SQL parsing
Python
AI-assisted extraction
```

mais les valeurs non certaines ne doivent pas être inventées.

---

# 54. Migration taux commission

Pour chaque chasseur :

```text
utilisateurs.taux_commission
```

peut créer un barème initial.

Exemple conceptuel :

```text
montant_min = 0
montant_max = NULL
taux_commission = legacy rate
```

Cette migration ne recrée pas un historique qui n'existe pas.

---

# 55. Données du générateur

Le script `generer_annonces.py` ne modifie pas le modèle legacy.

Il produit des données de test pour :

```text
recherches
annonces
```

qui doivent entrer via les pipelines Data.

---

# 56. Schémas ingestion futurs

```sql
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
```

Ces schémas seront développés dans la phase Data.

---

# 57. RAW

La zone RAW doit conserver au maximum le format source.

Exemple :

```text
raw.annonce_json
raw.annonce_csv
```

---

# 58. STAGING

La zone STAGING transforme :

```text
prix variants
date variants
field names
boolean variants
nested fields
```

vers une structure cohérente.

---

# 59. BIEN canonique

Seules les données validées et normalisées alimentent :

```text
real_estate.bien
```

---

# 60. Matching

Le moteur de matching consomme :

```text
real_estate.demande_version
```

et :

```text
real_estate.bien
```

et produit principalement :

```text
real_estate.presentation
```

---

# 61. Feedback

Les actions client/chasseur sont conservées dans :

```text
real_estate.commentaire
```

et peuvent ensuite servir :

```text
analytics
requalification
future ML
```

---

# 62. RGPD

Les données personnelles principales sont :

```text
client
chasseur
commentaire
paiement
document
```

Le modèle analytique devra éviter de les répliquer sans nécessité.

---

# 63. Privacy by Default

La colonne :

```sql
indexable_ia BOOLEAN DEFAULT FALSE
```

reste une décision importante.

Un document n'est pas automatiquement autorisé pour l'IA.

---

# 64. Suppression

Par défaut, les relations historiques utilisent :

```text
ON DELETE RESTRICT
```

pour empêcher la destruction accidentelle.

Exception :

```text
mandat_secteur
```

peut utiliser :

```text
ON DELETE CASCADE
```

sur le mandat car il s'agit uniquement d'une relation associative.

---

# 65. Soft lifecycle

Les suppressions métier normales privilégient :

```text
statut
```

plutôt que :

```text
DELETE
```

sur :

```text
client
mandat
bien
demande
```

---

# 66. Types financiers

Tous les montants utilisent :

```text
NUMERIC
```

et jamais :

```text
FLOAT
```

pour éviter les erreurs de représentation financière.

---

# 67. Dates

Dates contractuelles :

```text
DATE
```

Événements techniques :

```text
TIMESTAMPTZ
```

---

# 68. Performance

Le MPD n'ajoute pas tous les index possibles.

Cycle :

```text
query
 |
 v
EXPLAIN ANALYZE
 |
 v
index candidate
 |
 v
EXPLAIN ANALYZE
```

---

# 69. Scalabilité

Le modèle doit pouvoir gérer :

```text
several thousand mandates/week
```

et :

```text
hundreds / thousands of properties
per search
```

sans supposer qu'une architecture distribuée est immédiatement nécessaire.

---

# 70. Partitionnement futur

Tables candidates si le volume l'exige :

```text
bien
presentation
commentaire
warehouse facts
```

Le partitionnement ne fait pas partie de la migration V1.

---

# 71. Système source immuable

Règle :

```text
"Fil_Rouge_Depart"
=
READ / MIGRATION SOURCE
```

Le nouveau SI doit être construit à côté.

---

# 72. Tests structurels

Après migration :

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'real_estate'
ORDER BY table_name;
```

---

# 73. Tables attendues

```text
bareme_commission
bien
chasseur
client
commentaire
demande
demande_version
document
mandat
mandat_secteur
paiement
presentation
secteur
source
```

---

# 74. Test version active

Deux versions actives de la même demande doivent échouer.

---

# 75. Test auteur version

Une version avec :

```text
client + chasseur
```

simultanément doit échouer.

Une version sans auteur doit échouer.

---

# 76. Test auteur commentaire

Même logique :

```text
exactly one
client OR chasseur
```

---

# 77. Test mandat six mois

Créer un mandat avec :

```text
date_signature = 2026-01-01
date_fin = 2026-05-01
```

doit échouer si la contrainte exacte de six mois est activée.

---

# 78. Test budget

```text
budget_min > budget_max
```

doit échouer.

---

# 79. Test DPE

```text
dpe = 'Z'
```

doit échouer.

---

# 80. Test presentation

Deux présentations du même :

```text
demande_version + bien
```

doivent échouer.

---

# 81. Test commission

```text
taux_commission > 1
```

doit échouer.

---

# 82. Test paiement

Un montant financier négatif doit échouer.

---

# 83. Scripts futurs

L'implémentation sera séparée :

```text
database/
│
├── migrations/
│   └── 001_initial_schema.sql
│
├── seeds/
│   └── ...
│
├── oltp/
│   └── ...
│
├── olap/
│   └── ...
│
└── tests/
    └── ...
```

---

# 84. migration.sql

Le script de migration réel devra contenir :

```text
schema
tables
constraints
indexes
legacy migration
```

mais pas les données synthétiques de benchmark.

---

# 85. Seed data

Les données générées par l'école ne doivent pas être confondues avec le seed métier minimal.

Elles appartiennent à :

```text
data ingestion / benchmark
```

---

# 86. Rejouabilité

La stratégie de migration doit être déterministe et testable.

Nous éviterons d'utiliser un script destructif contre la base legacy.

---

# 87. Transaction

La migration initiale peut utiliser :

```sql
BEGIN;

...

COMMIT;
```

pour maintenir l'atomicité lorsque possible.

---

# 88. Validation post-migration

Après migration :

```text
legacy row count
target row count
mapping checks
FK integrity
constraint validation
```

devront être vérifiés.

---

# 89. Traceabilité héritage

La migration devra permettre de démontrer :

```text
legacy utilisateur 7
        |
        v
real_estate.client X
```

et :

```text
legacy mandat 3
        |
        v
real_estate.mandat Y
```

---

# 90. Mapping IDs

Pour une migration contrôlée, il peut être utile de conserver temporairement :

```text
legacy_id
```

ou des tables de mapping.

Cette décision sera prise dans le script de migration.

---

# 91. Alternative legacy_id

Une option simple :

```text
legacy_id BIGINT UNIQUE
```

dans les tables migrées.

Mais cela introduit une colonne purement technique persistante.

---

# 92. Option recommandée

Utiliser des tables temporaires de mapping pendant la migration lorsque possible :

```text
migration_client_map
migration_chasseur_map
```

puis les supprimer après validation si elles ne sont plus utiles.

---

# 93. Architecture finale

```text
"Fil_Rouge_Depart"
      |
      v
Migration
      |
      v
real_estate
      |
      +--> OLTP application
      |
      +--> Data pipelines
      |
      +--> Matching
      |
      +--> Analytics
```

---

# 94. Statut

| Élément | Statut |
|---|---|
| PostgreSQL schema | DEFINED |
| Client | DEFINED |
| Chasseur | DEFINED |
| Secteur | DEFINED |
| Mandat | DEFINED |
| Mandat multi-sector | DEFINED |
| Demande | DEFINED |
| Demande versioning | DEFINED |
| Author integrity | RESOLVED |
| Structured criteria | DEFINED |
| JSONB preferences | DEFINED |
| Source | DEFINED |
| Bien | DEFINED |
| Presentation | DEFINED |
| Commentaire | DEFINED |
| Document | DEFINED |
| Commission scale | DEFINED |
| Payment | DEFINED |
| Legacy mapping | DEFINED |
| StarterPack generator integration | DEFINED |
| Index baseline | DEFINED |
| Performance indexes | TO MEASURE |
| migration.sql | NEXT |

---

# 95. Conclusion

Le MPD PostgreSQL V2 transforme le modèle métier corrigé en une structure directement implémentable.

Le système cible sépare désormais correctement :

```text
CLIENT
vs
CHASSEUR
```

```text
MANDAT
vs
DEMANDE
vs
DEMANDE_VERSION
```

```text
MATCHING
vs
COMMENTAIRE
```

et ajoute les concepts indispensables :

```text
SECTEUR
BAREME_COMMISSION
PAIEMENT
```

tout en conservant les extensions Data/AI utiles :

```text
SOURCE
DOCUMENT
```

Le modèle est maintenant aligné avec :

```text
StarterPack
+
Legacy Database
+
Business Process
+
Data Growth
+
OLTP / OLAP
+
AI Matching
+
RGPD
```

---

**MPD POSTGRESQL V2 — READY FOR IMPLEMENTATION**