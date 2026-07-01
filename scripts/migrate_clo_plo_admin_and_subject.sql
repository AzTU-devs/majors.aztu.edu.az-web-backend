-- Migration: CLO↔PLO matching, admin profiles, and the subject out-of-class hours column.
-- The app also self-applies these on startup (see app/main.py ensure_schema), but this
-- script lets you apply them explicitly to an existing database.

-- 1. Auditoriya kənar saatlar (out-of-classroom hours) on subjects.
ALTER TABLE curricula_program ADD COLUMN out_of_class_hours VARCHAR;

-- 2. CLO ↔ PLO matching table.
CREATE TABLE IF NOT EXISTS clo_plo_match (
    id         INTEGER PRIMARY KEY,
    clo_code   VARCHAR NOT NULL,
    plo_code   VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE (clo_code, plo_code)
);
CREATE INDEX IF NOT EXISTS ix_clo_plo_match_clo_code ON clo_plo_match (clo_code);
CREATE INDEX IF NOT EXISTS ix_clo_plo_match_plo_code ON clo_plo_match (plo_code);

-- 3. Admin profile table (details for auth.role = 1 accounts).
CREATE TABLE IF NOT EXISTS admin_profile (
    id         INTEGER PRIMARY KEY,
    fin_kod    VARCHAR(7) NOT NULL,
    name       VARCHAR NOT NULL,
    surname    VARCHAR NOT NULL,
    email      VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    UNIQUE (fin_kod),
    UNIQUE (email),
    FOREIGN KEY (fin_kod) REFERENCES auth (fin_kod)
);
