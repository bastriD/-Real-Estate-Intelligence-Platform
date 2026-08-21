# Network Architecture

**Version:** 1.0  
**Status:** Draft  
**Owner:** Bastri Murad  
**Project:** Enterprise AI Platform  
**Business Application:** Real Estate Intelligence Platform  
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document defines the network architecture of the Enterprise AI Platform.

It describes how physical devices, virtual machines, Kubernetes nodes, platform services and external users communicate securely and efficiently.

The objective is to provide a reliable, maintainable and secure networking model supporting both the Enterprise AI Platform and all hosted business applications.

---

# 2. Scope

This document covers:

- Physical network
- Virtual networking
- Kubernetes networking
- DNS
- Ingress
- Service communication
- External access
- Internal traffic
- Network security
- Future evolution

---

# 3. Network Objectives

The network architecture is designed to provide:

- Reliable communication
- Low operational complexity
- Secure service exposure
- Internal service discovery
- TLS encryption
- High availability where possible
- Easy troubleshooting
- Reproducible configuration

---

# 4. Network Layers

The platform networking is organized into four layers.

```
Internet
      │
Home LAN
      │
Proxmox Virtual Network
      │
Kubernetes Cluster Network
```

Each layer has a clearly defined responsibility.

---

# 5. Physical Network

Current infrastructure consists of:

- ISP connection
- Residential router
- Ethernet switch
- Ethernet-connected servers
- Wi-Fi-connected worker nodes where appropriate

The physical network provides connectivity between all infrastructure components.

No VLAN segmentation is currently implemented.

---

# 6. Virtual Network

The virtualization layer is provided by Proxmox VE.

Responsibilities include:

- VM communication
- VM isolation
- Bridge networking
- Kubernetes node connectivity

Each virtual machine receives a static IP address within the local network.

---

# 7. Kubernetes Networking

Container networking is provided by:

**Flannel CNI**

Responsibilities:

- Pod-to-Pod communication
- Pod IP allocation
- Cross-node routing
- Cluster networking

Flannel provides a simple and stable networking model appropriate for the current platform size.

---

# 8. Service Networking

Kubernetes Services provide stable endpoints for workloads.

Supported service types include:

- ClusterIP
- NodePort (where required)
- LoadBalancer (future)
- Ingress

Application components communicate through Kubernetes Services rather than Pod IP addresses.

---

# 9. DNS Architecture

Two DNS layers are used.

## Internal Kubernetes DNS

Provided by:

- CoreDNS

Responsibilities:

- Service discovery
- Internal routing
- Namespace resolution

Example:

```
postgresql.retail-data.svc.cluster.local
```

---

## Platform DNS

The platform uses the domain:

```
lab.local
```

Examples:

```
gitlab.lab.local

argocd.lab.local

grafana.lab.local

airflow.lab.local

mlflow.lab.local

openmetadata.lab.local
```

This naming convention provides consistent access to platform services.

---

# 10. Ingress Architecture

External HTTP and HTTPS traffic enters the platform through:

- NGINX Ingress Controller

Responsibilities:

- TLS termination
- Reverse proxy
- Host-based routing
- Request forwarding
- Load balancing

Typical routing:

```
User

↓

https://grafana.lab.local

↓

NGINX Ingress

↓

Grafana Service

↓

Grafana Pods
```

---

# 11. Certificate Management

Certificates are managed through:

- cert-manager

Responsibilities:

- Certificate creation
- Renewal
- Secret management

Every public platform endpoint should use HTTPS.

---

# 12. Internal Communication

Platform services communicate using Kubernetes networking.

Examples include:

- Airflow → PostgreSQL
- MLflow → MinIO
- OpenMetadata → PostgreSQL
- Grafana → Prometheus
- Grafana → Loki
- Grafana → Tempo
- Argo CD → Kubernetes API

Communication remains internal unless explicitly exposed.

---

# 13. External Communication

External users access services through:

```
Browser

↓

HTTPS

↓

NGINX Ingress

↓

Application Service

↓

Pods
```

Direct Pod access is prohibited.

---

# 14. AI Network Traffic

AI services communicate internally.

Examples:

```
Application

↓

Recommendation API

↓

Ollama

↓

Model Inference

↓

Application Response
```

Future AI components such as Qdrant will follow the same pattern.

---

# 15. Data Platform Traffic

Typical data flow:

```
Data Source

↓

Airflow

↓

PostgreSQL

↓

OpenMetadata

↓

Analytics

↓

Business Application
```

All internal communication remains inside the Kubernetes cluster whenever possible.

---

# 16. Network Security

Current controls include:

- Kubernetes namespaces
- RBAC
- TLS
- Ingress restrictions

Future improvements include:

- Network Policies
- Zero Trust segmentation
- Mutual TLS
- Service Mesh

---

# 17. Failure Scenarios

| Failure | Expected Behaviour |
|----------|-------------------|
| DNS failure | Service resolution unavailable |
| Ingress failure | External access interrupted |
| Node network loss | Pods rescheduled where possible |
| Router failure | Platform isolated from Internet |
| Wi-Fi instability | Reduced worker availability |
| Certificate expiration | HTTPS unavailable until renewal |

---

# 18. Monitoring

Network health is monitored using:

- Prometheus
- Grafana
- Kubernetes metrics
- Ingress metrics
- Node metrics

Future monitoring may include:

- Flow metrics
- Network latency
- Packet loss
- DNS latency

---

# 19. Capacity Management

Network capacity is evaluated using:

- Node bandwidth
- Network latency
- Service response time
- Ingress throughput
- Error rates
- Connection counts

The current network is sufficient for the expected educational and development workloads.

---

# 20. Constraints

Current limitations include:

- Residential Internet connection
- Single LAN
- No VLAN segmentation
- No redundant routing
- No redundant switches
- Wi-Fi worker nodes

These constraints are accepted within the project scope.

---

# 21. Architecture Decisions

Key networking decisions include:

- Flannel as the CNI
- NGINX as the Ingress Controller
- CoreDNS for service discovery
- cert-manager for TLS
- Internal service communication through ClusterIP Services
- Host-based routing using `lab.local`
- Kubernetes-native networking
- HTTPS for externally exposed services

---

# 22. Current State

Current networking implementation:

- Residential LAN
- Proxmox bridge networking
- Flannel CNI
- CoreDNS
- NGINX Ingress
- cert-manager
- Kubernetes Services
- Internal DNS
- GitOps-managed ingress resources

The networking architecture is stable and supports all current platform services.

---

# 23. Target State

Planned improvements include:

- Network Policies
- Keycloak integration
- API Gateway
- Enhanced ingress security
- Better traffic observability
- Automated certificate monitoring

These enhancements strengthen security and operational visibility without changing the overall network architecture.

---

# 24. Related Documents

- Infrastructure Architecture
- Physical Architecture
- Virtual Infrastructure
- Kubernetes Architecture
- Security Architecture
- GitOps Strategy
- Observability Architecture
- Disaster Recovery Plan