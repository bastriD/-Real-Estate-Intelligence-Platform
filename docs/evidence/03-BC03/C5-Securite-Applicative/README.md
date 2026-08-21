# BC03 — C5 — Sécurité applicative

**Bloc de compétences :** BC03  
**Compétence :** C5 — Concevoir et intégrer les exigences de sécurité au niveau applicatif  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Baseline documentaire — preuves runtime à consolider

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves démontrant que la sécurité applicative est intégrée dès la conception.

La sécurité doit couvrir :

```text
Input
  |
  v
Authentication
  |
  v
Authorization
  |
  v
Business Logic
  |
  v
Data Access
  |
  v
External Services
  |
  v
Logging / Monitoring
```

Le principe général est :

```text
Security by Design
```

et non :

```text
Security after deployment
```

---

# 2. Sources de référence

Documents principaux :

```text
../../../60-SECURITY/01-Security-Architecture.md
../../../60-SECURITY/02-Identity-and-Access-Management.md
../../../60-SECURITY/03-Zero-Trust-Architecture.md
../../../60-SECURITY/04-Secret-Management.md
../../../60-SECURITY/05-Network-Security.md
../../../60-SECURITY/06-Application-Security.md
../../../60-SECURITY/07-Container-Security.md
../../../60-SECURITY/08-Kubernetes-Security.md
../../../60-SECURITY/09-Compliance-and-Risk.md
../../../60-SECURITY/10-Security-Monitoring.md
```

Documents applicatifs :

```text
../../../20-APPLICATION/01-Application-Architecture.md
```

Documents AI :

```text
../../../50-AI/07-AI-Governance.md
../../../50-AI/08-AI-Security.md
```

Diagramme principal :

```text
../../../99-DIAGRAMS/12-Security-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/12-Security-Architecture.svg
```

---

# 3. Principes de sécurité

Les principes appliqués sont :

- Least Privilege
- Defense in Depth
- Secure by Default
- Explicit Authorization
- Secret Separation
- Input Validation
- Secure Logging
- TLS
- Auditability
- Traceability
- Local-first AI

---

# 4. Defense in Depth

La sécurité repose sur plusieurs couches :

```text
Identity
  |
  v
Authentication
  |
  v
Authorization
  |
  v
Network
  |
  v
Runtime
  |
  v
Application
  |
  v
Data
  |
  v
AI
  |
  v
Monitoring
```

Aucun contrôle isolé ne suffit à protéger l'ensemble du système.

---

# 5. Authentification

L'authentification permet de déterminer :

```text
Who are you?
```

Architecture cible :

```text
User
 |
 v
Identity Provider
 |
 v
Token / Session
 |
 v
Application
```

Keycloak reste une technologie :

```text
TARGET
```

jusqu'à implémentation réelle.

---

# 6. Autorisation

L'autorisation répond à :

```text
What are you allowed to do?
```

Le contrôle doit être appliqué côté backend.

```text
Request
 |
 v
Authenticated?
 +---+---+
 |       |
NO      YES
 |       |
 v       v
401   Authorized?
        +---+---+
        |       |
       NO      YES
        |       |
        v       v
       403    Process
```

---

# 7. Least Privilege

Chaque identité doit disposer uniquement des permissions nécessaires.

Cela s'applique à :

- utilisateurs ;
- services ;
- Kubernetes ServiceAccounts ;
- bases de données ;
- CI/CD ;
- composants AI.

---

# 8. RBAC

Le modèle RBAC permet d'associer :

```text
Identity
   |
   v
Role
   |
   v
Permissions
```

Les rôles doivent correspondre aux besoins réels.

---

# 9. Kubernetes RBAC

Kubernetes RBAC contrôle :

- namespaces ;
- resources ;
- verbs.

Exemple conceptuel :

```text
Role
 |
 +-- get
 +-- list
 +-- watch
```

et non :

```text
cluster-admin
```

pour chaque workload.

---

# 10. Validation des entrées

Toutes les données entrantes doivent être considérées non fiables.

```text
External Input
      |
      v
Validation
      |
 +----+----+
 |         |
VALID    INVALID
 |         |
 v         v
Process   Reject
```

Pydantic peut fournir cette validation côté FastAPI.

---

# 11. Validation de type

Exemples :

```text
string
integer
decimal
date
enum
identifier
```

Les valeurs doivent être vérifiées avant utilisation.

---

# 12. Validation métier

La validation technique ne remplace pas la validation métier.

Exemple :

```text
price = -100
```

peut être techniquement un entier valide mais métier incorrect.

---

# 13. SQL Injection

Les requêtes SQL doivent utiliser des paramètres.

À éviter :

```python
query = f"SELECT * FROM users WHERE id = {user_input}"
```

Préférer :

```python
query = "SELECT * FROM users WHERE id = :id"
```

avec binding de paramètres.

---

# 14. ORM et SQL

SQLAlchemy peut réduire certains risques de construction de requêtes, mais :

```text
ORM
!=
automatic security
```

Les entrées, permissions et requêtes doivent toujours être maîtrisées.

---

# 15. XSS

Si un frontend est développé, les contenus utilisateurs doivent être rendus de manière sûre.

Les données non fiables ne doivent pas être injectées directement dans du HTML arbitraire.

---

# 16. CSRF

Les applications utilisant des sessions/cookies doivent analyser le risque CSRF.

Le mécanisme dépend de l'architecture d'authentification retenue.

---

# 17. CORS

CORS doit être configuré explicitement.

À éviter en production sans justification :

```text
Access-Control-Allow-Origin: *
```

pour une application sensible.

---

# 18. TLS

Les communications externes doivent utiliser HTTPS lorsque pertinent.

Architecture :

```text
Client
  |
 HTTPS
  |
  v
Ingress
  |
  v
Application
```

cert-manager supporte l'automatisation des certificats.

---

# 19. Secrets

Les secrets ne doivent jamais être stockés en clair dans Git.

Interdit :

```text
password
token
private key
API key
```

dans :

- code ;
- repository ;
- image ;
- documentation.

---

# 20. Secrets actuels

Les mécanismes actuels comprennent :

```text
Kubernetes Secrets
GitLab Protected Variables
```

HashiCorp Vault reste :

```text
TARGET
```

---

# 21. Environment Variables

Les secrets peuvent être injectés sous forme de variables d'environnement lorsque cela est approprié.

Cependant, ils doivent rester protégés dans leur source.

---

# 22. Logs

Les logs ne doivent pas contenir :

- passwords ;
- tokens ;
- secrets ;
- full personal documents ;
- authorization headers ;
- sensitive payloads.

---

# 23. Error Handling

Les réponses d'erreur ne doivent pas exposer inutilement :

- stack trace ;
- SQL ;
- internal paths ;
- credentials ;
- infrastructure details.

Exemple public :

```json
{
  "detail": "Internal server error"
}
```

Le détail technique reste dans les logs protégés.

---

# 24. HTTP Status Codes

Utiliser des codes cohérents :

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
429 Too Many Requests
500 Internal Server Error
```

---

# 25. Rate Limiting

Pour certaines APIs exposées, le rate limiting peut protéger contre :

- abuse ;
- brute force ;
- surcharge ;
- AI cost explosion.

Il doit être introduit selon le besoin réel.

---

# 26. Timeouts

Les appels vers des dépendances doivent avoir des timeouts.

Exemple :

```text
API
 |
 v
AI Service
```

ne doit pas bloquer indéfiniment.

---

# 27. Retry

Les retries doivent être :

- limités ;
- contrôlés ;
- appliqués uniquement aux erreurs temporaires.

---

# 28. Dependency Security

Les dépendances applicatives doivent être suivies.

Exemples :

```text
pip
npm
container images
```

La CI peut intégrer progressivement des contrôles de vulnérabilités.

---

# 29. Container Security

Les images doivent :

- utiliser une base maîtrisée ;
- limiter les paquets ;
- éviter root lorsque possible ;
- ne contenir aucun secret ;
- être reproductibles.

---

# 30. User non-root

Lorsque compatible, un conteneur applicatif doit éviter :

```text
root
```

et utiliser un utilisateur dédié.

---

# 31. Read-only Filesystem

Pour certains workloads, un filesystem read-only peut réduire la surface d'attaque.

Ce contrôle dépend des besoins d'écriture du service.

---

# 32. Kubernetes SecurityContext

Exemples de contrôles :

```yaml
securityContext:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
```

Les valeurs finales doivent être compatibles avec l'application.

---

# 33. Resource Limits

Les limites de ressources contribuent également à la résilience.

```text
CPU
Memory
```

Elles peuvent réduire l'impact d'une consommation incontrôlée.

---

# 34. Network Security

L'application ne doit exposer que les services nécessaires.

```text
Internet / LAN
    |
    v
Ingress
    |
    v
Application
```

Les bases de données ne doivent pas être exposées arbitrairement.

---

# 35. Network Policies

Les Network Policies font partie de la cible de sécurité.

Leur efficacité dépend du CNI utilisé.

Flannel doit être évalué sur ce point avant de déclarer une enforcement complète.

---

# 36. Database Security

PostgreSQL doit utiliser :

- comptes séparés ;
- permissions minimales ;
- mots de passe protégés ;
- accès réseau contrôlé ;
- audit lorsque nécessaire.

---

# 37. Database Roles

Exemple :

```text
app_read
app_write
etl_user
analytics_read
admin
```

Les rôles doivent être adaptés au besoin réel.

---

# 38. Data Security

Les données doivent être classifiées.

Exemple :

```text
Public
Internal
Confidential
Restricted
Personal Data
```

La classification influence :

- accès ;
- partage ;
- rétention ;
- AI usage.

---

# 39. RGPD

Pour les données personnelles, la sécurité doit soutenir :

- minimisation ;
- contrôle d'accès ;
- protection ;
- rétention ;
- suppression ;
- traçabilité.

---

# 40. AI Security

Les risques AI incluent :

- prompt injection ;
- data leakage ;
- unauthorized retrieval ;
- hallucination ;
- unsafe output ;
- external provider exposure.

---

# 41. Prompt Injection

Un document ou utilisateur peut tenter d'influencer le modèle.

Le système ne doit pas considérer le contenu récupéré comme une instruction de confiance absolue.

---

# 42. RAG Authorization

Le contrôle doit se produire avant ou pendant le retrieval.

```text
User
 |
 v
Permissions
 |
 v
Allowed Documents
 |
 v
Retriever
```

---

# 43. Sensitive Context

Les données sensibles ne doivent pas être envoyées à un modèle externe sans décision explicite.

Principe :

```text
External AI
=
Governed Exception
```

---

# 44. Local AI

L'architecture local-first réduit certains risques de transfert externe.

Mais elle n'élimine pas :

- contrôle d'accès ;
- logging ;
- data governance ;
- AI governance ;
- model risk.

---

# 45. AI Output

Une réponse AI ne doit pas automatiquement devenir une décision métier critique.

```text
AI Output
   |
   v
Human / Business Validation
```

lorsque le contexte le nécessite.

---

# 46. ML Model Security

Le lifecycle ML doit conserver :

- model version ;
- artifact ;
- parameters ;
- metrics ;
- source ;
- approval.

MLflow fournit une partie de cette traçabilité.

---

# 47. Supply Chain Security

Le pipeline logiciel comprend :

```text
Source
 |
 v
Dependencies
 |
 v
Build
 |
 v
Container Image
 |
 v
Registry
 |
 v
Deployment
```

Chaque étape peut introduire un risque.

---

# 48. Git Security

GitLab doit protéger autant que possible :

- branches critiques ;
- CI variables ;
- merge process ;
- repository permissions.

---

# 49. Merge Requests

Les changements importants doivent passer par review lorsque le workflow le permet.

```text
Change
 |
 v
Merge Request
 |
 v
Review
 |
 v
CI
 |
 v
Merge
```

---

# 50. CI Security

Les contrôles possibles comprennent :

```text
unit tests
dependency scan
secret detection
container scan
linting
policy checks
```

Les outils réellement implémentés doivent être distingués des contrôles cible.

---

# 51. Secret Detection

La CI peut bloquer des secrets détectés dans les commits.

Cela complète les bonnes pratiques développeur.

---

# 52. Container Scanning

Les images peuvent être analysées pour identifier :

- CVEs ;
- packages vulnérables ;
- configuration risquée.

---

# 53. SAST

L'analyse statique peut identifier certains problèmes dans le code.

Elle ne remplace pas les tests ni la revue humaine.

---

# 54. DAST

Les tests dynamiques peuvent compléter l'analyse si l'application est disponible.

---

# 55. Security Headers

Les applications web peuvent utiliser des headers pertinents :

```text
Content-Security-Policy
X-Content-Type-Options
Referrer-Policy
Strict-Transport-Security
```

selon leur architecture.

---

# 56. Security Monitoring

Les événements applicatifs pertinents doivent pouvoir être observés.

Exemples :

```text
authentication failure
authorization failure
5xx spike
unusual request rate
AI errors
```

---

# 57. Audit Logs

Certains événements doivent être traçables.

Exemples :

```text
Admin action
Permission change
Critical data modification
Model promotion
Governance change
```

---

# 58. Correlation ID

Un `request_id` ou `trace_id` permet de relier :

```text
API
Logs
Traces
Errors
```

---

# 59. Security Incident

Processus :

```text
Detection
 |
 v
Triage
 |
 v
Containment
 |
 v
Eradication
 |
 v
Recovery
 |
 v
Postmortem
```

---

# 60. Backup Security

Les backups contiennent potentiellement des données sensibles.

Ils doivent être :

- contrôlés ;
- protégés ;
- limités ;
- suivis selon la criticité.

---

# 61. Restore Security

Une restauration doit également préserver :

- permissions ;
- secrets ;
- integrity ;
- configuration.

---

# 62. Security Testing

Les tests peuvent inclure :

```text
Unauthorized access
Invalid token
Invalid input
SQL injection attempts
Secret exposure
TLS check
RBAC check
Dependency scan
```

---

# 63. Exemple test 401

```text
Given endpoint requires authentication
When request is sent without credentials
Then response is 401
```

---

# 64. Exemple test 403

```text
Given authenticated user lacks required role
When protected action is requested
Then response is 403
```

---

# 65. Exemple validation

```text
Given invalid input
When request is submitted
Then application rejects it
And no unsafe query is executed
```

---

# 66. Exemple SQL injection

Test possible :

```text
' OR 1=1 --
```

Le résultat attendu :

```text
Input rejected or parameterized safely
```

sans comportement anormal.

---

# 67. Exemple secret exposure

Rechercher dans le repository :

```text
password=
token=
api_key=
```

ou utiliser un scanner dédié.

La preuve finale doit provenir d'un test réellement exécuté.

---

# 68. Exemple TLS

Test possible :

```bash
curl -I https://application.example
```

La preuve doit correspondre à l'environnement réel.

---

# 69. Security Acceptance Criteria

Une fonctionnalité sensible peut être considérée terminée lorsque :

```text
Authentication
+
Authorization
+
Validation
+
Secure Logging
+
Test
```

sont vérifiés selon son périmètre.

---

# 70. Threat Modeling

Pour les fonctionnalités critiques, un modèle simple peut analyser :

```text
Asset
Threat
Vulnerability
Control
Residual Risk
```

---

# 71. Exemple menace AI

| Élément | Exemple |
|---|---|
| Asset | Confidential document |
| Threat | Unauthorized extraction |
| Vulnerability | Unfiltered RAG |
| Control | Authorization before retrieval |
| Residual Risk | Prompt-based leakage |

---

# 72. Exemple menace API

| Élément | Exemple |
|---|---|
| Asset | Business data |
| Threat | Unauthorized access |
| Vulnerability | Missing authorization |
| Control | Backend RBAC |
| Residual Risk | Misconfigured role |

---

# 73. OWASP

Les catégories OWASP constituent une source utile de bonnes pratiques.

Les thèmes pertinents comprennent notamment :

- broken access control ;
- injection ;
- security misconfiguration ;
- vulnerable components ;
- authentication failures ;
- logging failures.

Le projet doit appliquer les contrôles réellement pertinents au périmètre.

---

# 74. Zero Trust

Principe :

```text
Never Trust Automatically
Always Verify
```

Il s'applique aux identités et services selon la maturité de l'architecture.

---

# 75. Security and Usability

Un contrôle de sécurité doit rester utilisable.

Une sécurité trop complexe peut générer des contournements.

Le design doit rechercher :

```text
Security
+
Usability
```

---

# 76. Security and Availability

Un contrôle ne doit pas détruire inutilement la disponibilité.

Exemple :

```text
Infinite blocking security checks
```

peuvent devenir une source d'indisponibilité.

---

# 77. Security and Eco-design

Ajouter des outils de sécurité augmente les ressources.

Cependant, réduire la sécurité uniquement pour économiser du CPU serait un mauvais arbitrage.

Le but est :

```text
Proportionate Security
```

---

# 78. Traceability

Le modèle cible est :

```text
Security Requirement
      |
      v
Control
      |
      v
Implementation
      |
      v
Test
      |
      v
Evidence
```

---

# 79. Exemple de traçabilité

```text
REQ-SEC-001
External traffic must use TLS
        |
        v
cert-manager + Ingress
        |
        v
HTTPS endpoint
        |
        v
curl TLS test
```

---

# 80. Matrice sécurité

| Domaine | Contrôle |
|---|---|
| Input | Validation |
| Identity | Authentication |
| Access | Authorization |
| Transport | TLS |
| Secrets | Secret management |
| Database | Least privilege |
| Containers | Security context |
| Kubernetes | RBAC |
| Data | Classification |
| AI | Local-first + governance |
| Runtime | Monitoring |
| Delivery | CI controls |

---

# 81. Preuves existantes

| Élément | Statut |
|---|---|
| Security architecture | DOCUMENTÉE |
| IAM architecture | DOCUMENTÉE |
| Zero Trust | DOCUMENTÉ |
| Secret management | DOCUMENTÉ |
| Network security | DOCUMENTÉE |
| Application security | DOCUMENTÉE |
| Container security | DOCUMENTÉE |
| Kubernetes security | DOCUMENTÉE |
| AI security | DOCUMENTÉE |
| Security monitoring | DOCUMENTÉ |
| Runtime application security proof | À CONSOLIDER |
| Executed security tests | À CONSOLIDER |

---

# 82. Preuves à produire

Ce dossier pourra contenir :

```text
01-rbac-test.txt
02-tls-test.txt
03-input-validation.txt
04-authentication-test.txt
05-authorization-test.txt
06-secret-scan.txt
07-container-scan.txt
08-security-test-report.md
```

seulement après exécution réelle.

---

# 83. Ce qui ne doit pas être affirmé sans preuve

Ne pas déclarer :

```text
Keycloak implemented
Vault implemented
NetworkPolicy enforcement complete
SAST operational
DAST operational
```

si ces éléments sont seulement des cibles.

---

# 84. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Threat / Requirement
       |
       v
Security Control
       |
       v
Implementation
       |
       v
Test
       |
       v
Evidence
```

---

# 85. État actuel

```text
Security design              COMPLETE
Security architecture        COMPLETE
Application controls         DOCUMENTED
Data security                DOCUMENTED
AI security                  DOCUMENTED
Secrets model                DOCUMENTED
TLS architecture             DOCUMENTED
RBAC architecture            DOCUMENTED
Executed security tests      TO COMPLETE
Runtime evidence             TO COMPLETE
```

---

# 86. Conclusion

La sécurité applicative repose sur :

```text
Validate
+
Authenticate
+
Authorize
+
Protect Secrets
+
Encrypt
+
Observe
+
Test
```

et s'intègre dans une défense en profondeur.

Le principe directeur est :

```text
A documented security control
becomes convincing
when it is implemented,
tested and evidenced.
```

---

**BC03 / C5 — Sécurité applicative : DOCUMENTATION BASELINE COMPLETE**