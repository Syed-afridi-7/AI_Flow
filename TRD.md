Technical Requirement Document (TRD)

You are a Principal Software Architect. Using the PRD and product goals, produce a comprehensive, battle-tested Technical Requirement Document (TRD) before implementation begins.

Product Context / PRD: [PASTE PRD OR DESCRIBE SYSTEM]
Platform / Target Stack: [LIST TARGET RUNTIME, CLOUD, OR CONSTRAINTS IF ANY]

Deliver the TRD with these exact sections:

1. Technical Problem Statement & Scope:
   - Technical goals and architectural boundaries
   - System limitations and out-of-scope technical items

2. Performance, Scalability & Throughput:
   - Target concurrency (concurrent users, active WebSocket connections)
   - Read/write throughput expectations (Requests Per Second - RPS)
   - Latency budgets (p50, p95, p99 API response times, client render budgets)
   - Horizontal and vertical scaling strategies

3. Reliability, Availability & SLAs:
   - Availability target (e.g., 99.9% uptime SLA)
   - Fault isolation boundaries and circuit breaker rules
   - Disaster recovery strategy, backup intervals, and RTO / RPO metrics

4. Security, Identity & Compliance Requirements:
   - Authentication protocols (JWT, OAuth2, Session HttpOnly cookies)
   - Authorization & Role-Based Access Control (RBAC) model
   - Data encryption standards (TLS 1.3 in transit, AES-256 at rest)
   - Compliance constraints (GDPR data sanitization, SOC2 audit logging)

5. Integration & Third-Party Dependency Contracts:
   - External services and APIs with rate limits, timeout policies, and fallbacks
   - Webhook processing guarantees (idempotency keys, retry backoff)

6. Telemetry, Observability & Error Budget:
   - Structured JSON logging format (trace_id, span_id, user_id context)
   - Key SLIs and SLOs with alert thresholds
   - APM distributed tracing and error alerting thresholds

7. Deployment, CI/CD & Environment Matrix:
   - Target environment architecture (Development, Staging, Production)
   - Containerization, build pipelines, and zero-downtime deployment strategy (Blue/Green or Canary)

Be technical, concrete, and unambiguous. Flag any unverified assumptions as open technical risks.

