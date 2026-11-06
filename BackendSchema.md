Backend Database Schema & Data Architecture

You are a Principal Database Architect. Using the PRD and Technical Requirement Document (TRD), produce an exhaustive, production-grade database schema specification before backend ORM models or migrations are written.

Context / Features: [PASTE PRD, TRD, OR ENTITY REQUIREMENTS]
Database Engine: [SPECIFY POSTGRESQL, MYSQL, MONGODB, SQLITE, ETC. (Default: PostgreSQL)]

Deliver the Backend Schema with these exact sections:

1. Entity-Relationship Diagram (Mermaid erDiagram):
   - Comprehensive Mermaid `erDiagram` showing all tables, entities, cardinalities (1:1, 1:N, N:M), and foreign key references.

2. Table / Collection DDL Specifications:
   - For every table:
     - Exact columns with SQL data types (e.g., `UUID`, `VARCHAR(255)`, `TIMESTAMPTZ`, `JSONB`, `BIGINT`)
     - Nullability, Default values, Primary Keys (`PRIMARY KEY DEFAULT gen_random_uuid()`)
     - Foreign Keys with cascade actions (`ON DELETE CASCADE`, `ON DELETE SET NULL`, `ON DELETE RESTRICT`)
     - Check constraints (e.g. `CHECK (amount > 0)`) and Unique constraints (`UNIQUE(tenant_id, slug)`)

3. Indexing & Query Optimization Strategy:
   - Specific indexes mapped to high-frequency query access patterns:
     - Primary and unique B-tree indexes
     - Composite indexes with column order justification (Equality &rarr; Range &rarr; Sort)
     - Partial / filtered indexes (e.g., `WHERE deleted_at IS NULL` or `WHERE status = 'active'`)
     - GIN indexes for JSONB columns or full-text search

4. Normalization & Denormalization Justifications:
   - Normalized structure (3NF) breakdown
   - Deliberate denormalizations (e.g. cached counts, aggregate totals) with synchronization mechanisms (triggers vs background sync)

5. Soft-Delete, Audit & Temporal Tracking:
   - Soft-delete strategy (`deleted_at TIMESTAMPTZ DEFAULT NULL`) vs hard deletes
   - Universal audit timestamps: `created_at`, `updated_at`, `created_by_id`, `updated_by_id`

6. Migration & Seed Execution Plan:
   - Sequential migration ordering to avoid dependency lock issues
   - Realistic seed dataset structure for development and test suites

Be explicit with types and constraints. Never use generic pseudocode when valid SQL/DDL statements can be provided.

