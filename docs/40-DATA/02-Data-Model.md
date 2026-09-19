# Data Model — Real Estate Intelligence Platform

**Projet :** PROJECT_FIL_ROUGE / CHASSE_IMMOBILIERE
**Domaine :** Real Estate Intelligence Platform
**Version :** 3.0
**Statut :** Implémenté et aligné avec le runtime
**Périmètre :** migrations PostgreSQL 001 à 012
**Dernière mise à jour :** 2026-09-15

---

# 1. Objectif

Ce document présente le **modèle de données canonique** de la plateforme Real Estate Intelligence.

Il fournit une vue fonctionnelle et architecturale du modèle sans reproduire l'intégralité du schéma physique PostgreSQL.

Les niveaux détaillés sont documentés séparément :

```text
MCD
Concepts métier et cardinalités

MLD
Relations, clés et dépendances

MPD
Tables PostgreSQL, types, contraintes et nullabilité
```

La chaîne de référence est :

```text
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
Migrations 001 -> 012
      |
      v
PostgreSQL runtime
```

---

# 2. Principes de modélisation

Le modèle repose sur plusieurs principes structurants :

1. séparation entre identité applicative et identité métier ;
2. séparation entre demande, version de demande et affectation ;
3. historisation des périodes contractuelles ;
4. conservation du lineage des données ;
5. séparation entre matching, présentation, visite et vente ;
6. séparation entre vente, calcul de rémunération et paiement ;
7. historisation des paramètres financiers ;
8. conservation du snapshot ayant produit une rémunération ;
9. audit des opérations métier sensibles ;
10. séparation stricte entre OLTP et OLAP.

Le modèle doit permettre simultanément :

```text
intégrité
historisation
traçabilité
auditabilité
explicabilité
analytics
gouvernance
observabilité
évolution IA
```

---

# 3. Domaines fonctionnels

Le modèle OLTP est organisé autour de six ensembles.

## Identity & Security

```text
CLIENT
CHASSEUR
UTILISATEUR
```

## Contract

```text
MANDAT
MANDAT_PERIODE
SECTEUR
MANDAT_SECTEUR
```

## Search

```text
DEMANDE
DEMANDE_AFFECTATION
DEMANDE_VERSION
```

## Property & Matching

```text
SOURCE
BIEN
DOCUMENT
PRESENTATION
COMMENTAIRE
VISITE
```

## Transaction & Remuneration

```text
VENTE
PARAMETRES_HONORAIRES
BAREME_COMMISSION
PARAMETRES_REMUNERATION
PALIER_PERFORMANCE
PAIEMENT
```

## Cross-cutting

```text
AUDIT_LOG
```

Le schéma `real_estate` comporte ainsi actuellement **23 tables OLTP**.

---

# 4. Vue métier globale

Le parcours métier principal est :

```text
CLIENT
   |
   v
DEMANDE
   |
   v
DEMANDE_AFFECTATION
   |
   v
DEMANDE_VERSION
   |
   v
MATCHING
   |
   v
PRESENTATION
   |
   v
VISITE
   |
   v
VENTE
   |
   v
CALCUL HONORAIRES
   |
   v
CALCUL PERFORMANCE
   |
   v
CALCUL REMUNERATION
   |
   v
PAIEMENT
```

Le contexte contractuel associé est :

```text
CLIENT
   |
   v
MANDAT
   |
   v
MANDAT_PERIODE
```

Le `CHASSEUR` intervient notamment dans :

```text
MANDAT
DEMANDE_AFFECTATION
DEMANDE_VERSION
COMMENTAIRE
VENTE
PAIEMENT
```

---

# 5. Identity & Security

## CLIENT

`CLIENT` représente l'identité métier du client immobilier.

Informations principales :

```text
identité
coordonnées
ville
statut
consentement de contact
date de création
```

L'adresse email du client est unique.

Statuts :

```text
ACTIF
INACTIF
ARCHIVE
```

---

## CHASSEUR

`CHASSEUR` représente le professionnel chargé d'accompagner les clients.

Informations principales :

```text
identité
email
téléphone
date d'entrée
statut
```

La `date_entree` est notamment utilisée pour calculer l'ancienneté intervenant dans le système de rémunération.

Pour certaines données historiques, la date d'entrée provient de la première activité métier connue et non d'une source RH certifiée.

Cette provenance est explicitement documentée.

---

## UTILISATEUR

`UTILISATEUR` représente l'identité d'authentification et d'autorisation.

Rôles :

```text
ADMIN
CLIENT
CHASSEUR
SERVICE
```

Le modèle distingue donc :

```text
identité métier
        !=
identité applicative
```

Un utilisateur `CLIENT` référence un client.

Un utilisateur `CHASSEUR` référence un chasseur.

Un utilisateur `ADMIN` ou `SERVICE` n'est rattaché ni à un client ni à un chasseur.

Cette séparation supporte directement le RBAC de l'API.

---

# 6. Contract Domain

## MANDAT

`MANDAT` représente le contrat liant :

```text
CLIENT
   |
MANDAT
   |
CHASSEUR
```

Il contient notamment :

```text
référence
type
mode de signature
date de signature
date de début
date de fin
statut
```

Types :

```text
EXCLUSIF
NON_EXCLUSIF
```

Le mandat ne doit cependant plus être interprété comme une période contractuelle unique et écrasable.

---

# 7. MANDAT_PERIODE

`MANDAT_PERIODE` historise les périodes contractuelles.

```text
MANDAT
   |
   +--> période 1 INITIAL
   |
   +--> période 2 RENOUVELLEMENT
   |
   +--> période 3 RENOUVELLEMENT
   |
   ...
```

Types :

```text
INITIAL
RENOUVELLEMENT
```

Une période contractuelle standard dure **six mois calendaires**.

Un renouvellement crée une nouvelle période au lieu d'écraser la période précédente.

Le modèle permet donc de conserver :

```text
historique contractuel
durée réelle
renouvellements
période applicable à une vente
```

Les données historiques legacy pouvant ne pas respecter parfaitement cette règle sont explicitement identifiées.

`RENOUVELLEMENT_MANDAT` n'est donc pas une future table séparée.

Le renouvellement est déjà implémenté via `MANDAT_PERIODE`.

---

# 8. SECTEUR et MANDAT_SECTEUR

`SECTEUR` représente une zone géographique métier.

Exemples d'attributs :

```text
pays
ville
quartier
code postal
```

La relation entre mandat et secteur est N,N :

```text
MANDAT
   |
   v
MANDAT_SECTEUR
   ^
   |
SECTEUR
```

Un mandat peut couvrir plusieurs secteurs et un secteur peut appartenir à plusieurs mandats.

---

# 9. Search Domain

## DEMANDE

`DEMANDE` représente le besoin de recherche immobilier du client.

Évolution structurante du modèle :

```text
DEMANDE
peut exister
AVANT
MANDAT
```

Le lien :

```text
DEMANDE.id_mandat
```

est donc optionnel.

Cela permet le parcours :

```text
prospect / client
      |
      v
demande
      |
      v
qualification
      |
      v
affectation
      |
      v
mandat éventuel
```

Origines supportées :

```text
LEGACY
GENERATED
API
MANUEL
```

Les demandes historiques `LEGACY` restent rattachées à un mandat.

---

# 10. DEMANDE_AFFECTATION

`DEMANDE_AFFECTATION` sépare la demande du processus d'affectation à un chasseur.

```text
DEMANDE
   |
   v
DEMANDE_AFFECTATION
   |
   v
CHASSEUR
```

Statuts :

```text
ASSIGNEE
ACCEPTEE
REFUSEE
```

Le modèle conserve :

```text
chasseur affecté
date d'affectation
décision
date de décision
utilisateur ayant affecté
utilisateur ayant décidé
motif éventuel de refus
```

Cette structure évite de confondre :

```text
demande
et
propriété opérationnelle de la demande
```

---

# 11. DEMANDE_VERSION

Les critères de recherche ne sont pas écrasés directement dans `DEMANDE`.

Chaque évolution produit une `DEMANDE_VERSION`.

```text
DEMANDE
   |
   +--> VERSION 1
   |
   +--> VERSION 2
   |
   +--> VERSION 3
   |
   ...
```

Les critères structurés comprennent notamment :

```text
ville
code_postal
type_bien
budget_min
budget_max
surface_min
nb_pieces_min
nb_chambres_min
dpe_max
```

Les préférences complémentaires peuvent être stockées dans :

```text
criteres_souhaites
```

---

# 12. Auteur d'une version

Chaque version possède exactement un auteur logique :

```text
CLIENT
XOR
CHASSEUR
XOR
SYSTEME
```

Le modèle physique utilise :

```text
auteur_client_id
auteur_chasseur_id
auteur_systeme
```

Cette stratégie remplace l'ancien concept polymorphe :

```text
auteur_type
auteur_id
```

et permet de conserver de véritables contraintes référentielles PostgreSQL.

---

# 13. Lineage de la demande

`DEMANDE_VERSION` contient également des informations de provenance :

```text
source_recherche_ref
ingestion_batch
```

Elles permettent d'identifier la source ou le lot ayant participé à la création d'une version.

Le lineage n'est donc pas uniquement porté par la plateforme de métadonnées : certains éléments critiques sont également conservés transactionnellement.

---

# 14. Property Domain

## SOURCE

`SOURCE` décrit l'origine d'une annonce immobilière.

Exemples :

```text
AGENCE
PARTICULIER
PLATEFORME
API
OPEN_DATA
MANUEL
AUTRE
```

Une source peut également porter un niveau de confiance.

---

# 15. BIEN

`BIEN` représente une annonce ou un bien immobilier collecté.

Principaux attributs :

```text
référence externe
type
titre
adresse
ville
code postal
coordonnées
prix
surface
pièces
chambres
DPE
description
date de publication
date de collecte
statut
source
```

Une annonce est identifiée de manière unique dans une source par :

```text
(id_source, reference_externe)
```

---

# 16. DOCUMENT

`DOCUMENT` représente un fichier associé à un bien.

Il conserve notamment :

```text
nom
type
MIME type
emplacement de stockage
checksum
classification
indexabilité IA
```

Classifications :

```text
PUBLIC
INTERNE
CONFIDENTIEL
RESTREINT
```

Cette structure prépare également les usages documentaires et IA sans imposer que tous les documents soient indexables.

---

# 17. Matching

Le matching utilise :

```text
DEMANDE_VERSION
+
BIEN
```

pour produire des candidats.

Le baseline actuellement implémenté reste déterministe.

Les principaux critères utilisés sont :

```text
localisation
budget
type de bien
surface
nombre de pièces
nombre de chambres
DPE
```

Le budget constitue notamment un filtre dur.

Le résultat sélectionné est persisté dans `PRESENTATION`.

Le moteur de matching peut évoluer indépendamment du modèle transactionnel.

---

# 18. PRESENTATION

`PRESENTATION` matérialise la sélection d'un bien pour une version de demande.

```text
DEMANDE_VERSION
       |
       v
PRESENTATION
       ^
       |
      BIEN
```

Elle conserve notamment :

```text
score de matching
date de sélection
date de présentation
statut
```

Une même paire :

```text
(id_demande_version, id_bien)
```

ne peut être créée qu'une fois.

Cela permet l'idempotence des recommandations persistées.

---

# 19. COMMENTAIRE

`COMMENTAIRE` conserve le feedback sur un bien dans le contexte d'une version de demande.

Un commentaire possède exactement un auteur :

```text
CLIENT
XOR
CHASSEUR
```

Il peut contenir :

```text
contenu
priorité
décision
```

et contribue à la traçabilité des décisions métier.

---

# 20. VISITE

`VISITE` est une entité **implémentée**.

Elle n'est plus un concept futur.

```text
PRESENTATION
      |
      v
    VISITE
```

Une visite conserve notamment :

```text
date
statut
compte rendu
note
photos
date de création
```

Statuts :

```text
PLANIFIEE
REALISEE
ANNULEE
REPORTEE
```

La note est comprise entre :

```text
0 et 5
```

Les photos sont stockées sous forme de références structurées.

---

# 21. Transaction Domain

## VENTE

`VENTE` matérialise la transaction immobilière et l'acte authentique.

Elle peut référencer :

```text
MANDAT
MANDAT_PERIODE
PRESENTATION
BIEN
CHASSEUR bénéficiaire
```

Elle contient obligatoirement :

```text
origine de vente
date de l'acte authentique
montant d'achat
```

Origines :

```text
CHASSEUR
CLIENT_SEUL
AUTRE_AGENCE
```

Le modèle distingue donc explicitement :

```text
VISITE
!=
VENTE
```

et :

```text
VENTE
!=
PAIEMENT
```

---

# 22. Acte authentique

Le modèle ne possède actuellement pas une table séparée `ACTE`.

La matérialisation métier est portée par :

```text
VENTE.date_acte_authentique
```

associée aux informations de transaction.

Une entité autonome pourrait être introduite ultérieurement si des besoins documentaires ou notariaux plus complexes apparaissent.

---

# 23. Financial Configuration

Le moteur financier est configurable et historisé.

Il repose sur :

```text
PARAMETRES_HONORAIRES

BAREME_COMMISSION

PARAMETRES_REMUNERATION
        |
        v
PALIER_PERFORMANCE
```

Les paramètres utilisés pour une transaction ne doivent pas être remplacés rétroactivement.

Le paiement conserve les références vers la configuration ayant servi au calcul.

---

# 24. PARAMETRES_HONORAIRES

Cette table configure les honoraires de l'entreprise.

Le modèle actuel permet notamment une formule :

```text
H = F + t × P
```

où :

```text
H = honoraires entreprise
F = montant fixe
t = taux proportionnel
P = prix d'achat
```

La configuration actuellement utilisée par le scénario contrôlé correspond à :

```text
F = 3000 €
t = 2.5 %
```

Pour :

```text
P = 300000 €
```

on obtient :

```text
H
=
3000
+
0.025 × 300000

=
10500 €
```

---

# 25. BAREME_COMMISSION

`BAREME_COMMISSION` conserve les tranches de taux de base.

La grille métier validée est :

| Montant d'achat        | Taux de base |
| ---------------------- | -----------: |
| [0 €, 200 000 €)       |         30 % |
| [200 000 €, 350 000 €) |         35 % |
| [350 000 €, 500 000 €) |         40 % |
| [500 000 €, 750 000 €) |         45 % |
| [750 000 €, +∞)        |         50 % |

Les barèmes peuvent également conserver des données historiques issues du système legacy.

---

# 26. PARAMETRES_REMUNERATION

`PARAMETRES_REMUNERATION` configure le moteur de rémunération du chasseur.

Les cinq critères de performance sont :

```text
délai mandat -> acte
exclusivité
nombre de ventes
nombre de mandats
nombre de visites
```

Poids :

| Critère     |     Poids |
| ----------- | --------: |
| Délai       |      25 % |
| Exclusivité |      10 % |
| Ventes      |      25 % |
| Mandats     |      15 % |
| Visites     |      25 % |
| **Total**   | **100 %** |

La base impose que la somme des poids soit exactement égale à 1.

---

# 27. PALIER_PERFORMANCE

Les critères nécessitant des seuils utilisent `PALIER_PERFORMANCE`.

Ils comprennent actuellement :

```text
DELAI_SEMAINES
VISITES
```

## Délai mandat → acte

| Délai         | Note |
| ------------- | ---: |
| ≤ 12 semaines |  100 |
| ≤ 20          |   80 |
| ≤ 28          |   60 |
| ≤ 36          |   40 |
| ≤ 48          |   20 |
| > 48          |    0 |

## Visites

| Nombre de visites | Note |
| ----------------- | ---: |
| ≤ 3               |  100 |
| ≤ 6               |   80 |
| ≤ 9               |   60 |
| ≤ 12              |   40 |
| ≤ 15              |   20 |
| > 15              |    0 |

---

# 28. Autres composantes de performance

Exclusivité :

```text
EXCLUSIF     -> 100
NON_EXCLUSIF -> 60
```

Ventes :

```text
20 points / vente
plafond 100
```

Mandats :

```text
10 points / mandat
plafond 100
```

Fenêtre de calcul :

```text
12 mois
```

---

# 29. Ancienneté

La rémunération intègre également l'ancienneté du chasseur.

Configuration :

```text
+2 % par année complète
plafond +10 %
```

L'ancienneté utilise :

```text
CHASSEUR.date_entree
```

Le modèle conserve également dans `PAIEMENT` :

```text
annees_anciennete_calcul
```

afin de figer la valeur utilisée au moment du calcul.

---

# 30. Modulation de performance

Le moteur utilise :

```text
score pivot = 50
amplitude = ±20 %
```

avec :

```text
taux plancher = 20 %
taux plafond  = 60 %
```

La logique actuelle applique les modificateurs au taux de base.

Conceptuellement :

```text
taux_final
=
taux_base
×
(
    1
    + majoration_anciennete
    + modulation_performance
)
```

puis applique les bornes configurées.

---

# 31. PAIEMENT

`PAIEMENT` ne représente plus seulement un simple versement.

Il joue trois rôles :

```text
1. état financier
2. résultat de rémunération
3. snapshot explicable du calcul
```

Il conserve notamment :

```text
montant d'achat
honoraires entreprise
montant chasseur

vente
mandat
chasseur bénéficiaire

barème
paramètres honoraires
paramètres rémunération

éligibilité
motif éventuel de refus

indicateurs utilisés
notes utilisées
score de performance

taux de base
ancienneté
modulation
taux final
```

---

# 32. Pourquoi figer le calcul dans PAIEMENT ?

Sans snapshot, une modification ultérieure des paramètres pourrait rendre impossible l'explication d'un ancien paiement.

Le modèle conserve donc :

```text
configuration utilisée
+
inputs du calcul
+
scores
+
taux
+
montants
```

Cela garantit :

```text
reproductibilité
explicabilité
auditabilité
historisation
```

Cette donnée transactionnelle peut ensuite être propagée dans le Data Warehouse.

---

# 33. Cycle de paiement

Statuts :

```text
ATTENDU
RECU
VERIFIE
PROGRAMME
PAYE
ANNULE
```

Cycle nominal :

```text
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

Le système conserve également :

```text
date de réception des honoraires
date de paiement du chasseur
```

---

# 34. Audit

`AUDIT_LOG` fournit une capacité transverse d'audit.

Il conserve :

```text
date de l'événement
schéma
table
opération
record_id
utilisateur
ancienne valeur
nouvelle valeur
contexte
```

Opérations :

```text
INSERT
UPDATE
DELETE
```

Cette structure permet notamment d'auditer :

```text
présentations
visites
ventes
paiements
changements de statuts
opérations administratives
```

sans créer une FK polymorphe vers toutes les tables métier.

---

# 35. Exemple E2E contrôlé

Un scénario de validation contrôlé a traversé la chaîne complète.

```text
Mandat          17
Mandat période   2
Demande version 137
Bien          16025
Présentation    32
Visite           6
Vente            3
Paiement          9
```

Le bien avait un prix de :

```text
300000 €
```

Le matching a produit :

```text
score = 100
```

La visite a été réalisée.

La vente a ensuite été créée avec :

```text
montant_achat = 300000 €
origine       = CHASSEUR
```

---

# 36. Résultat financier du scénario contrôlé

Honoraires entreprise :

```text
3000
+
2.5 % × 300000

=
10500 €
```

Performance :

```text
score = 63
```

Taux de base :

```text
35 %
```

Ancienneté :

```text
+2 %
```

Modulation performance :

```text
+5.2 %
```

Taux final :

```text
37.52 %
```

Rémunération chasseur :

```text
10500 × 0.3752
=
3939.60 €
```

Ces valeurs sont persistées dans le snapshot du paiement.

Ce scénario est une **fixture de validation E2E contrôlée** et non une transaction commerciale réelle.

---

# 37. OLTP

Le schéma :

```text
real_estate
```

constitue la fondation transactionnelle.

Il gère :

```text
clients
chasseurs
demandes
mandats
biens
matching
présentations
visites
ventes
rémunérations
paiements
audit
```

Le rôle de l'OLTP est principalement :

```text
intégrité métier
transactions
état courant
historisation opérationnelle
référentiel métier
```

---

# 38. Data Pipeline

Les données sont propagées par le pipeline :

```text
Source
  |
  v
RAW
  |
  v
STAGING
  |
  v
OLTP
  |
  v
WAREHOUSE
  |
  v
dbt marts
```

Orchestration :

```text
Airflow
```

Le pipeline exécute des validations entre les différentes couches.

---

# 39. Data Warehouse

Le modèle analytique utilise notamment :

```text
dim_date
dim_source
dim_localisation
dim_bien
dim_chasseur
dim_client
dim_demande_version
dim_secteur
```

et :

```text
fact_annonce
fact_mandat
fact_mandat_periode
fact_paiement
fact_presentation
fact_demande
fact_matching
fact_bien_daily
```

La relation :

```text
MANDAT
    -> fact_mandat
```

est distincte de :

```text
MANDAT_PERIODE
    -> fact_mandat_periode
```

afin de ne pas casser le grain historique de `fact_mandat`.

---

# 40. Paiement OLTP → Gold

La propagation financière suit :

```text
real_estate.paiement
        |
        v
Airflow load_warehouse
        |
        v
warehouse.fact_paiement
```

Le scénario contrôlé :

```text
id_paiement = 9
```

a été propagé dans `fact_paiement` par le pipeline Airflow normal.

Le fait analytique conserve notamment :

```text
montant_achat
montant_honoraires
montant_chasseur
statut
date acte
date réception
date paiement chasseur
```

---

# 41. Data Quality

La qualité est contrôlée à plusieurs niveaux :

```text
RAW
STAGING
OLTP
WAREHOUSE
dbt
```

Pour `paiement`, les contrôles couvrent notamment :

```text
réconciliation du nombre de lignes

réconciliation montant_achat

réconciliation montant_honoraires

réconciliation montant_chasseur

réconciliation statut

cohérence :
montant_chasseur <= montant_honoraires

complétude PAYE

réconciliation des dates
```

Ces contrôles permettent de vérifier que la propagation OLTP → Warehouse ne modifie pas la signification financière des données.

---

# 42. Lineage

Le lineage principal du domaine financier est :

```text
VENTE
  |
  v
PAIEMENT
  |
  v
FACT_PAIEMENT
  |
  v
METRICS
  |
  v
PROMETHEUS
  |
  v
GRAFANA
```

Pour les recherches :

```text
SOURCE / INGESTION
        |
        v
DEMANDE_VERSION
        |
        v
MATCHING
        |
        v
PRESENTATION
```

OpenMetadata fournit la couche de gouvernance et de visualisation du lineage.

Il ne remplace pas le Data Warehouse.

---

# 43. Observabilité des données métier

Le pipeline publie des métriques vers Prometheus via Pushgateway.

Les métriques financières comprennent :

```text
real_estate_paiements_payes_total

real_estate_honoraires_total_euros

real_estate_remunerations_chasseur_total_euros

real_estate_taux_remuneration_moyen
```

Le scénario contrôlé est visible dans Grafana avec :

```text
Paid Payments
1

Company Fees Collected
€10.50K

Hunter Remuneration Paid
€3.94K

Average Hunter Remuneration Rate
37.52 %
```

La chaîne est donc :

```text
PostgreSQL OLTP
      |
      v
Warehouse
      |
      v
Airflow metrics collector
      |
      v
Pushgateway
      |
      v
Prometheus
      |
      v
Grafana
```

---

# 44. Gouvernance

OpenMetadata est utilisé pour :

```text
catalogue
metadata
lineage
profiler
data quality
classification
gouvernance
```

La plateforme distingue clairement :

```text
PostgreSQL
=
transactionnel

RAW / STAGING
=
pipeline data

Warehouse
=
analytique

OpenMetadata
=
gouvernance / metadata / lineage

MLflow
=
MLOps
```

---

# 45. Matching et ML

Le modèle de données ne dépend pas d'un algorithme de matching particulier.

Le baseline déterministe actuel peut être remplacé ou complété par un modèle ML.

Les éléments stables restent :

```text
DEMANDE_VERSION
BIEN
PRESENTATION
score_matching
feedback
```

Cela permet de comparer :

```text
baseline déterministe
vs
modèles ML futurs
```

sans casser le modèle transactionnel.

Les expérimentations ML sont suivies dans MLflow.

---

# 46. Modèle canonique actuel

Le modèle opérationnel canonique est :

```text
CLIENT
CHASSEUR
UTILISATEUR

SECTEUR

MANDAT
MANDAT_SECTEUR
MANDAT_PERIODE

DEMANDE
DEMANDE_AFFECTATION
DEMANDE_VERSION

SOURCE
BIEN
DOCUMENT

PRESENTATION
COMMENTAIRE
VISITE

VENTE

PARAMETRES_HONORAIRES
BAREME_COMMISSION
PARAMETRES_REMUNERATION
PALIER_PERFORMANCE
PAIEMENT

AUDIT_LOG
```

---

# 47. Concepts non implémentés

Les concepts suivants ne sont pas actuellement des tables du modèle opérationnel :

```text
OFFRE
FACTURE
NOTAIRE
```

Ils pourront être ajoutés si le besoin métier le justifie.

Il ne faut plus présenter comme futures :

```text
VISITE
RENOUVELLEMENT_MANDAT
VENTE
```

car :

```text
VISITE
=
implémentée

RENOUVELLEMENT
=
MANDAT_PERIODE

VENTE
=
implémentée
```

---

# 48. Documentation détaillée

Le détail MERISE et PostgreSQL est disponible dans :

```text
docs/evidence/05-BC05/C1-MCD-Migration-SQL/
```

Documents de référence :

```text
MCD-MERISE-PROJET.md
MLD-PROJET.md
MPD-POSTGRESQL.md
```

Répartition des responsabilités :

```text
02-Data-Model.md
    =
vue canonique et architecturale

MCD
    =
concepts métier

MLD
    =
relations logiques

MPD
    =
implémentation PostgreSQL
```

---

# 49. Source de vérité

En cas de divergence documentaire, la hiérarchie de validation du projet est :

```text
Runtime
   >
Source code
   >
CI
   >
GitOps desired state
   >
Documentation
   >
Assumptions
```

Pour le schéma physique PostgreSQL, le runtime et les migrations appliquées constituent les preuves principales.

La documentation doit être réalignée sur ces preuves et non l'inverse.

---

# 50. État d'implémentation

| Capacité                     | État             |
| ---------------------------- | ---------------- |
| Client                       | RUNTIME VERIFIED |
| Chasseur                     | RUNTIME VERIFIED |
| Auth identity                | RUNTIME VERIFIED |
| Mandat                       | RUNTIME VERIFIED |
| Mandat six mois              | RUNTIME VERIFIED |
| Renouvellement               | RUNTIME VERIFIED |
| Demande pré-mandat           | RUNTIME VERIFIED |
| Affectation chasseur         | RUNTIME VERIFIED |
| Versioning critères          | RUNTIME VERIFIED |
| Data lineage demande         | IMPLEMENTED      |
| Bien / source                | RUNTIME VERIFIED |
| Matching déterministe        | RUNTIME VERIFIED |
| Présentation                 | RUNTIME VERIFIED |
| Visite                       | RUNTIME VERIFIED |
| Vente                        | RUNTIME VERIFIED |
| Paramétrage honoraires       | IMPLEMENTED      |
| Paramétrage rémunération     | IMPLEMENTED      |
| Calcul rémunération          | RUNTIME VERIFIED |
| Snapshot paiement            | RUNTIME VERIFIED |
| Lifecycle paiement           | RUNTIME VERIFIED |
| Audit transactionnel         | RUNTIME VERIFIED |
| fact_mandat_periode          | RUNTIME VERIFIED |
| fact_paiement                | RUNTIME VERIFIED |
| Paiement OLTP → Warehouse    | RUNTIME VERIFIED |
| Pipeline Airflow complet     | RUNTIME VERIFIED |
| Financial Prometheus metrics | RUNTIME VERIFIED |
| Financial Grafana KPIs       | RUNTIME VERIFIED |
| MCD V3                       | SYNCHRONIZED     |
| MLD V3                       | SYNCHRONIZED     |
| MPD PostgreSQL V3            | SYNCHRONIZED     |

---

# 51. Conclusion

Le modèle de données ne se limite plus au périmètre initial :

```text
client
mandat
demande
bien
matching
```

Il couvre désormais le cycle opérationnel :

```text
CLIENT
   |
   v
DEMANDE
   |
   v
AFFECTATION
   |
   v
VERSION
   |
   v
MATCHING
   |
   v
PRESENTATION
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

avec :

```text
historisation contractuelle
RBAC
audit
lineage
data quality
warehouse
MLOps
gouvernance
observabilité
```

Le parcours financier est également traçable jusqu'à l'observabilité :

```text
VENTE
  |
  v
PAIEMENT
  |
  v
FACT_PAIEMENT
  |
  v
PROMETHEUS
  |
  v
GRAFANA
```

Cette architecture fournit une fondation cohérente pour la suite du projet Data & IA tout en maintenant une séparation claire entre :

```text
règles métier déterministes
données transactionnelles
analytics
gouvernance
observabilité
expérimentation ML
```

---

**DATA MODEL V3 — ALIGNED WITH MCD V3 / MLD V3 / MPD V3 / MIGRATIONS 001–012**
