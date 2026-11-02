from datetime import datetime, timedelta, timezone
from app.database.db import now_iso


class Repository:
    def __init__(self, db):
        self.db = db

    def get_or_create_user(self, telegram_id, username, display_name):
        with self.db.transaction() as c:
            row = c.execute(
                "SELECT * FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()

            if row:
                c.execute(
                    "UPDATE users SET username=?, display_name=? WHERE telegram_id=?",
                    (username, (display_name or "Learner")[:64], telegram_id),
                )
                row = c.execute(
                    "SELECT * FROM users WHERE telegram_id=?",
                    (telegram_id,),
                ).fetchone()
                return dict(row), False

            c.execute(
                "INSERT INTO users(telegram_id, username, display_name, created_at) VALUES(?,?,?,?)",
                (telegram_id, username, (display_name or "Learner")[:64], now_iso()),
            )
            row = c.execute(
                "SELECT * FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()
            return dict(row), True

    def get_user(self, telegram_id):
        with self.db.connect() as c:
            row = c.execute(
                "SELECT * FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()
            return dict(row) if row else None

    def set_level(self, telegram_id, level):
        with self.db.transaction() as c:
            c.execute(
                "UPDATE users SET level=? WHERE telegram_id=?",
                (level, telegram_id),
            )

    def add_xp(self, telegram_id, amount):
        today = datetime.now(timezone.utc).date().isoformat()

        with self.db.transaction() as c:
            row = c.execute(
                "SELECT xp, streak, last_study_date FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()

            if not row:
                return

            streak = row["streak"]
            last = row["last_study_date"]

            if last != today:
                if last:
                    try:
                        previous = datetime.fromisoformat(last).date()
                        current = datetime.fromisoformat(today).date()
                        streak = streak + 1 if (current - previous).days == 1 else 1
                    except ValueError:
                        streak = 1
                else:
                    streak = 1

            c.execute(
                "UPDATE users SET xp=xp+?, streak=?, last_study_date=? WHERE telegram_id=?",
                (amount, streak, today, telegram_id),
            )

    def log_answer(self, telegram_id, exercise_type, item_key, answer, correct):
        with self.db.transaction() as c:
            user = c.execute(
                "SELECT id FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()

            if user:
                c.execute(
                    """INSERT INTO answer_logs
                    (user_id, exercise_type, item_key, given_answer, is_correct, created_at)
                    VALUES(?,?,?,?,?,?)""",
                    (user["id"], exercise_type, item_key, str(answer), int(correct), now_iso()),
                )

    def stats(self, telegram_id):
        with self.db.connect() as c:
            user = c.execute(
                "SELECT * FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()

            if not user:
                return None

            counts = c.execute(
                "SELECT COUNT(*) total, SUM(is_correct) correct FROM answer_logs WHERE user_id=?",
                (user["id"],),
            ).fetchone()

            completed = c.execute(
                "SELECT COUNT(*) n FROM user_lesson_progress WHERE user_id=?",
                (user["id"],),
            ).fetchone()["n"]

            return {
                "xp": user["xp"],
                "streak": user["streak"],
                "level": user["level"] or "تعیین نشده",
                "total": counts["total"] or 0,
                "correct": counts["correct"] or 0,
                "lessons": completed,
            }

    def due_words(self, telegram_id, limit=10):
        now = now_iso()

        with self.db.connect() as c:
            user = c.execute(
                "SELECT id FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()

            if not user:
                return []

            rows = c.execute(
                """SELECT word_key, repetitions FROM word_progress
                WHERE user_id=? AND due_at<=? ORDER BY due_at LIMIT ?""",
                (user["id"], now, limit),
            ).fetchall()

            return [dict(row) for row in rows]

    def review_word(self, telegram_id, word_key, remembered):
        with self.db.transaction() as c:
            user = c.execute(
                "SELECT id FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()

            if not user:
                return

            row = c.execute(
                "SELECT * FROM word_progress WHERE user_id=? AND word_key=?",
                (user["id"], word_key),
            ).fetchone()

            reps = (row["repetitions"] if row else 0) + (1 if remembered else 0)
            interval = (
                (1 if reps <= 1 else 3 if reps == 2 else min(30, 3 * (2 ** (reps - 2))))
                if remembered else 0
            )
            due = (
                datetime.now(timezone.utc) + timedelta(days=interval or 1)
            ).isoformat(timespec="seconds")

            if row:
                c.execute(
                    """UPDATE word_progress
                    SET repetitions=?, interval_days=?, due_at=? WHERE id=?""",
                    (reps, interval, due, row["id"]),
                )
            else:
                c.execute(
                    """INSERT INTO word_progress
                    (user_id, word_key, repetitions, interval_days, due_at)
                    VALUES(?,?,?,?,?)""",
                    (user["id"], word_key, reps, interval, due),
                )

    def save_lesson(self, telegram_id, lesson_key):
        with self.db.transaction() as c:
            user = c.execute(
                "SELECT id FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()

            if user:
                c.execute(
                    """INSERT INTO user_lesson_progress
                    (user_id, lesson_key, completed_at)
                    VALUES(?,?,?) ON CONFLICT(user_id, lesson_key) DO NOTHING""",
                    (user["id"], lesson_key, now_iso()),
                )

    def create_group(self, telegram_id, name, code):
        with self.db.transaction() as c:
            user = c.execute(
                "SELECT id FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()

            if not user:
                return None

            query = (
                "INSERT INTO groups(name,invite_code,created_by,created_at) "
                "VALUES(?,?,?,?)"
            )

            params = (name[:64], code, user["id"], now_iso())

            if self.db.is_postgres:
                group_id = c.execute(
                    query + " RETURNING id",
                    params,
                ).fetchone()["id"]
            else:
                cursor = c.execute(query, params)
                group_id = cursor.lastrowid

            c.execute(
                "INSERT INTO memberships(user_id,group_id,role,joined_at) VALUES(?,?,?,?)",
                (user["id"], group_id, "admin", now_iso()),
            )

            return code

    def join_group(self, telegram_id, code):
        with self.db.transaction() as c:
            user = c.execute(
                "SELECT id FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()

            group = c.execute(
                "SELECT id FROM groups WHERE invite_code=?",
                (code.upper(),),
            ).fetchone()

            if not user or not group:
                return False, "کد گروه پیدا نشد."

            exists = c.execute(
                "SELECT 1 FROM memberships WHERE user_id=? AND group_id=?",
                (user["id"], group["id"]),
            ).fetchone()

            if exists:
                return True, "از قبل عضو این گروه هستی."

            c.execute(
                "INSERT INTO memberships(user_id,group_id,role,joined_at) VALUES(?,?,?,?)",
                (user["id"], group["id"], "member", now_iso()),
            )

            return True, "با موفقیت عضو گروه شدی."

    def user_groups(self, telegram_id):
        with self.db.connect() as c:
            user = c.execute(
                "SELECT id FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()

            if not user:
                return []

            rows = c.execute(
                """SELECT g.name,g.invite_code,m.role,
                (SELECT COUNT(*) FROM memberships mm WHERE mm.group_id=g.id) members
                FROM memberships m JOIN groups g ON g.id=m.group_id
                WHERE m.user_id=? ORDER BY g.id DESC""",
                (user["id"],),
            ).fetchall()

            return [dict(row) for row in rows]

    def group_members(self, telegram_id, code):
        with self.db.connect() as c:
            user = c.execute(
                "SELECT id FROM users WHERE telegram_id=?",
                (telegram_id,),
            ).fetchone()

            group = c.execute(
                "SELECT id,name FROM groups WHERE invite_code=?",
                (code.upper(),),
            ).fetchone()

            if not user or not group:
                return None

            member = c.execute(
                "SELECT 1 FROM memberships WHERE user_id=? AND group_id=?",
                (user["id"], group["id"]),
            ).fetchone()

            if not member:
                return None

            rows = c.execute(
                """SELECT u.display_name,u.level,u.xp
                FROM memberships m JOIN users u ON u.id=m.user_id
                WHERE m.group_id=? ORDER BY u.xp DESC""",
                (group["id"],),
            ).fetchall()

            return group["name"], [dict(row) for row in rows]
