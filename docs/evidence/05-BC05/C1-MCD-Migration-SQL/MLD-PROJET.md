# MLD — Real Estate Intelligence Platform

**Projet :** Real Estate Intelligence Platform  
**Méthode :** MERISE  
**Version :** 2.0  
**Statut :** Baseline logique corrigée  
**Source :** `MCD-MERISE-PROJET.md` V2

---

# 1. Objectif

Le Modèle Logique de Données traduit le MCD cible en relations relationnelles indépendantes des détails physiques PostgreSQL.

Chaîne :

```text
Legacy Model
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
```

Le MLD définit :

- relations ;
- clés primaires ;
- clés étrangères ;
- associations ;
- contraintes d'unicité ;
- historisation ;
- dépendances logiques.

---

# 2. Modèle hérité

Le système existant contient :

```text
SECTEURS
UTILISATEURS
MANDATS
```

Le modèle cible ne modifie pas directement ces relations.

Il crée une nouvelle structure puis migre les données depuis l'existant.

---

# 3. Relations cibles

Le MLD V2 contient :

```text
CLIENT
CHASSEUR
SECTEUR
MANDAT
MANDAT_SECTEUR
DEMANDE
DEMANDE_VERSION
SOURCE
BIEN
PRESENTATION
COMMENTAIRE
DOCUMENT
BAREME_COMMISSION
PAIEMENT
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
    ville,
    date_creation,
    statut,
    consentement_contact
)
```

Clé primaire :

```text
#id_client
```

Contrainte candidate :

```text
UNIQUE(email)
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
    date_entree,
    statut
)
```

Clé primaire :

```text
#id_chasseur
```

Contrainte :

```text
UNIQUE(email)
```

Le champ historique :

```text
utilisateurs.taux_commission
```

n'est pas conservé directement ici.

Il est migré vers :

```text
BAREME_COMMISSION
```

---

# 6. SECTEUR

```text
SECTEUR(
    #id_secteur,
    pays,
    ville,
    quartier,
    code_postal,
    actif
)
```

Clé primaire :

```text
#id_secteur
```

Cette relation est dérivée de la table héritée :

```text
secteurs
```

avec extension pour l'internationalisation.

---

# 7. MANDAT

```text
MANDAT(
    #id_mandat,
    reference_mandat,
    type_mandat,
    date_signature,
    mode_signature,
    date_debut,
    date_fin,
    statut,
    commentaire,

    id_client,
    id_chasseur
)
```

Clés :

```text
PK #id_mandat

FK id_client
   -> CLIENT.id_client

FK id_chasseur
   -> CHASSEUR.id_chasseur
```

Contrainte :

```text
UNIQUE(reference_mandat)
```

---

# 8. Règle durée mandat

Le besoin métier impose une durée de six mois.

Règle logique :

```text
date_fin = date_signature + 6 mois
```

ou équivalent selon le processus de renouvellement.

Le MPD devra préciser si cette règle est :

- calculée ;
- générée ;
- vérifiée par CHECK ;
- appliquée dans la couche applicative.

---

# 9. MANDAT_SECTEUR

Le MCD permet à un mandat de cibler plusieurs secteurs.

Association N,N :

```text
MANDAT
   |
   v
MANDAT_SECTEUR
   ^
   |
SECTEUR
```

MLD :

```text
MANDAT_SECTEUR(
    #id_mandat,
    #id_secteur
)
```

Clés :

```text
PK(
    id_mandat,
    id_secteur
)

FK id_mandat
   -> MANDAT.id_mandat

FK id_secteur
   -> SECTEUR.id_secteur
```

---

# 10. DEMANDE

```text
DEMANDE(
    #id_demande,
    date_creation,
    statut,

    id_mandat
)
```

Clés :

```text
PK #id_demande

FK id_mandat
   -> MANDAT.id_mandat
```

---

# 11. Pourquoi DEMANDE

`MANDAT` et `DEMANDE` représentent deux concepts différents.

```text
MANDAT
=
Contractual relationship
```

```text
DEMANDE
=
Real-estate search
```

Cette séparation permet :

- renouvellement de mandat ;
- historisation des critères ;
- évolution métier ;
- meilleure modélisation IA.

---

# 12. DEMANDE_VERSION

```text
DEMANDE_VERSION(
    #id_demande_version,

    numero_version,
    date_version,

    auteur_type,
    auteur_id,
    motif_modification,

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

    id_demande
)
```

Clés :

```text
PK #id_demande_version

FK id_demande
   -> DEMANDE.id_demande
```

Contrainte :

```text
UNIQUE(
    id_demande,
    numero_version
)
```

---

# 13. Historisation demande

Le système conserve :

```text
DEMANDE
    |
    +--> VERSION 1
    +--> VERSION 2
    +--> VERSION 3
```

Chaque version doit conserver :

```text
date_version
auteur_type
auteur_id
motif_modification
```

---

# 14. auteur_type

Valeurs candidates :

```text
CLIENT
CHASSEUR
SYSTEME
```

---

# 15. auteur_id

`auteur_id` est un identifiant logique dépendant de :

```text
auteur_type
```

Cette modélisation est volontairement flexible mais soulève une difficulté d'intégrité référentielle.

Deux options seront évaluées au MPD :

```text
1. auteur_client_id + auteur_chasseur_id
```

ou :

```text
2. author abstraction / actor table
```

Le MPD devra choisir une approche qui permette une intégrité réelle.

---

# 16. Critères structurés

Les critères tels que :

```text
ville
code_postal
type_bien
budget_max
surface_min
nb_pieces_min
nb_chambres_min
dpe_max
criteres_souhaites
```

proviennent du besoin métier et du générateur de données StarterPack.

---

# 17. criteres_souhaites

Au niveau logique, ce champ représente un ensemble de préférences.

Possibilités physiques futures :

```text
JSONB
```

ou :

```text
DEMANDE_CRITERE
```

Le choix sera effectué au MPD.

---

# 18. SOURCE

```text
SOURCE(
    #id_source,
    nom,
    type_source,
    url_base,
    actif,
    niveau_confiance
)
```

Clé primaire :

```text
#id_source
```

---

# 19. BIEN

```text
BIEN(
    #id_bien,

    reference_externe,
    type_bien,
    titre,

    adresse,
    code_postal,
    ville,

    latitude,
    longitude,

    prix,
    surface,

    nb_pieces,
    nb_chambres,

    dpe,

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

Contrainte logique :

```text
UNIQUE(
    id_source,
    reference_externe
)
```

---

# 20. Données brutes et BIEN

Les données générées et les futures sources ne doivent pas être insérées directement dans `BIEN` sans normalisation.

Architecture :

```text
RAW
 |
 v
STAGING
 |
 v
VALIDATION
 |
 v
BIEN
```

`BIEN` représente le modèle canonique normalisé.

---

# 21. PRESENTATION

```text
PRESENTATION(
    #id_presentation,

    date_selection,
    date_presentation,

    score_matching,

    statut,

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

Contrainte :

```text
UNIQUE(
    id_demande_version,
    id_bien
)
```

---

# 22. Rôle de PRESENTATION

Cette relation représente :

```text
DEMANDE_VERSION
       |
       v
Matching / Selection
       |
       v
BIEN
```

Elle porte les données propres au rapprochement :

```text
score
status
selection date
presentation date
```

---

# 23. COMMENTAIRE

```text
COMMENTAIRE(
    #id_commentaire,

    date_commentaire,

    auteur_type,
    auteur_id,

    contenu,
    priorite,
    decision,

    id_demande_version,
    id_bien
)
```

Clés :

```text
PK #id_commentaire

FK id_demande_version
   -> DEMANDE_VERSION.id_demande_version

FK id_bien
   -> BIEN.id_bien
```

---

# 24. Auteur commentaire

Un commentaire peut provenir d'un :

```text
CLIENT
```

ou d'un :

```text
CHASSEUR
```

Comme pour `DEMANDE_VERSION`, le MPD doit résoudre proprement cette relation polymorphe.

---

# 25. Décisions commentaire

Valeurs candidates :

```text
RETENIR
ECARTER
VISITER
REQUALIFIER
INFORMATION
```

Elles seront validées au MPD.

---

# 26. PRESENTATION vs COMMENTAIRE

`PRESENTATION` est une relation système/métier :

```text
this property was selected
for this request version
```

`COMMENTAIRE` représente :

```text
a human interaction or opinion
on this property
within the context of the request
```

Plusieurs commentaires peuvent exister pour une même présentation.

---

# 27. DOCUMENT

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

# 28. BAREME_COMMISSION

```text
BAREME_COMMISSION(
    #id_bareme,

    montant_min,
    montant_max,

    taux_commission,
    montant_fixe,

    date_debut_validite,
    date_fin_validite,

    actif,

    id_chasseur
)
```

Clés :

```text
PK #id_bareme

FK id_chasseur
   -> CHASSEUR.id_chasseur
```

---

# 29. Pourquoi BAREME_COMMISSION

Le SI hérité stocke :

```text
taux_commission
```

directement dans `utilisateurs`.

Cela ne permet pas correctement :

```text
historisation
different ranges
different periods
```

Le modèle cible permet :

```text
CHASSEUR
   |
   +--> BAREME A
   +--> BAREME B
   +--> BAREME C
```

---

# 30. Tranches de montant

Un barème peut s'appliquer à :

```text
montant_min <= montant < montant_max
```

selon la règle physique retenue.

Le MPD devra éviter :

```text
overlapping active ranges
```

pour un même chasseur et une même période lorsque nécessaire.

---

# 31. Temporalité barème

Le barème doit conserver :

```text
date_debut_validite
date_fin_validite
```

pour connaître la règle applicable historiquement.

---

# 32. PAIEMENT

```text
PAIEMENT(
    #id_paiement,

    date_acte_authentique,

    montant_achat,
    montant_honoraires,
    montant_chasseur,

    date_reception_honoraires,
    date_paiement_chasseur,

    statut,

    id_mandat,
    id_bareme
)
```

Clés :

```text
PK #id_paiement

FK id_mandat
   -> MANDAT.id_mandat

FK id_bareme
   -> BAREME_COMMISSION.id_bareme
```

---

# 33. Pourquoi id_bareme dans PAIEMENT

Le paiement doit pouvoir répondre historiquement à :

```text
Which commission scale was used?
```

Sans cette relation, une modification future du barème rendrait le calcul historique moins traçable.

---

# 34. Statuts paiement

Valeurs candidates :

```text
ATTENDU
RECU
VERIFIE
PROGRAMME
PAYE
ANNULE
```

Le MPD devra confirmer les valeurs retenues.

---

# 35. Flux financier

```text
Acte authentique
       |
       v
Honoraires entreprise
       |
       v
PAIEMENT
       |
       v
Barème applicable
       |
       v
Rémunération chasseur
```

---

# 36. MLD complet

```text
CLIENT(
    #id_client,
    nom,
    prenom,
    email,
    telephone,
    ville,
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
    date_entree,
    statut
)


SECTEUR(
    #id_secteur,
    pays,
    ville,
    quartier,
    code_postal,
    actif
)


MANDAT(
    #id_mandat,
    reference_mandat,
    type_mandat,
    date_signature,
    mode_signature,
    date_debut,
    date_fin,
    statut,
    commentaire,

    id_client,
    id_chasseur
)


MANDAT_SECTEUR(
    #id_mandat,
    #id_secteur
)


DEMANDE(
    #id_demande,
    date_creation,
    statut,

    id_mandat
)


DEMANDE_VERSION(
    #id_demande_version,
    numero_version,
    date_version,

    auteur_type,
    auteur_id,
    motif_modification,

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

    id_demande
)


SOURCE(
    #id_source,
    nom,
    type_source,
    url_base,
    actif,
    niveau_confiance
)


BIEN(
    #id_bien,
    reference_externe,
    type_bien,
    titre,

    adresse,
    code_postal,
    ville,

    latitude,
    longitude,

    prix,
    surface,

    nb_pieces,
    nb_chambres,

    dpe,

    description,

    date_publication,
    date_collecte,

    statut,

    id_source
)


PRESENTATION(
    #id_presentation,

    date_selection,
    date_presentation,

    score_matching,
    statut,

    id_demande_version,
    id_bien
)


COMMENTAIRE(
    #id_commentaire,

    date_commentaire,

    auteur_type,
    auteur_id,

    contenu,
    priorite,
    decision,

    id_demande_version,
    id_bien
)


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


BAREME_COMMISSION(
    #id_bareme,

    montant_min,
    montant_max,

    taux_commission,
    montant_fixe,

    date_debut_validite,
    date_fin_validite,

    actif,

    id_chasseur
)


PAIEMENT(
    #id_paiement,

    date_acte_authentique,

    montant_achat,
    montant_honoraires,
    montant_chasseur,

    date_reception_honoraires,
    date_paiement_chasseur,

    statut,

    id_mandat,
    id_bareme
)
```

---

# 37. Foreign Keys

```text
MANDAT.id_client
    -> CLIENT.id_client
```

```text
MANDAT.id_chasseur
    -> CHASSEUR.id_chasseur
```

```text
MANDAT_SECTEUR.id_mandat
    -> MANDAT.id_mandat
```

```text
MANDAT_SECTEUR.id_secteur
    -> SECTEUR.id_secteur
```

```text
DEMANDE.id_mandat
    -> MANDAT.id_mandat
```

```text
DEMANDE_VERSION.id_demande
    -> DEMANDE.id_demande
```

```text
BIEN.id_source
    -> SOURCE.id_source
```

```text
PRESENTATION.id_demande_version
    -> DEMANDE_VERSION.id_demande_version
```

```text
PRESENTATION.id_bien
    -> BIEN.id_bien
```

```text
COMMENTAIRE.id_demande_version
    -> DEMANDE_VERSION.id_demande_version
```

```text
COMMENTAIRE.id_bien
    -> BIEN.id_bien
```

```text
DOCUMENT.id_bien
    -> BIEN.id_bien
```

```text
BAREME_COMMISSION.id_chasseur
    -> CHASSEUR.id_chasseur
```

```text
PAIEMENT.id_mandat
    -> MANDAT.id_mandat
```

```text
PAIEMENT.id_bareme
    -> BAREME_COMMISSION.id_bareme
```

---

# 38. Contraintes d'unicité

```text
CLIENT.email
```

```text
CHASSEUR.email
```

```text
MANDAT.reference_mandat
```

```text
DEMANDE_VERSION(
    id_demande,
    numero_version
)
```

```text
BIEN(
    id_source,
    reference_externe
)
```

```text
PRESENTATION(
    id_demande_version,
    id_bien
)
```

```text
MANDAT_SECTEUR(
    id_mandat,
    id_secteur
)
```

---

# 39. Contraintes numériques

```text
budget_min >= 0
budget_max >= 0
budget_min <= budget_max
```

```text
surface_min >= 0
```

```text
prix >= 0
surface >= 0
```

```text
score_matching BETWEEN 0 AND 100
```

```text
montant_min >= 0
montant_max >= montant_min
```

```text
taux_commission >= 0
```

```text
montant_achat >= 0
montant_honoraires >= 0
montant_chasseur >= 0
```

---

# 40. DPE

Valeurs candidates :

```text
A
B
C
D
E
F
G
```

et éventuellement :

```text
NULL
```

lorsqu'absent.

---

# 41. Une version active

La règle :

```text
one active version
per DEMANDE
```

devra être matérialisée physiquement.

PostgreSQL permet un :

```text
partial unique index
```

---

# 42. Relation auteur polymorphe

Deux relations restent volontairement à résoudre au MPD :

```text
DEMANDE_VERSION.auteur_type / auteur_id
COMMENTAIRE.auteur_type / auteur_id
```

Une base relationnelle ne peut pas faire une FK classique vers deux tables différentes.

Le MPD devra donc choisir entre :

```text
A. ACTEUR
```

ou :

```text
B. separate nullable foreign keys
```

---

# 43. Option ACTEUR

Une possibilité :

```text
ACTEUR
├── id_acteur
├── type
└── ...
```

puis :

```text
CLIENT -> ACTEUR
CHASSEUR -> ACTEUR
```

Cependant cela réintroduit partiellement une abstraction proche de l'ancien `utilisateurs`.

Cette option n'est donc pas retenue automatiquement.

---

# 44. Option FK séparées

Alternative :

```text
auteur_client_id
auteur_chasseur_id
auteur_systeme
```

avec contrainte garantissant qu'un seul auteur logique est défini.

Cette approche sera probablement plus lisible pour le MVP.

---

# 45. Migration héritée

Mapping principal :

```text
utilisateurs.role = client
        |
        v
CLIENT
```

```text
utilisateurs.role = chasseur
        |
        v
CHASSEUR
```

---

# 46. Migration taux commission

```text
utilisateurs.taux_commission
        |
        v
BAREME_COMMISSION
```

Une ligne initiale sera créée pour chaque chasseur disposant d'un taux.

Le barème hérité ne contient pas nécessairement l'historique complet ; cette limitation devra être documentée.

---

# 47. Migration budget_max

Le champ hérité :

```text
utilisateurs.budget_max
```

associé aux clients est une anomalie de modélisation.

La valeur doit être migrée vers la première demande structurée lorsqu'elle peut être reliée correctement.

---

# 48. Migration mandat

```text
legacy mandats
      |
      v
MANDAT
```

Les informations existantes telles que :

```text
client_id
chasseur_id
secteur_id
exclusif
date_debut
statut
```

seront migrées.

---

# 49. description_recherche

```text
legacy mandats.description_recherche
```

doit être conservé comme source de migration.

La transformation vers :

```text
DEMANDE_VERSION
```

ne doit pas inventer des valeurs non déductibles.

---

# 50. Première demande

Pour chaque mandat hérité :

```text
MANDAT
   |
   v
DEMANDE
   |
   v
DEMANDE_VERSION 1
```

peut être créé.

Les champs structurables sont alimentés lorsque l'information est disponible.

---

# 51. StarterPack Generator

Les données générées :

```text
recherches.csv
annonces.csv
json/*.json
```

ne sont pas des données héritées.

Elles alimenteront les pipelines de test et d'ingestion.

---

# 52. Mapping recherche générée

```text
recherches.reference
      |
      v
DEMANDE / external reference if needed
```

```text
recherches.ville
      |
      v
DEMANDE_VERSION.ville
```

```text
budget_max
surface_min
type_bien
...
      |
      v
DEMANDE_VERSION
```

---

# 53. Mapping annonce générée

Les annonces passent d'abord par :

```text
RAW
```

puis :

```text
STAGING
```

avant d'alimenter :

```text
SOURCE
BIEN
```

---

# 54. Internationalisation

Le modèle logique évite de supposer que :

```text
code_postal
```

est toujours un code postal français.

La conception physique devra éviter des types ou validations trop franco-françaises.

---

# 55. Performance chasseur

Les indicateurs de performance ne deviennent pas nécessairement une table OLTP.

Ils peuvent être calculés dans :

```text
warehouse
analytics
```

à partir de :

```text
MANDAT
PRESENTATION
PAIEMENT
future VISITE
```

---

# 56. Extensions futures

Le parcours complet peut nécessiter :

```text
VISITE
OFFRE
FACTURE
ACTE
RENOUVELLEMENT_MANDAT
```

Elles ne font pas partie du MLD V2 minimum.

---

# 57. Pourquoi ne pas tout ajouter immédiatement

Le modèle doit satisfaire :

```text
current required deliverables
+
future AI/data requirements
```

sans créer prématurément une application métier complète.

---

# 58. Dépendances de création

Ordre logique :

```text
1. CLIENT
2. CHASSEUR
3. SECTEUR
4. SOURCE

5. MANDAT
6. MANDAT_SECTEUR

7. DEMANDE
8. DEMANDE_VERSION

9. BIEN

10. PRESENTATION
11. COMMENTAIRE
12. DOCUMENT

13. BAREME_COMMISSION
14. PAIEMENT
```

---

# 59. Vue relationnelle

```text
CLIENT
   |
   v
MANDAT <------- CHASSEUR
   |
   +--------> MANDAT_SECTEUR <------ SECTEUR
   |
   v
DEMANDE
   |
   v
DEMANDE_VERSION
   |
   +-----------> PRESENTATION <---------- BIEN
   |
   +-----------> COMMENTAIRE <-----------+
                                            |
                                            +--> SOURCE
                                            |
                                            +--> DOCUMENT


CHASSEUR
    |
    v
BAREME_COMMISSION
    |
    v
PAIEMENT <--------- MANDAT
```

---

# 60. Traçabilité MCD → MLD

| MCD | MLD |
|---|---|
| CLIENT | CLIENT |
| CHASSEUR | CHASSEUR |
| SECTEUR | SECTEUR |
| MANDAT | MANDAT |
| MANDAT ↔ SECTEUR | MANDAT_SECTEUR |
| DEMANDE | DEMANDE |
| DEMANDE_VERSION | DEMANDE_VERSION |
| SOURCE | SOURCE |
| BIEN | BIEN |
| PRESENTATION | PRESENTATION |
| COMMENTAIRE | COMMENTAIRE |
| DOCUMENT | DOCUMENT |
| BAREME_COMMISSION | BAREME_COMMISSION |
| PAIEMENT | PAIEMENT |

---

# 61. Différence MLD V1 → V2

Ajouts :

```text
SECTEUR
MANDAT_SECTEUR
DEMANDE
COMMENTAIRE
BAREME_COMMISSION
PAIEMENT
```

Corrections :

```text
MANDAT
DEMANDE_VERSION
```

---

# 62. DEMANDE_VERSION corrigée

La version précédente ne conservait pas explicitement :

```text
author
reason
```

La V2 ajoute :

```text
auteur_type
auteur_id
motif_modification
```

conformément au besoin d'historisation.

---

# 63. MANDAT corrigé

La V2 ajoute :

```text
type_mandat
date_signature
mode_signature
date_fin
```

pour représenter correctement le mandat légal.

---

# 64. Commission corrigée

La rémunération n'est plus un simple attribut du chasseur.

```text
CHASSEUR
      |
      v
BAREME_COMMISSION
```

permet :

- tranches ;
- historique ;
- évolution temporelle.

---

# 65. Matching

Le matching conserve le modèle :

```text
DEMANDE_VERSION
        |
        v
PRESENTATION
        ^
        |
       BIEN
```

Cette partie de notre conception précédente reste pertinente.

---

# 66. Feedback métier

Les commentaires sont désormais modélisés séparément :

```text
DEMANDE_VERSION
      +
BIEN
      +
AUTHOR
      |
      v
COMMENTAIRE
```

Cela correspond mieux au parcours utilisateur officiel.

---

# 67. RGPD

Les relations les plus sensibles sont notamment :

```text
CLIENT
CHASSEUR
COMMENTAIRE
PAIEMENT
DOCUMENT
```

Le Data Warehouse ne devra pas recopier automatiquement toutes leurs colonnes.

---

# 68. IA

Le matching doit pouvoir fonctionner à partir de :

```text
DEMANDE_VERSION
+
BIEN
```

sans exposer inutilement :

```text
CLIENT
```

au modèle.

---

# 69. MLD minimum cible

Le modèle logique adopté avant MPD est :

```text
CLIENT
CHASSEUR
SECTEUR
MANDAT
MANDAT_SECTEUR
DEMANDE
DEMANDE_VERSION
SOURCE
BIEN
PRESENTATION
COMMENTAIRE
DOCUMENT
BAREME_COMMISSION
PAIEMENT
```

---

# 70. Questions MPD

Le prochain document devra décider précisément :

```text
PostgreSQL types
identity strategy
enum/check strategy
JSONB vs criterion relation
author FK strategy
date_fin enforcement
commission range enforcement
indexes
schema naming
migration strategy
```

---

# 71. Statut

| Élément | Statut |
|---|---|
| Legacy mapping | COMPLETE |
| Client / hunter split | COMPLETE |
| Sector mapping | COMPLETE |
| Mandate correction | COMPLETE |
| Structured demand | COMPLETE |
| Demand history | COMPLETE |
| Matching model | COMPLETE |
| Comments | COMPLETE |
| Commission model | COMPLETE |
| Payment model | COMPLETE |
| Generator mapping | COMPLETE |
| Logical constraints | COMPLETE |
| Polymorphic author strategy | TO RESOLVE IN MPD |
| PostgreSQL types | NEXT |
| MPD V2 | NEXT |
| migration.sql | AFTER MPD |

---

# 72. Conclusion

Le MLD V2 traduit désormais le modèle métier attendu en un schéma relationnel cohérent.

La transformation principale est :

```text
LEGACY
utilisateurs
secteurs
mandats

      |
      v

TARGET

CLIENT
CHASSEUR
SECTEUR
MANDAT
DEMANDE
DEMANDE_VERSION
BIEN
COMMENTAIRE
PRESENTATION
BAREME_COMMISSION
PAIEMENT
```

avec des extensions utiles pour :

```text
SOURCE
DOCUMENT
```

Le modèle est maintenant prêt pour une traduction physique PostgreSQL.

---

**MLD V2 — READY FOR MPD POSTGRESQL V2**