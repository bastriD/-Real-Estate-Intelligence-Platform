# Architecture Playbook
Version: 1.0

## Purpose
This playbook defines the engineering standards, architectural conventions, and delivery rules for the project. Unlike the Project Constitution (governance) and the Master Prompt (AI behavior), this document standardizes *how* the solution is designed and implemented.

---

# 1. Architecture Principles

- Business requirements drive architecture.
- Prefer simplicity before complexity.
- Cloud-native and container-first.
- API-first design.
- Security by Design.
- Infrastructure as Code.
- GitOps for deployments.
- Observability by default.
- Automation over manual work.
- Documentation as code.

---

# 2. Repository Structure

```
docs/
architecture/
adr/
diagrams/
backend/
frontend/
data/
infrastructure/
tests/
scripts/
```

Documentation lives beside the code whenever possible.

---

# 3. Documentation Standards

Each major component must contain:

- Purpose
- Responsibilities
- Dependencies
- Interfaces
- Risks
- Security considerations
- Operational notes

Use Markdown only.

---

# 4. Architecture Documentation

Maintain:

- Context Diagram (C4 L1)
- Container Diagram (L2)
- Component Diagram (L3)
- Deployment Diagram
- Data Flow Diagram
- Sequence Diagrams
- ERD / MCD
- Infrastructure Diagram

Prefer Mermaid.

---

# 5. ADR (Architecture Decision Records)

Every important decision requires an ADR.

Template:

- Title
- Status
- Context
- Decision
- Alternatives
- Consequences
- References

Never overwrite previous ADRs.

---

# 6. Naming Conventions

Repositories:
- lowercase-with-dashes

Containers:
- lowercase

Namespaces:
- project-purpose

Branches:
- feature/
- bugfix/
- hotfix/
- release/

---

# 7. Coding Standards

General:

- Small functions
- SOLID
- DRY
- KISS
- YAGNI
- Meaningful naming
- Strong typing
- Code reviews required

---

# 8. API Standards

REST unless justified otherwise.

Endpoints:

```
GET
POST
PUT
PATCH
DELETE
```

OpenAPI documentation mandatory.

Version APIs.

---

# 9. Database Standards

- Normalize OLTP
- Star/Snowflake for OLAP
- Primary keys
- Foreign keys
- Constraints
- Indexes
- Migration scripts
- No manual schema edits

---

# 10. Security Checklist

- Authentication
- Authorization
- Secrets management
- TLS
- Input validation
- Least privilege
- Dependency scanning
- Image scanning
- RBAC
- Audit logging

---

# 11. DevOps Standards

Mandatory:

- Docker
- Kubernetes
- Helm
- GitOps
- CI/CD
- Automated testing
- Rollback strategy

---

# 12. Observability

Every service must expose:

- Logs
- Metrics
- Traces
- Health endpoints

Dashboards and alerts required.

---

# 13. Testing Strategy

Minimum:

- Unit Tests
- Integration Tests
- API Tests
- End-to-End Tests
- Performance Tests
- Security Tests

Coverage target: >=80%.

---

# 14. AI & Data Governance

- Dataset versioning
- Model versioning
- Explainability
- Prompt versioning
- Bias assessment
- Human validation
- GDPR compliance

---

# 15. Definition of Done

A feature is complete only if:

- Requirements satisfied
- Tests passing
- Documentation updated
- Architecture updated
- ADR written (if applicable)
- Security reviewed
- Monitoring added
- CI/CD passing
- Code reviewed

---

# 16. Architecture Review Checklist

Before approval verify:

- Functional correctness
- Scalability
- Reliability
- Maintainability
- Performance
- Security
- Cost
- Sustainability
- Compliance
- Operational readiness

---

# 17. Release Checklist

Before production:

- CI green
- Tests green
- Documentation complete
- Backup verified
- Rollback validated
- Monitoring enabled
- Alerts configured
- Stakeholder approval

---

# 18. RNCP40573 Traceability

For every deliverable maintain links to:

- Competency block (BC01–BC05)
- Requirement
- ADR
- Architecture component
- Test evidence
- Documentation

This ensures complete auditability for certification.

---

# 19. Continuous Improvement

After each milestone perform:

- Technical retrospective
- Architecture review
- Security review
- Performance review
- Documentation review
- Lessons learned

Update this playbook when engineering practices evolve.
