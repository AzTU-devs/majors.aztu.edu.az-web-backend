"""Split topics that share a topic_code, so each subject shows only its own.

Background
----------
``generate_topic_code`` used to return ``PLO-{random 10000..99999}`` with no
uniqueness check and no unique index. At ~350 topics a collision is more likely
than not, and the platform is well past that. Because a topic's name/description
/result live in ``topic_translations`` keyed *only* by topic_code, and the read
path uses ``.first()``, a collision makes the second topic render the first
one's text — a topic nobody entered appearing in a subject's topic list.

Repair
------
Within one collided code, the topic rows and their translation rows were
inserted in the same transaction, so both id sequences advance in the same
order. The i-th topic (by id) therefore owns the i-th ``az`` row and the i-th
``en`` row (by id). The lowest-id topic keeps the original code — its URLs stay
valid — and every later one gets a fresh unique code, taking its own
translations with it.

A group is only rewritten when the counts line up exactly (n topics, n az, n
en). Anything else is reported and skipped rather than guessed at.

TLOs are *not* reassigned. ``add_tlo`` resolved its parent with ``.first()``, so
every TLO under a collided code was stamped with the lowest-id topic's
subject_code and there is no signal left as to which topic it was meant for.
Groups with TLOs are listed for manual review.

Usage
-----
    python scripts/repair_topic_code_collisions.py            # dry run, default
    python scripts/repair_topic_code_collisions.py --apply    # commit changes
"""

import argparse
import asyncio
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func, select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.models.tlo import Tlo  # noqa: E402
from app.models.topic import Topic  # noqa: E402
from app.models.translation.topic_translations import TopicTranslations  # noqa: E402
from app.utils.code_generator import generate_code  # noqa: E402


async def find_collided_codes(db):
    """topic_codes carried by more than one topic row."""
    rows = await db.execute(
        select(Topic.topic_code)
        .group_by(Topic.topic_code)
        .having(func.count() > 1)
    )
    return list(rows.scalars().all())


async def repair(apply: bool) -> int:
    try:
        return await _repair(apply)
    finally:
        # Without this the driver's connection pool keeps a non-daemon worker
        # thread alive and the process hangs after printing its report.
        await engine.dispose()


async def _repair(apply: bool) -> int:
    async with AsyncSessionLocal() as db:
        codes = await find_collided_codes(db)
        if not codes:
            print("No collided topic codes. Nothing to do.")
            return 0

        total_topics = (await db.execute(select(func.count()).select_from(Topic))).scalar()
        print(f"{len(codes)} collided topic codes out of {total_topics} topics total.\n")

        rewritten = 0
        skipped = []
        with_tlos = []

        for code in codes:
            topics = (
                await db.execute(
                    select(Topic).where(Topic.topic_code == code).order_by(Topic.id)
                )
            ).scalars().all()

            translations = (
                await db.execute(
                    select(TopicTranslations)
                    .where(TopicTranslations.topic_code == code)
                    .order_by(TopicTranslations.id)
                )
            ).scalars().all()

            by_lang = defaultdict(list)
            for tr in translations:
                by_lang[tr.language_code].append(tr)

            # Only rewrite when every language has exactly one row per topic;
            # otherwise the i-th/i-th pairing is not trustworthy.
            n = len(topics)
            if any(len(rows) != n for rows in by_lang.values()) or not by_lang:
                skipped.append(
                    f"  {code}: {n} topics but "
                    + ", ".join(f"{lang}={len(rows)}" for lang, rows in sorted(by_lang.items()))
                )
                continue

            tlos = (
                await db.execute(select(Tlo.id).where(Tlo.topic_code == code))
            ).scalars().all()
            if tlos:
                with_tlos.append(f"  {code}: {len(tlos)} TLO(s) left on topic id={topics[0].id}")

            subjects = ", ".join(t.subject_code for t in topics)
            print(f"{code}  ({n} topics across subjects: {subjects})")
            print(f"  keep  topic id={topics[0].id} subject={topics[0].subject_code} -> {code}")

            for i in range(1, n):
                topic = topics[i]
                new_code = generate_code("TOPIC")
                for rows in by_lang.values():
                    rows[i].topic_code = new_code
                topic.topic_code = new_code
                rewritten += 1
                named = by_lang.get("az") or by_lang[sorted(by_lang)[0]]
                name = named[i].topic_name
                print(
                    f"  move  topic id={topic.id} subject={topic.subject_code} "
                    f"-> {new_code}  ({name!r})"
                )
            print()

        if skipped:
            print("SKIPPED — translation counts do not line up, review by hand:")
            print("\n".join(skipped))
            print()

        if with_tlos:
            print("TLOs under a collided code (ownership unrecoverable, review by hand):")
            print("\n".join(with_tlos))
            print()

        print(f"{rewritten} topic(s) would be re-coded; {len(skipped)} group(s) skipped.")

        if apply:
            await db.commit()
            print("Committed.")
        else:
            await db.rollback()
            print("Dry run — nothing written. Re-run with --apply to commit.")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="commit the changes")
    args = parser.parse_args()
    sys.exit(asyncio.run(repair(args.apply)))
