-- Migration: make TLO (topic learning outcome) belong to a topic.
--
-- The "Tlo" table originally had (subject_code, clo_code) but the application
-- treats a TLO as the learning outcome of a TOPIC. This adds topic_code and
-- tlo_code, and relaxes the now-unused clo_code column.
--
-- Safe to run multiple times (IF NOT EXISTS / DROP NOT NULL are idempotent).
--
-- PostgreSQL:
--   psql "$DATABASE_URL" -f scripts/migrate_tlo_topic_code.sql

ALTER TABLE "Tlo" ADD COLUMN IF NOT EXISTS topic_code VARCHAR;
ALTER TABLE "Tlo" ADD COLUMN IF NOT EXISTS tlo_code   VARCHAR;

-- clo_code is no longer written by the application.
ALTER TABLE "Tlo" ALTER COLUMN clo_code DROP NOT NULL;

CREATE INDEX IF NOT EXISTS ix_Tlo_topic_code ON "Tlo" (topic_code);
CREATE INDEX IF NOT EXISTS ix_Tlo_tlo_code   ON "Tlo" (tlo_code);
