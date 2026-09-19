# MLD — Real Estate Intelligence Platform

**Projet :** PROJECT_FIL_ROUGE / CHASSE_IMMOBILIERE
**Méthode :** MERISE
**Version :** 3.0
**Statut :** Modèle logique aligné avec l’implémentation
**Source conceptuelle :** `MCD-MERISE-PROJET.md` V3
**Périmètre :** migrations 001 à 012
**Dernière mise à jour :** 2026-09-15

---

# 1. Objectif

Le Modèle Logique de Données traduit le MCD V3 en relations relationnelles.

La chaîne de conception est :

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
MPD PostgreSQL
      |
      v
Migrations 001 -> 012
      |
      v
PostgreSQL runtime
```

Cette version remplace le MLD V2 historique.

Elle ne décrit plus un modèle futur à construire : elle représente le modèle relationnel actuellement implémenté.

---

# 2. Principales évolutions depuis le MLD V2

Le MLD V2 contenait principalement :

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

Le modèle courant ajoute notamment :

```text
MANDAT_PERIODE
DEMANDE_AFFECTATION
UTILISATEUR
VISITE
VENTE
PARAMETRES_HONORAIRES
PARAMETRES_REMUNERATION
PALIER_PERFORMANCE
AUDIT_LOG
```

Le modèle comporte donc actuellement **23 relations OLTP**.

Plusieurs relations historiques ont également évolué :

```text
DEMANDE
DEMANDE_VERSION
CHASSEUR
BAREME_COMMISSION
PAIEMENT
```

---

# 3. Relations du modèle logique

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
PRESENTATION
COMMENTAIRE
DOCUMENT
VISITE

VENTE

BAREME_COMMISSION
PARAMETRES_HONORAIRES
PARAMETRES_REMUNERATION
PALIER_PERFORMANCE
PAIEMENT

AUDIT_LOG
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
PK(id_client)
```

Contrainte candidate :

```text
UNIQUE(email)
```

Statuts :

```text
ACTIF
INACTIF
ARCHIVE
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
PK(id_chasseur)
```

Contrainte :

```text
UNIQUE(email)
```

Statuts :

```text
ACTIF
INACTIF
```

`date_entree` participe au calcul de l’ancienneté utilisé par la rémunération.

Pour les données historiques ne disposant pas d’une source RH certifiée, cette date peut provenir de la première activité métier connue avec provenance documentée.

---

# 6. UTILISATEUR

```text
UTILISATEUR(
    #id_utilisateur,
    email,
    password_hash,
    role,
    actif,
    id_client?,
    id_chasseur?,
    derniere_connexion,
    date_creation,
    date_modification
)
```

Clés :

```text
PK(id_utilisateur)

FK id_client
    -> CLIENT.id_client

FK id_chasseur
    -> CHASSEUR.id_chasseur
```

Rôles :

```text
ADMIN
CLIENT
CHASSEUR
SERVICE
```

Règle d’identité métier :

```text
role = CLIENT
    => id_client NOT NULL
       AND id_chasseur NULL

role = CHASSEUR
    => id_chasseur NOT NULL
       AND id_client NULL

role IN (ADMIN, SERVICE)
    => id_client NULL
       AND id_chasseur NULL
```

`UTILISATEUR` représente l’identité applicative.

`CLIENT` et `CHASSEUR` restent les identités métier.

---

# 7. SECTEUR

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

Clé :

```text
PK(id_secteur)
```

Unicité logique :

```text
UNIQUE(
    pays,
    ville,
    quartier,
    code_postal
)
```

---

# 8. MANDAT

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
PK(id_mandat)

FK id_client
    -> CLIENT.id_client

FK id_chasseur
    -> CHASSEUR.id_chasseur
```

Contrainte :

```text
UNIQUE(reference_mandat)
```

Types :

```text
EXCLUSIF
NON_EXCLUSIF
```

Modes de signature :

```text
PAPIER
ELECTRONIQUE
AUTRE
INCONNU
```

Statuts :

```text
BROUILLON
ACTIF
SUSPENDU
TERMINE
EXPIRE
ANNULE
```

Règle temporelle minimale :

```text
date_fin >= date_debut
```

La durée contractuelle détaillée est historisée dans `MANDAT_PERIODE`.

---

# 9. MANDAT_SECTEUR

Association N,N entre mandat et secteur :

```text
MANDAT_SECTEUR(
    #id_mandat,
    #id_secteur
)
```

Clé primaire composée :

```text
PK(
    id_mandat,
    id_secteur
)
```

Clés étrangères :

```text
FK id_mandat
    -> MANDAT.id_mandat

FK id_secteur
    -> SECTEUR.id_secteur
```

---

# 10. MANDAT_PERIODE

```text
MANDAT_PERIODE(
    #id_mandat_periode,
    id_mandat,
    numero_periode,
    type_periode,
    date_debut,
    date_fin,
    date_renouvellement,
    commentaire,
    est_historique_legacy,
    created_at
)
```

Clés :

```text
PK(id_mandat_periode)

FK id_mandat
    -> MANDAT.id_mandat
```

Unicité :

```text
UNIQUE(
    id_mandat,
    numero_periode
)
```

Types :

```text
INITIAL
RENOUVELLEMENT
```

Règle :

```text
numero_periode >= 1
```

Pour une période standard :

```text
date_fin = date_debut + 6 mois
```

Les périodes explicitement identifiées comme historiques legacy peuvent être exemptées de cette contrainte lorsque la donnée historique ne permet pas de garantir la durée contractuelle.

Règle de renouvellement :

```text
INITIAL
    => date_renouvellement IS NULL

RENOUVELLEMENT
    => date_renouvellement IS NOT NULL
```

Le renouvellement ne remplace pas une période précédente.

Il crée une nouvelle relation `MANDAT_PERIODE`.

---

# 11. DEMANDE

```text
DEMANDE(
    #id_demande,
    reference_demande,
    date_creation,
    statut,
    id_mandat?,
    origine
)
```

Clés :

```text
PK(id_demande)

FK id_mandat
    -> MANDAT.id_mandat
```

`id_mandat` est **optionnel**.

C’est une évolution importante par rapport au MLD V2 :

```text
DEMANDE
peut exister
AVANT
MANDAT
```

Unicité :

```text
UNIQUE(reference_demande)
```

Statuts :

```text
ACTIVE
SUSPENDUE
CLOTUREE
ANNULEE
```

Origines :

```text
LEGACY
GENERATED
API
MANUEL
```

Règle historique :

```text
origine = LEGACY
    => id_mandat NOT NULL
```

---

# 12. DEMANDE_AFFECTATION

```text
DEMANDE_AFFECTATION(
    #id_affectation,
    id_demande,
    id_chasseur,
    statut,
    date_affectation,
    date_decision,
    id_utilisateur_affectation?,
    id_utilisateur_decision?,
    motif_refus
)
```

Clés :

```text
PK(id_affectation)

FK id_demande
    -> DEMANDE.id_demande

FK id_chasseur
    -> CHASSEUR.id_chasseur

FK id_utilisateur_affectation
    -> UTILISATEUR.id_utilisateur

FK id_utilisateur_decision
    -> UTILISATEUR.id_utilisateur
```

Statuts :

```text
ASSIGNEE
ACCEPTEE
REFUSEE
```

Cycle logique :

```text
ASSIGNEE
    => date_decision NULL

ACCEPTEE
    => date_decision NOT NULL

REFUSEE
    => date_decision NOT NULL
```

Règle temporelle :

```text
date_decision >= date_affectation
```

Le motif de refus n’est applicable qu’à une affectation refusée.

Une règle d’unicité opérationnelle empêche plusieurs affectations courantes simultanées pour une même demande.

---

# 13. DEMANDE_VERSION

```text
DEMANDE_VERSION(
    #id_demande_version,
    numero_version,
    date_version,
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

    description_recherche_legacy,
    active,

    id_demande,

    auteur_client_id?,
    auteur_chasseur_id?,
    auteur_systeme,

    source_recherche_ref,
    ingestion_batch
)
```

Clés :

```text
PK(id_demande_version)

FK id_demande
    -> DEMANDE.id_demande

FK auteur_client_id
    -> CLIENT.id_client

FK auteur_chasseur_id
    -> CHASSEUR.id_chasseur
```

Unicité :

```text
UNIQUE(
    id_demande,
    numero_version
)
```

Règle :

```text
numero_version > 0
```

---

# 14. Auteur de DEMANDE_VERSION

L’ancien modèle :

```text
auteur_type
+
auteur_id
```

n’est plus utilisé.

La stratégie relationnelle retenue est :

```text
auteur_client_id
auteur_chasseur_id
auteur_systeme
```

avec la règle :

```text
exactement un auteur logique
```

Donc :

```text
CLIENT
XOR
CHASSEUR
XOR
SYSTEME
```

Cette décision permet de conserver de vraies contraintes référentielles.

Elle n’est plus « à résoudre au MPD ».

---

# 15. Critères de recherche

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

Règles :

```text
budget_min >= 0
budget_max >= 0

budget_min <= budget_max

surface_min >= 0

nb_pieces_min >= 0
nb_chambres_min >= 0
```

DPE :

```text
A
B
C
D
E
F
G
```

---

# 16. Critères complémentaires

```text
criteres_souhaites
```

représente les préférences complémentaires structurées.

Au niveau logique, il s’agit d’une collection de critères supplémentaires.

Le MPD PostgreSQL la matérialise en `JSONB`.

---

# 17. Lineage de DEMANDE_VERSION

Deux attributs contribuent au lineage d’ingestion :

```text
source_recherche_ref
ingestion_batch
```

Ils permettent de relier une version de demande à la source ou au lot ayant participé à sa génération.

---

# 18. SOURCE

```text
SOURCE(
    #id_source,
    nom,
    type_source,
    url_base,
    actif,
    niveau_confiance,
    date_creation
)
```

Clé :

```text
PK(id_source)
```

Types :

```text
AGENCE
PARTICULIER
PLATEFORME
API
OPEN_DATA
MANUEL
AUTRE
```

Niveaux de confiance :

```text
FAIBLE
MOYEN
ELEVE
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
PK(id_bien)

FK id_source
    -> SOURCE.id_source
```

Unicité :

```text
UNIQUE(
    id_source,
    reference_externe
)
```

Statuts :

```text
ACTIF
EXPIRE
VENDU
INDISPONIBLE
```

Contraintes principales :

```text
prix >= 0

surface >= 0

nb_pieces >= 0

nb_chambres >= 0

-90 <= latitude <= 90

-180 <= longitude <= 180
```

DPE :

```text
A..G
```

---

# 20. PRESENTATION

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
PK(id_presentation)

FK id_demande_version
    -> DEMANDE_VERSION.id_demande_version

FK id_bien
    -> BIEN.id_bien
```

Unicité :

```text
UNIQUE(
    id_demande_version,
    id_bien
)
```

Score :

```text
0 <= score_matching <= 100
```

Statuts :

```text
IDENTIFIE
QUALIFIE
PRESENTE
REJETE
VISITE
RETENU
```

`PRESENTATION` matérialise le résultat du matching entre une version de demande et un bien.

---

# 21. COMMENTAIRE

```text
COMMENTAIRE(
    #id_commentaire,
    date_commentaire,
    contenu,
    priorite,
    decision,
    id_demande_version,
    id_bien,
    auteur_client_id?,
    auteur_chasseur_id?
)
```

Clés :

```text
PK(id_commentaire)

FK id_demande_version
    -> DEMANDE_VERSION.id_demande_version

FK id_bien
    -> BIEN.id_bien

FK auteur_client_id
    -> CLIENT.id_client

FK auteur_chasseur_id
    -> CHASSEUR.id_chasseur
```

Un commentaire possède exactement un auteur :

```text
CLIENT
XOR
CHASSEUR
```

Priorité :

```text
1..5
```

Décisions :

```text
RETENIR
ECARTER
VISITER
REQUALIFIER
INFORMATION
```

---

# 22. DOCUMENT

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
PK(id_document)

FK id_bien
    -> BIEN.id_bien
```

Classifications :

```text
PUBLIC
INTERNE
CONFIDENTIEL
RESTREINT
```

---

# 23. VISITE

```text
VISITE(
    #id_visite,
    date_visite,
    statut,
    compte_rendu,
    note,
    photos,
    date_creation,
    id_presentation
)
```

Clés :

```text
PK(id_visite)

FK id_presentation
    -> PRESENTATION.id_presentation
```

Statuts :

```text
PLANIFIEE
REALISEE
ANNULEE
REPORTEE
```

Note :

```text
0 <= note <= 5
```

`photos` représente une collection de références de photos.

Le MPD la matérialise en tableau JSON.

`VISITE` n’est plus une extension future.

---

# 24. VENTE

```text
VENTE(
    #id_vente,
    id_mandat,
    id_mandat_periode?,
    id_presentation?,
    id_bien?,
    id_chasseur_beneficiaire?,
    origine_vente,
    date_acte_authentique,
    montant_achat,
    date_creation
)
```

Clés :

```text
PK(id_vente)

FK id_mandat
    -> MANDAT.id_mandat

FK id_mandat_periode
    -> MANDAT_PERIODE.id_mandat_periode

FK id_presentation
    -> PRESENTATION.id_presentation

FK id_bien
    -> BIEN.id_bien

FK id_chasseur_beneficiaire
    -> CHASSEUR.id_chasseur
```

Origines :

```text
CHASSEUR
CLIENT_SEUL
AUTRE_AGENCE
```

Règle :

```text
montant_achat > 0
```

La vente matérialise l’acte authentique.

Elle est distincte du calcul de rémunération et du paiement.

---

# 25. PARAMETRES_HONORAIRES

```text
PARAMETRES_HONORAIRES(
    #id_parametres_honoraires,
    date_debut_validite,
    date_fin_validite?,
    montant_fixe,
    taux_pourcentage,
    actif,
    date_creation
)
```

Clé :

```text
PK(id_parametres_honoraires)
```

Contraintes :

```text
montant_fixe >= 0

0 <= taux_pourcentage <= 1

date_fin_validite IS NULL
OR
date_fin_validite >= date_debut_validite
```

Ces paramètres permettent d’historiser la formule :

```text
honoraires =
montant_fixe
+
taux_pourcentage * montant_achat
```

---

# 26. BAREME_COMMISSION

```text
BAREME_COMMISSION(
    #id_bareme,
    montant_min,
    montant_max?,
    taux_commission,
    montant_fixe,
    date_debut_validite,
    date_fin_validite?,
    actif,
    id_chasseur?,
    statut_usage
)
```

Clés :

```text
PK(id_bareme)

FK id_chasseur
    -> CHASSEUR.id_chasseur
```

Contraintes :

```text
montant_min >= 0

montant_max IS NULL
OR
montant_max >= montant_min

0 <= taux_commission <= 1

montant_fixe >= 0
```

Statuts d’usage :

```text
HISTORIQUE
APPROUVE
```

La relation facultative avec `CHASSEUR` permet de conserver les barèmes historiques issus du système hérité.

---

# 27. PARAMETRES_REMUNERATION

```text
PARAMETRES_REMUNERATION(
    #id_parametres_remuneration,

    date_debut_validite,
    date_fin_validite?,

    fenetre_mois,

    poids_delai,
    poids_exclusivite,
    poids_ventes,
    poids_mandats,
    poids_visites,

    note_exclusif,
    note_non_exclusif,

    points_par_vente,
    points_par_mandat,

    taux_anciennete_par_annee,
    plafond_anciennete,

    score_pivot,
    amplitude_performance,

    taux_plancher,
    taux_plafond,

    actif,
    date_creation
)
```

Clé :

```text
PK(id_parametres_remuneration)
```

Règle fondamentale :

```text
poids_delai
+ poids_exclusivite
+ poids_ventes
+ poids_mandats
+ poids_visites
= 1
```

Autres contraintes :

```text
fenetre_mois > 0

0 <= note_exclusif <= 100
0 <= note_non_exclusif <= 100

points_par_vente >= 0
points_par_mandat >= 0

taux_anciennete_par_annee >= 0

0 <= plafond_anciennete <= 1

0 <= score_pivot <= 100

0 <= amplitude_performance <= 1

0 <= taux_plancher <= taux_plafond <= 1
```

---

# 28. PALIER_PERFORMANCE

```text
PALIER_PERFORMANCE(
    #id_palier_performance,
    id_parametres_remuneration,
    critere,
    ordre,
    borne_max?,
    note
)
```

Clés :

```text
PK(id_palier_performance)

FK id_parametres_remuneration
    -> PARAMETRES_REMUNERATION.id_parametres_remuneration
```

Unicité :

```text
UNIQUE(
    id_parametres_remuneration,
    critere,
    ordre
)
```

Critères configurables :

```text
DELAI_SEMAINES
VISITES
```

Contraintes :

```text
ordre >= 1

borne_max >= 0

0 <= note <= 100
```

---

# 29. Calcul de rémunération

Le calcul métier exploite :

```text
VENTE
MANDAT
MANDAT_PERIODE
CHASSEUR
VISITE
BAREME_COMMISSION
PARAMETRES_HONORAIRES
PARAMETRES_REMUNERATION
PALIER_PERFORMANCE
```

Le calcul produit notamment :

```text
éligibilité

honoraires entreprise

semaines mandat -> acte
nombre de visites
ancienneté
ventes sur fenêtre
mandats sur fenêtre

notes de performance
score global

taux de base
majoration ancienneté
modulation performance
taux final

montant chasseur
```

Ces valeurs sont figées dans `PAIEMENT`.

---

# 30. PAIEMENT

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
    id_bareme?,
    id_vente?,
    id_chasseur_beneficiaire?,
    id_parametres_honoraires?,
    id_parametres_remuneration?,

    date_calcul,

    droit_remuneration,
    motif_refus,

    semaines_mandat_acte,
    nb_visites_calcul,
    annees_anciennete_calcul,
    nb_ventes_fenetre,
    nb_mandats_fenetre,

    note_delai,
    note_exclusivite,
    note_ventes,
    note_mandats,
    note_visites,

    score_performance,

    taux_base,
    majoration_anciennete,
    modulation_performance,
    taux_final
)
```

Clés :

```text
PK(id_paiement)

FK id_mandat
    -> MANDAT.id_mandat

FK id_bareme
    -> BAREME_COMMISSION.id_bareme

FK id_vente
    -> VENTE.id_vente

FK id_chasseur_beneficiaire
    -> CHASSEUR.id_chasseur

FK id_parametres_honoraires
    -> PARAMETRES_HONORAIRES.id_parametres_honoraires

FK id_parametres_remuneration
    -> PARAMETRES_REMUNERATION.id_parametres_remuneration
```

---

# 31. Statuts de PAIEMENT

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

Règle temporelle :

```text
date_paiement_chasseur
>=
date_reception_honoraires
```

lorsque les deux dates sont renseignées.

---

# 32. Éligibilité de rémunération

```text
droit_remuneration
```

indique si le chasseur possède un droit à rémunération pour la vente.

Règle :

```text
droit_remuneration = TRUE
    => motif_refus NULL

droit_remuneration = FALSE
    => motif_refus NOT NULL
```

Motifs actuellement représentés :

```text
MANDAT_EXPIRE
HORS_DISPOSITIF
```

---

# 33. Snapshot de calcul

Contrairement au MLD V2, les indicateurs de performance utilisés pour une rémunération ne sont pas seulement considérés comme des données analytiques recalculables.

`PAIEMENT` conserve le snapshot utilisé lors du calcul :

```text
semaines_mandat_acte

nb_visites_calcul
annees_anciennete_calcul
nb_ventes_fenetre
nb_mandats_fenetre

note_delai
note_exclusivite
note_ventes
note_mandats
note_visites

score_performance

taux_base
majoration_anciennete
modulation_performance
taux_final
```

Cela garantit :

```text
reproductibilité
explicabilité
auditabilité
historisation
```

---

# 34. Contraintes du snapshot

Compteurs :

```text
>= 0
```

Notes :

```text
0 <= note <= 100
```

Score :

```text
0 <= score_performance <= 100
```

Taux :

```text
0 <= taux_base <= 1

0 <= majoration_anciennete <= 1

-1 <= modulation_performance <= 1

0 <= taux_final <= 1
```

Montants :

```text
montant_achat >= 0
montant_honoraires >= 0
montant_chasseur >= 0
```

---

# 35. AUDIT_LOG

```text
AUDIT_LOG(
    #id_audit,
    date_evenement,
    schema_name,
    table_name,
    operation,
    record_id,
    utilisateur,
    ancienne_valeur,
    nouvelle_valeur,
    contexte
)
```

Clé :

```text
PK(id_audit)
```

Opérations :

```text
INSERT
UPDATE
DELETE
```

`AUDIT_LOG` est transverse.

Il ne possède volontairement pas de FK métier polymorphe vers toutes les relations auditées.

L’identification repose sur :

```text
schema_name
table_name
record_id
```

Les valeurs avant/après et le contexte permettent de conserver une preuve détaillée des opérations sensibles.

---

# 36. MLD relationnel complet

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

UTILISATEUR(
    #id_utilisateur,
    email,
    password_hash,
    role,
    actif,
    id_client?,
    id_chasseur?,
    derniere_connexion,
    date_creation,
    date_modification
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

MANDAT_PERIODE(
    #id_mandat_periode,
    id_mandat,
    numero_periode,
    type_periode,
    date_debut,
    date_fin,
    date_renouvellement,
    commentaire,
    est_historique_legacy,
    created_at
)

DEMANDE(
    #id_demande,
    reference_demande,
    date_creation,
    statut,
    id_mandat?,
    origine
)

DEMANDE_AFFECTATION(
    #id_affectation,
    id_demande,
    id_chasseur,
    statut,
    date_affectation,
    date_decision,
    id_utilisateur_affectation?,
    id_utilisateur_decision?,
    motif_refus
)

DEMANDE_VERSION(
    #id_demande_version,
    numero_version,
    date_version,
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
    description_recherche_legacy,
    active,
    id_demande,
    auteur_client_id?,
    auteur_chasseur_id?,
    auteur_systeme,
    source_recherche_ref,
    ingestion_batch
)

SOURCE(
    #id_source,
    nom,
    type_source,
    url_base,
    actif,
    niveau_confiance,
    date_creation
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
    contenu,
    priorite,
    decision,
    id_demande_version,
    id_bien,
    auteur_client_id?,
    auteur_chasseur_id?
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

VISITE(
    #id_visite,
    date_visite,
    statut,
    compte_rendu,
    note,
    photos,
    date_creation,
    id_presentation
)

VENTE(
    #id_vente,
    id_mandat,
    id_mandat_periode?,
    id_presentation?,
    id_bien?,
    id_chasseur_beneficiaire?,
    origine_vente,
    date_acte_authentique,
    montant_achat,
    date_creation
)

BAREME_COMMISSION(
    #id_bareme,
    montant_min,
    montant_max?,
    taux_commission,
    montant_fixe,
    date_debut_validite,
    date_fin_validite?,
    actif,
    id_chasseur?,
    statut_usage
)

PARAMETRES_HONORAIRES(
    #id_parametres_honoraires,
    date_debut_validite,
    date_fin_validite?,
    montant_fixe,
    taux_pourcentage,
    actif,
    date_creation
)

PARAMETRES_REMUNERATION(
    #id_parametres_remuneration,
    date_debut_validite,
    date_fin_validite?,
    fenetre_mois,
    poids_delai,
    poids_exclusivite,
    poids_ventes,
    poids_mandats,
    poids_visites,
    note_exclusif,
    note_non_exclusif,
    points_par_vente,
    points_par_mandat,
    taux_anciennete_par_annee,
    plafond_anciennete,
    score_pivot,
    amplitude_performance,
    taux_plancher,
    taux_plafond,
    actif,
    date_creation
)

PALIER_PERFORMANCE(
    #id_palier_performance,
    id_parametres_remuneration,
    critere,
    ordre,
    borne_max?,
    note
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
    id_bareme?,
    id_vente?,
    id_chasseur_beneficiaire?,
    id_parametres_honoraires?,
    id_parametres_remuneration?,
    date_calcul,
    droit_remuneration,
    motif_refus,
    semaines_mandat_acte,
    nb_visites_calcul,
    annees_anciennete_calcul,
    nb_ventes_fenetre,
    nb_mandats_fenetre,
    note_delai,
    note_exclusivite,
    note_ventes,
    note_mandats,
    note_visites,
    score_performance,
    taux_base,
    majoration_anciennete,
    modulation_performance,
    taux_final
)

AUDIT_LOG(
    #id_audit,
    date_evenement,
    schema_name,
    table_name,
    operation,
    record_id,
    utilisateur,
    ancienne_valeur,
    nouvelle_valeur,
    contexte
)
```

---

# 37. Graphe relationnel principal

```text
CLIENT
  |
  +----------------------+
  |                      |
  v                      v
DEMANDE                MANDAT <---------------- CHASSEUR
  |                      |                         ^
  |                      +--> MANDAT_PERIODE       |
  |                      |                         |
  |                      +--> MANDAT_SECTEUR       |
  |                               |                |
  |                               v                |
  |                            SECTEUR             |
  |                                                |
  +--> DEMANDE_AFFECTATION ------------------------+
  |
  v
DEMANDE_VERSION
  |
  +-------------> PRESENTATION <------------- BIEN
  |                    |                       |
  |                    v                       +--> SOURCE
  |                  VISITE                    |
  |                                            +--> DOCUMENT
  +-------------> COMMENTAIRE <----------------+
```

Transaction :

```text
MANDAT
  |
  +--> MANDAT_PERIODE
  |
  +----------------------+
                         |
PRESENTATION ------------+
                         |
BIEN --------------------+
                         |
CHASSEUR ----------------+
                         |
                         v
                       VENTE
                         |
                         v
                      PAIEMENT
```

Configuration financière :

```text
PARAMETRES_HONORAIRES --------+
                               |
BAREME_COMMISSION -------------+
                               |
PARAMETRES_REMUNERATION -------+--> PAIEMENT
          |
          v
PALIER_PERFORMANCE
```

---

# 38. Foreign Keys principales

```text
UTILISATEUR.id_client
    -> CLIENT.id_client

UTILISATEUR.id_chasseur
    -> CHASSEUR.id_chasseur

MANDAT.id_client
    -> CLIENT.id_client

MANDAT.id_chasseur
    -> CHASSEUR.id_chasseur

MANDAT_SECTEUR.id_mandat
    -> MANDAT.id_mandat

MANDAT_SECTEUR.id_secteur
    -> SECTEUR.id_secteur

MANDAT_PERIODE.id_mandat
    -> MANDAT.id_mandat

DEMANDE.id_mandat
    -> MANDAT.id_mandat

DEMANDE_AFFECTATION.id_demande
    -> DEMANDE.id_demande

DEMANDE_AFFECTATION.id_chasseur
    -> CHASSEUR.id_chasseur

DEMANDE_AFFECTATION.id_utilisateur_affectation
    -> UTILISATEUR.id_utilisateur

DEMANDE_AFFECTATION.id_utilisateur_decision
    -> UTILISATEUR.id_utilisateur

DEMANDE_VERSION.id_demande
    -> DEMANDE.id_demande

DEMANDE_VERSION.auteur_client_id
    -> CLIENT.id_client

DEMANDE_VERSION.auteur_chasseur_id
    -> CHASSEUR.id_chasseur

BIEN.id_source
    -> SOURCE.id_source

PRESENTATION.id_demande_version
    -> DEMANDE_VERSION.id_demande_version

PRESENTATION.id_bien
    -> BIEN.id_bien

COMMENTAIRE.id_demande_version
    -> DEMANDE_VERSION.id_demande_version

COMMENTAIRE.id_bien
    -> BIEN.id_bien

COMMENTAIRE.auteur_client_id
    -> CLIENT.id_client

COMMENTAIRE.auteur_chasseur_id
    -> CHASSEUR.id_chasseur

DOCUMENT.id_bien
    -> BIEN.id_bien

VISITE.id_presentation
    -> PRESENTATION.id_presentation

VENTE.id_mandat
    -> MANDAT.id_mandat

VENTE.id_mandat_periode
    -> MANDAT_PERIODE.id_mandat_periode

VENTE.id_presentation
    -> PRESENTATION.id_presentation

VENTE.id_bien
    -> BIEN.id_bien

VENTE.id_chasseur_beneficiaire
    -> CHASSEUR.id_chasseur

BAREME_COMMISSION.id_chasseur
    -> CHASSEUR.id_chasseur

PALIER_PERFORMANCE.id_parametres_remuneration
    -> PARAMETRES_REMUNERATION.id_parametres_remuneration

PAIEMENT.id_mandat
    -> MANDAT.id_mandat

PAIEMENT.id_bareme
    -> BAREME_COMMISSION.id_bareme

PAIEMENT.id_vente
    -> VENTE.id_vente

PAIEMENT.id_chasseur_beneficiaire
    -> CHASSEUR.id_chasseur

PAIEMENT.id_parametres_honoraires
    -> PARAMETRES_HONORAIRES.id_parametres_honoraires

PAIEMENT.id_parametres_remuneration
    -> PARAMETRES_REMUNERATION.id_parametres_remuneration
```

---

# 39. Contraintes d’unicité principales

```text
CLIENT.email

CHASSEUR.email

MANDAT.reference_mandat

MANDAT_SECTEUR(
    id_mandat,
    id_secteur
)

MANDAT_PERIODE(
    id_mandat,
    numero_periode
)

DEMANDE.reference_demande

DEMANDE_VERSION(
    id_demande,
    numero_version
)

BIEN(
    id_source,
    reference_externe
)

PRESENTATION(
    id_demande_version,
    id_bien
)

SECTEUR(
    pays,
    ville,
    quartier,
    code_postal
)

PALIER_PERFORMANCE(
    id_parametres_remuneration,
    critere,
    ordre
)
```

Des index partiels ou contraintes physiques complémentaires peuvent également implémenter des règles métier qui ne se traduisent pas par une contrainte `UNIQUE` classique.

---

# 40. Suppression référentielle

Le modèle utilise principalement :

```text
ON DELETE RESTRICT
```

afin d’éviter la suppression de données référencées.

Deux associations structurelles utilisent une suppression en cascade :

```text
MANDAT
    -> MANDAT_SECTEUR

MANDAT
    -> MANDAT_PERIODE
```

Cette stratégie reste limitée aux relations dont l’existence dépend structurellement du mandat.

---

# 41. Modèle transactionnel

La chaîne transactionnelle est :

```text
MANDAT
  |
  v
MANDAT_PERIODE
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
CALCUL REMUNERATION
  |
  v
PAIEMENT
```

Il ne faut pas interpréter cette représentation comme une obligation que toutes les relations intermédiaires soient renseignées dans tous les cas.

Par exemple, certaines origines de vente peuvent ne pas provenir directement d’une présentation du chasseur.

---

# 42. Séparation des responsabilités

Le modèle applique notamment :

```text
CLIENT
!=
UTILISATEUR

CHASSEUR
!=
UTILISATEUR

MANDAT
!=
DEMANDE

DEMANDE
!=
DEMANDE_VERSION

DEMANDE
!=
DEMANDE_AFFECTATION

MANDAT
!=
MANDAT_PERIODE

PRESENTATION
!=
VISITE

VISITE
!=
VENTE

VENTE
!=
PAIEMENT

PARAMETRES
!=
RESULTAT DE CALCUL
```

Cette séparation est structurante pour l’auditabilité du SI.

---

# 43. OLTP et analytique

Les relations décrites ici appartiennent au modèle opérationnel `real_estate`.

Elles alimentent ensuite le modèle analytique.

Exemples :

```text
MANDAT
    -> warehouse.fact_mandat

MANDAT_PERIODE
    -> warehouse.fact_mandat_periode

PAIEMENT
    -> warehouse.fact_paiement

PRESENTATION
    -> warehouse.fact_presentation
```

Les grains OLTP et OLAP restent distincts.

---

# 44. Concepts non implémentés

Les concepts suivants ne font pas partie du MLD opérationnel actuellement vérifié :

```text
OFFRE
FACTURE
NOTAIRE
```

Ils peuvent être ajoutés ultérieurement si le besoin métier l’exige.

`VISITE` ne doit plus être présenté comme futur.

`RENOUVELLEMENT_MANDAT` ne nécessite pas de relation autonome car il est représenté par :

```text
MANDAT_PERIODE
+
type_periode = RENOUVELLEMENT
```

La date de l’acte authentique est actuellement portée par `VENTE`.

---

# 45. Traçabilité MCD V3 → MLD V3

| Concept MCD                | Relation MLD            |
| -------------------------- | ----------------------- |
| Client                     | CLIENT                  |
| Chasseur                   | CHASSEUR                |
| Identité applicative       | UTILISATEUR             |
| Secteur                    | SECTEUR                 |
| Mandat                     | MANDAT                  |
| Mandat ↔ secteur           | MANDAT_SECTEUR          |
| Période contractuelle      | MANDAT_PERIODE          |
| Demande                    | DEMANDE                 |
| Affectation                | DEMANDE_AFFECTATION     |
| Version de demande         | DEMANDE_VERSION         |
| Source                     | SOURCE                  |
| Bien                       | BIEN                    |
| Matching / sélection       | PRESENTATION            |
| Feedback                   | COMMENTAIRE             |
| Document                   | DOCUMENT                |
| Visite                     | VISITE                  |
| Vente                      | VENTE                   |
| Barème                     | BAREME_COMMISSION       |
| Configuration honoraires   | PARAMETRES_HONORAIRES   |
| Configuration rémunération | PARAMETRES_REMUNERATION |
| Palier de performance      | PALIER_PERFORMANCE      |
| Calcul figé / paiement     | PAIEMENT                |
| Audit                      | AUDIT_LOG               |

---

# 46. Évolution MLD V2 → V3

## Ajouts

```text
UTILISATEUR
MANDAT_PERIODE
DEMANDE_AFFECTATION
VISITE
VENTE
PARAMETRES_HONORAIRES
PARAMETRES_REMUNERATION
PALIER_PERFORMANCE
AUDIT_LOG
```

## DEMANDE corrigée

Avant :

```text
DEMANDE
    -> mandat obligatoire
```

Maintenant :

```text
DEMANDE
    -> mandat optionnel
```

Cela supporte le besoin pré-mandat.

---

## DEMANDE_VERSION corrigée

Avant :

```text
auteur_type
auteur_id
```

Maintenant :

```text
auteur_client_id
auteur_chasseur_id
auteur_systeme
```

avec exclusivité logique de l’auteur.

---

## MANDAT corrigé

La durée et les renouvellements ne sont plus implicitement représentés uniquement par les dates du mandat.

Ils disposent de :

```text
MANDAT_PERIODE
```

---

## VISITE corrigée

Avant :

```text
future VISITE
```

Maintenant :

```text
VISITE
=
relation implémentée
```

---

## Transaction corrigée

Le MLD V2 ne possédait pas de relation explicite de vente.

Le MLD V3 ajoute :

```text
VENTE
```

pour représenter l’acte authentique.

---

## Rémunération corrigée

Avant :

```text
BAREME_COMMISSION
+
PAIEMENT simplifié
```

Maintenant :

```text
BAREME_COMMISSION

PARAMETRES_HONORAIRES

PARAMETRES_REMUNERATION
        |
        v
PALIER_PERFORMANCE

VENTE
        |
        v
CALCUL
        |
        v
PAIEMENT snapshot
```

---

# 47. Statut

| Élément                    | Statut                     |
| -------------------------- | -------------------------- |
| MCD V3                     | COMPLETE                   |
| Relations OLTP             | RUNTIME VERIFIED           |
| 23 tables OLTP             | RUNTIME VERIFIED           |
| Physical columns           | RUNTIME VERIFIED           |
| PK/FK/CHECK constraints    | RUNTIME VERIFIED           |
| Pre-mandate demand         | IMPLEMENTED                |
| Demand assignment          | RUNTIME VERIFIED           |
| Mandate periods            | RUNTIME VERIFIED           |
| Six-month lifecycle        | RUNTIME VERIFIED           |
| Authentication identity    | IMPLEMENTED                |
| Explicit authorship        | IMPLEMENTED                |
| Matching / presentation    | RUNTIME VERIFIED           |
| Visit                      | RUNTIME VERIFIED           |
| Sale                       | RUNTIME VERIFIED           |
| Remuneration configuration | IMPLEMENTED                |
| Remuneration calculation   | RUNTIME VERIFIED           |
| Payment lifecycle          | RUNTIME VERIFIED           |
| Audit                      | RUNTIME VERIFIED           |
| MLD synchronization        | COMPLETE WITH THIS VERSION |
| MPD synchronization        | NEXT                       |

---

# 48. Conclusion

Le MLD V3 traduit le MCD V3 dans un modèle relationnel cohérent avec le système actuellement implémenté.

La chaîne principale devient :

```text
CLIENT
   |
   v
DEMANDE
   |
   +--> DEMANDE_AFFECTATION --> CHASSEUR
   |
   v
DEMANDE_VERSION
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
PAIEMENT
```

avec le contexte contractuel :

```text
CLIENT
   |
   v
MANDAT
   |
   v
MANDAT_PERIODE
```

et le moteur financier :

```text
PARAMETRES_HONORAIRES
        +
BAREME_COMMISSION
        +
PARAMETRES_REMUNERATION
        |
        v
PALIER_PERFORMANCE
        |
        v
CALCUL DETERMINISTE
        |
        v
PAIEMENT
```

Le modèle conserve ainsi les propriétés nécessaires à une plateforme Data & IA industrialisée :

```text
historisation
traçabilité
intégrité référentielle
explicabilité
auditabilité
sécurité
lineage
analytics
observabilité
évolution IA
```

Le MLD est désormais suffisamment stabilisé pour reconstruire le **MPD PostgreSQL V3** à partir du schéma réellement déployé.

---

**MLD V3 — ALIGNED WITH MCD V3 AND RUNTIME MODEL THROUGH MIGRATION 012**

**NEXT: MPD PostgreSQL V3**
