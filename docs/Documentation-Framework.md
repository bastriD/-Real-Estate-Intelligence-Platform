# Documentation Framework

## Purpose

This framework defines how all documentation in this repository is organized, written, reviewed, versioned and maintained.

The objective is to keep every document consistent, traceable and reusable.

---

# Repository Structure

```text
docs/
├── README.md
├── 00-FOUNDATION/
├── 10-BUSINESS/
├── 20-APPLICATION/
├── 30-INFRASTRUCTURE/
├── 40-DATA/
├── 50-AI/
├── 60-SECURITY/
├── 70-DEVOPS/
├── 80-OPERATIONS/
├── 90-OBSERVABILITY/
├── 95-GOVERNANCE/
├── 98-ADR/
└── 99-DIAGRAMS/
```

---

# Document Naming

Use:

- UPPERCASE for top folders
- Pascal-Case for document names
- One topic per document

Example:

```
Application-Architecture.md
GitOps-Strategy.md
Security-Architecture.md
```

---

# Standard Metadata

Every document begins with:

```markdown
# Title

Version: 1.0
Status: Draft | Review | Approved
Owner:
Last Updated:
Related ADRs:
Related Components:
RNCP Competencies:
```

---

# Standard Sections

Each architecture document follows the same structure.

## 1. Purpose

Why the document exists.

## 2. Scope

What is covered.

## 3. Context

Business and technical background.

## 4. Architecture

Concepts, components and interactions.

## 5. Design Decisions

Key implementation choices.

## 6. Implementation

Deployment, configuration and operational details.

## 7. Security

Authentication, authorization, secrets, compliance.

## 8. Monitoring

Metrics, logs, traces and alerts.

## 9. Risks

Known limitations and mitigation.

## 10. References

Links to ADRs, diagrams and related documents.

---

# Diagram Standards

Prefer Mermaid for embedded diagrams.

Recommended diagram types:

- Flowcharts
- Sequence
- ER
- C4 Context
- C4 Container
- State
- Gantt (roadmaps)

Store editable Draw.io diagrams under:

```
99-DIAGRAMS/
```

---

# ADR Traceability

Every major architectural decision must have an ADR.

Documents should reference ADRs.

Example:

- ADR-0001 GitOps
- ADR-0002 Kubernetes
- ADR-0003 Keycloak

---

# GitOps Traceability

Each document should identify:

- Git repository
- Argo CD application
- Kubernetes namespace
- Helm chart
- Values file

---

# Code Traceability

Reference:

- Source repository
- API
- Docker image
- Helm release
- CI/CD pipeline

---

# Documentation Lifecycle

Draft
→ Review
→ Approved
→ Deprecated (if applicable)

Changes require version updates and changelog entries.

---

# Review Checklist

Before approval verify:

- Purpose is clear
- Scope is complete
- Diagrams updated
- Security reviewed
- References valid
- Links functional
- Terminology consistent
- Grammar checked
- RNCP mapping updated

---

# Quality Rules

- One responsibility per document
- Keep diagrams close to explanations
- Prefer tables over long prose
- Avoid duplication
- Cross-reference instead of copying
- Use consistent terminology
- Keep examples executable where possible

---

# Definition of Done

A document is complete when:

- Metadata completed
- Sections filled
- Diagrams included
- ADR references added
- GitOps references added
- Security reviewed
- Operations documented
- Version updated
- Peer reviewed
- Ready for publication
