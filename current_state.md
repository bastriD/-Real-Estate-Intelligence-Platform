# Pipeline d'ingestion Real Estate --- Implémentation et validation

**Projet :** Chasse Immobilière\
**Composant :** Pipeline Data / Airflow\
**État documenté :** 23 août 2026\
**Statut :** ✅ Implémenté et validé de bout en bout

------------------------------------------------------------------------

## 1. Objectif

Ce document décrit l'implémentation et la validation du pipeline
d'ingestion de données immobilières du projet **Chasse Immobilière**.

Le pipeline automatise :

``` text
Génération des données sources
→ Stockage objet MinIO
→ PostgreSQL RAW
→ Contrôles qualité RAW
→ Transformation RAW → STAGING
→ Contrôles qualité STAGING
→ Chargement STAGING → OLTP
→ Contrôles qualité OLTP
```

L'orchestration complète est assurée par **Apache Airflow 2.10.5** sur
Kubernetes.

## 2. Architecture d'exécution

``` text
GitLab chasse_immobiliere
        │
        ├── CI/CD → build image data-pipeline
        │                 ↓
        │        GitLab Container Registry
        │
        └── CI/CD → publication DAGs
                          ↓
                       Airflow
                          ↓
                generate_source_data
                          ↓
                        MinIO
              real-estate/raw/generated
                          ↓
                      load_raw
                          ↓
                  PostgreSQL RAW
                          ↓
                   validate_raw
                          ↓
                transform_staging
                          ↓
                PostgreSQL STAGING
                          ↓
                validate_staging
                          ↓
                     load_oltp
                          ↓
             PostgreSQL real_estate OLTP
                          ↓
                   validate_oltp
                          ↓
                       SUCCESS
```

## 3. Composants techniques

  Composant                   Rôle
  --------------------------- ---------------------------------------------------
  Kubernetes                  Plateforme d'exécution
  Apache Airflow 2.10.5       Orchestration
  KubernetesPodOperator       Pods dédiés aux traitements
  PostgreSQL                  RAW, STAGING et OLTP
  MinIO                       Stockage des datasets générés
  GitLab CI/CD                Build image et publication DAGs
  GitLab Container Registry   Registre privé
  Python 3.12                 Génération, parsing, transformation et chargement
  psql                        Exécution des contrôles qualité SQL

Namespaces utilisés :

-   `airflow` : Airflow et pods KubernetesPodOperator ;
-   `real-estate` : PostgreSQL du projet.

## 4. Image Data Pipeline

Image :

``` text
gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
```

Base :

``` dockerfile
FROM python:3.12-slim
```

Scripts intégrés et utilisés pendant cette phase :

``` text
database/seeds/generer_annonces.py
database/seeds/upload_generated_to_s3.py
database/seeds/download_generated_from_s3.py
database/seeds/load_raw_generated_data.py
database/seeds/transform_raw_to_staging.py
database/seeds/load_staging_to_oltp.py
database/tests/004_raw_data_quality.sql
database/tests/006_oltp_data_quality.sql
```

Le client PostgreSQL est installé dans l'image pour permettre les
validations SQL depuis les pods.

## 5. CI/CD

Le pipeline GitLab construit et pousse l'image `data-pipeline:latest`
dans le registre privé.

Les DAGs présents sous :

``` text
pipelines/airflow/*.py
```

sont publiés par CI vers le dépôt :

``` text
root/airflow-dags
```

Le scheduler Airflow consomme ensuite cette version publiée.

## 6. Authentification au registre GitLab

Le registre étant privé, un secret de type Docker Registry a été créé
dans le namespace `airflow` :

``` text
gitlab-registry
```

Les KubernetesPodOperator utilisent :

``` python
image_pull_secrets=[
    k8s.V1LocalObjectReference(name="gitlab-registry")
]
```

Les identifiants et tokens sont volontairement exclus de cette
documentation.

## 7. Secret PostgreSQL

Le secret :

``` text
real-estate-postgresql-secret
```

contient les clés confirmées :

``` text
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PASSWORD
POSTGRES_PORT
POSTGRES_USER
```

Les pods récupèrent ces variables avec `env_from`. Les valeurs sensibles
ne sont pas inscrites dans le DAG.

## 8. DAG Airflow

DAG :

``` text
real_estate_ingestion
```

Chaîne validée :

``` text
start
→ generate_source_data
→ load_raw
→ validate_raw
→ transform_staging
→ validate_staging
→ load_oltp
→ validate_oltp
→ end
```

## 9. Génération et stockage source

`generate_source_data` génère le dataset, produit les CSV/JSON et les
charge dans MinIO.

Batch de référence :

``` text
generated-20260822T000000
```

Préfixe :

``` text
s3://real-estate/raw/generated/generated-20260822T000000/
```

Résultat :

``` text
PASS: 1002 files uploaded
```

Dataset métier :

-   5 recherches ;
-   1000 annonces.

Fichiers principaux :

``` text
recherches.csv
annonces.csv
json/annonce_XXXX.json
```

## 10. Chargement RAW

`load_raw` télécharge les CSV depuis MinIO et les charge dans
PostgreSQL.

Résultat :

``` text
LOADED: 5 rows into raw.recherches
LOADED: 1000 rows into raw.annonces
PASS: 5 RAW recherches loaded
PASS: 1000 RAW annonces loaded
RAW ingestion completed successfully.
```

## 11. Validation RAW

Le contrôle qualité vérifie notamment les volumes, les références, ainsi
que le parsing de valeurs telles que prix et surfaces.

Résultat :

``` text
PASS | generated-20260822T000000
RAW data quality validated successfully
```

Répartition des 1000 annonces :

  Type                 Nombre
  ------------------ --------
  Appartement             200
  Duplex                  200
  Local commercial        200
  Loft                    200
  Villa                   200

  Ville          Nombre
  ------------ --------
  Limoges           400
  Annecy            200
  Marseille         200
  Strasbourg        200

## 12. Transformation RAW → STAGING

Premier résultat :

``` text
RAW recherches: 5
RAW annonces: 1000
PASS: 5 recherches reconciled RAW -> STAGING
PASS: 1000 annonces reconciled RAW -> STAGING
QUALITY: invalid recherches = 0
QUALITY: invalid annonces = 261
```

La réconciliation était complète, mais 261 annonces étaient invalidées
par le contrôle de `date_publication`.

## 13. Incident qualité : parsing des dates

Cause identifiée :

``` text
date_publication | invalid datetime format | 261
```

Exemples rencontrés :

``` text
01-25-2025
03-14-2025
11 avril 2025
12 décembre 2024
14 janvier 2025
1 décembre 2025
26 juillet 2026
```

Le parseur Python initial ne couvrait pas tous les formats réellement
générés.

La logique de parsing a été étendue, notamment pour les formats
supplémentaires et les noms de mois français.

Après reconstruction de l'image :

``` text
PASS: 5 recherches reconciled RAW -> STAGING
PASS: 1000 annonces reconciled RAW -> STAGING
QUALITY: invalid recherches = 0
QUALITY: invalid annonces = 0
```

Les 261 erreurs ont été supprimées sans perte de lignes.

## 14. Validation STAGING

Résultat :

``` text
PASS | generated-20260822T000000
STAGING data quality validated successfully
```

Indicateurs :

``` text
total_annonces        = 1000
missing_dpe           = 204
missing_nb_pieces     = 0
missing_nb_chambres   = 510
missing_contact_email = 491
missing_latitude      = 537
missing_longitude     = 537
average_price         = 213189.63
average_surface       = 213.77
min_price             = 56592.00
max_price             = 458060.00
min_surface           = 34.00
max_surface           = 400.00
```

Les champs optionnels manquants restent `NULL` au lieu d'être remplacés
par des valeurs artificielles.

## 15. Chargement STAGING → OLTP

Tables métier utilisées :

``` text
real_estate.source
real_estate.bien
```

`real_estate.bien` impose notamment l'unicité :

``` text
(id_source, reference_externe)
```

Résultat :

``` text
Valid staging annonces: 1000
Created source: id_source=4
UPSERTED: 1000 annonces into real_estate.bien
Current biens for source 4: 1000
PASS: 1000 validated staging annonces reconciled with real_estate.bien
PASS: no duplicate (id_source, reference_externe) pairs
STAGING -> OLTP load completed successfully.
```

Source créée :

``` text
nom              = GENERATEUR_ANNONCES
type_source      = AUTRE
actif            = true
niveau_confiance = MOYEN
```

## 16. Validation OLTP

Tous les contrôles finaux ont réussi :

``` text
PASS: generated source exists exactly once
PASS: generated source is active
PASS: 1000 biens loaded for current batch
PASS: all staging references exist in OLTP
PASS: no duplicate source/reference pairs
PASS: bien -> source foreign keys are valid
PASS: mandatory bien fields are populated
PASS: bien prices are valid
PASS: bien surfaces are valid
PASS: room counts are valid
PASS: DPE values are valid
PASS: latitude values are valid
PASS: longitude values are valid
PASS: bien statuses are valid
```

Réconciliation :

``` text
generated-20260822T000000
staging_valid_annonces = 1000
oltp_matched_biens     = 1000
```

Résultat final :

``` text
PASS | generated-20260822T000000
OLTP data quality validated successfully
```

## 17. État OLTP obtenu

``` text
total_biens = 1000
statut ACTIF = 1000
```

Répartition :

  Type                 Biens
  ------------------ -------
  Appartement            200
  Duplex                 200
  Local commercial       200
  Loft                   200
  Villa                  200

  Ville          Biens
  ------------ -------
  Limoges          400
  Annecy           200
  Marseille        200
  Strasbourg       200

Statistiques :

``` text
min_price   = 56592.00
max_price   = 458060.00
avg_price   = 213189.63
min_surface = 34.00
max_surface = 400.00
avg_surface = 213.77
```

## 18. Incidents rencontrés et corrections

### 18.1 ImagePullBackOff / 403 GitLab Registry

Erreur :

``` text
failed to fetch anonymous token: 403 Forbidden
```

Correction :

-   création du secret `gitlab-registry` ;
-   ajout de `image_pull_secrets` aux pods Airflow.

### 18.2 DuplicateTaskIdFound

Erreur :

``` text
Task id 'load_raw' has already been added to the DAG
```

Correction : suppression de la déclaration dupliquée du task ID.

### 18.3 validate_raw_task non défini

Erreur :

``` text
NameError: name 'validate_raw_task' is not defined
```

Correction : remise en cohérence de la définition des tâches et de la
chaîne de dépendances.

### 18.4 Loader OLTP absent de l'image

Erreur :

``` text
python: can't open file '/app/database/seeds/load_staging_to_oltp.py'
[Errno 2] No such file or directory
```

Le fichier n'avait pas été sauvegardé/intégré lors du premier essai.

Correction :

-   sauvegarde du loader ;
-   ajout au Dockerfile ;
-   reconstruction et publication de l'image ;
-   contrôle direct dans Kubernetes.

Validation :

``` text
PASS: OLTP loader exists and compiles
```

### 18.5 261 dates invalides

Correction du parseur de dates/datetimes.

Évolution :

``` text
invalid annonces: 261 → 0
```

## 19. Validation de l'image dans Kubernetes

L'image publiée a été testée directement dans un pod :

``` text
/app/database/seeds/load_staging_to_oltp.py
```

Puis compilée :

``` text
python -m py_compile /app/database/seeds/load_staging_to_oltp.py
```

Résultat :

``` text
PASS: OLTP loader exists and compiles
```

## 20. Validation end-to-end

Une exécution complète du DAG a été déclenchée après les validations
unitaires des tâches.

Run :

``` text
manual__2026-08-23T07:37:15+00:00
```

État final :

``` text
success
```

  Tâche                  État
  ---------------------- ------------
  start                  ✅ success
  generate_source_data   ✅ success
  load_raw               ✅ success
  validate_raw           ✅ success
  transform_staging      ✅ success
  validate_staging       ✅ success
  load_oltp              ✅ success
  validate_oltp          ✅ success
  end                    ✅ success

Horodatage :

``` text
start_date = 2026-08-23T07:37:16.408384+00:00
end_date   = 2026-08-23T07:40:01.427073+00:00
```

Durée : environ **2 minutes 45 secondes**.

## 21. Milestone validé

Le chemin suivant est désormais démontré fonctionnel :

``` text
GitLab
→ GitLab CI/CD
→ GitLab Container Registry
→ Airflow
→ KubernetesPodOperator
→ génération dataset
→ MinIO
→ RAW PostgreSQL
→ RAW Quality Gate
→ STAGING PostgreSQL
→ STAGING Quality Gate
→ OLTP PostgreSQL
→ OLTP Quality Gate
→ SUCCESS
```

Critères :

-   [x] génération automatisée ;
-   [x] persistance MinIO ;
-   [x] chargement RAW ;
-   [x] qualité RAW ;
-   [x] transformation RAW → STAGING ;
-   [x] normalisation des dates ;
-   [x] qualité STAGING ;
-   [x] chargement STAGING → OLTP ;
-   [x] upsert métier ;
-   [x] absence de doublons métier ;
-   [x] intégrité référentielle ;
-   [x] qualité OLTP ;
-   [x] registre GitLab privé utilisable par Kubernetes ;
-   [x] publication CI/CD du DAG ;
-   [x] orchestration complète Airflow ;
-   [x] run end-to-end `success`.

## 22. Conclusion

Au **23 août 2026**, le pipeline d'ingestion immobilier est
**implémenté, déployé et validé de bout en bout**.

Le batch de référence :

``` text
generated-20260822T000000
```

est réconcilié jusqu'au modèle OLTP avec :

``` text
1000 staging_valid_annonces
1000 oltp_matched_biens
0 doublon métier
PASS RAW
PASS STAGING
PASS OLTP
```

Milestone :

> **REAL ESTATE INGESTION PIPELINE --- END-TO-END VALIDATED ✅**

Les prochaines évolutions pourront traiter l'industrialisation :
planification récurrente, observabilité, alerting, rétention,
durcissement de la gestion des secrets, GitOps et couches analytiques.
