# Application Architecture

**Version:** 1.0  
**Status:** Draft  
**Owner:** Bastri Murad  
**Project:** Real Estate Intelligence Platform  
**Platform:** Enterprise AI Platform  
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document describes the application architecture of the Real Estate Intelligence Platform.

It defines the logical components, business services, communication patterns, responsibilities, and interactions between the application and the Enterprise AI Platform.

The objective is to provide a modular, scalable, maintainable, and secure application architecture following modern cloud-native principles.

---

# 2. Architecture Overview

The Real Estate Intelligence Platform is implemented as a modular service-oriented application deployed on Kubernetes.

Rather than embedding infrastructure capabilities within the application, it consumes shared services provided by the Enterprise AI Platform.

The architecture separates:

- Presentation
- Business Logic
- Data Processing
- AI Services
- Platform Services

---

# 3. High-Level Architecture

```text
                    Users
                       │
            React Web Application
                       │
────────────────────────────────────────────

                 FastAPI Gateway

────────────────────────────────────────────

Business Services

• Property Service
• Search Service
• Recommendation Service
• Notification Service
• Analytics Service
• User Service

────────────────────────────────────────────

Enterprise AI Platform

Authentication
Data Platform
AI Platform
Observability
Infrastructure

────────────────────────────────────────────

Kubernetes
```

---

# 4. Architectural Style

The application follows a modular service-oriented architecture.

Key characteristics:

- API-first
- Stateless services
- Domain separation
- Shared platform services
- Independent deployment
- Event-ready architecture

Future evolution may progressively introduce microservices where justified by business needs.

---

# 5. Logical Components

## Frontend

Responsibilities:

- User interface
- Authentication
- Property search
- Dashboards
- Administration

Technology:

- React

---

## API Layer

Responsibilities:

- Request routing
- Validation
- Authentication
- Authorization
- OpenAPI documentation

Technology:

- FastAPI

---

## Business Layer

Contains business logic.

Modules include:

- Property Management
- Search
- User Management
- Recommendations
- Analytics
- Notifications

---

## Data Layer

Responsible for:

- Data persistence
- Queries
- Transactions
- Data integrity

Primary database:

- PostgreSQL

---

## AI Layer

Responsibilities:

- Recommendation Engine
- Semantic Search
- Market Analysis
- AI Assistant (future)

Technologies:

- MLflow
- Ollama
- Qdrant

---

## Platform Layer

Provided by the Enterprise AI Platform.

Includes:

- Keycloak
- PostgreSQL
- Airflow
- OpenMetadata
- Monitoring
- Vault
- GitOps

---

# 6. Component Responsibilities

| Component | Responsibility |
|------------|---------------|
| React | User Interface |
| FastAPI | REST API |
| Property Service | Property lifecycle |
| Search Service | Property discovery |
| Recommendation Service | AI recommendations |
| Analytics Service | Business analytics |
| Notification Service | Alerts |
| User Service | User profiles |
| PostgreSQL | Persistence |
| Airflow | Data workflows |
| MLflow | Model lifecycle |
| Qdrant | Semantic search |

---

# 7. Communication

Current communication:

```
Frontend
      │
 REST API
      │
 FastAPI
      │
 PostgreSQL
```

Future communication:

```
Frontend
      │
 REST API
      │
 FastAPI
      │
Kafka Events
      │
Business Services
```

---

# 8. Deployment Model

Each component is deployed independently using Kubernetes.

Deployment is managed through GitOps using Argo CD.

All workloads include:

- Resource limits
- Health probes
- Monitoring
- Logging
- TLS
- RBAC

---

# 9. Security

Authentication:

- Keycloak
- OAuth2
- OpenID Connect

Authorization:

- RBAC

Secrets:

- Vault

Communication:

- HTTPS
- TLS

---

# 10. Scalability

Application services are horizontally scalable.

Future scaling includes:

- Kafka consumers
- AI inference workers
- Background processing
- Event-driven services

---

# 11. Availability

The application benefits from platform capabilities:

- Kubernetes self-healing
- ReplicaSets
- Rolling updates
- Automatic restart
- GitOps reconciliation

---

# 12. Design Principles

The application follows:

- Single Responsibility
- Separation of Concerns
- Stateless Services
- API-first
- Reuse before Build
- Security by Design
- Observability by Default

---

# 13. Future Evolution

Future capabilities include:

- Mobile application
- Public API
- AI Agent
- Event-driven microservices
- GraphQL API
- Multi-tenant architecture

---

# 14. Related Documents

- Business Architecture
- Infrastructure Architecture
- Kubernetes Architecture
- Security Architecture
- Data Architecture
- AI Architecture
- GitOps Strategy