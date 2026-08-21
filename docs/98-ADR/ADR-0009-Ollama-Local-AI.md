# ADR-0009 — Adopt Ollama and Local AI Inference as the Default Enterprise AI Execution Model

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** AI / Security / Infrastructure / Governance
**Project:** Enterprise AI Platform
**Related ADRs:** ADR-0001, ADR-0002, ADR-0007, ADR-0008
**Related Technologies:** Ollama, Qwen, NVIDIA GTX 1080, Kubernetes, MLflow, OpenMetadata
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform requires Large Language Model and AI inference capabilities for use cases such as:

* Internal assistants
* RAG
* Document analysis
* Data exploration
* Governance assistance
* Knowledge search
* AI-enabled business applications
* Future agentic workflows

These workloads may process:

* Internal documentation
* Metadata
* Business information
* Data architecture information
* Potentially sensitive enterprise content

The platform already provides local AI compute based on NVIDIA GPUs and runs Ollama with Qwen-family models.

The architecture must therefore determine whether AI inference should primarily depend on external AI providers or remain local to the enterprise platform.

---

# 2. Problem

External AI APIs can provide strong model capability, but they introduce several concerns:

* Data leaving the controlled platform
* Dependency on external providers
* Cost variability
* Internet dependency
* Provider availability
* Vendor lock-in
* Data residency concerns
* Unclear future provider policy changes
* Potential governance complexity

At the same time, local inference introduces:

* Limited GPU resources
* Smaller model choices
* Lower maximum concurrency
* Operational responsibility
* Potentially lower performance than large hosted models

The architecture must balance sovereignty, security, performance, cost, and operational complexity.

---

# 3. Decision

The Enterprise AI Platform will use **local AI inference as the default execution model**.

The current local inference stack is:

```text
NVIDIA GPU Infrastructure
        │
        ▼
      Ollama
        │
        ▼
     Qwen Models
        │
        ▼
Internal AI Services
```

External AI providers may be used only when explicitly justified and governed.

Local inference is therefore the preferred platform path for enterprise data and internal AI workloads.

---

# 4. Architectural Principle

The decision establishes:

> Enterprise data should remain inside the controlled platform by default during AI inference.

This principle supports:

* Data sovereignty
* Security
* Privacy
* Predictable cost
* Offline capability
* Architectural independence

It does not imply that external AI services are permanently prohibited.

They require explicit governance.

---

# 5. Current Implementation

Local Ollama inference is already operational.

Current implementation includes:

* Dedicated AI compute hosts
* NVIDIA GTX 1080 GPUs
* 8 GB VRAM per GPU
* CUDA-capable environment
* Ollama
* Qwen model
* Remote Ollama API access from Kubernetes
* Internal network connectivity

Existing validation has demonstrated successful remote inference from Kubernetes to the local Ollama endpoint.

Current state:

```text
IMPLEMENTED
```

---

# 6. Current Physical AI Architecture

The current AI compute environment includes:

```text
AI Host 1
└── NVIDIA GTX 1080
    └── 8 GB VRAM

AI Host 2
└── NVIDIA GTX 1080
    └── 8 GB VRAM
```

The architecture assumes these GPUs remain the principal local AI hardware for the current project phase.

No near-term hardware expansion is required by this ADR.

---

# 7. Model Strategy

The platform currently uses Qwen-family models through Ollama.

The model-selection strategy should prioritize:

* Good instruction following
* Efficient inference
* Quantized model availability
* Suitable multilingual capability
* Appropriate VRAM footprint
* Local execution
* Open model ecosystem

Model selection must remain workload-specific.

---

# 8. Why Ollama

Ollama provides:

* Simple local model deployment
* Straightforward model management
* HTTP API
* Quantized model support
* NVIDIA GPU acceleration
* Low operational barrier
* Broad model ecosystem

It provides a practical inference runtime for the existing hardware.

---

# 9. Alternatives Considered

## Option 1 — Ollama with Local Models

Advantages:

* Local inference
* Data sovereignty
* No per-request API cost
* Simple deployment
* Good model ecosystem
* Offline capability
* Easy experimentation
* Low vendor lock-in

Disadvantages:

* Limited by local GPU capacity
* Smaller feasible model sizes
* Requires GPU operations
* Lower peak capability than some hosted frontier models

Selected.

---

## Option 2 — OpenAI or Other Hosted AI API

Advantages:

* Access to highly capable models
* No local GPU operations
* Easy scaling
* Strong managed infrastructure

Disadvantages:

* External data processing
* Internet dependency
* API cost
* Provider dependency
* Data-governance considerations
* Vendor lock-in risk

Not selected as the default enterprise inference path.

---

## Option 3 — Cloud GPU Infrastructure

Advantages:

* Larger GPUs
* Elastic capacity
* Support for larger models

Disadvantages:

* Cost
* Cloud dependency
* More infrastructure
* Data residency considerations
* Current workloads do not justify it

Not selected as the current default.

---

## Option 4 — Dedicated Enterprise AI Appliance

Advantages:

* High local performance
* Enterprise support
* Large model capacity

Disadvantages:

* Significant hardware cost
* Current project does not require this investment

Not selected.

---

# 10. Decision Criteria

The decision considered:

| Criterion                     | Importance |
| ----------------------------- | ---------: |
| Data sovereignty              |   Critical |
| Privacy                       |   Critical |
| Local execution               |   Critical |
| Cost predictability           |       High |
| Resource efficiency           |       High |
| Operational simplicity        |       High |
| Model capability              |       High |
| External dependency reduction |       High |
| Scalability                   |     Medium |
| Maximum model size            |     Medium |

Local Ollama inference provides the best fit for the current architecture.

---

# 11. Data Sovereignty

Local inference provides the preferred data path:

```text
Enterprise Data
      │
      ▼
Internal AI Service
      │
      ▼
Local Ollama
      │
      ▼
Local Model
      │
      ▼
Response
```

The default path does not require sending prompts or enterprise context to an external AI provider.

---

# 12. Security Consequences

Local inference reduces several external data-exposure risks but creates internal security responsibilities.

Required controls include:

* Restricted network exposure
* Authentication or gateway controls
* Network segmentation
* API access control
* Logging
* Model provenance
* Host hardening
* Patch management

Local does not automatically mean secure.

---

# 13. Ollama Network Exposure

Ollama should not be exposed directly to the public Internet.

Preferred model:

```text
Internal Application
      │
      ▼
AI Gateway / Controlled API
      │
      ▼
Ollama
```

Direct internal API access may remain acceptable during the current platform phase.

A governed AI Gateway is a target-state capability.

---

# 14. AI Gateway Evolution

A future AI Gateway may provide:

* Authentication
* Authorization
* Request routing
* Model routing
* Rate limiting
* Audit logging
* Prompt policies
* Observability
* Cost/resource accounting
* External-provider routing

This would prevent business applications from becoming tightly coupled to Ollama itself.

---

# 15. Application Decoupling

Applications should ideally depend on a stable internal AI interface.

Preferred future architecture:

```text
Business Application
        │
        ▼
Internal AI API
        │
        ▼
AI Gateway
        │
        ├── Ollama
        └── Governed External Provider
```

This allows inference backends to evolve without rewriting every application.

---

# 16. Resource Constraints

The most important limitation of the local architecture is GPU capacity.

Current constraints include:

* 8 GB VRAM per GPU
* Limited model size
* Limited concurrent inference
* Model loading overhead
* Shared AI workloads

The architecture must explicitly respect these limits.

---

# 17. Resource Strategy

The platform should prioritize:

* Quantized models
* Appropriate model size
* Controlled concurrency
* Workload scheduling
* Queueing
* Resource monitoring
* Model unload/load management where useful

The solution to capacity pressure should not automatically be larger hardware.

---

# 18. Model Quantization

Quantization is a central capability for the current hardware.

Benefits include:

* Reduced VRAM requirement
* Ability to run larger logical model families
* Lower memory consumption

Trade-off:

* Potential quality reduction
* Potential performance differences

Model quality should therefore be evaluated rather than assumed.

---

# 19. GPU Scheduling

AI workloads should not be allowed to compete unpredictably for GPU resources.

Future controls may include:

```text
Request
  │
  ▼
AI Queue
  │
  ▼
GPU Scheduler / Routing
  │
  ▼
Available Ollama Instance
```

This becomes more important as multiple AI services are introduced.

---

# 20. GPU Observability

The platform should progressively monitor:

* GPU utilization
* VRAM usage
* Temperature
* Active processes
* Model memory footprint
* Queue depth
* Inference latency

This supports capacity governance.

---

# 21. AI Service Metrics

AI operational metrics should include:

```text
ai_inference_requests_total
ai_inference_failures_total
ai_inference_duration_seconds
```

Additional useful measurements may include:

* Tokens per second
* Time to first token
* Queue time
* Model name
* Model load duration

---

# 22. AI Quality vs Infrastructure Health

The architecture explicitly separates:

```text
GPU Healthy
Ollama Healthy
Request Successful
```

from:

```text
Answer Correct
Answer Grounded
Answer Relevant
```

Technical service health does not prove AI quality.

---

# 23. RAG

RAG is a major target use case for local AI.

Conceptual architecture:

```text
Enterprise Documents
       │
       ▼
Governed Ingestion
       │
       ▼
Chunking
       │
       ▼
Embedding
       │
       ▼
Vector Search
       │
       ▼
Context
       │
       ▼
Local Qwen
       │
       ▼
Grounded Answer
```

RAG improves access to enterprise knowledge while keeping inference under platform control.

---

# 24. RAG Data Governance

RAG must respect:

* Source ownership
* Data classification
* Access control
* Retention
* Provenance
* Data quality

A document being available to the RAG pipeline does not automatically mean every user should be allowed to retrieve it.

---

# 25. Vector Storage

The platform should evaluate PostgreSQL + pgvector before introducing another vector database.

This follows the architecture principle:

```text
Reuse Existing Capability
        │
        ▼
Add New Technology Only When Required
```

A separate ADR is required if a dedicated vector database is adopted.

---

# 26. Embeddings

Embedding models should preferably run locally where practical.

Benefits include:

* Data sovereignty
* Reduced external dependency
* Consistent governance model

Embedding models should be versioned and documented.

---

# 27. Prompt Governance

Prompts used by business applications should eventually become governed assets.

Metadata may include:

```text
prompt_id
version
owner
model
purpose
input_schema
output_schema
risk_level
```

Prompt definitions should be version controlled.

---

# 28. Prompt Injection Risk

RAG and AI applications introduce prompt-injection risks.

Controls may include:

* Source validation
* Context isolation
* Tool restrictions
* Output validation
* Human approval
* Prompt security testing

Local inference does not remove prompt-injection risk.

---

# 29. Hallucination Risk

Local models can produce incorrect or unsupported answers.

Mitigation includes:

* RAG
* Citations
* Output validation
* Constrained schemas
* Evaluation
* Human review
* Appropriate user messaging

AI-generated output should not automatically become authoritative enterprise data.

---

# 30. Human Oversight

Higher-impact AI actions should require stronger human oversight.

Example:

```text
AI Suggestion
     │
     ▼
Human Review
     │
     ▼
Business Action
```

Autonomous execution should only be introduced for clearly bounded and low-risk operations.

---

# 31. Agentic AI

Future AI agents may use:

* Databases
* APIs
* Metadata services
* Automation tools

Agent capabilities must follow least privilege.

An AI agent should not automatically receive unrestricted infrastructure access.

---

# 32. Tool Governance

Agent tools should define:

* Tool ID
* Owner
* Allowed operations
* Required permissions
* Risk classification
* Approval requirements

This supports AI Governance as Code.

---

# 33. MLflow Relationship

MLflow remains responsible for:

* ML experiments
* Model versions
* Model registry
* Evaluation metadata

Ollama remains primarily an inference runtime.

```text
MLflow
→ Model lifecycle

Ollama
→ Model execution
```

The systems are complementary.

---

# 34. Model Inventory

AI Governance should eventually maintain a complete inventory including:

* Ollama models
* Custom MLflow models
* Embedding models
* External models
* Future agents

Every production AI asset should have an owner.

---

# 35. Model Provenance

Models should ideally record:

* Model source
* Version
* Quantization
* License
* Checksum where useful
* Approval state

This supports supply-chain and AI governance.

---

# 36. Model Licensing

Open models have license conditions.

Technology Governance should track licensing requirements for production use.

Model availability in Ollama does not automatically prove unrestricted commercial or enterprise usage rights.

---

# 37. External AI Provider Exception

External AI may be permitted when:

* Local capability is insufficient
* Business value justifies it
* Data classification allows it
* Privacy requirements are satisfied
* Security review passes
* Cost is understood
* Architecture approval exists

This is an explicit governed exception or hybrid architecture decision.

---

# 38. External AI Data Classification

Before sending information to an external provider, data should be evaluated.

Conceptually:

```text
Prompt / Context
      │
      ▼
Data Classification
      │
      ├── Allowed
      │      ▼
      │   External AI
      │
      └── Restricted
             ▼
          Local AI Only
```

This can eventually become Policy as Code.

---

# 39. Hybrid AI Architecture

A future hybrid architecture may support:

```text
AI Gateway
   │
   ├── Local Model
   │
   └── External Model
```

Routing decisions could consider:

* Classification
* Required capability
* Cost
* Latency
* Availability
* Risk

Local remains the preferred default.

---

# 40. Graceful Degradation

AI should not become a mandatory dependency for core business functionality unless explicitly required.

Preferred design:

```text
AI Available
→ Enhanced functionality

AI Unavailable
→ Core service remains available
```

This reduces operational risk.

---

# 41. Offline Capability

Local inference provides resilience during:

* Internet outages
* Provider outages
* API disruptions

This is an important sovereignty and availability benefit.

---

# 42. Availability Limitations

Local inference also introduces local failure domains.

Examples:

* GPU failure
* AI host failure
* Ollama failure
* CUDA/driver issue
* VRAM exhaustion

These risks must be monitored.

---

# 43. AI Host Redundancy

Two AI hosts provide potential workload distribution.

However they should not be represented as automatic HA unless:

* Requests can route between them
* Models exist on both
* Health is monitored
* Failover is tested

Physical redundancy alone is not complete service HA.

---

# 44. Model Replication

Important models may need to exist on more than one AI host.

This should be balanced against:

* Disk space
* VRAM
* Operational complexity

Only required models should be replicated.

---

# 45. AI Disaster Recovery

AI recovery is generally lower priority than core database and platform recovery.

Conceptual order:

```text
Core Infrastructure
        │
        ▼
Kubernetes
        │
        ▼
Data
        │
        ▼
Business Applications
        │
        ▼
AI Inference
```

unless AI becomes business-critical.

---

# 46. AI Recovery

Recovery requires:

* AI host
* NVIDIA drivers
* Ollama
* Model files
* Configuration
* Network access
* Application connectivity

Model definitions and configuration should be documented/version controlled where practical.

---

# 47. Model Re-download

Where model artifacts can be safely re-obtained from trusted sources, full backup of every model binary may not be necessary.

However:

* Exact model/version
* Quantization
* Configuration
* Source

must remain documented for reproducibility.

---

# 48. Observability Failure Strategy

AI inference should continue where possible if telemetry is unavailable.

Telemetry export must not become a synchronous hard dependency.

---

# 49. Security Logging

AI logs should record operational information such as:

* Model
* Status
* Duration
* Error
* Trace ID

Avoid logging by default:

* Full prompts
* Full generated responses
* Sensitive retrieved documents

---

# 50. Auditability

Important AI operations should progressively provide evidence of:

* Model used
* Prompt version
* Data source
* Tool actions
* Evaluation
* Human approval where required

This enables AI governance without storing hidden model reasoning.

---

# 51. AI Governance as Code

The target governance chain is:

```text
AI Asset
   │
   ▼
Machine-Readable Metadata
   │
   ▼
Risk Classification
   │
   ▼
Policy
   │
   ▼
Evaluation
   │
   ▼
Approval
   │
   ▼
Deployment
   │
   ▼
Runtime Evidence
```

Ollama becomes one governed runtime target in this model.

---

# 52. Example AI Asset Definition

```yaml
id: AI-MODEL-001
name: qwen3-8b
runtime: ollama
deployment: local

owner: ai-platform

classification:
  data_processing: internal
  external_transfer: false

resources:
  gpu_required: true
  vram_target_gb: 8

monitoring_required: true
```

This is a target Governance as Code representation.

---

# 53. SLOs

Future AI SLOs may include:

* Inference success
* Availability
* Time to first token
* Response duration

Targets must reflect local hardware capacity.

They should not copy cloud AI service expectations without validation.

---

# 54. AI Capacity Planning

Capacity should be evaluated using:

```text
Request Rate
×
Inference Duration
×
Model VRAM
×
Concurrency
```

This provides a realistic basis for scaling decisions.

---

# 55. Scaling Strategy

Preferred scaling order:

```text
Optimize model
    ↓
Quantize
    ↓
Control concurrency
    ↓
Improve scheduling
    ↓
Use second host
    ↓
Evaluate architecture
    ↓
Only then consider new hardware
```

This aligns with the fixed-infrastructure roadmap.

---

# 56. Technology Governance Status

Recommended status:

```text
Technology: Ollama
Category: AI Inference
Lifecycle: ADOPT
```

Qwen models should be tracked as governed AI assets rather than only as generic infrastructure technologies.

---

# 57. Technical Debt Consideration

Local AI is not technical debt.

The limited GPU capacity is a **constraint**.

Potential AI debt includes:

* No AI Gateway yet
* Missing prompt registry
* Missing formal AI SLOs
* Incomplete automated evaluation
* Unmanaged model copies

These should be addressed through the Architecture Roadmap.

---

# 58. Risks

## Risk — GPU Capacity Exhaustion

Mitigation:

* Quantization
* Queueing
* Monitoring
* Concurrency limits

## Risk — AI Host Failure

Mitigation:

* Multiple hosts
* Recovery procedures
* Graceful degradation

## Risk — Hallucination

Mitigation:

* RAG
* Evaluation
* Human oversight

## Risk — Prompt Injection

Mitigation:

* Input/context governance
* Tool isolation
* Security testing

## Risk — Sensitive External Transfer

Mitigation:

* Local inference default
* External-provider governance

---

# 59. Positive Consequences

The platform gains:

* AI sovereignty
* Strong privacy posture
* Cost predictability
* Offline inference
* Reduced vendor dependency
* Strong learning and engineering value
* Direct control of model lifecycle
* Strong foundation for governed RAG

---

# 60. Negative Consequences

The platform accepts:

* Limited model size
* Limited concurrency
* AI host operational responsibility
* GPU driver management
* Model lifecycle management
* Lower capability than some large hosted models for certain tasks

These trade-offs are intentional.

---

# 61. Success Criteria

The decision remains successful while:

* Local AI satisfies core use cases
* Sensitive information remains under enterprise control
* GPU resources remain manageable
* Model quality is sufficient
* AI services remain observable
* External providers are not required for normal core operation

---

# 62. Review Triggers

Review this ADR if:

* Local models cannot satisfy critical business requirements
* AI workload volume materially exceeds local capacity
* External AI becomes mandatory for a justified use case
* New hardware architecture is approved
* Regulatory requirements change materially
* Ollama no longer satisfies runtime requirements

---

# 63. Governance as Code Metadata

Future machine-readable representation:

```yaml
id: ADR-0009
title: Adopt Ollama and Local AI Inference as Default Enterprise AI Execution Model
status: accepted

domain:
  - ai
  - security
  - infrastructure
  - governance

technologies:
  - ollama
  - qwen

owner: ai-platform
implementation_status: implemented

principles:
  - local-inference-first
  - data-sovereignty
  - external-ai-by-exception

constraints:
  - gpu-vram-8gb
  - fixed-physical-infrastructure

related_adrs:
  - ADR-0001
  - ADR-0002
  - ADR-0007
  - ADR-0008

supersedes: null
superseded_by: null
```

---

# 64. Related Documents

* ADR-0001-Kubernetes
* ADR-0002-ArgoCD-GitOps
* ADR-0007-MLflow
* ADR-0008-OpenMetadata
* AI Architecture
* AI Security Architecture
* AI Governance
* MLOps Architecture
* RAG Architecture
* Infrastructure Architecture
* Capacity Management
* Risk Management
* Technology Governance
* Architecture Roadmap
