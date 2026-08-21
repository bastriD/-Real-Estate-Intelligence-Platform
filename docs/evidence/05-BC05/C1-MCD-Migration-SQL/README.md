# BC05 — C1 — MCD & Migration SQL

**Bloc de compétences :** BC05  
**Compétence :** C1 — Concevoir le modèle de données et produire le script de création/migration associé  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Modèle existant — preuve SQL à consolider

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves démontrant la capacité à :

- analyser les données métier ;
- identifier les entités ;
- définir les relations ;
- construire un MCD ;
- traduire ce modèle en schéma relationnel ;
- produire un script SQL de création ou migration ;
- vérifier l'exécution du script ;
- conserver la traçabilité entre modèle et base réelle.

Le chemin attendu est :

```text
Business Need
     |
     v
Entities / Rules
     |
     v
MCD
     |
     v
Relational Model
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

---

# 2. Source principale — MCD

Le livrable principal existant est :

```text
MCD-MERISE.md
```

Ce document doit rester la source de vérité pour le modèle conceptuel.

Le présent dossier ne doit pas dupliquer le MCD.

Il sert à montrer comment le modèle est relié à l'implémentation SQL.

---

# 3. Sources Data complémentaires

Références utiles :

```text
../../../40-DATA/01-Data-Architecture.md
../../../40-DATA/02-Data-Model.md
../../../40-DATA/03-Data-Warehouse.md
../../../40-DATA/08-Master-Reference-Data.md
```

Architecture générale :

```text
../../../99-DIAGRAMS/07-Data-Architecture.puml
```

---

# 4. Rôle du MCD

Le MCD décrit :

```text
Entities
+
Attributes
+
Relationships
+
Cardinalities
+
Business Rules
```

Il doit rester indépendant des détails techniques PostgreSQL autant que possible.

Exemple :

```text
CUSTOMER
   |
   | places
   |
   v
ORDER
```

Le MCD répond à :

> Quelles informations métier existent et comment sont-elles liées ?

---

# 5. MCD vs modèle physique

Le projet distingue :

```text
MCD
=
Conceptual Business Model
```

et :

```text
Physical Database Schema
=
Technical Implementation
```

Exemple :

```text
Entity CUSTOMER
```

peut devenir :

```sql
customer
```

avec :

- primary key ;
- types SQL ;
- constraints ;
- indexes.

---

# 6. Règles métier

Chaque relation importante doit correspondre à une règle métier.

Exemple :

```text
A customer can create several searches.
A search belongs to one customer.
```

La cardinalité du MCD doit refléter cette règle.

---

# 7. Identifiants

Chaque entité persistée doit disposer d'une stratégie d'identification.

Exemples :

```text
INTEGER
BIGINT
UUID
Business Key
```

Le choix doit être cohérent avec le besoin.

---

# 8. Clés primaires

Exemple :

```sql
id BIGSERIAL PRIMARY KEY
```

ou :

```sql
id UUID PRIMARY KEY
```

selon le modèle réel.

---

# 9. Clés étrangères

Les relations du MCD doivent être matérialisées.

Exemple :

```sql
customer_id BIGINT NOT NULL
REFERENCES customer(id)
```

---

# 10. Cardinalité 1,N

Exemple conceptuel :

```text
CUSTOMER (1)
    |
    |
    +-------- SEARCH (N)
```

Implémentation :

```text
SEARCH.customer_id -> CUSTOMER.id
```

---

# 11. Cardinalité N,N

Une relation plusieurs-à-plusieurs devient généralement une table d'association.

```text
PROPERTY
    |
    v
PROPERTY_TAG
    ^
    |
TAG
```

---

# 12. Contraintes

Le schéma doit traduire les contraintes utiles.

Exemples :

```text
NOT NULL
UNIQUE
FOREIGN KEY
CHECK
DEFAULT
```

---

# 13. Exemple CHECK

```sql
CHECK (price >= 0)
```

si le métier interdit les valeurs négatives.

---

# 14. Types SQL

Les types doivent correspondre à la donnée.

Exemples :

```text
TEXT
VARCHAR
INTEGER
BIGINT
NUMERIC
BOOLEAN
DATE
TIMESTAMP
JSONB
```

Éviter de tout stocker en texte.

---

# 15. Dates

Le modèle doit distinguer si nécessaire :

```text
DATE
TIMESTAMP
TIMESTAMPTZ
```

selon le besoin.

---

# 16. Montants

Pour les valeurs financières :

```text
NUMERIC
```

est généralement préférable à des types flottants si une précision exacte est nécessaire.

---

# 17. Données géographiques

Si le projet utilise des coordonnées, elles peuvent être stockées selon le niveau de besoin.

Exemple simple :

```text
latitude
longitude
```

Une extension spécialisée comme PostGIS ne doit être ajoutée que si les besoins géospatiaux le justifient.

---

# 18. Normalisation

Le modèle OLTP doit limiter la duplication inutile.

Principes possibles :

```text
1NF
2NF
3NF
```

selon le modèle.

L'objectif est :

- cohérence ;
- intégrité ;
- réduction des anomalies.

---

# 19. Dénormalisation

La dénormalisation peut être pertinente dans :

```text
OLAP
Analytics
```

mais ne doit pas être appliquée arbitrairement au modèle transactionnel.

---

# 20. Schéma PostgreSQL

Le projet distingue plusieurs espaces logiques.

Exemple Data Platform :

```text
raw
staging
warehouse
analytics
```

Le schéma applicatif métier peut rester séparé si nécessaire.

---

# 21. Migration SQL

Le livrable attendu doit comprendre un script réel :

```text
migration.sql
```

Le script doit pouvoir créer ou faire évoluer le schéma.

---

# 22. Principes migration.sql

Le script doit être :

- versionné ;
- reproductible ;
- lisible ;
- ordonné ;
- exécutable ;
- vérifiable.

---

# 23. Ordre de création

L'ordre doit respecter les dépendances.

Exemple :

```text
1. Reference tables
2. Parent entities
3. Child entities
4. Association tables
5. Indexes
6. Views if required
```

---

# 24. Exemple structure

```sql
BEGIN;

CREATE TABLE customer (...);

CREATE TABLE property (...);

CREATE TABLE search (
    ...
    customer_id BIGINT REFERENCES customer(id)
);

COMMIT;
```

L'exemple est illustratif.

Le fichier final doit correspondre au MCD réel.

---

# 25. Transaction de migration

Lorsque cela est compatible :

```sql
BEGIN;
...
COMMIT;
```

permet d'éviter un état partiellement appliqué en cas d'erreur.

---

# 26. Idempotence

Certaines migrations initiales peuvent utiliser :

```sql
CREATE TABLE IF NOT EXISTS
```

mais ce choix doit être maîtrisé.

Un framework de migration versionnée peut être préférable pour l'évolution applicative.

---

# 27. Versioning

Exemples :

```text
V001__initial_schema.sql
V002__add_property_status.sql
```

ou :

```text
Alembic revision
```

selon la stratégie finale.

---

# 28. Indexes

Les index ne doivent pas être ajoutés au hasard.

Ils doivent être reliés :

```text
Query Pattern
    |
    v
EXPLAIN
    |
    v
Index Decision
```

Les preuves d'optimisation seront traitées dans :

```text
../C2-OLTP-Optimisation/
```

---

# 29. Index clé étrangère

Certaines foreign keys fréquemment utilisées dans des joins peuvent nécessiter un index.

Exemple :

```sql
CREATE INDEX idx_search_customer_id
ON search(customer_id);
```

Seulement si le workload le justifie.

---

# 30. Uniqueness

Une contrainte d'unicité doit traduire une règle métier.

Exemple :

```sql
UNIQUE(reference)
```

si une référence doit être unique.

---

# 31. Referential Integrity

Les foreign keys permettent de protéger :

```text
Parent
  |
  v
Child
```

contre certaines incohérences.

---

# 32. DELETE behavior

Le comportement doit être choisi explicitement.

Exemples :

```text
ON DELETE RESTRICT
ON DELETE CASCADE
ON DELETE SET NULL
```

Il doit correspondre au métier.

---

# 33. Audit fields

Selon le besoin :

```text
created_at
updated_at
created_by
```

peuvent améliorer la traçabilité.

Ils ne doivent pas être ajoutés systématiquement sans besoin.

---

# 34. Soft Delete

Un pattern possible :

```text
deleted_at
```

peut être utilisé si le métier nécessite une restauration ou une traçabilité.

Mais il introduit une complexité dans toutes les requêtes.

---

# 35. Data Classification

Les tables et colonnes sensibles doivent pouvoir être associées à une classification.

Exemples :

```text
Personal Data
Confidential
Internal
```

OpenMetadata peut servir à matérialiser cette classification.

---

# 36. RGPD

Le modèle doit permettre de déterminer :

```text
Where is personal data stored?
```

et :

```text
What entities reference it?
```

Le MCD contribue à cette visibilité.

---

# 37. Validation du script

Après exécution de `migration.sql`, plusieurs vérifications sont nécessaires.

---

# 38. Vérification tables

Exemple :

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
```

---

# 39. Vérification colonnes

```sql
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

Adapter le schéma au projet réel.

---

# 40. Vérification constraints

```sql
SELECT
    conname,
    contype,
    conrelid::regclass
FROM pg_constraint
ORDER BY conrelid::regclass::text;
```

---

# 41. Vérification indexes

```sql
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
ORDER BY schemaname, tablename, indexname;
```

---

# 42. Test d'insertion

Un test doit vérifier qu'une ligne valide peut être ajoutée.

```text
Valid Data
   |
   v
INSERT
   |
   v
SUCCESS
```

---

# 43. Test contrainte

Un test doit vérifier qu'une donnée invalide est rejetée.

Exemple :

```text
Missing mandatory FK
      |
      v
INSERT
      |
      v
FAIL as expected
```

---

# 44. Test foreign key

```text
Child references nonexistent parent
      |
      v
Database rejects insert
```

si la foreign key est active.

---

# 45. Test unique

```text
Duplicate unique value
      |
      v
Database rejects insert
```

---

# 46. Test CHECK

```text
Invalid business value
      |
      v
Database rejects value
```

---

# 47. Script de rollback

Un rollback complet peut être difficile.

Pour une initialisation de lab, un script séparé peut éventuellement permettre :

```sql
DROP TABLE ...
```

mais il ne doit pas être utilisé inconsidérément en production.

---

# 48. Backup avant migration

Une migration critique doit considérer :

```text
Backup
+
Validated Migration
```

avant modification destructive.

---

# 49. Migration et CI

La CI peut valider la migration sur une base temporaire.

```text
migration.sql
     |
     v
Temporary PostgreSQL
     |
     v
Execute
     |
     v
Schema Tests
```

---

# 50. Source of Truth

Le modèle doit conserver une cohérence entre :

```text
MCD-MERISE.md
       |
       v
migration.sql
       |
       v
PostgreSQL runtime
```

Ces trois niveaux ne doivent pas diverger.

---

# 51. Traceability Matrix

| MCD | SQL | Evidence |
|---|---|---|
| Entity | Table | `information_schema` |
| Attribute | Column | column query |
| Identifier | PK | constraint query |
| Relationship | FK | `pg_constraint` |
| Unique rule | UNIQUE | constraint test |
| Business rule | CHECK | invalid insert test |

---

# 52. Evidence directory

Ce dossier doit progressivement contenir :

```text
C1-MCD-Migration-SQL/
│
├── README.md
├── migration.sql
├── schema-validation.txt
├── constraints-validation.txt
└── migration-test.txt
```

Les fichiers de preuve doivent provenir de l'exécution réelle.

---

# 53. migration.sql

Le prochain artifact concret à produire pour cette compétence est :

```text
migration.sql
```

Il doit être construit à partir du MCD existant.

Il ne doit pas être inventé indépendamment du modèle.

---

# 54. Preuves attendues

Minimum recommandé :

```text
MCD-MERISE.md
migration.sql
successful execution
table listing
constraint listing
at least one valid insert
at least one invalid constraint test
```

---

# 55. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Business Rule
      |
      v
MCD
      |
      v
Relational Design
      |
      v
SQL
      |
      v
Database
      |
      v
Executed Validation
```

---

# 56. Statut actuel

| Élément | Statut |
|---|---|
| MCD | EXISTANT |
| Data architecture | DOCUMENTÉE |
| Data model documentation | DOCUMENTÉE |
| Relational principles | DOCUMENTÉS |
| migration.sql | À PRODUIRE / CENTRALISER |
| Migration execution | À PROUVER |
| Constraints evidence | À PRODUIRE |
| Schema evidence | À PRODUIRE |
| MCD → SQL traceability | À CONSOLIDER |

---

# 57. Conclusion

La preuve attendue pour cette compétence ne s'arrête pas au diagramme.

Elle doit démontrer :

```text
Conceptual Model
        |
        v
Executable SQL
        |
        v
Real Database Schema
        |
        v
Validation
```

Le prochain travail concret consiste donc à produire et exécuter le `migration.sql` correspondant exactement au `MCD-MERISE.md`.

---

**BC05 / C1 — MCD & Migration SQL : BASELINE COMPLETE / EXECUTABLE SQL REQUIRED**