-- ============================================================
-- SQLite-compatible CREATE TABLE queries
-- Run this after connecting to your dev.db file
-- Enable FK enforcement first:
PRAGMA foreign_keys = ON;
-- ============================================================

-- 1. universities
CREATE TABLE IF NOT EXISTS universities (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    university_code       TEXT NOT NULL UNIQUE,
    university_name       TEXT NOT NULL UNIQUE,
    university_short_name TEXT NOT NULL UNIQUE,
    is_frozen             INTEGER NOT NULL DEFAULT 0,
    frozen_at             DATETIME,
    created_at            DATETIME NOT NULL,
    updated_at            DATETIME,
    deleted_at            DATETIME
);

-- 2. faculties
CREATE TABLE IF NOT EXISTS faculties (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_code TEXT NOT NULL UNIQUE,
    created_at   DATETIME NOT NULL,
    updated_at   DATETIME NOT NULL
);

-- 3. auth
CREATE TABLE IF NOT EXISTS auth (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    fin_kod    TEXT NOT NULL UNIQUE,
    password   TEXT NOT NULL,
    role       INTEGER NOT NULL,
    approved   INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME
);

-- 4. cafedras  (depends on: faculties)
CREATE TABLE IF NOT EXISTS cafedras (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_code TEXT NOT NULL REFERENCES faculties(faculty_code),
    cafedra_code TEXT NOT NULL UNIQUE,
    created_at   DATETIME NOT NULL,
    updated_at   DATETIME NOT NULL
);

-- 5. otp  (depends on: auth)
CREATE TABLE IF NOT EXISTS otp (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    fin_kod        TEXT NOT NULL UNIQUE REFERENCES auth(fin_kod),
    otp            TEXT NOT NULL,
    otp_expires_at DATETIME NOT NULL
);

-- 6. user  (depends on: auth, cafedras)
CREATE TABLE IF NOT EXISTS "user" (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    fin_kod      TEXT NOT NULL UNIQUE REFERENCES auth(fin_kod),
    name         TEXT NOT NULL,
    surname      TEXT NOT NULL,
    father_name  TEXT NOT NULL,
    email        TEXT NOT NULL UNIQUE,
    cafedra_code TEXT NOT NULL UNIQUE REFERENCES cafedras(cafedra_code),
    created_at   DATETIME NOT NULL,
    updated_at   DATETIME
);

-- 7. specialties  (depends on: cafedras)
CREATE TABLE IF NOT EXISTS specialties (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    cafedra_code   TEXT NOT NULL REFERENCES cafedras(cafedra_code),
    specialty_code TEXT NOT NULL UNIQUE,
    created_at     DATETIME NOT NULL,
    updated_at     DATETIME
);

-- 8. faculty_translations  (depends on: faculties)
CREATE TABLE IF NOT EXISTS faculty_translations (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_code TEXT NOT NULL REFERENCES faculties(faculty_code) ON DELETE CASCADE,
    lang_code    TEXT NOT NULL,
    faculty_name TEXT NOT NULL UNIQUE,
    created_at   DATETIME NOT NULL,
    updated_at   DATETIME NOT NULL
);

-- 9. cafedra_translations  (depends on: cafedras)
CREATE TABLE IF NOT EXISTS cafedra_translations (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    cafedra_code TEXT NOT NULL REFERENCES cafedras(cafedra_code) ON DELETE CASCADE,
    lang_code    TEXT NOT NULL,
    cafedra_name TEXT NOT NULL,
    created_at   DATETIME NOT NULL,
    updated_at   DATETIME NOT NULL
);

-- 10. specialty_translations  (depends on: specialties)
CREATE TABLE IF NOT EXISTS specialty_translations (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    specialty_code TEXT NOT NULL UNIQUE REFERENCES specialties(specialty_code),
    language_code  TEXT NOT NULL CHECK (language_code IN ('en', 'az')),
    specialty_name TEXT NOT NULL UNIQUE,
    created_at     DATETIME NOT NULL,
    updated_at     DATETIME
);

-- 11. plo  (depends on: specialties)
CREATE TABLE IF NOT EXISTS plo (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    specialty_code TEXT NOT NULL REFERENCES specialties(specialty_code),
    plo_code       TEXT NOT NULL UNIQUE
);

-- 12. slo  (depends on: specialties)
CREATE TABLE IF NOT EXISTS slo (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    specialty_code TEXT NOT NULL REFERENCES specialties(specialty_code),
    slo_code       TEXT NOT NULL UNIQUE
);

-- 13. graduate_career_opportunities  (depends on: specialties)
CREATE TABLE IF NOT EXISTS graduate_career_opportunities (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    specialty_code TEXT NOT NULL REFERENCES specialties(specialty_code),
    career_code    TEXT NOT NULL UNIQUE
);

-- 14. competency  (depends on: specialties)
CREATE TABLE IF NOT EXISTS competency (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    specialty_code  TEXT NOT NULL REFERENCES specialties(specialty_code),
    competency_code TEXT NOT NULL UNIQUE,
    -- 1 = Peşə (Job), 2 = İxtisas (Specialty)
    competency_type INTEGER NOT NULL DEFAULT 2
);

-- 15. specialty_characteristics  (depends on: specialties)
CREATE TABLE IF NOT EXISTS specialty_characteristics (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    specialty_code TEXT NOT NULL REFERENCES specialties(specialty_code)
);

-- 16. curricula_program  (depends on: specialties)
CREATE TABLE IF NOT EXISTS curricula_program (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    specialty_code TEXT NOT NULL REFERENCES specialties(specialty_code),
    subject_code   TEXT NOT NULL,
    semester       INTEGER NOT NULL,   -- 1=autumn, 2=spring
    status         INTEGER NOT NULL,   -- 1=selection, 2=mandatory, 3=other
    credit         INTEGER NOT NULL,
    year           INTEGER NOT NULL,
    hours_per_week INTEGER NOT NULL,
    created_at     DATETIME NOT NULL,
    updated_at     DATETIME NOT NULL
);

-- 17. plo_translations  (depends on: plo)
CREATE TABLE IF NOT EXISTS plo_translations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    plo_code      TEXT NOT NULL REFERENCES plo(plo_code),
    language_code TEXT NOT NULL,
    plo_content   TEXT NOT NULL,
    UNIQUE (plo_code, language_code)
);

-- 18. slo_translations  (depends on: slo)
CREATE TABLE IF NOT EXISTS slo_translations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    slo_code      TEXT NOT NULL REFERENCES slo(slo_code),
    language_code TEXT NOT NULL,
    slo_content   TEXT NOT NULL,
    UNIQUE (slo_code, language_code)
);

-- 19. graduate_career_opportunities_translations  (depends on: graduate_career_opportunities)
CREATE TABLE IF NOT EXISTS graduate_career_opportunities_translations (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    career_code    TEXT NOT NULL REFERENCES graduate_career_opportunities(career_code),
    career_title   TEXT,
    language_code  TEXT NOT NULL,
    career_content TEXT NOT NULL
);

-- 20. competency_translation  (depends on: competency)
CREATE TABLE IF NOT EXISTS competency_translation (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    competency_code    TEXT NOT NULL REFERENCES competency(competency_code),
    language_code      TEXT NOT NULL,
    competency_content TEXT NOT NULL
);

-- 21. specialty_characteristics_translations  (depends on: specialty_characteristics)
CREATE TABLE IF NOT EXISTS specialty_characteristics_translations (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    specialty_characteristic_id INTEGER NOT NULL REFERENCES specialty_characteristics(id),
    language_code               TEXT NOT NULL,
    program_desc                TEXT,
    degree_requirements         TEXT
);

-- 22. curricula_program_translations  (depends on: curricula_program)
CREATE TABLE IF NOT EXISTS curricula_program_translations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code        TEXT NOT NULL,
    language_code       TEXT NOT NULL,
    subject_name        TEXT NOT NULL,
    subject_description TEXT,
    created_at          DATETIME NOT NULL,
    updated_at          DATETIME NOT NULL
);

-- 23. clo
CREATE TABLE IF NOT EXISTS clo (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code TEXT NOT NULL,
    clo_code     TEXT NOT NULL,
    created_at   DATETIME NOT NULL,
    updated_at   DATETIME
);

-- 24. clo_translations
CREATE TABLE IF NOT EXISTS clo_translations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    clo_code      TEXT NOT NULL,
    language_code TEXT NOT NULL,
    clo_content   TEXT NOT NULL,
    created_at    DATETIME NOT NULL,
    updated_at    DATETIME
);

-- 25. Tlo  (case-sensitive name as in the model)
CREATE TABLE IF NOT EXISTS "Tlo" (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code TEXT NOT NULL,
    topic_code   TEXT NOT NULL,
    tlo_code     TEXT NOT NULL,
    created_at   DATETIME NOT NULL,
    updated_at   DATETIME
);

-- 26. tlo_translations
CREATE TABLE IF NOT EXISTS tlo_translations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    tlo_code      TEXT NOT NULL,
    language_code TEXT NOT NULL,
    tlo_content   TEXT NOT NULL,
    created_at    DATETIME NOT NULL,
    updated_at    DATETIME
);

-- 27. topic
CREATE TABLE IF NOT EXISTS topic (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code TEXT NOT NULL,
    topic_code   TEXT NOT NULL,
    topic_url    TEXT NOT NULL,
    topic_type   INTEGER NOT NULL,  -- 1=muhazire, 2=mesgele, 3=laboratoriya, 4=serbest is
    created_at   DATETIME NOT NULL,
    updated_at   DATETIME
);

-- 28. topic_translations
CREATE TABLE IF NOT EXISTS topic_translations (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_code        TEXT NOT NULL,
    topic_name        TEXT NOT NULL,
    topic_description TEXT,
    topic_result      TEXT,
    language_code     TEXT NOT NULL,
    created_at        DATETIME NOT NULL,
    updated_at        DATETIME
);

-- 28b. subject_plo_match  (links subjects to PLOs)
CREATE TABLE IF NOT EXISTS subject_plo_match (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code TEXT NOT NULL,
    plo_code     TEXT NOT NULL,
    created_at   DATETIME NOT NULL,
    UNIQUE (subject_code, plo_code)
);

-- 28c. subject_competency_match  (links subjects to competencies)
CREATE TABLE IF NOT EXISTS subject_competency_match (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code    TEXT NOT NULL,
    competency_code TEXT NOT NULL,
    created_at      DATETIME NOT NULL,
    UNIQUE (subject_code, competency_code)
);

-- 29. literature
CREATE TABLE IF NOT EXISTS literature (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    literature_code INTEGER NOT NULL UNIQUE,
    specialty_code  INTEGER NOT NULL,
    url             TEXT NOT NULL,
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME
);

-- 30. literature_translations
CREATE TABLE IF NOT EXISTS literature_translations (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    language_code    TEXT NOT NULL,
    literature_code  TEXT NOT NULL,
    literature_name  TEXT NOT NULL,
    created_at       DATETIME NOT NULL,
    updated_at       DATETIME NOT NULL
);
