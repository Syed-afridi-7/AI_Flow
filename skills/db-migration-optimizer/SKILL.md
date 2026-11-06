---
name: db-migration-optimizer
description: Use when authoring, reviewing, or optimizing database DDL migrations for zero downtime, preventing table lock contention in PostgreSQL or MySQL, auditing online schema changes (e.g., gh-ost, pg_repack), or converting blocking ALTER TABLE operations into safe phased migrations.
---

# Database Migration Optimizer

## Overview
Acts as a Principal Database Reliability Engineer (DBRE) to design, review, and optimize zero-downtime DDL schema migrations for PostgreSQL, MySQL, and distributed relational databases. Specializes in eliminating catalog lock contention, preventing query queue pile-ups, converting blocking table rewrites into non-blocking phased operations (Expand and Contract pattern), safely backfilling large tables in throttled batches, and validating online index builds.

## When to Use
- **Trigger symptoms:** When adding columns, dropping columns, creating indexes, altering column types, renaming tables or columns, or adding foreign key and NOT NULL constraints on large production tables (>100,000 rows or high QPS).
- **When NOT to use:** Initial greenfield database design with zero production traffic (use `backend-schema`), authoring API contracts (use `api-contract-generator`), or writing application-level CRUD repository queries.

## Instructions

Execute the database migration optimization across four structured phases:

### Phase 1: Lock Risk & Table Profiling
1. **Analyze Table Characteristics:**
   - Document table row count, table disk size, average read/write QPS, and replication replica lag sensitivity.
2. **Catalog Lock Classification:**
   - Map every intended DDL command to its required lock level in PostgreSQL (`ACCESS EXCLUSIVE`, `SHARE UPDATE EXCLUSIVE`, `SHARE ROW EXCLUSIVE`) or MySQL (`ALGORITHM=INPLACE`, `ALGORITHM=COPY`, `LOCK=NONE`, `LOCK=EXCLUSIVE`).
3. **Queue Safety Protocol:**
   - Mandate short lock and statement timeouts on every DDL session to avoid holding up concurrent client read/write queries:
     ```sql
     SET lock_timeout = '2s';
     SET statement_timeout = '10s';
     ```

### Phase 2: Non-Blocking DDL Transformation Patterns
1. **Safe Column Additions:**
   - **PostgreSQL 11+:** `ALTER TABLE users ADD COLUMN bio text DEFAULT NULL;` (instant metadata change). Non-volatile defaults are also fast in PostgreSQL 11+, but volatile functions (e.g., `DEFAULT clock_timestamp()`) trigger full table rewrites and must be avoided.
   - **MySQL 8.0:** Ensure `ALGORITHM=INSTANT` is supported for the added column; fallback to `gh-ost` or `pt-online-schema-change` if a table copy is required.
2. **Safe Index Creation:**
   - In PostgreSQL, ALWAYS build indexes using `CREATE INDEX CONCURRENTLY` outside of transaction blocks (`BEGIN/COMMIT`).
   - In MySQL, specify `ALGORITHM=INPLACE, LOCK=NONE`.
3. **Safe `NOT NULL` Enforcement:**
   - Never run `ALTER TABLE orders ALTER COLUMN status SET NOT NULL;` directly on high-volume tables (scans entire table under `ACCESS EXCLUSIVE` lock).
   - PostgreSQL 3-Step Protocol:
     1. Add constraint marked `NOT VALID`:
        ```sql
        ALTER TABLE orders ADD CONSTRAINT chk_status_not_null CHECK (status IS NOT NULL) NOT VALID;
        ```
     2. Validate constraint in a separate transaction (takes only `SHARE UPDATE EXCLUSIVE` lock, non-blocking):
        ```sql
        ALTER TABLE orders VALIDATE CONSTRAINT chk_status_not_null;
        ```
     3. (PostgreSQL 12+) Convert validated check constraint to formal `NOT NULL` metadata.
4. **Safe Foreign Key Addition:**
   - Add foreign key with `NOT VALID`, then validate in a follow-up non-blocking transaction:
     ```sql
     ALTER TABLE payments ADD CONSTRAINT fk_payments_user_id FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;
     ALTER TABLE payments VALIDATE CONSTRAINT fk_payments_user_id;
     ```

### Phase 3: The Expand and Contract Architecture
For column renames, type changes, or column deletions, execute a phased multi-deployment rollout:
1. **Phase 1 (Expand):**
   - Add new target column as nullable.
   - Deploy application code that performs **dual writes** (writes to both old and new columns) while continuing to read from the old column.
2. **Phase 2 (Backfill):**
   - Run a throttled, batched background worker to populate the new column for historical rows:
     ```sql
     UPDATE orders SET total_amount_cents = (total_amount * 100)::bigint
     WHERE id BETWEEN :start_id AND :end_id AND total_amount_cents IS NULL;
     ```
   - Sleep 100ms between batches to prevent replication lag and I/O saturation.
3. **Phase 3 (Switch Read):**
   - Deploy application code reading from the new column while still dual-writing.
4. **Phase 4 (Contract):**
   - Remove dual-writing code in the application.
   - Add `NOT NULL` constraints on the new column if required.
   - Safely drop old column or mark as unused.

### Phase 4: Rollback Strategy & Pre-Flight Verification
1. **Deterministic Down Migrations:** Every migration step must have an explicit, tested rollback script.
2. **Idempotency Guarantees:** Wrap DDL with `IF EXISTS` / `IF NOT EXISTS` guards where supported.
3. **Query Plan Verification:** Execute `EXPLAIN (ANALYZE, BUFFERS)` on critical queries against the new schema before promoting changes to production.

## Rules & Constraints
- **Zero Table Rewrites:** Never run blocking `ALTER TABLE` operations that trigger full table copies or exclusive locks longer than 2 seconds.
- **Concurrent Indexing Only:** Index creation on tables exceeding 10,000 rows must use `CONCURRENTLY` (PostgreSQL) or `LOCK=NONE` (MySQL).
- **Mandatory Lock Timeouts:** Every DDL script must set a conservative `lock_timeout` (maximum 2-3 seconds) to prevent head-of-line blocking in connection pools.
- **Batched Updates:** Data backfills must be batched by primary key ranges with pauses; never execute unbounded `UPDATE` or `DELETE` statements.

## Common Anti-Patterns
| Anti-Pattern | Correction |
| :--- | :--- |
| `ALTER TABLE large_table ADD COLUMN status VARCHAR(20) NOT NULL;` | Add column as nullable, backfill existing rows in batches, then add `NOT VALID` constraint and validate. |
| `CREATE INDEX idx_user_email ON users(email);` inside a transaction | Run `CREATE INDEX CONCURRENTLY idx_user_email ON users(email);` outside a transaction block. |
| Dropping a column immediately in single deployment | Follow Expand & Contract: Stop reading &rarr; stop writing &rarr; drop column after deprecation grace period. |
| Running unbounded `UPDATE table SET column = val;` | Batch by indexed chunk: `UPDATE table SET column = val WHERE id BETWEEN ? AND ?;` with sleep intervals. |
| Neglecting `lock_timeout` during migration execution | Set `SET lock_timeout = '2s';` so DDL aborts quickly if blocked by long-running transactions. |
