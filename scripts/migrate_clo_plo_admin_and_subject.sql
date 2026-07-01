-- Migration for this change set: CLO↔PLO matching, admin profiles, subject
-- out-of-class hours, and the academic-year type change.
--
-- The app ALSO self-applies all of these on startup (app/main.py -> ensure_schema),
-- so running this by hand is only needed if you prefer explicit migrations.
--
-- ============================ POSTGRES (Neon) ============================

-- 1. Academic year (Akademik il): legacy INTEGER -> free text VARCHAR "2025-2026".
ALTER TABLE curricula_program
    ALTER COLUMN year TYPE VARCHAR USING year::varchar;

-- 2. Auditoriya kənar saatlar (out-of-classroom hours) on subjects.
ALTER TABLE curricula_program
    ADD COLUMN IF NOT EXISTS out_of_class_hours VARCHAR;

-- 3. CLO ↔ PLO matching table.
CREATE TABLE IF NOT EXISTS clo_plo_match (
    id         SERIAL PRIMARY KEY,
    clo_code   VARCHAR NOT NULL,
    plo_code   VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT uq_clo_plo_match UNIQUE (clo_code, plo_code)
);
CREATE INDEX IF NOT EXISTS ix_clo_plo_match_clo_code ON clo_plo_match (clo_code);
CREATE INDEX IF NOT EXISTS ix_clo_plo_match_plo_code ON clo_plo_match (plo_code);

-- 4. Admin profile table (details for auth.role = 1 accounts).
CREATE TABLE IF NOT EXISTS admin_profile (
    id         SERIAL PRIMARY KEY,
    fin_kod    VARCHAR(7) NOT NULL,
    name       VARCHAR NOT NULL,
    surname    VARCHAR NOT NULL,
    email      VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    CONSTRAINT uq_admin_profile_fin_kod UNIQUE (fin_kod),
    CONSTRAINT uq_admin_profile_email UNIQUE (email),
    CONSTRAINT fk_admin_profile_auth FOREIGN KEY (fin_kod) REFERENCES auth (fin_kod)
);

-- (Optional) SLO was removed from the app. The tables are simply unused; drop
-- them only if you want them gone:
-- DROP TABLE IF EXISTS slo_translations;
-- DROP TABLE IF EXISTS slo;

-- ============================ SQLite (local dev) =========================
-- SQLite is dynamically typed, so the INTEGER "year" column already accepts
-- "2025-2026" text with no ALTER. For the rest:
--   ALTER TABLE curricula_program ADD COLUMN out_of_class_hours VARCHAR;
--   CREATE TABLE clo_plo_match (id INTEGER PRIMARY KEY, clo_code VARCHAR NOT NULL,
--       plo_code VARCHAR NOT NULL, created_at TIMESTAMP NOT NULL,
--       UNIQUE (clo_code, plo_code));
--   CREATE TABLE admin_profile (id INTEGER PRIMARY KEY, fin_kod VARCHAR(7) NOT NULL,
--       name VARCHAR NOT NULL, surname VARCHAR NOT NULL, email VARCHAR NOT NULL,
--       created_at TIMESTAMP NOT NULL, updated_at TIMESTAMP,
--       UNIQUE (fin_kod), UNIQUE (email),
--       FOREIGN KEY (fin_kod) REFERENCES auth (fin_kod));
