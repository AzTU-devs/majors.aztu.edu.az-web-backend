-- Make topic_code collisions impossible.
--
-- topic_code is the only link between a topic and its translations and TLOs —
-- there is no foreign key. While codes could repeat, two unrelated subjects
-- shared one topic, and the ``.first()`` translation lookup made one render the
-- other's text. Unique indexes turn that class of bug into an insert error.
--
-- PREREQUISITE: run
--     python scripts/repair_topic_code_collisions.py --apply
-- until it reports zero collided codes AND zero skipped groups. These
-- statements fail while any duplicate remains — that is intentional, it means
-- data still needs splitting.
--
-- Verify first:
--   SELECT topic_code, COUNT(*) FROM topic GROUP BY topic_code HAVING COUNT(*) > 1;
--   SELECT topic_code, language_code, COUNT(*) FROM topic_translations
--     GROUP BY topic_code, language_code HAVING COUNT(*) > 1;

CREATE UNIQUE INDEX IF NOT EXISTS ux_topic_topic_code
    ON topic (topic_code);

CREATE UNIQUE INDEX IF NOT EXISTS ux_topic_translations_code_lang
    ON topic_translations (topic_code, language_code);

-- TLOs carry the identical defect one level down (generate_tlo_code used the
-- same 90k random space). Check for collisions before enabling these:
--   SELECT tlo_code, COUNT(*) FROM "Tlo" GROUP BY tlo_code HAVING COUNT(*) > 1;
--
-- CREATE UNIQUE INDEX IF NOT EXISTS ux_tlo_tlo_code ON "Tlo" (tlo_code);
-- CREATE UNIQUE INDEX IF NOT EXISTS ux_tlo_translations_code_lang
--     ON tlo_translations (tlo_code, language_code);

-- NOT unique: curricula_program.subject_code. General subjects and
-- additional_specialty_codes deliberately create one row per specialty sharing
-- a code. Cause 1 is guarded in add_curricula instead.
