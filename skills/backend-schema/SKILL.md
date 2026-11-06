---
name: backend-schema
description: Use when designing database schemas, modeling relational or document entities, writing DDL table migrations, establishing foreign keys, or creating indexing strategies for query performance.
---

# Backend Schema & Data Architecture

## Overview
Acts as a Principal Database Architect to design production-grade relational (SQL) or document (NoSQL) schemas. Enforces strict typing, constraint validation, foreign key cascades, high-performance indexing strategies, audit tracking, and zero-downtime migration planning.

## When to Use
- **Trigger symptoms:** When designing database models, authoring ORM schemas (Prisma, Drizzle, SQLAlchemy, TypeORM), writing SQL migrations, planning data normalization, or optimizing slow database queries.
- **When NOT to use:** Writing frontend CSS, designing static marketing pages, or configuring simple environment variables.

## Instructions

Produce the Backend Schema specification across these 6 structured sections:

### 1. Entity-Relationship Diagram (ERD)
- Visual data model using Mermaid (`erDiagram`).
- Detail all entities, attributes, primary keys (`PK`), foreign keys (`FK`), and cardinalities (`||--o{`, `}|--|{`, `||--||`).

### 2. Comprehensive DDL / Table Specifications
Provide production-ready SQL table definitions:
- **Columns & Types:** Exact PostgreSQL / MySQL data types (`UUID`, `VARCHAR`, `TIMESTAMPTZ`, `JSONB`, `NUMERIC(12,2)`). Never use generic pseudocode.
- **Keys & Defaults:** Explicit `PRIMARY KEY`, default values (`DEFAULT now()`, `DEFAULT gen_random_uuid()`).
- **Referential Integrity:** Foreign keys with explicit cascade behaviors (`ON DELETE RESTRICT`, `ON DELETE CASCADE`, or `ON DELETE SET NULL`).
- **Constraints:** Column and table check constraints (`CHECK (price >= 0)`), composite unique constraints (`UNIQUE (org_id, slug)`).

### 3. Strategic Indexing Plan
Map concrete indexes to query access patterns:
- **B-Tree Indexes:** For high-cardinality equality lookups and primary keys.
- **Composite Indexes:** Specify column ordering based on query patterns (Filter columns first, then Sort columns).
- **Partial / Filtered Indexes:** e.g., `CREATE INDEX idx_active_users ON users(email) WHERE deleted_at IS NULL;`
- **GIN Indexes:** For JSONB document structures or vector/full-text search.

### 4. Normalization & Denormalization Architecture
- Third Normal Form (3NF) core schema.
- Explicit justifications for any intentional denormalization (e.g. storing `orders_count` on `customers`), with data reconciliation mechanisms documented.

### 5. Audit Logging & Temporal Tracking
- Standard audit columns on all core tables: `created_at`, `updated_at`, `deleted_at`, `created_by`, `updated_by`.
- Soft-delete conventions and index exclusions for deleted rows.

### 6. Migration Sequence & Seed Plan
- Ordered migration script numbers (`001_create_tenants.sql`, `002_create_users.sql`, `003_create_orders.sql`).
- Deterministic test seed data script structure with realistic relation graphs.

## Rules & Constraints
- Always use timezone-aware timestamps (`TIMESTAMPTZ` in PostgreSQL).
- Never use floats for financial amounts; use `NUMERIC` or `BIGINT` (cents).
- Every foreign key MUST explicitly specify its `ON DELETE` behavior.

## Rationalization Table
| Temptation / Shortcut | Reality |
| :--- | :--- |
| "We'll let the ORM auto-generate whatever schema it wants." | ORM auto-migrations frequently omit check constraints, cascade rules, and optimized composite indexes. |
| "Indexes can be added when queries get slow." | Retrofitting indexes on massive production tables causes lock contention and downtime. |
| "Storing everything in a JSON column is faster to build." | Unstructured JSON destroys query performance, validation guarantees, and relational integrity. |
