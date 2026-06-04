-- Migration: competency type (Job vs Specialty) + subject↔competency match table.
--
--   * competency.competency_type: 1 = Peşə (Job), 2 = İxtisas (Specialty).
--     Existing rows default to 2 (Specialty).
--   * subject_competency_match: links subjects to competencies (mirrors subject_plo_match).
--
-- Idempotent. PostgreSQL:
--   psql "$DATABASE_URL" -f scripts/migrate_competency_type_and_match.sql

ALTER TABLE competency ADD COLUMN IF NOT EXISTS competency_type INTEGER NOT NULL DEFAULT 2;

CREATE TABLE IF NOT EXISTS subject_competency_match (
    id              SERIAL PRIMARY KEY,
    subject_code    VARCHAR NOT NULL,
    competency_code VARCHAR NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    CONSTRAINT uq_subject_competency UNIQUE (subject_code, competency_code)
);
CREATE INDEX IF NOT EXISTS ix_subject_competency_match_subject_code    ON subject_competency_match (subject_code);
CREATE INDEX IF NOT EXISTS ix_subject_competency_match_competency_code ON subject_competency_match (competency_code);
