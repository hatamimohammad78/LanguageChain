import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import load_settings


import sqlite3
import psycopg



TABLES = {
    "users": (
        "id", "telegram_id", "username", "display_name",
        "level", "xp", "streak", "last_study_date", "created_at",
    ),
    "groups": (
        "id", "name", "invite_code", "created_by", "created_at",
    ),
    "memberships": (
        "id", "user_id", "group_id", "role", "joined_at",
    ),
    "answer_logs": (
        "id", "user_id", "exercise_type", "item_key",
        "given_answer", "is_correct", "created_at",
    ),
    "word_progress": (
        "id", "user_id", "word_key", "repetitions",
        "interval_days", "due_at",
    ),
    "user_lesson_progress": (
        "id", "user_id", "lesson_key", "completed_at",
    ),
}


def main():
    settings = load_settings()

    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is missing.")

    source = sqlite3.connect(settings.database_path)
    source.row_factory = sqlite3.Row

    try:
        source_counts = {
            table: source.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            for table in TABLES
        }

        print("SQLite source:")
        for table, count in source_counts.items():
            print(f"  {table}: {count}")

        with psycopg.connect(
            settings.database_url,
            connect_timeout=15,
        ) as target:
            with target.cursor() as cursor:

                target_counts = {}
                for table in TABLES:
                    cursor.execute(
                        f"SELECT COUNT(*) FROM {table}"
                    )
                    target_counts[table] = cursor.fetchone()[0]

                if any(target_counts.values()):
                    raise RuntimeError(
                        "Migration stopped: PostgreSQL is not empty."
                    )

                for table, columns in TABLES.items():
                    column_sql = ", ".join(columns)
                    placeholders = ", ".join(
                        ["%s"] * len(columns)
                    )

                    rows = source.execute(
                        f"SELECT {column_sql} FROM {table}"
                    ).fetchall()

                    if rows:
                        query = (
                            f"INSERT INTO {table} "
                            f"({column_sql}) VALUES ({placeholders})"
                        )
                        cursor.executemany(
                            query,
                            [tuple(row) for row in rows],
                        )

                    print(f"Transferred {table}: {len(rows)}")

                for table in TABLES:
                    cursor.execute(
                        f"""
                        SELECT setval(
                            pg_get_serial_sequence(
                                'public.{table}', 'id'
                            ),
                            COALESCE(MAX(id), 1),
                            MAX(id) IS NOT NULL
                        )
                        FROM {table}
                        """
                    )

                for table, expected in source_counts.items():
                    cursor.execute(
                        f"SELECT COUNT(*) FROM {table}"
                    )
                    actual = cursor.fetchone()[0]

                    if actual != expected:
                        raise RuntimeError(
                            f"Verification failed for {table}"
                        )

        print("\nMIGRATION SUCCESSFUL")

    finally:
        source.close()


if __name__ == "__main__":
    main()


