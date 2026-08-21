# ADR-0004 — Adopt NGINX Ingress as the Standard Kubernetes North-South Entry Point

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** Kubernetes / Networking / Platform
**Project:** Enterprise AI Platform
**Related ADRs:** ADR-0001, ADR-0002, ADR-0003
**Related Technologies:** NGINX Ingress Controller, Kubernetes, cert-manager, Internal DNS
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform hosts multiple Kubernetes services that require HTTP or HTTPS access.

Examples include:

* Argo CD
* Airflow
* MLflow
* OpenMetadata
* Grafana
* Business APIs
* Internal platform applications
* Future AI and RAG services

Directly exposing every Kubernetes Service using individual external ports would create:

* Port-management complexity
* Inconsistent TLS handling
* Weak routing standardization
* Difficult hostname management
* Increased attack surface
* Poor user experience
* Operational duplication

The platform therefore requires a standardized north-south traffic entry point.

---

# 2. Problem

The Kubernetes platform needs a mechanism that can:

* Route HTTP and HTTPS traffic
* Use host-based routing
* Support internal DNS names
* Terminate TLS
* Integrate with cert-manager
* Expose multiple applications through a common entry model
* Support GitOps deployment
* Remain simple to operate
* Fit existing infrastructure resources

---

# 3. Decision

The platform will use **NGINX Ingress Controller** as the standard Kubernetes north-south HTTP/HTTPS entry point.

The standard flow is:

```text
Client
  │
  ▼
Internal DNS
  │
  ▼
Ingress Endpoint
  │
  ▼
NGINX Ingress Controller
  │
  ▼
Kubernetes Service
  │
  ▼
Application Pod
```

TLS certificate lifecycle is handled through **cert-manager** where appropriate.

---

# 4. Architecture Role

NGINX Ingress Controller provides:

* Host-based routing
* Path-based routing
* TLS termination
* Centralized HTTP entry
* Kubernetes-native Ingress resource support
* Integration with cert-manager
* Standardized application exposure

It becomes the default HTTP/HTTPS exposure model for Kubernetes applications unless a documented exception exists.

---

# 5. Current Implementation

NGINX Ingress is already deployed and operational.

Current platform ingress examples include internal hostnames such as:

```text
airflow.lab.local
mlflow.lab.local
```

Current status:

```text
IMPLEMENTED
```

---

# 6. High-Level Architecture

```text
User / Internal Client
        │
        ▼
      DNS
        │
        ▼
Ingress Address
        │
        ▼
┌─────────────────────────┐
│ NGINX Ingress Controller│
└────────────┬────────────┘
             │
      ┌──────┼───────┐
      │      │       │
      ▼      ▼       ▼
   Airflow  MLflow   API
```

This allows multiple applications to share a common routing architecture.

---

# 7. Alternatives Considered

## Option 1 — NGINX Ingress Controller

Advantages:

* Mature
* Widely adopted
* Strong Kubernetes integration
* Simple host/path routing
* Good cert-manager integration
* Existing operational familiarity
* Appropriate for current scale

Disadvantages:

* Additional Kubernetes component
* Configuration through annotations can become complex
* Traditional Ingress API has limitations compared with newer Gateway API models

Selected.

---

## Option 2 — Traefik

Advantages:

* Kubernetes-native
* Dynamic configuration
* Good dashboard and middleware capabilities
* Strong integration ecosystem

Disadvantages:

* No compelling requirement to replace the existing NGINX deployment
* Migration adds operational work
* Additional technology change without clear benefit

Not selected.

---

## Option 3 — HAProxy Ingress

Advantages:

* Mature
* High-performance proxy
* Advanced traffic handling

Disadvantages:

* Smaller fit with the current operational model
* No significant current advantage over NGINX

Not selected.

---

## Option 4 — Direct NodePort Exposure

Advantages:

* Simple
* No ingress controller required

Disadvantages:

* Poor hostname routing
* Port sprawl
* Weak centralized TLS model
* Harder governance
* Poor scalability

Not selected as the standard.

---

## Option 5 — Individual LoadBalancer Services

Advantages:

* Direct exposure per service
* Simple conceptual isolation

Disadvantages:

* Requires suitable external load-balancer implementation
* More addresses/resources
* Repeated configuration
* Weak standardization for the current private environment

Not selected as the default pattern.

---

# 8. Decision Criteria

The decision considered:

| Criterion                           | Importance |
| ----------------------------------- | ---------: |
| Operational simplicity              |       High |
| Kubernetes integration              |   Critical |
| TLS support                         |   Critical |
| DNS integration                     |       High |
| GitOps support                      |       High |
| Resource efficiency                 |       High |
| Community maturity                  |       High |
| Advanced service-mesh functionality |        Low |
| Gateway API requirement             |     Future |

NGINX Ingress provides the best current fit.

---

# 9. DNS Integration

Applications should use stable DNS names rather than IP addresses or arbitrary ports.

Example:

```text
airflow.lab.local
```

rather than:

```text
192.168.x.x:31234
```

This improves:

* Usability
* Service identity
* TLS management
* Configuration portability

---

# 10. TLS Architecture

TLS should be used where appropriate.

Conceptual flow:

```text
Client
  │
 HTTPS
  │
  ▼
NGINX Ingress
  │
TLS Termination
  │
  ▼
Application Service
```

Internal upstream encryption may be added where security requirements justify it.

---

# 11. cert-manager Integration

cert-manager is used to automate certificate lifecycle.

Relationship:

```text
Ingress
   │
   ▼
Certificate Resource
   │
   ▼
cert-manager
   │
   ▼
Issuer / ClusterIssuer
   │
   ▼
TLS Secret
   │
   ▼
NGINX Ingress
```

This reduces manual certificate operations.

---

# 12. Certificate Governance

Certificate controls should include:

* Defined issuer
* Certificate expiry monitoring
* TLS secret protection
* Renewal monitoring
* Restricted private-key access

Certificate automation does not eliminate certificate governance.

---

# 13. Exposure Policy

Not every Kubernetes Service should be exposed through ingress.

Preferred model:

```text
Internal-only service
→ ClusterIP

User-facing HTTP service
→ Ingress where justified
```

Exposure should be intentional.

---

# 14. Internal vs External Exposure

The current platform primarily operates in a private environment.

Most ingress endpoints are intended for:

* Internal users
* Administrative interfaces
* Platform services

Public Internet exposure should require explicit security review.

---

# 15. Security Consequences

The ingress controller becomes a significant security boundary.

Controls should include:

* TLS
* Restricted exposure
* Authentication at application or proxy layer
* Updated controller versions
* Monitoring
* Logging
* Network controls
* Minimal administrative access

---

# 16. Authentication

NGINX Ingress itself does not replace application authentication.

The architecture separates:

```text
Traffic Routing
       │
       ▼
NGINX Ingress

Authentication / Authorization
       │
       ▼
Application / Identity Layer
```

Authentication mechanisms should be selected according to the service.

---

# 17. Ingress Annotations

Annotations can provide additional behavior.

Examples may include:

* Rewrite
* Timeouts
* Body-size limits
* Backend protocol
* Authentication integration

However excessive annotation-based customization should be avoided.

If ingress configuration becomes highly complex, architecture review may be required.

---

# 18. Standardization

Applications should follow a standard ingress pattern where practical.

Example:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: application
spec:
  ingressClassName: nginx
  rules:
    - host: application.lab.local
```

Exact production configuration remains service-specific.

---

# 19. Governance as Code

Ingress definitions are Kubernetes resources and therefore part of Governance as Code.

Potential automated controls include:

* Require approved ingress class
* Require TLS for selected namespaces
* Require owner labels
* Block unsupported annotations
* Restrict public hostnames
* Require standard naming

These can later be validated through CI and Policy as Code.

---

# 20. GitOps Consequences

Ingress configuration should be stored in Git.

Flow:

```text
Ingress Change
      │
      ▼
Git
      │
      ▼
CI Validation
      │
      ▼
Argo CD
      │
      ▼
Kubernetes
```

Manual ingress changes should not become permanent runtime configuration.

---

# 21. Observability

Ingress should provide visibility into:

* Request rate
* HTTP status
* Latency
* Upstream errors
* Controller health
* TLS behavior

Ingress logs should integrate with Loki.

Metrics should integrate with Prometheus.

---

# 22. Ingress Logging

Useful logging fields include:

* Host
* HTTP method
* Route
* Status
* Request duration
* Upstream duration
* Request ID

Sensitive authentication headers should not be logged.

---

# 23. Ingress Metrics

Useful metrics include:

* Requests per second
* Error rate
* P95 latency
* Active connections
* Controller health

These support both application and platform investigation.

---

# 24. Failure Model

Possible failure chain:

```text
DNS Failure
    │
    ▼
Ingress Unreachable
    │
    ▼
Application Appears Down
```

or:

```text
Ingress Healthy
    │
    ▼
Backend Service Failure
    │
    ▼
502 / 503 Response
```

Troubleshooting must distinguish ingress failure from backend failure.

---

# 25. Availability Consequences

A failure of the ingress layer may affect multiple exposed applications simultaneously.

Therefore ingress is a shared platform dependency.

Availability should be improved through:

* Multiple controller replicas where resources permit
* Kubernetes rescheduling
* Readiness/liveness probes
* Monitoring

---

# 26. Shared Failure Domain

Centralized ingress introduces a shared logical failure domain.

This trade-off is accepted because it also provides:

* Standardized routing
* Centralized TLS
* Reduced port exposure
* Easier operations

The controller must therefore be treated as a critical platform service.

---

# 27. Resource Consequences

NGINX Ingress has a modest resource footprint for the current platform scale.

Resource requests and limits should be configured based on observed traffic rather than arbitrary over-provisioning.

---

# 28. Timeout Governance

AI and data endpoints may require longer request durations than conventional APIs.

Examples:

```text
AI inference
→ potentially longer timeout

Standard API
→ shorter timeout
```

Timeouts should be service-specific and should not be globally increased without justification.

---

# 29. AI Workload Considerations

Future AI services may have:

* Slow inference
* Streaming responses
* Larger payloads

Ingress configuration should support these requirements without weakening global defaults unnecessarily.

---

# 30. WebSocket / Streaming

If future applications require:

* WebSockets
* Server-sent events
* Streaming AI responses

NGINX configuration should be validated for those workloads.

No controller replacement is currently required for these patterns.

---

# 31. Rate Limiting

Future security or reliability requirements may justify rate limiting.

Possible enforcement points include:

* NGINX Ingress
* AI Gateway
* Application layer

The correct layer depends on the use case.

---

# 32. Gateway API Consideration

Kubernetes Gateway API provides a newer and more expressive traffic-management model than traditional Ingress.

Potential advantages include:

* Better role separation
* Rich routing model
* More standardized advanced traffic configuration

However the platform does not currently require migration.

---

# 33. Gateway API Review Trigger

The architecture should reconsider the ingress model if:

* Advanced traffic policies become common
* Multi-team route delegation becomes necessary
* Gateway API becomes materially simpler for requirements
* Current Ingress annotation complexity becomes excessive
* NGINX Ingress support strategy changes

Migration should be requirement-driven.

---

# 34. Service Mesh

A service mesh is not required merely because NGINX Ingress is used.

The concerns differ:

```text
Ingress
→ North-South Traffic

Service Mesh
→ Primarily East-West Service Communication
```

A service mesh would introduce significant additional complexity and requires a separate ADR if ever considered.

---

# 35. Disaster Recovery

Ingress is an early platform recovery dependency.

Typical reconstruction:

```text
Kubernetes
   │
   ▼
CNI
   │
   ▼
Ingress Controller
   │
   ▼
cert-manager
   │
   ▼
Application Ingress Resources
```

GitOps should restore most configuration.

---

# 36. Recovery Validation

After ingress recovery, validate:

```bash
kubectl get pods -n ingress-nginx
kubectl get ingress -A
```

Then validate DNS and HTTPS access to a known service.

---

# 37. Risks

## Risk — Shared Ingress Failure

Mitigation:

* Replicas
* Kubernetes self-healing
* Monitoring

## Risk — Misconfiguration Exposes Service

Mitigation:

* Git review
* Policy as Code
* Exposure standards

## Risk — TLS Misconfiguration

Mitigation:

* cert-manager
* Certificate monitoring
* Standard templates

## Risk — Controller Vulnerability

Mitigation:

* Version governance
* Security monitoring
* Controlled updates

---

# 38. Technical Debt Consideration

NGINX Ingress is not currently technical debt.

It satisfies current requirements.

It becomes a debt candidate only if:

* Required traffic capabilities cannot be implemented safely
* Support declines
* Configuration complexity becomes excessive
* A migration is intentionally deferred after requirements change

---

# 39. Technology Governance Status

Recommended classification:

```text
Technology: NGINX Ingress Controller
Category: Kubernetes Networking
Lifecycle: ADOPT
```

---

# 40. Success Criteria

The decision remains valid while:

* Applications are routed reliably
* DNS-based access works
* TLS lifecycle operates correctly
* Resource usage remains appropriate
* Operational complexity remains manageable
* Security requirements can be met
* No critical routing capability is blocked

---

# 41. Review Triggers

Review this ADR if:

* NGINX Ingress becomes unsupported
* Gateway API becomes a clear operational requirement
* Traffic-management requirements exceed current capabilities
* Public-facing scale changes significantly
* Security requirements change materially
* Service mesh adoption changes the traffic architecture

---

# 42. Governance as Code Metadata

Future machine-readable representation:

```yaml
id: ADR-0004
title: Adopt NGINX Ingress as Standard Kubernetes North-South Entry Point
status: accepted

domain:
  - kubernetes
  - networking
  - platform

technologies:
  - nginx-ingress
  - cert-manager

owner: platform
implementation_status: implemented

alternatives:
  - traefik
  - haproxy-ingress
  - nodeport
  - gateway-api

review_triggers:
  - gateway-api-required
  - advanced-routing-required
  - nginx-ingress-support-change

supersedes: null
superseded_by: null
```

---

# 43. Related Documents

* ADR-0001-Kubernetes
* ADR-0002-ArgoCD-GitOps
* ADR-0003-Flannel-CNI
* Network Architecture
* Kubernetes Architecture
* Security Architecture
* TLS / Certificate Management
* Observability Architecture
* Disaster Recovery
* Technology Governance
* Governance Architecture
