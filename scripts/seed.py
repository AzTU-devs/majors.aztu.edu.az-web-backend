"""Seed the local SQLite database with reference data + an admin user.

Idempotent: rows are inserted with INSERT OR IGNORE.

Admin credentials:
    fin_kod  = ADMIN001
    password = Admin123!
"""
import os
import sqlite3
import sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app.utils.security import hash_password  # noqa: E402

DB_PATH = os.path.join(ROOT, "local.db")

ADMIN_FIN_KOD = "ADMIN001"
ADMIN_PASSWORD = "Admin123!"
ADMIN_ROLE = 1  # 1 = admin
NOW = datetime.utcnow().isoformat()


def _exists(cur: sqlite3.Cursor, sql: str, params: tuple) -> bool:
    cur.execute(sql, params)
    return cur.fetchone() is not None


def seed(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # University
    cur.execute(
        """INSERT OR IGNORE INTO universities
           (university_code, university_name, university_short_name,
            is_frozen, frozen_at, created_at, updated_at, deleted_at)
           VALUES (?, ?, ?, 0, NULL, ?, NULL, NULL)""",
        ("AZTU", "Azerbaijan Technical University", "AZTU", NOW),
    )

    # Faculty
    cur.execute(
        """INSERT OR IGNORE INTO faculties (faculty_code, created_at, updated_at)
           VALUES (?, ?, ?)""",
        ("ITF", NOW, NOW),
    )
    if not _exists(
        cur,
        "SELECT 1 FROM faculty_translations WHERE faculty_code = ? AND lang_code = ?",
        ("ITF", "az"),
    ):
        cur.execute(
            """INSERT INTO faculty_translations
               (faculty_code, lang_code, faculty_name, created_at, updated_at)
               VALUES (?, 'az', ?, ?, ?)""",
            ("ITF", "İnformasiya Texnologiyaları Fakültəsi", NOW, NOW),
        )

    # Cafedra
    cur.execute(
        """INSERT OR IGNORE INTO cafedras
           (faculty_code, cafedra_code, created_at, updated_at)
           VALUES (?, ?, ?, ?)""",
        ("ITF", "CE", NOW, NOW),
    )
    if not _exists(
        cur,
        "SELECT 1 FROM cafedra_translations WHERE cafedra_code = ? AND lang_code = ?",
        ("CE", "az"),
    ):
        cur.execute(
            """INSERT INTO cafedra_translations
               (cafedra_code, lang_code, cafedra_name, created_at, updated_at)
               VALUES (?, 'az', ?, ?, ?)""",
            ("CE", "Kompüter mühəndisliyi kafedrası", NOW, NOW),
        )

    # Admin auth + user
    hashed = hash_password(ADMIN_PASSWORD)
    cur.execute(
        """INSERT OR IGNORE INTO auth
           (fin_kod, password, role, approved, created_at, updated_at)
           VALUES (?, ?, ?, 1, ?, NULL)""",
        (ADMIN_FIN_KOD, hashed, ADMIN_ROLE, NOW),
    )
    cur.execute(
        """INSERT OR IGNORE INTO "user"
           (fin_kod, name, surname, father_name, email, cafedra_code, created_at, updated_at)
           VALUES (?, 'Admin', 'Aztu', 'Adminoglu', 'admin@aztu.local', ?, ?, NULL)""",
        (ADMIN_FIN_KOD, "CE", NOW),
    )

    # Specialty
    cur.execute(
        """INSERT OR IGNORE INTO specialties
           (cafedra_code, specialty_code, created_at, updated_at)
           VALUES (?, ?, ?, NULL)""",
        ("CE", "050631", NOW),
    )
    cur.execute(
        """INSERT OR IGNORE INTO specialty_translations
           (specialty_code, language_code, specialty_name, created_at, updated_at)
           VALUES (?, 'az', ?, ?, NULL)""",
        ("050631", "Kompüter mühəndisliyi", NOW),
    )

    # PLOs
    for code, az, en in [
        ("PLO-1", "Mühəndislik problemlərini həll edə bilmək", "Solve engineering problems"),
        ("PLO-2", "Komandada işləməyi bacarmaq", "Work effectively in a team"),
    ]:
        cur.execute(
            "INSERT OR IGNORE INTO plo (specialty_code, plo_code) VALUES (?, ?)",
            ("050631", code),
        )
        cur.execute(
            "INSERT OR IGNORE INTO plo_translations (plo_code, language_code, plo_content) VALUES (?, 'az', ?)",
            (code, az),
        )
        cur.execute(
            "INSERT OR IGNORE INTO plo_translations (plo_code, language_code, plo_content) VALUES (?, 'en', ?)",
            (code, en),
        )

    # SLOs — removed from the platform (kept commented for reference).
    # for code, az, en in [
    #     ("SLO-1", "Alqoritmləri analiz etmək", "Analyse algorithms"),
    #     ("SLO-2", "Verilənlər bazası dizayn etmək", "Design databases"),
    # ]:
    #     cur.execute(
    #         "INSERT OR IGNORE INTO slo (specialty_code, slo_code) VALUES (?, ?)",
    #         ("050631", code),
    #     )
    #     cur.execute(
    #         "INSERT OR IGNORE INTO slo_translations (slo_code, language_code, slo_content) VALUES (?, 'az', ?)",
    #         (code, az),
    #     )
    #     cur.execute(
    #         "INSERT OR IGNORE INTO slo_translations (slo_code, language_code, slo_content) VALUES (?, 'en', ?)",
    #         (code, en),
    #     )

    # Curricula subject + translations + CLO
    if not _exists(
        cur,
        "SELECT 1 FROM curricula_program WHERE specialty_code = ? AND subject_code = ?",
        ("050631", "CE-101"),
    ):
        cur.execute(
            """INSERT INTO curricula_program
               (specialty_code, subject_code, semester, status, credit, year, hours_per_week, created_at, updated_at)
               VALUES (?, ?, 1, 2, 5, 2, 4, ?, ?)""",
            ("050631", "CE-101", NOW, NOW),
        )
    if not _exists(
        cur,
        "SELECT 1 FROM curricula_program_translations WHERE subject_code = ? AND language_code = ?",
        ("CE-101", "az"),
    ):
        cur.execute(
            """INSERT INTO curricula_program_translations
               (subject_code, language_code, subject_name, subject_description, created_at, updated_at)
               VALUES (?, 'az', ?, ?, ?, ?)""",
            ("CE-101", "Proqramlaşdırmaya giriş", "Proqramlaşdırmanın əsasları", NOW, NOW),
        )
    if not _exists(
        cur,
        "SELECT 1 FROM clo WHERE subject_code = ? AND clo_code = ?",
        ("CE-101", "CLO-1"),
    ):
        cur.execute(
            """INSERT INTO clo (subject_code, clo_code, created_at, updated_at)
               VALUES (?, ?, ?, NULL)""",
            ("CE-101", "CLO-1", NOW),
        )
    if not _exists(
        cur,
        "SELECT 1 FROM clo_translations WHERE clo_code = ? AND language_code = ?",
        ("CLO-1", "az"),
    ):
        cur.execute(
            """INSERT INTO clo_translations (clo_code, language_code, clo_content, created_at, updated_at)
               VALUES (?, 'az', ?, ?, NULL)""",
            ("CLO-1", "Sadə proqramlar yaza bilmək", NOW),
        )

    conn.commit()


def main() -> None:
    if not os.path.exists(DB_PATH):
        sys.exit(f"Database not found at {DB_PATH}. Run scripts/init_db.py first.")
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        seed(conn)
    finally:
        conn.close()
    print(f"Seed complete. Admin login: {ADMIN_FIN_KOD} / {ADMIN_PASSWORD}")


if __name__ == "__main__":
    main()
