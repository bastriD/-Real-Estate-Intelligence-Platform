# Mandat Lifecycle - Documentation technique et preuves d'execution

**Projet :** Chasse Immobiliere - Diginamic Fil Rouge  
**Perimetre :** Cycle de vie contractuel du Mandat, renouvellement, audit, warehouse et orchestration  
**Etat :** IMPLEMENTE - TESTE - DEPLOYE - VERIFIE EN RUNTIME  
**Date de cloture de l'increment :** 11 septembre 2026

---

## 1. Objectif

L'objectif de cet increment est de couvrir le cycle de vie contractuel du Mandat immobilier conformément aux exigences metier suivantes :

- un mandat est conclu pour une periode de **six mois calendaires** ;
- il peut etre **renouvele** ;
- chaque renouvellement doit etre **historise** ;
- l'historique ne doit pas etre ecrase par la periode courante ;
- le backend doit exposer cet historique et permettre le renouvellement ;
- les operations doivent respecter l'authentification, l'ownership et l'audit ;
- le cycle de vie doit etre propage dans le warehouse analytique ;
- le chargement doit rester idempotent et s'integrer au pipeline Airflow existant.

La regle retenue est volontairement precise : **six mois calendaires**, et non un nombre fixe de jours.

---

## 2. Positionnement dans l'architecture

Le Mandat reste l'identite contractuelle principale dans le schema OLTP.

La table `real_estate.mandat` conserve les dates de la **periode contractuelle courante** afin de maintenir la compatibilite avec le backend et les consommateurs existants.

L'historique est porte par une nouvelle table enfant :

```text
real_estate.mandat
        |
        +---- 1..N ----> real_estate.mandat_periode
                              |
                              | ETL / Airflow
                              v
warehouse.fact_mandat_periode
```

Le grain analytique reste volontairement separe :

- `warehouse.fact_mandat` : **1 ligne par Mandat** ;
- `warehouse.fact_mandat_periode` : **1 ligne par periode contractuelle**.

Cette separation evite de casser les consommateurs historiques de `fact_mandat` tout en permettant l'analyse des renouvellements.

---

## 3. Modele OLTP

### 3.1 Table `real_estate.mandat_periode`

La migration `008_mandat_lifecycle.sql` introduit la table de periodes contractuelles.

Les informations principales sont :

- `id_mandat_periode` : identifiant technique ;
- `id_mandat` : Mandat parent ;
- `numero_periode` : ordre chronologique ;
- `type_periode` : `INITIAL` ou `RENOUVELLEMENT` ;
- `date_debut` ;
- `date_fin` ;
- `date_renouvellement` ;
- `commentaire` ;
- `est_historique_legacy` ;
- `created_at`.

### 3.2 Regles d'integrite

La base protege les invariants du domaine :

1. une seule periode `INITIAL` par Mandat ;
2. la periode initiale porte le numero 1 ;
3. une nouvelle periode non legacy dure exactement six mois calendaires ;
4. une periode de renouvellement suit la periode precedente ;
5. convention de frontiere :
   `nouvelle.date_debut = precedente.date_fin` ;
6. les periodes ne doivent pas se chevaucher ;
7. les lignes de `mandat_periode` sont immuables ;
8. les donnees legacy existantes sont conservees sans reecriture artificielle.

La convention choisie correspond a des intervalles contractuels contigus de type demi-ouvert. Aucun `+1 jour` n'est applique au renouvellement.

---

## 4. Migration 008 - historique contractuel

La migration :

```text
database/migrations/008_mandat_lifecycle.sql
```

a :

- cree `real_estate.mandat_periode` ;
- ajoute les contraintes et index ;
- ajoute les triggers de validation et d'immutabilite ;
- backfille les Mandats historiques ;
- enregistre la migration dans `migration_control.schema_version`.

Les **17 Mandats historiques** ont ete backfilles avec exactement une periode :

```text
type_periode           = INITIAL
numero_periode         = 1
est_historique_legacy  = true
```

Les dates historiques n'ont pas ete modifiees pour forcer artificiellement la regle des six mois.

Le test SQL associe est :

```text
database/tests/011_mandat_lifecycle.sql
```

Il couvre notamment les periodes initiales, renouvellements successifs, contraintes de duree, sequentialite, chevauchement et immutabilite.

**Etat migration 008 :**

```text
DESIGNED           OK
IMPLEMENTED        OK
CI VALIDATED       OK
APPLIED            OK
TESTED             OK
RUNTIME VERIFIED   OK
```

---

## 5. Backend FastAPI

Le backend a ete etendu avec :

```text
src/api/db/models/mandat_periode.py
src/api/repositories/mandat.py
src/api/schemas/mandat.py
src/api/services/mandat.py
```

### 5.1 API d'historique

Endpoint :

```http
GET /api/v1/mandats/{mandat_id}/periodes
```

Il retourne l'ensemble des periodes du Mandat dans l'ordre contractuel.

Le endpoint est protege par JWT.

Preuve runtime sans authentification :

```text
GET /api/v1/mandats/11/periodes
HTTP 401
{"detail":"Authentication required"}
```

Cela confirme que la route est presente dans le backend deploye et que l'authentification est appliquee.

Avec un compte ADMIN authentifie :

```text
GET /api/v1/mandats/11/periodes
HTTP 200
```

Avant renouvellement, Mandat 11 retournait :

```json
[
  {
    "id_mandat_periode": 1,
    "id_mandat": 11,
    "numero_periode": 1,
    "type_periode": "INITIAL",
    "date_debut": "2026-01-05",
    "date_fin": "2026-07-05",
    "date_renouvellement": null,
    "est_historique_legacy": true
  }
]
```

Mandat 5 a egalement ete lu avec succes en ADMIN (`HTTP 200`), ce qui confirme le comportement non restreint de ce role sur cette ressource.

### 5.2 API de renouvellement

Endpoint :

```http
POST /api/v1/mandats/{mandat_id}/renew
```

Schema runtime OpenAPI :

```json
{
  "date_renouvellement": "date - obligatoire",
  "commentaire": "string | null"
}
```

Reponse attendue : `HTTP 201`, contenant :

- le Mandat mis a jour ;
- la nouvelle `MandatPeriode`.

---

## 6. Regle de renouvellement implementee

Le service deploye applique :

```text
previous_period = derniere periode du Mandat

new_date_debut = previous_period.date_fin
new_date_fin   = add_calendar_months(new_date_debut, 6)

numero_periode = previous.numero_periode + 1
type_periode   = RENOUVELLEMENT
legacy         = false
```

Puis, dans la meme transaction :

1. creation de la nouvelle `mandat_periode` ;
2. mise a jour de `mandat.date_debut` ;
3. mise a jour de `mandat.date_fin` ;
4. audit de l'insertion de la periode ;
5. audit de la mise a jour du Mandat ;
6. `COMMIT`.

En cas de violation d'une contrainte d'integrite, la transaction est rollbackee.

**Important :** aucun automate de passage automatique du statut a `EXPIRE` n'a ete implemente dans cet increment. Aucune matrice supplementaire de statuts autorisant/interdisant un renouvellement ne doit etre consideree comme implementee.

---

## 7. Preuve runtime du renouvellement

Un renouvellement reel a ete execute sur :

```text
Mandat : 11
Reference : LEGACY-MANDAT-11
Type : EXCLUSIF
Acteur : admin.auth.test@example.com
```

### 7.1 Etat avant renouvellement

```text
Periode 1
type         = INITIAL
date_debut   = 2026-01-05
date_fin     = 2026-07-05
legacy       = true
```

### 7.2 Appel API

```text
POST /api/v1/mandats/11/renew
HTTP 201
```

Payload utilise :

```json
{
  "date_renouvellement": "2026-07-05",
  "commentaire": "Runtime validation of Mandat six-month renewal lifecycle"
}
```

### 7.3 Reponse runtime

Le backend a retourne :

```text
Mandat:
  date_debut = 2026-07-05
  date_fin   = 2027-01-05
  statut     = ACTIF

Nouvelle periode:
  id_mandat_periode     = 18
  numero_periode        = 2
  type_periode          = RENOUVELLEMENT
  date_debut            = 2026-07-05
  date_fin              = 2027-01-05
  date_renouvellement   = 2026-07-05
  est_historique_legacy = false
```

La regle des **six mois calendaires** est donc verifiee en environnement d'execution.

---

## 8. Verification directe PostgreSQL

La verification apres l'appel API confirme la projection courante :

```text
id_mandat | reference_mandat | date_debut | date_fin   | statut
11        | LEGACY-MANDAT-11 | 2026-07-05 | 2027-01-05 | ACTIF
```

Et l'historique complet :

```text
periode 1 | INITIAL        | 2026-01-05 -> 2026-07-05 | legacy=true
periode 2 | RENOUVELLEMENT | 2026-07-05 -> 2027-01-05 | legacy=false
```

L'historique initial n'a donc pas ete ecrase par le renouvellement.

---

## 9. Audit runtime

Le renouvellement a genere deux evenements d'audit a la meme date transactionnelle :

```text
id_audit = 14
table    = mandat_periode
operation= INSERT
record   = 18
user     = admin.auth.test@example.com
context  = {
  "action": "renew_mandat",
  "source": "api",
  "id_mandat": 11
}
```

et :

```text
id_audit = 15
table    = mandat
operation= UPDATE
record   = 11
user     = admin.auth.test@example.com
context  = {
  "action": "renew_mandat",
  "source": "api",
  "numero_periode": 2
}
```

Cela apporte une tracabilite explicite :

```text
acteur -> action API -> nouvelle periode -> modification du contrat courant
```

---

## 10. Tests backend

Les tests du service et de l'API Mandat lifecycle ont ete executes avec succes.

Resultat cible service/API :

```text
62 passed
```

Regression backend complete apres implementation :

```text
265 passed
```

Le baseline precedent avant cet increment etait de 235 tests backend valides.

Cela fournit une preuve de non-regression en plus des preuves runtime.

---

## 11. Warehouse analytique

La migration :

```text
database/migrations/009_mandat_lifecycle_warehouse.sql
```

ajoute :

```text
warehouse.fact_mandat_periode
```

### 11.1 Grain

```text
1 ligne = 1 periode contractuelle d'un Mandat
```

Le fait historique `warehouse.fact_mandat` conserve son grain :

```text
1 ligne = 1 Mandat
```

### 11.2 Colonnes principales

```text
mandat_periode_fact_key
id_mandat_periode_source
mandat_fact_key
numero_periode
type_periode
date_debut_key
date_fin_key
date_renouvellement_key
est_historique_legacy
duree_jours
periode_count
created_at_source
dw_loaded_at
```

Les dimensions dates utilisent les cles `YYYYMMDD` de `warehouse.dim_date`.

Le warehouse peut ainsi supporter notamment :

- nombre de renouvellements ;
- nombre de periodes par Mandat ;
- duree contractuelle cumulee ;
- premiere/periode courante ;
- taux de renouvellement ;
- futures analyses de performance liees aux renouvellements.

---

## 12. Migration 009 - preuves

Le registre runtime contient :

```text
version     = 009
description = Add Mandat period lifecycle fact to analytical warehouse
applied_at  = 2026-09-11 21:37:13.661981+00
```

Le test :

```text
database/tests/012_mandat_lifecycle_warehouse.sql
```

a ete valide en CI.

Avant le renouvellement runtime, la verification montrait :

```text
OLTP mandate periods      = 17
Warehouse mandate periods = 17
Duplicate periods         = 0
```

**Etat migration 009 :**

```text
DESIGNED           OK
IMPLEMENTED        OK
CI VALIDATED       OK
APPLIED            OK
TESTED             OK
RUNTIME VERIFIED   OK
```

---

## 13. Loader warehouse

Le loader :

```text
database/olap/load_warehouse.py
```

contient maintenant :

```text
load_fact_mandat_periode()
```

Le chargement :

- lit `real_estate.mandat_periode` ;
- retrouve le Mandat analytique via `warehouse.fact_mandat` ;
- genere les cles dates ;
- calcule `duree_jours` ;
- charge `warehouse.fact_mandat_periode` ;
- utilise un UPSERT pour rendre le chargement analytique idempotent.

L'UPSERT du warehouse ne remet pas en cause l'immutabilite OLTP : il sert a la reconciliation/reconstruction analytique et ne modifie jamais `real_estate.mandat_periode`.

Le nouvel artefact `data-pipeline` a ete verifie dans Kubernetes avec le digest :

```text
sha256:3bcd3859f16886126456d21e04d57e2512c79de36a25e1bc9f3c20f3b2c3e535
```

Le digest precedent etait :

```text
sha256:011535ea81cff35f252f25677d836b197ee996e959c1fd9e2e5cfdead2de0d9d
```

La presence runtime de `load_fact_mandat_periode` et de son appel dans `main()` a ete verifiee dans l'image Kubernetes.

---

## 14. Airflow - preuve end-to-end

DAG :

```text
real_estate_ingestion
```

Run de validation :

```text
manual__2026-09-11T21:55:47+00:00
```

Etat global :

```text
SUCCESS
```

Toutes les taches ont termine en `success` :

```text
generate_source_data  success
load_raw              success
validate_raw          success
transform_staging     success
validate_staging      success
load_oltp             success
validate_oltp         success
load_warehouse        success
validate_warehouse    success
dbt_run               success
dbt_test              success
collect_metrics       success
end                   success
```

Cette execution prouve que le nouveau loader est compatible avec le chemin d'execution reel :

```text
source
  -> raw
  -> validation raw
  -> staging
  -> validation staging
  -> OLTP
  -> validation OLTP
  -> warehouse
  -> validation warehouse
  -> dbt
  -> dbt tests
  -> metriques
```

---

## 15. Verification d'idempotence apres Airflow

Apres le run Airflow, une verification directe a donne :

```text
oltp_periods       = 17
warehouse_periods  = 17
duplicate_periods  = 0
```

Cette preuve a ete obtenue **avant** la creation du renouvellement runtime de Mandat 11.

Depuis le renouvellement, l'OLTP contient desormais une 18e periode. La propagation de cette nouvelle periode vers le warehouse depend du prochain passage de `load_warehouse`; il ne faut donc pas presenter `18/18` comme deja prouve tant qu'un nouveau chargement n'a pas ete execute.

---

## 16. Securite et ownership

Le cycle de vie Mandat reutilise les controles existants :

- authentification JWT ;
- roles applicatifs `ADMIN`, `CHASSEUR`, `SERVICE`, `CLIENT` ;
- ownership Mandat pour `CHASSEUR` ;
- ADMIN non restreint ;
- acces cross-owner CHASSEUR masque par `404` ;
- CHASSEUR sans `id_chasseur` rejete par `403`.

L'ownership Mandat avait deja ete prouve en runtime :

```text
CHASSEUR 1 -> Mandat 11 -> HTTP 200
CHASSEUR 1 -> Mandat 5  -> HTTP 404
```

Le renouvellement runtime documente ici a ete execute avec le compte ADMIN afin de valider le comportement fonctionnel et l'audit.

Il ne faut pas confondre cette preuve ADMIN avec une nouvelle preuve runtime du renouvellement par CHASSEUR. La logique d'ownership est couverte par les tests et par les preuves Mandat precedentes.

---

## 17. Ce qui est explicitement hors perimetre

Cet increment ne prouve pas et ne pretend pas implementer :

- expiration automatique des Mandats ;
- ordonnanceur de changement de statut ;
- matrice metier supplementaire des statuts autorisant le renouvellement ;
- remuneration ou calcul de commission ;
- paiement ;
- calcul final de performance a l'acte authentique ;
- modele ML final GPU en production ;
- RAG ;
- Databricks, Snowflake ou Kubeflow.

Ces sujets doivent rester des increments separes.

---

## 18. Etat final de l'increment

### OLTP / Database

```text
Modelisation              OK
Migration 008             OK
Contraintes               OK
Historisation             OK
Backfill legacy           OK
Tests SQL                 OK
Application runtime       OK
```

### Backend

```text
Schemas                   OK
Repository                OK
Service                   OK
GET historique            OK
POST renouvellement       OK
JWT                       OK
Ownership integration     OK
Audit                     OK
Tests                     OK
Runtime                   OK
```

### Warehouse / Data Platform

```text
Migration 009             OK
fact_mandat_periode       OK
Loader                    OK
Image data-pipeline       OK
Airflow E2E               OK
Validation warehouse      OK
dbt run                   OK
dbt test                  OK
Metrics collection        OK
No duplicate              OK
```

### Statut global

```text
MANDAT LIFECYCLE
==============================
DESIGNED           COMPLETE
IMPLEMENTED        COMPLETE
TESTED             COMPLETE
DEPLOYED           COMPLETE
RUNTIME VERIFIED   COMPLETE
AUDITED            COMPLETE
WAREHOUSE ENABLED  COMPLETE
DOCUMENTED         COMPLETE
```

---

## 19. Valeur pour le Fil Rouge / RNCP

Cet increment fournit des preuves transverses importantes pour le dossier de certification :

- **BC01** : traduction d'une regle metier en solution exploitable et tracable ;
- **BC02** : choix d'architecture, separation OLTP/OLAP, preservation de compatibilite ;
- **BC03** : implementation backend, API, transaction, validation et non-regression ;
- **BC04** : authentification, autorisation/ownership et journalisation ;
- **BC05** : modelisation relationnelle, migration, contraintes, historisation, warehouse et qualite ;
- **BC06** : CI/CD, image conteneurisee, Kubernetes, Airflow, execution runtime et observabilite.

Les preuves sont issues de plusieurs niveaux : code, tests, CI, base de donnees, API runtime, Kubernetes et orchestration Airflow.

---

## 20. Prochaine mission

Le cycle de vie du Mandat est maintenant ferme.

La prochaine lacune fonctionnelle majeure du parcours commercial est :

```text
REMUNERATION / PAIEMENT
```

Le prochain increment devra couvrir, sans inventer les regles metier non specifiees :

```text
transaction / acte authentique
        ->
eligibilite
        ->
bareme/version applicable
        ->
entrees financieres figees
        ->
calcul Decimal deterministe
        ->
resultat fige et reproductible
        ->
cycle financier
        ->
paiement
        ->
audit
        ->
warehouse / indicateurs / gouvernance
```

Les regles exactes de remuneration et de performance devront etre etablies avant implementation.
