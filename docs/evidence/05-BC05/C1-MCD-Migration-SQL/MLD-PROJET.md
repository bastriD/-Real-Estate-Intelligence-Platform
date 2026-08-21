# MLD — Real Estate Intelligence Platform

**Projet :** Real Estate Intelligence Platform  
**Méthode :** MERISE  
**Version :** 1.0  
**Statut :** Baseline logique  
**Source :** `MCD-MERISE-PROJET.md`

---

# 1. Objectif

Le Modèle Logique de Données traduit le MCD en relations compatibles avec un SGBD relationnel.

Le chemin est :

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
```

Le MLD introduit :

- relations ;
- clés primaires ;
- clés étrangères ;
- contraintes logiques ;
- tables associatives.

Il reste encore indépendant de certains détails physiques PostgreSQL.

---

# 2. Règles de transformation

Les principales règles MERISE utilisées sont :

```text
Entity
  ->
Relation / Table
```

```text
1,N association
  ->
Foreign key on N side
```

```text
N,N association
  ->
Association relation
```

Dans le projet, `PRESENTATION` est déjà une entité associative porteuse d'attributs.

---

# 3. Relations principales

Le MLD contient :

```text
CLIENT
CHASSEUR
MANDAT
DEMANDE_VERSION
SOURCE
BIEN
PRESENTATION
DOCUMENT
```

---

# 4. CLIENT

```text
CLIENT(
    #id_client,
    nom,
    prenom,
    email,
    telephone,
    date_creation,
    statut,
    consentement_contact
)
```

Clé primaire :

```text
#id_client
```

---

# 5. CHASSEUR

```text
CHASSEUR(
    #id_chasseur,
    nom,
    prenom,
    email,
    telephone,
    statut,
    date_entree
)
```

Clé primaire :

```text
#id_chasseur
```

---

# 6. MANDAT

Relation issue des associations :

```text
CLIENT (0,N) --- SIGNE --- MANDAT (1,1)

CHASSEUR (0,N) --- GERE --- MANDAT (1,1)
```

MLD :

```text
MANDAT(
    #id_mandat,
    reference_mandat,
    date_signature,
    date_debut,
    date_fin,
    statut,
    budget_min,
    budget_max,
    commentaire,

    id_client,
    id_chasseur
)
```

Clés :

```text
PK  #id_mandat
FK  id_client   -> CLIENT.id_client
FK  id_chasseur -> CHASSEUR.id_chasseur
```

---

# 7. DEMANDE_VERSION

Association :

```text
MANDAT (0,N)
    |
 VERSIONNE
    |
DEMANDE_VERSION (1,1)
```

MLD :

```text
DEMANDE_VERSION(
    #id_demande_version,
    numero_version,
    date_version,
    type_bien,
    localisation,
    budget_min,
    budget_max,
    surface_min,
    nb_pieces_min,
    nb_chambres_min,
    exterieur_requis,
    parking_requis,
    ascenseur_requis,
    commentaire,
    active,

    id_mandat
)
```

Clés :

```text
PK #id_demande_version

FK id_mandat
   -> MANDAT.id_mandat
```

Contrainte logique :

```text
UNIQUE(id_mandat, numero_version)
```

---

# 8. SOURCE

```text
SOURCE(
    #id_source,
    nom,
    type_source,
    url_base,
    active,
    niveau_confiance,
    date_creation
)
```

Clé primaire :

```text
#id_source
```

---

# 9. BIEN

Association :

```text
SOURCE (0,N)
   |
 FOURNIT
   |
BIEN (1,1)
```

MLD :

```text
BIEN(
    #id_bien,
    reference_externe,
    titre,
    type_bien,
    adresse,
    code_postal,
    ville,
    latitude,
    longitude,
    prix,
    surface,
    nb_pieces,
    nb_chambres,
    etage,
    ascenseur,
    parking,
    balcon,
    terrasse,
    jardin,
    description,
    date_publication,
    date_collecte,
    statut,

    id_source
)
```

Clés :

```text
PK #id_bien

FK id_source
   -> SOURCE.id_source
```

---

# 10. PRESENTATION

`PRESENTATION` traduit la relation N,N entre :

```text
DEMANDE_VERSION
```

et :

```text
BIEN
```

avec attributs supplémentaires.

MLD :

```text
PRESENTATION(
    #id_presentation,
    date_selection,
    date_presentation,
    score_matching,
    score_budget,
    score_localisation,
    score_surface,
    score_criteres,
    statut,
    motif_rejet,
    commentaire_chasseur,
    feedback_client,

    id_demande_version,
    id_bien
)
```

Clés :

```text
PK #id_presentation

FK id_demande_version
   -> DEMANDE_VERSION.id_demande_version

FK id_bien
   -> BIEN.id_bien
```

Contrainte logique :

```text
UNIQUE(id_demande_version, id_bien)
```

---

# 11. DOCUMENT

Association :

```text
BIEN (0,N)
   |
 POSSEDE
   |
DOCUMENT (1,1)
```

MLD :

```text
DOCUMENT(
    #id_document,
    nom_fichier,
    type_document,
    mime_type,
    chemin_stockage,
    checksum,
    date_ajout,
    classification,
    indexable_ia,

    id_bien
)
```

Clés :

```text
PK #id_document

FK id_bien
   -> BIEN.id_bien
```

---

# 12. MLD complet

```text
CLIENT(
    #id_client,
    nom,
    prenom,
    email,
    telephone,
    date_creation,
    statut,
    consentement_contact
)


CHASSEUR(
    #id_chasseur,
    nom,
    prenom,
    email,
    telephone,
    statut,
    date_entree
)


MANDAT(
    #id_mandat,
    reference_mandat,
    date_signature,
    date_debut,
    date_fin,
    statut,
    budget_min,
    budget_max,
    commentaire,

    id_client,
    id_chasseur
)

FK id_client
   -> CLIENT.id_client

FK id_chasseur
   -> CHASSEUR.id_chasseur


DEMANDE_VERSION(
    #id_demande_version,
    numero_version,
    date_version,
    type_bien,
    localisation,
    budget_min,
    budget_max,
    surface_min,
    nb_pieces_min,
    nb_chambres_min,
    exterieur_requis,
    parking_requis,
    ascenseur_requis,
    commentaire,
    active,

    id_mandat
)

FK id_mandat
   -> MANDAT.id_mandat

UNIQUE(id_mandat, numero_version)


SOURCE(
    #id_source,
    nom,
    type_source,
    url_base,
    active,
    niveau_confiance,
    date_creation
)


BIEN(
    #id_bien,
    reference_externe,
    titre,
    type_bien,
    adresse,
    code_postal,
    ville,
    latitude,
    longitude,
    prix,
    surface,
    nb_pieces,
    nb_chambres,
    etage,
    ascenseur,
    parking,
    balcon,
    terrasse,
    jardin,
    description,
    date_publication,
    date_collecte,
    statut,

    id_source
)

FK id_source
   -> SOURCE.id_source


PRESENTATION(
    #id_presentation,
    date_selection,
    date_presentation,
    score_matching,
    score_budget,
    score_localisation,
    score_surface,
    score_criteres,
    statut,
    motif_rejet,
    commentaire_chasseur,
    feedback_client,

    id_demande_version,
    id_bien
)

FK id_demande_version
   -> DEMANDE_VERSION.id_demande_version

FK id_bien
   -> BIEN.id_bien

UNIQUE(id_demande_version, id_bien)


DOCUMENT(
    #id_document,
    nom_fichier,
    type_document,
    mime_type,
    chemin_stockage,
    checksum,
    date_ajout,
    classification,
    indexable_ia,

    id_bien
)

FK id_bien
   -> BIEN.id_bien
```

---

# 13. Vue relationnelle

```text
CLIENT
  |
  | 1,N
  v
MANDAT
  ^
  |
  | 1,N
CHASSEUR


MANDAT
  |
  | 1,N
  v
DEMANDE_VERSION


SOURCE
  |
  | 1,N
  v
BIEN


DEMANDE_VERSION
      |
      | 1,N
      v
PRESENTATION
      ^
      | 1,N
      |
     BIEN


BIEN
  |
  | 1,N
  v
DOCUMENT
```

---

# 14. Dépendances de création

Le futur script SQL devra respecter l'ordre :

```text
1. CLIENT
2. CHASSEUR
3. SOURCE
4. MANDAT
5. DEMANDE_VERSION
6. BIEN
7. PRESENTATION
8. DOCUMENT
```

Pourquoi :

```text
MANDAT
depends on
CLIENT + CHASSEUR
```

```text
DEMANDE_VERSION
depends on
MANDAT
```

```text
BIEN
depends on
SOURCE
```

```text
PRESENTATION
depends on
DEMANDE_VERSION + BIEN
```

```text
DOCUMENT
depends on
BIEN
```

---

# 15. Contraintes d'unicité

Contraintes proposées :

```text
CLIENT.email
```

à confirmer selon la règle métier.

```text
CHASSEUR.email
```

doit probablement être unique.

```text
MANDAT.reference_mandat
```

unique.

```text
DEMANDE_VERSION(id_mandat, numero_version)
```

unique.

```text
PRESENTATION(id_demande_version, id_bien)
```

unique.

---

# 16. Règles CHECK

Les règles proposées pour le MPD sont :

```text
budget_min >= 0
budget_max >= 0
budget_min <= budget_max
```

```text
surface_min >= 0
```

```text
nb_pieces_min >= 0
nb_chambres_min >= 0
```

```text
prix >= 0
surface >= 0
```

```text
score_matching BETWEEN 0 AND 100
score_budget BETWEEN 0 AND 100
score_localisation BETWEEN 0 AND 100
score_surface BETWEEN 0 AND 100
score_criteres BETWEEN 0 AND 100
```

---

# 17. Statuts CLIENT

Valeurs candidates :

```text
ACTIF
INACTIF
ARCHIVE
```

La stratégie technique sera décidée au MPD :

```text
CHECK
```

ou éventuellement table de référence.

Pour le MVP, un `CHECK` peut suffire.

---

# 18. Statuts CHASSEUR

```text
ACTIF
INACTIF
```

---

# 19. Statuts MANDAT

```text
BROUILLON
ACTIF
SUSPENDU
TERMINE
ANNULE
```

---

# 20. Statuts BIEN

```text
ACTIF
EXPIRE
VENDU
INDISPONIBLE
```

---

# 21. Statuts PRESENTATION

```text
IDENTIFIE
QUALIFIE
PRESENTE
REJETE
VISITE
RETENU
```

---

# 22. Classification DOCUMENT

Valeurs candidates :

```text
PUBLIC
INTERNE
CONFIDENTIEL
RESTREINT
```

---

# 23. Referential Integrity

Le modèle doit empêcher des situations telles que :

```text
MANDAT without CLIENT
```

```text
DEMANDE_VERSION without MANDAT
```

```text
PRESENTATION without BIEN
```

```text
DOCUMENT without BIEN
```

---

# 24. DELETE policy

Les suppressions doivent être prudentes.

## CLIENT

Un client avec historique de mandat ne doit pas forcément être supprimé physiquement.

Approche recommandée :

```text
restrict / archive
```

plutôt que cascade immédiate.

---

# 25. MANDAT

Supprimer un mandat pourrait supprimer son historique métier.

Approche recommandée :

```text
status = ANNULE / TERMINE
```

plutôt qu'une suppression physique dans le workflow normal.

---

# 26. SOURCE

Une source ayant fourni des biens historiques ne devrait pas provoquer la suppression des biens.

Approche :

```text
ON DELETE RESTRICT
```

ou :

```text
source inactive
```

---

# 27. BIEN

Un bien relié à des présentations doit préserver la traçabilité historique.

Approche :

```text
status
```

plutôt que suppression fréquente.

---

# 28. DOCUMENT

La suppression physique peut dépendre :

- du stockage objet ;
- de la rétention ;
- du RGPD ;
- de la classification.

---

# 29. Règle — une version active

Le MCD indique :

```text
one active DEMANDE_VERSION
per MANDAT
```

Une simple contrainte UNIQUE ne suffit pas directement si plusieurs lignes historiques ont :

```text
active = false
```

En PostgreSQL, le MPD pourra utiliser un **partial unique index** :

```sql
CREATE UNIQUE INDEX ...
ON demande_version(id_mandat)
WHERE active = true;
```

Cette décision appartient au MPD.

---

# 30. SOURCE + reference_externe

Une référence externe n'est unique qu'à l'intérieur d'une source.

Contrainte logique recommandée :

```text
UNIQUE(id_source, reference_externe)
```

Cela évite :

```text
Portal A / reference 123
```

d'entrer en conflit avec :

```text
Portal B / reference 123
```

---

# 31. DOCUMENT checksum

`checksum` peut éventuellement être unique si le système doit empêcher les doublons exacts.

Cependant, deux biens pourraient théoriquement partager un même fichier.

La contrainte UNIQUE globale n'est donc pas imposée dans le MLD initial.

---

# 32. Nullability logique

Certains attributs sont obligatoires.

## CLIENT

```text
nom
email
date_creation
statut
```

selon règle métier.

---

## CHASSEUR

```text
nom
email
statut
```

---

## MANDAT

```text
reference_mandat
id_client
id_chasseur
statut
```

---

## DEMANDE_VERSION

```text
numero_version
date_version
id_mandat
active
```

---

## SOURCE

```text
nom
type_source
active
```

---

## BIEN

```text
id_source
reference_externe
type_bien
statut
```

Les autres champs peuvent dépendre de la qualité de la source.

---

## PRESENTATION

```text
id_demande_version
id_bien
statut
date_selection
```

---

## DOCUMENT

```text
id_bien
nom_fichier
chemin_stockage
date_ajout
classification
indexable_ia
```

---

# 33. Matching

Les attributs :

```text
score_matching
score_budget
score_localisation
score_surface
score_criteres
```

appartiennent à :

```text
PRESENTATION
```

car ils dépendent du couple :

```text
DEMANDE_VERSION + BIEN
```

---

# 34. Historisation

Le modèle conserve :

```text
MANDAT
  |
  v
DEMANDE_VERSION 1
DEMANDE_VERSION 2
...
```

Les présentations restent liées à la version qui a servi au matching.

Cela permet de comprendre historiquement :

> Pourquoi ce bien a-t-il été sélectionné à cette date ?

---

# 35. RGPD

Données personnelles identifiables :

```text
CLIENT
CHASSEUR
```

Potentiellement :

```text
feedback_client
commentaire_chasseur
DOCUMENT
```

Les règles de conservation devront être reliées au registre RGPD.

---

# 36. RAG

Le champ :

```text
DOCUMENT.indexable_ia
```

permet de distinguer :

```text
Document stored
```

de :

```text
Document authorized for AI indexing
```

Il ne remplace pas les contrôles d'autorisation runtime.

---

# 37. Data Quality

Le futur MPD et les pipelines pourront contrôler :

```text
PK completeness
FK integrity
unique references
valid status
numeric ranges
business constraints
```

---

# 38. Indexes

Les index physiques ne sont pas définis complètement au niveau MLD.

Cependant, des candidats sont identifiés :

```text
MANDAT.id_client
MANDAT.id_chasseur

DEMANDE_VERSION.id_mandat

BIEN.id_source
BIEN.ville
BIEN.prix
BIEN.type_bien

PRESENTATION.id_demande_version
PRESENTATION.id_bien

DOCUMENT.id_bien
```

Ils devront être justifiés par les requêtes et `EXPLAIN ANALYZE`.

---

# 39. Recherche immobilière

Des requêtes probables incluent :

```text
WHERE ville = ?
```

```text
WHERE prix BETWEEN ? AND ?
```

```text
WHERE surface >= ?
```

```text
WHERE type_bien = ?
```

Ces patterns guideront l'indexation dans BC05 / C2.

---

# 40. MLD résumé

```text
CLIENT
   |
   v
MANDAT
   ^
   |
CHASSEUR

MANDAT
   |
   v
DEMANDE_VERSION

SOURCE
   |
   v
BIEN

DEMANDE_VERSION
   |
   v
PRESENTATION
   ^
   |
BIEN

BIEN
   |
   v
DOCUMENT
```

---

# 41. Préparation du MPD PostgreSQL

La prochaine étape doit décider :

- types PostgreSQL ;
- identity strategy ;
- constraints ;
- timestamps ;
- indexes ;
- partial index ;
- schemas ;
- naming convention.

---

# 42. Naming convention proposée

Tables :

```text
snake_case
singular
```

Exemple :

```text
client
chasseur
mandat
demande_version
source
bien
presentation
document
```

---

# 43. Colonnes

Convention :

```text
snake_case
```

Exemple :

```text
reference_mandat
date_signature
score_matching
```

---

# 44. PK

Convention :

```text
id_<entity>
```

Exemple :

```text
id_client
id_bien
id_mandat
```

---

# 45. FK

La foreign key conserve le nom de la PK référencée.

Exemple :

```text
id_client
```

dans :

```text
mandat
```

---

# 46. Date de création technique

Le MPD peut ajouter certains champs techniques absents du MCD strict si utiles :

```text
created_at
updated_at
```

Ces champs devront être documentés comme **attributs techniques**, pas comme nouveaux concepts métier.

---

# 47. Future entities

Les évolutions suivantes restent hors scope :

```text
VISITE
OFFRE
TRANSACTION
PUBLICATION
AI_EVALUATION
```

Le MLD V1 ne les inclut pas.

---

# 48. Preuve de cohérence

Le jury doit pouvoir suivre :

```text
MCD entity
   |
   v
MLD relation
   |
   v
SQL table
```

Exemple :

```text
MCD:
DEMANDE_VERSION

MLD:
DEMANDE_VERSION(... id_mandat)

SQL:
CREATE TABLE demande_version (...)
```

---

# 49. Matrice MCD → MLD

| MCD | MLD |
|---|---|
| CLIENT | CLIENT |
| CHASSEUR | CHASSEUR |
| MANDAT | MANDAT + FK CLIENT/CHASSEUR |
| DEMANDE_VERSION | DEMANDE_VERSION + FK MANDAT |
| SOURCE | SOURCE |
| BIEN | BIEN + FK SOURCE |
| PRESENTATION | PRESENTATION + 2 FK |
| DOCUMENT | DOCUMENT + FK BIEN |

---

# 50. Cardinalités → clés étrangères

| Association | Traduction MLD |
|---|---|
| CLIENT 0,N → MANDAT 1,1 | `MANDAT.id_client` |
| CHASSEUR 0,N → MANDAT 1,1 | `MANDAT.id_chasseur` |
| MANDAT 0,N → DEMANDE_VERSION 1,1 | `DEMANDE_VERSION.id_mandat` |
| SOURCE 0,N → BIEN 1,1 | `BIEN.id_source` |
| DEMANDE_VERSION 0,N → PRESENTATION 1,1 | `PRESENTATION.id_demande_version` |
| BIEN 0,N → PRESENTATION 1,1 | `PRESENTATION.id_bien` |
| BIEN 0,N → DOCUMENT 1,1 | `DOCUMENT.id_bien` |

---

# 51. Contraintes supplémentaires proposées

```text
UNIQUE chasseur.email

UNIQUE mandat.reference_mandat

UNIQUE (demande_version.id_mandat, numero_version)

UNIQUE (bien.id_source, reference_externe)

UNIQUE (
    presentation.id_demande_version,
    presentation.id_bien
)
```

Pour `client.email`, la décision doit dépendre du besoin métier réel.

---

# 52. Questions restantes avant MPD

À confirmer :

```text
1. CLIENT.email doit-il être unique ?
2. Un mandat doit-il obligatoirement avoir un chasseur dès sa création ?
3. Un bien peut-il exister sans source ?
4. Tous les scores de PRESENTATION sont-ils optionnels avant matching ?
5. DOCUMENT doit-il pouvoir être lié au mandat en plus du bien ?
```

Pour le MVP actuel, les hypothèses retenues sont :

```text
1. CLIENT.email unique
2. CHASSEUR obligatoire sur mandat
3. SOURCE obligatoire sur bien
4. Scores nullable jusqu'au calcul
5. DOCUMENT lié uniquement à BIEN
```

Ces hypothèses pourront évoluer via migration.

---

# 53. Validation MLD

Le MLD V1 est cohérent avec le MCD si :

```text
No entity lost
No relationship lost
Cardinalities translated
N,N resolved
Historical request preserved
Matching relationship preserved
```

---

# 54. Étape suivante

Nous pouvons maintenant construire le :

```text
MPD PostgreSQL
```

puis :

```text
migration.sql
```

Le MPD définira les choix techniques précis nécessaires pour PostgreSQL.

---

# 55. Statut

| Élément | Statut |
|---|---|
| MCD | COMPLETE |
| Entity → relation mapping | COMPLETE |
| FK mapping | COMPLETE |
| N,N mapping | COMPLETE |
| Logical constraints | COMPLETE |
| Status domains | DEFINED |
| Nullability | BASELINE DEFINED |
| Index candidates | IDENTIFIED |
| PostgreSQL types | NEXT |
| MPD | NEXT |
| migration.sql | AFTER MPD |

---

# 56. Conclusion

Le MLD traduit le modèle conceptuel en huit relations principales :

```text
CLIENT
CHASSEUR
MANDAT
DEMANDE_VERSION
SOURCE
BIEN
PRESENTATION
DOCUMENT
```

avec les relations :

```text
CLIENT -> MANDAT
CHASSEUR -> MANDAT
MANDAT -> DEMANDE_VERSION
SOURCE -> BIEN
DEMANDE_VERSION -> PRESENTATION
BIEN -> PRESENTATION
BIEN -> DOCUMENT
```

La structure est désormais suffisamment précise pour produire le modèle physique PostgreSQL sans perdre la logique métier définie dans le MCD.

---

**MLD V1 — READY FOR POSTGRESQL MPD**