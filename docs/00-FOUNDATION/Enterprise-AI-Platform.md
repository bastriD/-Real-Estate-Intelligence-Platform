# Enterprise AI Platform Architecture

## Purpose

This document defines the target architecture of the Enterprise AI Platform that will host multiple applications, including the RNCP Real Estate Intelligence Platform. The objective is to evolve the existing Kubernetes platform instead of building isolated projects.

---

# Vision

The platform provides:

- Platform Engineering
- DevSecOps
- Data Engineering
- MLOps
- AI Platform Engineering
- GitOps
- Observability
- Governance

Every application is deployed as a workload on the same Kubernetes platform.

---

# Architecture Layers

```text
                 GitLab
                    │
              GitLab CI/CD
                    │
          Container Registry
                    │
                 Argo CD
                    │
================================================

          Kubernetes Enterprise Platform

================================================

Security
---------
Keycloak
Vault
Cert-Manager
External Secrets

Data
----
PostgreSQL
Redis
Kafka
MinIO
Qdrant

AI
--
Airflow
MLflow
OpenMetadata
Ollama
Feature Store (future)

Applications
------------
FastAPI APIs
React Frontends
Recommendation Engine
Matching Engine
Analytics API
Notification Service

Observability
-------------
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
Alertmanager

Infrastructure
--------------
NGINX Ingress
Velero
StorageClass
DNS
```

---

# Namespace Strategy

```
argocd
platform
security
data
ai
applications
monitoring
infrastructure
```

---

# Repository Strategy

```
lab-gitops/
platform-charts/
platform-manifests/
applications/
terraform/
ansible/
docs/
```

---

# GitOps Layout

```
apps/
 ├── platform/
 ├── security/
 ├── data/
 ├── ai/
 ├── applications/
 ├── monitoring/
 └── infrastructure/
```

---

# Security Layer

## Keycloak

- Single Sign-On
- OAuth2 / OpenID Connect
- JWT
- RBAC
- Identity Federation (future)

## Vault

- Secrets
- Dynamic credentials
- PKI

## Cert-Manager

- Internal CA
- TLS automation

---

# Data Layer

## PostgreSQL

Transactional databases.

## Redis

Distributed cache.

## Kafka

Event streaming.

Example events:

- UserRegistered
- PropertyCreated
- PropertyUpdated
- VisitBooked
- OfferAccepted
- ModelRetrained

## MinIO

Object storage for datasets, artifacts, exports and documents.

## Qdrant

Vector database for semantic search, recommendations and RAG.

---

# AI Layer

## Airflow

Workflow orchestration.

## MLflow

Model lifecycle.

## Ollama

Local LLM inference.

## OpenMetadata

Data catalog, lineage, governance and quality.

---

# Application Layer

Current target applications:

- Real Estate API
- Real Estate Frontend
- Recommendation Engine
- Matching Engine
- Analytics API
- Notification Service

Applications communicate through REST and Kafka.

---

# Observability

- Prometheus
- Grafana
- Loki
- Tempo
- OpenTelemetry
- Alertmanager

Unified dashboards and tracing across all workloads.

---

# Roadmap

## Phase 1

- Platform standardization
- Namespace structure
- GitOps refactoring
- Documentation

## Phase 2

- Keycloak
- Redis
- Authentication

## Phase 3

- Kafka
- Qdrant
- Event-driven services

## Phase 4

- AI Gateway
- Production RAG
- Multi-agent services

---

# Definition of Done

A component is considered production-ready when:

- Managed by GitOps
- Documented
- Monitored
- Backed up
- TLS enabled
- RBAC configured
- Resource limits defined
- Health probes configured
- Integrated with observability
- Included in disaster recovery procedures

---

# Long-Term Goal

Build a reusable Enterprise AI Platform capable of hosting multiple business applications while demonstrating Platform Engineering, DevSecOps, Data Engineering, MLOps and AI Platform Engineering best practices.
