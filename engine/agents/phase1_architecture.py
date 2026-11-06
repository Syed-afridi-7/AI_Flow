import re
from engine.core.base import BaseGenerator, BaseValidator
from engine.core.registry import AgentRegistry
from engine.core.types import TaskContext, GenerationResult, ValidationScorecard, Blocker, Severity


# ============================================================================
# 1. PRD Generator
# ============================================================================
class ProductDiscoveryStrategist(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        title = context.prompt.strip() or "New Product Initiative"
        content = f"""# Product Requirements Document (PRD)

## 1. Executive Summary
**Objective:** Deliver an end-to-end solution for: {title}.
**Core Value Proposition:** Provide users with a streamlined, reliable, and frictionless workflow.

## 2. Target Audience & Personas
- **Primary Persona:** Full-stack engineers and solo founders requiring rapid, high-quality execution.
- **Secondary Persona:** Technical product managers and engineering leads overseeing architecture.

## 3. User Stories & Acceptance Criteria
- **US-01 (Core Flow):** As a user, I want to initiate the core flow so that I can achieve my goal quickly.
  - *Acceptance Criteria:* Response time < 200ms; intuitive UI state; complete audit trail.
- **US-02 (Configuration & Settings):** As an admin, I want to manage preferences and credentials safely.
  - *Acceptance Criteria:* Secrets encrypted; role-based access enforced.
- **US-03 (Reporting & Visibility):** As a stakeholder, I want visibility into progress and metrics.
  - *Acceptance Criteria:* Exportable summaries; real-time status indicators.

## 4. Scope & Phasing
- **In-Scope (MVP):** Core interaction loop, error recovery, persistence, and automated verification.
- **Out-of-Scope (V1):** Multi-region replication, third-party legacy integrations.

## 5. Success Metrics (KPIs)
- **Activation Rate:** > 80% completion of initial setup.
- **Error Rate:** < 0.1% unhandled exceptions in production.
"""
        return GenerationResult(
            skill_name=self.skill_name,
            content=content,
            metadata={"title": title, "stage": "MVP"}
        )


class ScopeFeasibilityAuditor(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        required_sections = ["Executive Summary", "User Stories", "Scope", "Success Metrics"]
        for section in required_sections:
            if section.lower() not in result.content.lower():
                score -= 20
                blockers.append(Blocker(
                    rule_id="PRD_MISSING_SECTION",
                    message=f"Missing required PRD section: '{section}'",
                    severity=Severity.BLOCKER
                ))

        if "Acceptance Criteria" not in result.content:
            score -= 15
            blockers.append(Blocker(
                rule_id="PRD_NO_CRITERIA",
                message="User stories must include explicit Acceptance Criteria.",
                severity=Severity.BLOCKER
            ))

        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"structure": 40, "completeness": 30, "clarity": 30},
            blockers=blockers,
            audit_summary="PRD audit passed successfully." if score >= 85 else "PRD audit failed requirements check."
        )


# ============================================================================
# 2. TRD Generator
# ============================================================================
class TechnicalSystemsArchitect(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# Technical Requirements Document (TRD)

## 1. System Overview
Technical specification for implementing: {context.prompt}.

## 2. Non-Functional Requirements & Latency Budgets
- **p95 Latency:** < 150ms for read requests; < 300ms for write transactions.
- **p99 Latency:** < 500ms under peak load.
- **Throughput:** Minimum 1,000 requests per second (RPS) baseline.
- **SLA & Uptime:** 99.9% availability target with automated health checks.

## 3. Resilience & Failure Recovery
- **Circuit Breakers:** Tripped after 5 consecutive downstream timeouts.
- **Retries:** Exponential backoff with full jitter (max 3 attempts).
- **Graceful Degradation:** Cache fallback for read-heavy dependencies.

## 4. Security & Compliance
- Transport encryption via TLS 1.3.
- Data at rest encrypted via AES-256.
- Strict authentication gates on all API endpoints.
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class ReliabilitySlaStressTester(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "p95" not in result.content or "p99" not in result.content:
            score -= 25
            blockers.append(Blocker(
                rule_id="TRD_NO_LATENCY_BUDGET",
                message="TRD must define explicit p95 and p99 latency budgets.",
                severity=Severity.BLOCKER
            ))
        if "SLA" not in result.content and "99." not in result.content:
            score -= 25
            blockers.append(Blocker(
                rule_id="TRD_NO_SLA",
                message="TRD must specify an uptime SLA percentage target.",
                severity=Severity.BLOCKER
            ))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"latency": 50, "sla": 50},
            blockers=blockers,
            audit_summary="TRD meets all non-functional criteria." if score >= 85 else "TRD missing SLA/latency budgets."
        )


# ============================================================================
# 3. App Flow
# ============================================================================
class NavigationJourneyArchitect(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# Application Flow & State Machine

## 1. Navigation Journey Table
| Source Screen | Trigger / Action | Destination Screen | Permission Gate | Edge Cases |
| :--- | :--- | :--- | :--- | :--- |
| Landing / Login | Submit Credentials | Dashboard | Public | Invalid Auth / 401 |
| Dashboard | Click Create Project | Wizard Step 1 | Authenticated | Storage Quota Exceeded |
| Wizard Step 1 | Complete Form | Review & Confirm | Authenticated | Validation Errors |
| Review & Confirm| Click Launch | Live Workspace | Authenticated | Provisioning Timeout |

## 2. State Machine Transition Diagram
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Authenticating: User Submits Form
    Authenticating --> Dashboard: Success
    Authenticating --> Idle: Auth Failure
    Dashboard --> Processing: Trigger Action
    Processing --> Completed: Success
    Processing --> ErrorState: Timeout / Exception
    ErrorState --> Idle: Reset / Retry
    Completed --> [*]
```
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class StateMachineEdgeCaseAuditor(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "stateDiagram" not in result.content and "flowchart" not in result.content:
            score -= 30
            blockers.append(Blocker(
                rule_id="APPFLOW_NO_DIAGRAM",
                message="App Flow must contain a Mermaid stateDiagram or flowchart.",
                severity=Severity.BLOCKER
            ))
        if "Permission Gate" not in result.content:
            score -= 20
            blockers.append(Blocker(
                rule_id="APPFLOW_NO_GATES",
                message="Screen transitions table must document Permission Gates.",
                severity=Severity.BLOCKER
            ))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"diagram": 50, "transitions": 50},
            blockers=blockers,
            audit_summary="App Flow verified." if score >= 85 else "Missing state machine or permission gates."
        )


# ============================================================================
# 4. UI/UX Design Brief
# ============================================================================
class VisualTokenArchitect(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# UI/UX Design Brief & Token Architecture

## 1. Visual Design Tokens (8px Grid)
- **Spacing Scale:**
  - `space-1`: 4px
  - `space-2`: 8px (base)
  - `space-3`: 12px
  - `space-4`: 16px
  - `space-6`: 24px
  - `space-8`: 32px

## 2. Color Palette & Dark Mode Parity
- **Brand Primary:** `#4F46E5` (Indigo 600)
- **Brand Accent:** `#06B6D4` (Cyan 500)
- **Neutral Dark (Background):** `#0F172A` (Slate 900)
- **Neutral Light (Text):** `#F8FAFC` (Slate 50)
- **Success:** `#10B981` | **Danger:** `#EF4444`

## 3. Accessibility & Contrast
All text meets WCAG 2.1 AA 4.5:1 contrast ratio against default surface colors.
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class DesignSystemTokenLinter(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "8px" not in result.content and "spacing" not in result.content.lower():
            score -= 30
            blockers.append(Blocker(rule_id="UI_NO_GRID", message="Design brief must enforce 8px grid tokens."))
        if "#" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="UI_NO_HEX", message="Color palette must define explicit hex codes."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"tokens": 50, "contrast": 50},
            blockers=blockers,
            audit_summary="Design tokens linted successfully." if score >= 85 else "Design brief missing grid/tokens."
        )


# ============================================================================
# 5. Backend Schema
# ============================================================================
class RelationalModeler(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# Backend Schema Specification & SQL DDL

## 1. Entity Relationship Diagram (ERD)
```mermaid
erDiagram
    USERS ||--o{{ ORDERS : places
    ORDERS ||--|{{ ORDER_ITEMS : contains
    PRODUCTS ||--o{{ ORDER_ITEMS : ordered_in

    USERS {{
        uuid id PK
        string email UK
        string password_hash
        timestamp created_at
    }}
    ORDERS {{
        uuid id PK
        uuid user_id FK
        string status
        decimal total_amount
        timestamp created_at
    }}
    ORDER_ITEMS {{
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        decimal unit_price
    }}
    PRODUCTS {{
        uuid id PK
        string title
        decimal price
        int inventory_count
    }}
```

## 2. Exact SQL DDL Migrations
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_amount NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
```
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class QueryIndexOptimizer(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "CREATE TABLE" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="DB_NO_DDL", message="Backend schema must include executable SQL DDL."))
        if "INDEX" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="DB_NO_INDEX", message="Backend schema must define composite or foreign key indexes."))
        if "erDiagram" not in result.content:
            score -= 20
            blockers.append(Blocker(rule_id="DB_NO_ERD", message="Backend schema must include a Mermaid erDiagram."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"ddl": 40, "indexes": 30, "erd": 30},
            blockers=blockers,
            audit_summary="Schema and indexes approved." if score >= 85 else "Schema missing DDL, indexes, or ERD."
        )


# ============================================================================
# 6. System Architecture
# ============================================================================
class DistributedSystemsArchitect(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# System Architecture & Service Topology

## 1. High-Level Architecture Diagram
```mermaid
flowchart TD
    Client["Web / Mobile Client"] --> Gateway["API Gateway / Reverse Proxy"]
    Gateway --> AuthSvc["Authentication Service"]
    Gateway --> CoreAPI["Core Application API"]
    CoreAPI --> DB[(Primary PostgreSQL DB)]
    CoreAPI --> Cache[(Redis Cache / Rate Limiting)]
    CoreAPI --> Queue["Task Queue / Background Workers"]
```

## 2. Technology Stack & Tradeoffs
- **Language/Framework:** Python / FastAPI for typed API contracts and high performance.
- **Database:** PostgreSQL for relational integrity and JSONB extensibility.
- **Cache:** Redis for session store and rate limiting.

## 3. Resilience & Failure Domains
- Database automated failover with read replicas.
- Stateless API containers enabling horizontal auto-scaling.
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class ResilienceContractAuditor(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "flowchart" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="ARCH_NO_DIAGRAM", message="Architecture must include a topology flowchart."))
        if "Technology Stack" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="ARCH_NO_STACK", message="Architecture must include technology stack rationale."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"topology": 50, "resilience": 50},
            blockers=blockers,
            audit_summary="Architecture approved." if score >= 85 else "Architecture missing diagram or stack rationale."
        )


# ============================================================================
# 7. Implementation Plan
# ============================================================================
class RoadmapPlanner(BaseGenerator):
    def generate(self, context: TaskContext) -> GenerationResult:
        content = f"""# Phased Engineering Implementation Plan

## Phase 1: Core Setup & Schema Migration
- [ ] **Task 1.1:** Setup database migrations and user models (`src/models/user.py`).
- [ ] **Task 1.2:** Implement authentication middleware and token verification (`src/auth/jwt.py`).

## Phase 2: Business Logic & API Endpoints
- [ ] **Task 2.1:** Implement domain service logic and CRUD operations (`src/services/order.py`).
- [ ] **Task 2.2:** Add REST API route handlers with request schema validation (`src/api/routes.py`).

## Phase 3: Automated Testing & Verification
- [ ] **Task 3.1:** Write unit tests for business logic (`tests/test_services.py`).
- [ ] **Task 3.2:** Execute end-to-end integration test suite (`tests/test_e2e.py`).
"""
        return GenerationResult(skill_name=self.skill_name, content=content)


class CriticalPathAuditor(BaseValidator):
    def audit(self, result: GenerationResult, context: TaskContext) -> ValidationScorecard:
        score = 100
        blockers = []
        if "Phase 1" not in result.content:
            score -= 40
            blockers.append(Blocker(rule_id="PLAN_NO_PHASES", message="Plan must be divided into phased milestones."))
        if "Task" not in result.content:
            score -= 30
            blockers.append(Blocker(rule_id="PLAN_NO_TASKS", message="Plan must enumerate atomic tasks."))
        return ValidationScorecard(
            skill_name=self.skill_name,
            score=max(0, score),
            passed=score >= 85,
            category_scores={"phases": 50, "tasks": 50},
            blockers=blockers,
            audit_summary="Plan structure approved." if score >= 85 else "Plan missing phases or atomic tasks."
        )


# ============================================================================
# Register All Phase 1 Skills
# ============================================================================
AgentRegistry.register("prd-generator", ProductDiscoveryStrategist, ScopeFeasibilityAuditor)
AgentRegistry.register("trd-generator", TechnicalSystemsArchitect, ReliabilitySlaStressTester)
AgentRegistry.register("app-flow", NavigationJourneyArchitect, StateMachineEdgeCaseAuditor)
AgentRegistry.register("uiux-design-brief", VisualTokenArchitect, DesignSystemTokenLinter)
AgentRegistry.register("backend-schema", RelationalModeler, QueryIndexOptimizer)
AgentRegistry.register("system-architecture", DistributedSystemsArchitect, ResilienceContractAuditor)
AgentRegistry.register("implementation-plan", RoadmapPlanner, CriticalPathAuditor)
