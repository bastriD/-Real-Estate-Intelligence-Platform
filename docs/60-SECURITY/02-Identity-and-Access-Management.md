# Identity & Access Management (IAM)

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document defines the Identity and Access Management (IAM) architecture of the Enterprise AI Platform.

It describes how identities are created, authenticated, authorized, managed and audited across the platform.

IAM provides the foundation for secure access to infrastructure, applications, APIs, AI services and enterprise data.

---

# 2. Scope

This document applies to:

- Human users
- Service accounts
- APIs
- Kubernetes workloads
- CI/CD pipelines
- Git repositories
- Databases
- AI services
- Administrative access

---

# 3. Objectives

The IAM architecture aims to:

- Centralize identity management
- Enable Single Sign-On (SSO)
- Enforce Least Privilege
- Improve authentication security
- Simplify user administration
- Secure service-to-service communication
- Provide complete auditability

---

# 4. IAM Principles

The platform follows these principles:

- One identity per user
- Centralized authentication
- Federated identity where appropriate
- Least Privilege
- Default Deny
- Role-Based Access Control (RBAC)
- Continuous identity verification

---

# 5. IAM Architecture

```
Users

↓

Keycloak

↓

Identity Tokens

↓

Applications

↓

APIs

↓

Enterprise Platform

↓

Data Platform

↓

Infrastructure
```

Keycloak becomes the enterprise Identity Provider (IdP).

---

# 6. Identity Types

The platform manages multiple identity categories.

## Human Users

Examples:

- Platform Administrators
- Data Engineers
- AI Engineers
- Business Users
- Analysts
- Developers

---

## Service Accounts

Used for:

- Airflow
- dbt
- MLflow
- OpenMetadata
- GitLab Runner
- Kubernetes workloads

Service accounts should never be shared.

---

## Machine Identities

Examples:

- Kubernetes Pods
- Scheduled Jobs
- CI/CD Pipelines
- Internal APIs

Machine identities enable secure automation.

---

# 7. Authentication

Current authentication mechanisms include:

- Kubernetes authentication
- PostgreSQL authentication
- OpenMetadata authentication
- Git authentication

Future enterprise authentication includes:

- Keycloak
- OAuth2
- OpenID Connect (OIDC)
- SAML (if required)
- Multi-Factor Authentication (MFA)

---

# 8. Single Sign-On (SSO)

Future architecture provides centralized authentication.

```
User

↓

Keycloak Login

↓

Authentication

↓

Identity Token

↓

Enterprise Applications
```

Benefits include:

- Single login experience
- Central policy enforcement
- Simplified administration
- Improved security

---

# 9. Authorization

Authorization determines what authenticated identities may access.

The platform uses RBAC.

Permissions are assigned through:

- Roles
- Groups
- Responsibilities
- Business domains

Authorization decisions should be centrally governed.

---

# 10. Enterprise Roles

Typical platform roles include:

| Role | Responsibilities |
|------|------------------|
| Platform Administrator | Platform management |
| Security Administrator | Security configuration |
| Data Engineer | Data pipelines |
| AI Engineer | AI platform |
| Business Analyst | Reporting |
| Developer | Application development |
| Read-Only User | Observation only |

Roles should reflect business responsibilities rather than technical implementation.

---

# 11. Kubernetes IAM

Current implementation includes:

- RBAC
- Service Accounts
- Namespace isolation
- Cluster Roles
- Role Bindings

Future improvements:

- OIDC integration
- Keycloak authentication
- Fine-grained authorization

---

# 12. Database Access

Database access should follow:

- Individual accounts where practical
- Service accounts for automation
- Role-based permissions
- Principle of Least Privilege

Direct administrative access should be limited.

---

# 13. API Authentication

Enterprise APIs should support:

- OAuth2
- JWT access tokens
- HTTPS
- Token expiration
- Refresh tokens

Public APIs should never expose administrative functionality.

---

# 14. Service-to-Service Authentication

Internal platform services should authenticate securely.

Examples:

- Airflow → PostgreSQL
- MLflow → MinIO
- OpenMetadata → PostgreSQL
- APIs → AI Platform

Future improvements include:

- Mutual TLS (mTLS)
- Short-lived service tokens
- Automated credential rotation

---

# 15. Privileged Access Management

Administrative accounts require additional protection.

Recommendations include:

- MFA
- Separate administrative accounts
- Audit logging
- Session review
- Restricted access windows where appropriate

Privileged accounts should not be used for routine activities.

---

# 16. Identity Lifecycle

Identity management follows this lifecycle.

```
Create

↓

Approve

↓

Provision

↓

Authenticate

↓

Authorize

↓

Review

↓

Disable

↓

Delete
```

Identity reviews should occur periodically.

---

# 17. Audit and Monitoring

IAM events should be logged.

Examples include:

- Login attempts
- Failed authentication
- Role changes
- Permission changes
- Token issuance
- Administrative actions

Audit logs support compliance and incident investigations.

---

# 18. Current Implementation

Current platform capabilities include:

- Kubernetes RBAC
- PostgreSQL roles
- OpenMetadata user management
- Git repository permissions
- Service Accounts
- Namespace isolation

The platform already implements foundational IAM controls.

---

# 19. Future Evolution

Planned enhancements include:

- Keycloak deployment
- SSO
- MFA
- Identity Federation
- OIDC integration
- SCIM user provisioning
- Centralized RBAC
- Policy-based access control
- Automated access reviews

The architecture evolves toward a centralized enterprise IAM model.

---

# 20. Architecture Decisions

Key architectural decisions include:

- Keycloak as the enterprise Identity Provider
- RBAC as the primary authorization model
- OAuth2/OIDC for authentication
- Service accounts for automation
- Centralized SSO
- Least Privilege enforcement
- Auditable identity lifecycle

---

# 21. Related Documents

- Security Architecture
- Zero Trust Architecture
- Kubernetes Security
- Application Security
- Data Security
- Network Security
- Secret Management
- Compliance & Risk