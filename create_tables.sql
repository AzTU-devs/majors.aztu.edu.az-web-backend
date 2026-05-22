-- ============================================================
-- CREATE TABLE queries generated from SQLAlchemy models
-- Order: parent tables first (respects FK dependencies)
-- ============================================================

-- 1. universities
CREATE TABLE IF NOT EXISTS universities (
    id                    SERIAL PRIMARY KEY,
    university_code       VARCHAR NOT NULL UNIQUE,
    university_name       VARCHAR NOT NULL UNIQUE,
    university_short_name VARCHAR NOT NULL UNIQUE,
    is_frozen             BOOLEAN NOT NULL DEFAULT FALSE,
    frozen_at             TIMESTAMP,
    created_at            TIMESTAMP NOT NULL,
    updated_at            TIMESTAMP,
    deleted_at            TIMESTAMP
);

-- 2. faculties
CREATE TABLE IF NOT EXISTS faculties (
    id           SERIAL PRIMARY KEY,
    faculty_code VARCHAR NOT NULL UNIQUE,
    created_at   TIMESTAMP NOT NULL,
    updated_at   TIMESTAMP NOT NULL
);

-- 3. auth
CREATE TABLE IF NOT EXISTS auth (
    id         SERIAL PRIMARY KEY,
    fin_kod    VARCHAR NOT NULL UNIQUE,
    password   VARCHAR NOT NULL,
    role       INTEGER NOT NULL,
    approved   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- 4. cafedras  (depends on: faculties)
CREATE TABLE IF NOT EXISTS cafedras (
    id           SERIAL PRIMARY KEY,
    faculty_code VARCHAR NOT NULL REFERENCES faculties(faculty_code),
    cafedra_code VARCHAR NOT NULL UNIQUE,
    created_at   TIMESTAMP NOT NULL,
    updated_at   TIMESTAMP NOT NULL
);

-- 5. otp  (depends on: auth)
CREATE TABLE IF NOT EXISTS otp (
    id             SERIAL PRIMARY KEY,
    fin_kod        VARCHAR(7) NOT NULL UNIQUE REFERENCES auth(fin_kod),
    otp            VARCHAR(255) NOT NULL,
    otp_expires_at TIMESTAMP NOT NULL
);

-- 6. user  (depends on: auth, cafedras)
CREATE TABLE IF NOT EXISTS "user" (
    id           SERIAL PRIMARY KEY,
    fin_kod      VARCHAR(7) NOT NULL UNIQUE REFERENCES auth(fin_kod),
    name         VARCHAR NOT NULL,
    surname      VARCHAR NOT NULL,
    father_name  VARCHAR NOT NULL,
    email        VARCHAR NOT NULL UNIQUE,
    cafedra_code VARCHAR NOT NULL UNIQUE REFERENCES cafedras(cafedra_code),
    created_at   TIMESTAMP NOT NULL,
    updated_at   TIMESTAMP
);

-- 7. specialties  (depends on: cafedras)
CREATE TABLE IF NOT EXISTS specialties (
    id             SERIAL PRIMARY KEY,
    cafedra_code   VARCHAR NOT NULL REFERENCES cafedras(cafedra_code),
    specialty_code VARCHAR NOT NULL UNIQUE,
    created_at     TIMESTAMP NOT NULL,
    updated_at     TIMESTAMP
);

-- 8. faculty_translations  (depends on: faculties)
CREATE TABLE IF NOT EXISTS faculty_translations (
    id           SERIAL PRIMARY KEY,
    faculty_code VARCHAR NOT NULL REFERENCES faculties(faculty_code) ON DELETE CASCADE,
    lang_code    VARCHAR(2) NOT NULL,
    faculty_name VARCHAR NOT NULL UNIQUE,
    created_at   TIMESTAMP NOT NULL,
    updated_at   TIMESTAMP NOT NULL
);

-- 9. cafedra_translations  (depends on: cafedras)
CREATE TABLE IF NOT EXISTS cafedra_translations (
    id           SERIAL PRIMARY KEY,
    cafedra_code VARCHAR NOT NULL REFERENCES cafedras(cafedra_code) ON DELETE CASCADE,
    lang_code    VARCHAR(2) NOT NULL,
    cafedra_name VARCHAR NOT NULL,
    created_at   TIMESTAMP NOT NULL,
    updated_at   TIMESTAMP NOT NULL
);

-- 10. specialty_translations  (depends on: specialties)
CREATE TABLE IF NOT EXISTS specialty_translations (
    id             SERIAL PRIMARY KEY,
    specialty_code VARCHAR NOT NULL REFERENCES specialties(specialty_code),
    language_code  VARCHAR NOT NULL,
    specialty_name VARCHAR NOT NULL,
    created_at     TIMESTAMP NOT NULL,
    updated_at     TIMESTAMP,
    CONSTRAINT uq_specialty_lang      UNIQUE (specialty_code, language_code),
    CONSTRAINT uq_specialty_name_lang UNIQUE (specialty_name, language_code),
    CONSTRAINT chk_specialty_lang_code CHECK (language_code IN ('en', 'az'))
);

-- 11. plo  (depends on: specialties)
CREATE TABLE IF NOT EXISTS plo (
    id             SERIAL PRIMARY KEY,
    specialty_code VARCHAR NOT NULL REFERENCES specialties(specialty_code),
    plo_code       VARCHAR NOT NULL UNIQUE
);

-- 12. slo  (depends on: specialties)
CREATE TABLE IF NOT EXISTS slo (
    id             SERIAL PRIMARY KEY,
    specialty_code VARCHAR NOT NULL REFERENCES specialties(specialty_code),
    slo_code       VARCHAR NOT NULL UNIQUE
);

-- 13. graduate_career_opportunities  (depends on: specialties)
CREATE TABLE IF NOT EXISTS graduate_career_opportunities (
    id             SERIAL PRIMARY KEY,
    specialty_code VARCHAR NOT NULL REFERENCES specialties(specialty_code),
    career_code    VARCHAR NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS ix_gco_career_code ON graduate_career_opportunities (career_code);

-- 14. competency  (depends on: specialties)
CREATE TABLE IF NOT EXISTS competency (
    id              SERIAL PRIMARY KEY,
    specialty_code  VARCHAR NOT NULL REFERENCES specialties(specialty_code),
    competency_code VARCHAR NOT NULL UNIQUE
);

-- 15. specialty_characteristics  (depends on: specialties)
CREATE TABLE IF NOT EXISTS specialty_characteristics (
    id             SERIAL PRIMARY KEY,
    specialty_code VARCHAR NOT NULL REFERENCES specialties(specialty_code)
);

-- 16. curricula_program  (depends on: specialties)
CREATE TABLE IF NOT EXISTS curricula_program (
    id             SERIAL PRIMARY KEY,
    specialty_code VARCHAR NOT NULL REFERENCES specialties(specialty_code),
    subject_code   VARCHAR NOT NULL,
    semester       INTEGER NOT NULL,
    -- 1=autumn, 2=spring
    status         INTEGER NOT NULL,
    -- 1=selection, 2=mandatory, 3=other
    credit         INTEGER NOT NULL,
    year           INTEGER NOT NULL,
    hours_per_week INTEGER NOT NULL,
    created_at     TIMESTAMP NOT NULL,
    updated_at     TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_curricula_program_subject_code ON curricula_program (subject_code);

-- 17. plo_translations  (depends on: plo)
CREATE TABLE IF NOT EXISTS plo_translations (
    id            SERIAL PRIMARY KEY,
    plo_code      VARCHAR NOT NULL REFERENCES plo(plo_code),
    language_code CHAR(2) NOT NULL,
    plo_content   TEXT NOT NULL,
    CONSTRAINT uq_plo_lang UNIQUE (plo_code, language_code)
);

-- 18. slo_translations  (depends on: slo)
CREATE TABLE IF NOT EXISTS slo_translations (
    id            SERIAL PRIMARY KEY,
    slo_code      VARCHAR NOT NULL REFERENCES slo(slo_code),
    language_code CHAR(2) NOT NULL,
    slo_content   TEXT NOT NULL,
    CONSTRAINT uq_slo_lang UNIQUE (slo_code, language_code)
);

-- 19. graduate_career_opportunities_translations  (depends on: graduate_career_opportunities)
CREATE TABLE IF NOT EXISTS graduate_career_opportunities_translations (
    id             SERIAL PRIMARY KEY,
    career_code    VARCHAR NOT NULL REFERENCES graduate_career_opportunities(career_code),
    career_title   VARCHAR,
    language_code  CHAR(2) NOT NULL,
    career_content TEXT NOT NULL
);

-- 20. competency_translation  (depends on: competency)
CREATE TABLE IF NOT EXISTS competency_translation (
    id                 SERIAL PRIMARY KEY,
    competency_code    VARCHAR NOT NULL REFERENCES competency(competency_code),
    language_code      CHAR(2) NOT NULL,
    competency_content TEXT NOT NULL
);

-- 21. specialty_characteristics_translations  (depends on: specialty_characteristics)
CREATE TABLE IF NOT EXISTS specialty_characteristics_translations (
    id                          SERIAL PRIMARY KEY,
    specialty_characteristic_id INTEGER NOT NULL REFERENCES specialty_characteristics(id),
    language_code               CHAR(2) NOT NULL,
    program_desc                VARCHAR,
    degree_requirements         VARCHAR
);

-- 22. curricula_program_translations  (no FK: subject_code is not unique in curricula_program)
CREATE TABLE IF NOT EXISTS curricula_program_translations (
    id                  SERIAL PRIMARY KEY,
    subject_code        VARCHAR NOT NULL,
    language_code       VARCHAR(2) NOT NULL,
    subject_name        VARCHAR NOT NULL,
    subject_description VARCHAR,
    created_at          TIMESTAMP NOT NULL,
    updated_at          TIMESTAMP NOT NULL,
    CONSTRAINT uq_curricula_subject_lang UNIQUE (subject_code, language_code)
);

-- 23. clo
CREATE TABLE IF NOT EXISTS clo (
    id           SERIAL PRIMARY KEY,
    subject_code VARCHAR NOT NULL,
    clo_code     VARCHAR NOT NULL,
    created_at   TIMESTAMP NOT NULL,
    updated_at   TIMESTAMP
);

-- 24. clo_translations
CREATE TABLE IF NOT EXISTS clo_translations (
    id            SERIAL PRIMARY KEY,
    clo_code      VARCHAR NOT NULL,
    language_code VARCHAR(2) NOT NULL,
    clo_content   VARCHAR NOT NULL,
    created_at    TIMESTAMP NOT NULL,
    updated_at    TIMESTAMP
);

-- 25. "Tlo"  (table name is case-sensitive as defined in model)
CREATE TABLE IF NOT EXISTS "Tlo" (
    id           SERIAL PRIMARY KEY,
    subject_code VARCHAR NOT NULL,
    clo_code     VARCHAR NOT NULL,
    created_at   TIMESTAMP NOT NULL,
    updated_at   TIMESTAMP
);

-- 26. tlo_translations
CREATE TABLE IF NOT EXISTS tlo_translations (
    id            SERIAL PRIMARY KEY,
    tlo_code      VARCHAR NOT NULL,
    language_code VARCHAR(2) NOT NULL,
    tlo_content   VARCHAR NOT NULL,
    created_at    TIMESTAMP NOT NULL,
    updated_at    TIMESTAMP
);

-- 27. topic
CREATE TABLE IF NOT EXISTS topic (
    id           SERIAL PRIMARY KEY,
    subject_code VARCHAR NOT NULL,
    topic_code   VARCHAR NOT NULL,
    topic_url    VARCHAR NOT NULL,
    topic_type   INTEGER NOT NULL,
    -- 1=muhazire, 2=mesgele, 3=laboratoriya, 4=serbest is
    created_at   TIMESTAMP NOT NULL,
    updated_at   TIMESTAMP
);

-- 28. topic_translations
CREATE TABLE IF NOT EXISTS topic_translations (
    id                SERIAL PRIMARY KEY,
    topic_code        VARCHAR NOT NULL,
    topic_name        VARCHAR NOT NULL,
    topic_description VARCHAR,
    topic_result      VARCHAR,
    language_code     VARCHAR(2) NOT NULL,
    created_at        TIMESTAMP NOT NULL,
    updated_at        TIMESTAMP
);

-- 29. literature  (note: specialty_code is INTEGER in the model)
CREATE TABLE IF NOT EXISTS literature (
    id              SERIAL PRIMARY KEY,
    literature_code INTEGER NOT NULL UNIQUE,
    specialty_code  INTEGER NOT NULL,
    url             VARCHAR NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP
);

-- 30. literature_translations
CREATE TABLE IF NOT EXISTS literature_translations (
    id              SERIAL PRIMARY KEY,
    language_code   VARCHAR(2) NOT NULL,
    literature_code VARCHAR NOT NULL,
    literature_name VARCHAR NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL
);

-- 31. subject_plo_match
CREATE TABLE IF NOT EXISTS subject_plo_match (
    id           SERIAL PRIMARY KEY,
    subject_code VARCHAR NOT NULL,
    plo_code     VARCHAR NOT NULL,
    created_at   TIMESTAMP NOT NULL,
    CONSTRAINT uq_subject_plo UNIQUE (subject_code, plo_code)
);
CREATE INDEX IF NOT EXISTS ix_subject_plo_match_subject_code ON subject_plo_match (subject_code);
CREATE INDEX IF NOT EXISTS ix_subject_plo_match_plo_code     ON subject_plo_match (plo_code);
