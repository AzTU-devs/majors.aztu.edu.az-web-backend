-- Migration: attach literature to a subject instead of a specialty.
--
--   * Adds literature.subject_code (the curricula_program.subject_code it belongs to).
--   * Relaxes the legacy specialty_code NOT NULL so new subject-scoped rows insert.
--
-- Idempotent. PostgreSQL:
--   psql "$DATABASE_URL" -f scripts/migrate_literature_subject.sql

ALTER TABLE literature ADD COLUMN IF NOT EXISTS subject_code VARCHAR;
ALTER TABLE literature ALTER COLUMN specialty_code DROP NOT NULL;
CREATE INDEX IF NOT EXISTS ix_literature_subject_code ON literature (subject_code);
