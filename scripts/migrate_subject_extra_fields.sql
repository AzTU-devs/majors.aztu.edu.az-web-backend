-- Migration: extra subject (curricula_program) fields for the syllabus.
--
--   form_of_education       1 = Əyani (Full-time), 2 = Qiyabi (Correspondence)
--   language_of_instruction 1 = Azerbaijani, 2 = English, 3 = Russian
--   in_class_hours          free text (e.g. "a) 30 saat - mühazirə b) 15 saat - seminar")
--   teaching_methods        comma-separated method keys
--   assessment              JSON array of {form, description, score, ftn}
--
-- Idempotent. PostgreSQL:
--   psql "$DATABASE_URL" -f scripts/migrate_subject_extra_fields.sql

ALTER TABLE curricula_program ADD COLUMN IF NOT EXISTS form_of_education       INTEGER;
ALTER TABLE curricula_program ADD COLUMN IF NOT EXISTS language_of_instruction INTEGER;
ALTER TABLE curricula_program ADD COLUMN IF NOT EXISTS in_class_hours          VARCHAR;
ALTER TABLE curricula_program ADD COLUMN IF NOT EXISTS teaching_methods        VARCHAR;
ALTER TABLE curricula_program ADD COLUMN IF NOT EXISTS assessment              VARCHAR;
