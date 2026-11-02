import logging
import re
import secrets
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.bot.keyboards import (main_menu, levels_keyboard, options_keyboard, word_keyboard, back_keyboard, conversation_categories, conversation_continue)
from app.learning.service import (
    words_for_level, grammar_for_level, questions_for_level,
    placement_questions, placement_level, placement_level_from_breakdown, find_word, conversations_for_level, conversation_by_id,
)
from app.content import CONVERSATIONS

log = logging.getLogger(__name__)

def progress_bar(value, maximum=100, width=10):
    ratio = max(0, min(1, value / maximum)) if maximum else 0
    filled = round(ratio * width)
    return "▰" * filled + "▱" * (width - filled)

def dashboard_text(user, stats):
    level = (user or {}).get("level") or "تعیین‌نشده"
    xp = stats["xp"] if stats else 0
    streak = stats["streak"] if stats else 0
    accuracy = round(stats["correct"] / stats["total"] * 100) if stats and stats["total"] else 0
    return (
        "✦  L A N G U A G E C H A I N  ✦\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"سلام {((user or {}).get('display_name') or 'زبان‌آموز')}، خوش اومدی! 👋\n\n"
        "مسیر یادگیری انگلیسی تو از اینجا ادامه پیدا می‌کنه.\n\n"
        "╭─── ✧ پروفایل یادگیری ✧ ───╮\n"
        f"  سطح فعلی: {level}\n"
        f"  امتیاز تجربه: {xp} XP\n"
        f"  دقت تمرین‌ها: {accuracy}%\n"
        f"  تداوم مطالعه: {streak} روز 🔥\n"
        f"  پیشرفت تا ۱۰۰ XP بعدی: {progress_bar(xp % 100) }\n"
        "╰────────────────────╯\n\n"
        "از مسیرهای زیر انتخاب کن و قدم‌به‌قدم پیش برو. 🌱"
    )

def repo(context):
    return context.application.bot_data["repo"]

async def send_home(update: Update, context: ContextTypes.DEFAULT_TYPE, text=None):
    message = update.effective_message
    if message:
        await message.reply_text(text or "از منوی زیر یکی از بخش‌ها رو انتخاب کن:", reply_markup=main_menu())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg = update.effective_user
    user, created = repo(context).get_or_create_user(tg.id, tg.username, tg.full_name)
    stats = repo(context).stats(tg.id)
    await update.effective_message.reply_text(dashboard_text(user, stats), reply_markup=main_menu())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "راهنمای LanguageChain\n\n"
        "/start — منوی اصلی\n"
        "/join CODE — عضویت در گروه با کد دعوت\n"
        "/groups — نمایش گروه‌های من\n"
        "/help — راهنما\n\n"
        "از دکمه‌های منو برای درس، آزمون، مرور و مشاهده پیشرفت استفاده کن."
    )
    await update.effective_message.reply_text(text, reply_markup=main_menu())

async def groups_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    groups = repo(context).user_groups(update.effective_user.id)
    if not groups:
        await update.effective_message.reply_text(
            "هنوز عضو گروهی نیستی. از منوی «گروه‌ها» یک گروه بساز یا با /join CODE عضو شو.",
            reply_markup=main_menu(),
        )
        return
    lines = ["👥 گروه‌های تو:"]
    for g in groups:
        lines.append(f"• {g['name']} | کد: {g['invite_code']} | اعضا: {g['members']}")
    await update.effective_message.reply_text("\n".join(lines), reply_markup=main_menu())

async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("فرمت دستور:\n/join CODE")
        return
    ok, msg = repo(context).join_group(update.effective_user.id, context.args[0].strip())
    await update.effective_message.reply_text(msg, reply_markup=main_menu())

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    user_id = update.effective_user.id
    r = repo(context)

    if data == "menu:home":
        context.user_data.pop("conversation", None)
        user = r.get_user(user_id)
        stats = r.stats(user_id)
        await query.edit_message_text(dashboard_text(user, stats), reply_markup=main_menu())
        return
    if data == "menu:help":
        await query.edit_message_text(
            "از این ربات می‌تونی برای یادگیری لغت و گرامر، آزمون، مرور و گروه‌های دوستانه استفاده کنی.\n\n"
            "برای عضویت در گروه: /join CODE",
            reply_markup=back_keyboard(),
        )
        return
    if data == "menu:placement":
        context.user_data["placement"] = {"index": 0, "score": 0, "by_level": {level: 0 for level in ("A1", "A2", "B1", "B2", "C1", "C2")}}
        q = placement_questions()[0]
        await query.edit_message_text(
            f"🎯 آزمون تعیین سطح (۱ از ۳۰)\n\n{q['question']}",
            reply_markup=options_keyboard("place", 0, q["options"]),
        )
        return
    if data.startswith("place:"):
        _, idx_s, opt_s = data.split(":")
        idx, opt = int(idx_s), int(opt_s)
        qs = placement_questions()
        state = context.user_data.get("placement", {"index": 0, "score": 0})
        if idx != state["index"]:
            await query.answer("این سؤال قبلاً پاسخ داده شده یا منقضی شده.", show_alert=True)
            return
        q = qs[idx]
        if opt == q["answer"]:
            state["score"] += 1
            state.setdefault("by_level", {}).setdefault(q["level"], 0)
            state["by_level"][q["level"]] += 1
        state["index"] += 1
        if state["index"] >= len(qs):
            level = placement_level_from_breakdown(state.get("by_level", {}))
            r.set_level(user_id, level)
            context.user_data.pop("placement", None)
            await query.edit_message_text(
                f"نتیجه تعیین سطح تو: {level} 🌟\n"
                f"پاسخ درست: {state['score']} از {len(qs)}\n"
                f"تفکیک پاسخ‌ها: " + " | ".join(f"{band}: {state.get('by_level', {}).get(band, 0)}/5" for band in ("A1", "A2", "B1", "B2", "C1", "C2")) + "\n\n"
                "این آزمون ۳۰ سؤالی تخمین اولیه است و جایگزین آزمون استاندارد CEFR یا ارزیابی چهار مهارت نیست.",
                reply_markup=main_menu(),
            )
        else:
            context.user_data["placement"] = state
            next_q = qs[state["index"]]
            await query.edit_message_text(
                f"🎯 آزمون تعیین سطح ({state['index'] + 1} از {len(qs)})\n\n{next_q['question']}",
                reply_markup=options_keyboard("place", state["index"], next_q["options"]),
            )
        return

    if data == "menu:conversation":
        user = r.get_user(user_id)
        level = user["level"] if user and user["level"] else None
        items = conversations_for_level(level) if level else CONVERSATIONS
        await query.edit_message_text(
            "🗣  تمرین مکالمه واقعی\n━━━━━━━━━━━━━━━━━━━━\n"
            "یک موقعیت روزمره انتخاب کن. نقش طرف مقابل را من بازی می‌کنم و تو با انگلیسی جواب می‌دهی.\n\n"
            "سطح مکالمه‌ها از A1 تا C2 طراحی شده و برای هر پاسخ، راهنمایی و نمونه طبیعی می‌بینی.\n\n"
            "📌 نکته: ارزیابی پاسخ‌ها در این نسخه بر اساس عبارت‌های کلیدی است، نه داوری هوش مصنوعی.",
            reply_markup=conversation_categories(items),
        )
        return
    if data.startswith("conv:page:"):
        page = int(data.split(":")[2])
        user = r.get_user(user_id)
        level = user["level"] if user and user["level"] else None
        items = conversations_for_level(level) if level else CONVERSATIONS
        await query.edit_message_text(
            "🗣  تمرین مکالمه واقعی\n━━━━━━━━━━━━━━━━━━━━\n"
            "یک موقعیت را انتخاب کن. پاسخ‌ها را به انگلیسی بنویس.\n"
            "برای دیدن موقعیت‌های بیشتر از دکمه‌های صفحه‌بندی استفاده کن.",
            reply_markup=conversation_categories(items, page),
        )
        return

    if data.startswith("conv:start:"):
        conversation_id = data.split(":", 2)[2]
        item = conversation_by_id(conversation_id)
        if not item:
            await query.edit_message_text("این سناریو پیدا نشد.", reply_markup=back_keyboard())
            return
        context.user_data["conversation"] = {"id": conversation_id, "index": 0, "matched": 0}
        first = item["turns"][0]
        await query.edit_message_text(
            f"🗣 {item['title']}  ·  {item['level']}\n━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 موقعیت: {item['situation']}\n\n"
            f"🤝 طرف مقابل: {first['npc']}\n\n"
            f"💡 راهنما: {first['hint']}\n\n"
            "✍️ حالا پاسخ خودت را به انگلیسی در چت بنویس.",
            reply_markup=back_keyboard(),
        )
        return

    if data == "menu:words":
        user = r.get_user(user_id)
        level = user["level"] if user and user["level"] else "A1"
        await query.edit_message_text("سطح درس لغت را انتخاب کن:", reply_markup=levels_keyboard("words"))
        return
    if data.startswith("words:"):
        level = data.split(":")[1]
        words = words_for_level(level)
        context.user_data["word_lesson"] = {"level": level, "index": 0}
        await show_word(query, context, words, 0)
        return
    if data.startswith("word:"):
        _, action, key = data.split(":", 2)
        word = find_word(key)
        if action in ("known", "review"):
            r.review_word(user_id, key, action == "known")
            r.add_xp(user_id, 2 if action == "known" else 1)
            state = context.user_data.get("word_lesson")
            if state:
                words = words_for_level(state["level"])
                next_index = state["index"] + 1
                if next_index < len(words):
                    state["index"] = next_index
                    await show_word(query, context, words, next_index)
                else:
                    r.save_lesson(user_id, f"vocab_{state['level']}")
                    context.user_data.pop("word_lesson", None)
                    await query.edit_message_text("آفرین! درس لغت این سطح تمام شد. 🎉", reply_markup=main_menu())
            else:
                await query.edit_message_text("کلمه برای مرور ثبت شد.", reply_markup=main_menu())
        return

    if data == "menu:grammar":
        await query.edit_message_text("سطح گرامر را انتخاب کن:", reply_markup=levels_keyboard("grammar"))
        return
    if data.startswith("grammar:"):
        level = data.split(":")[1]
        lessons = grammar_for_level(level)
        if not lessons:
            await query.edit_message_text("درسی برای این سطح پیدا نشد.", reply_markup=back_keyboard())
            return
        context.user_data["grammar_lessons"] = {"level": level, "index": 0}
        await show_grammar(query, context, lessons, 0)
        return
    if data.startswith("gram:"):
        _, action, index_s = data.split(":")
        state = context.user_data.get("grammar_lessons")
        if not state:
            await query.edit_message_text("این درس منقضی شده است.", reply_markup=main_menu())
            return
        lessons = grammar_for_level(state["level"])
        if action == "next":
            next_index = int(index_s)
            if next_index >= len(lessons):
                r.save_lesson(user_id, f"grammar_{state['level']}")
                r.add_xp(user_id, 5)
                context.user_data.pop("grammar_lessons", None)
                await query.edit_message_text("درس گرامر تمام شد. +۵ امتیاز 🌟", reply_markup=main_menu())
            else:
                state["index"] = next_index
                await show_grammar(query, context, lessons, next_index)
        return

    if data == "menu:quiz":
        user = r.get_user(user_id)
        level = user["level"] if user and user["level"] else "A1"
        context.user_data["quiz"] = {"questions": questions_for_level(level), "index": 0, "score": 0}
        await show_quiz_question(query, context)
        return
    if data.startswith("quiz:"):
        _, idx_s, opt_s = data.split(":")
        state = context.user_data.get("quiz")
        if not state or int(idx_s) != state["index"]:
            await query.answer("این آزمون منقضی شده است.", show_alert=True)
            return
        idx, opt = int(idx_s), int(opt_s)
        q = state["questions"][idx]
        correct = opt == q["answer"]
        if correct:
            state["score"] += 1
            r.add_xp(user_id, 5)
        r.log_answer(user_id, "quiz", f"{q['level']}:{idx}", q["options"][opt], correct)
        state["index"] += 1
        if state["index"] >= len(state["questions"]):
            score = state["score"]
            total = len(state["questions"])
            context.user_data.pop("quiz", None)
            await query.edit_message_text(
                f"آزمون تمام شد! 🎉\nنتیجه: {score} از {total}\n"
                f"امتیاز کسب‌شده: {score * 5} XP",
                reply_markup=main_menu(),
            )
        else:
            feedback = ("✅ پاسخ درست بود!\n" if correct else f"❌ پاسخ درست: {q['options'][q['answer']]}\n") + q["explanation"]
            await show_quiz_question(query, context, feedback=feedback)
        return

    if data == "menu:review":
        due = r.due_words(user_id)
        if not due:
            await query.edit_message_text(
                "فعلاً کلمه‌ای برای مرور زمان‌بندی نشده. از بخش درس لغت چند کلمه مطالعه کن.",
                reply_markup=main_menu(),
            )
            return
        context.user_data["review_queue"] = [x["word_key"] for x in due]
        await show_review(query, context, 0)
        return
    if data.startswith("review:"):
        _, action, index_s = data.split(":")
        queue = context.user_data.get("review_queue", [])
        idx = int(index_s)
        if idx >= len(queue):
            await query.edit_message_text("مرور امروز تمام شد. آفرین! 🌟", reply_markup=main_menu())
            return
        key = queue[idx]
        r.review_word(user_id, key, action == "known")
        r.add_xp(user_id, 2 if action == "known" else 1)
        next_idx = idx + 1
        if next_idx >= len(queue):
            context.user_data.pop("review_queue", None)
            await query.edit_message_text("مرور امروز تمام شد. آفرین! 🌟", reply_markup=main_menu())
        else:
            await show_review(query, context, next_idx)
        return

    if data == "menu:stats":
        s = r.stats(user_id)
        if not s:
            await query.edit_message_text("ابتدا /start را بزن.", reply_markup=main_menu())
            return
        accuracy = round((s["correct"] / s["total"]) * 100) if s["total"] else 0
        await query.edit_message_text(
            "📊 گزارش پیشرفت تو\n\n"
            f"سطح: {s['level']}\nXP: {s['xp']}\nروزهای متوالی مطالعه: {s['streak']}\n"
            f"تعداد پاسخ‌ها: {s['total']}\nپاسخ درست: {s['correct']}\n"
            f"دقت آزمون‌ها: {accuracy}%\nدرس‌های تکمیل‌شده: {s['lessons']}",
            reply_markup=main_menu(),
        )
        return
    if data == "menu:groups":
        groups = r.user_groups(user_id)
        rows = [
            [InlineKeyboardButton("➕ ساخت گروه جدید", callback_data="group:create")],
            [InlineKeyboardButton("📈 مشاهده گروه‌ها", callback_data="group:list")],
        ]
        await query.edit_message_text(
            "بخش گروه‌ها\n\nبرای عضویت در گروه دیگران از دستور /join CODE استفاده کن.",
            reply_markup=InlineKeyboardMarkup(rows + [[InlineKeyboardButton("⬅️ منوی اصلی", callback_data="menu:home")]]),
        )
        return
    if data == "group:create":
        code = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))
        user = r.get_user(user_id)
        name = f"گروه {user['display_name'][:30]}"
        code = r.create_group(user_id, name, code)
        await query.edit_message_text(
            f"گروه ساخته شد! 🎉\n\nنام: {name}\nکد دعوت: `{code}`\n\n"
            f"دوستانت می‌توانند با دستور زیر عضو شوند:\n`/join {code}`",
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )
        return
    if data == "group:list":
        groups = r.user_groups(user_id)
        if not groups:
            await query.edit_message_text("هنوز عضو گروهی نیستی.", reply_markup=main_menu())
            return
        rows = []
        for g in groups:
            rows.append([InlineKeyboardButton(f"{g['name']} ({g['members']} نفر)", callback_data=f"group:show:{g['invite_code']}")])
        rows.append([InlineKeyboardButton("⬅️ منوی اصلی", callback_data="menu:home")])
        await query.edit_message_text("گروه‌های تو:", reply_markup=InlineKeyboardMarkup(rows))
        return
    if data.startswith("group:show:"):
        code = data.split(":")[2]
        result = r.group_members(user_id, code)
        if not result:
            await query.edit_message_text("گروه پیدا نشد یا عضو آن نیستی.", reply_markup=main_menu())
            return
        name, members = result
        lines = [f"👥 {name}", ""]
        for i, member in enumerate(members, 1):
            lines.append(f"{i}. {member['display_name']} | {member['level'] or 'بدون سطح'} | {member['xp']} XP")
        await query.edit_message_text("\n".join(lines), reply_markup=back_keyboard())
        return

async def show_word(query, context, words, index):
    if index >= len(words):
        await query.edit_message_text("درس تمام شد.", reply_markup=main_menu())
        return
    w = words[index]
    text = (
        f"📚 واژه‌نامه  ·  {w['level']}\n"
        f"پیشرفت درس: {progress_bar(index + 1, len(words), 12)}  {index + 1}/{len(words)}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"✦ {w['word']}\n"
        f"نوع واژه: {w['pos']}\n"
        f"معنی: {w['meaning']}\n\n"
        f"📝 مثال کاربردی:\n{w['example']}\n\n"
        f"موضوع: {w.get('topic', 'عمومی')}"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=word_keyboard(w["key"]))

async def show_grammar(query, context, lessons, index):
    lesson = lessons[index]
    text = (
        f"🧠 آکادمی گرامر  ·  {lesson.get('level', '')}\n"
        f"پیشرفت فصل: {progress_bar(index + 1, len(lessons), 12)}  {index + 1}/{len(lessons)}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"✦ {lesson['title']}\n\n"
        f"📖 توضیح: {lesson['explanation']}\n\n"
        f"🧩 ساختار: {lesson.get('structure', 'به مثال توجه کن.')}\n\n"
        f"✅ مثال: {lesson['example']}\n\n"
        f"⚠️ نکته: {lesson.get('mistake', 'به ترتیب کلمات دقت کن.')}"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("ادامه درس ➡️", callback_data=f"gram:next:{index+1}")
    ], [InlineKeyboardButton("⬅️ منوی اصلی", callback_data="menu:home")]])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def show_quiz_question(query, context, feedback=None):
    state = context.user_data.get("quiz")
    if not state:
        return
    idx = state["index"]
    q = state["questions"][idx]
    prefix = (feedback + "\n\n━━━━━━━━━━━━━━━━━━━━\n") if feedback else ""
    await query.edit_message_text(
        prefix + f"✍️ آزمون  ·  سؤال {idx + 1} از {len(state['questions'])}\n\n{q['question']}",
        reply_markup=options_keyboard("quiz", idx, q["options"]),
    )

async def show_review(query, context, index):
    queue = context.user_data.get("review_queue", [])
    if index >= len(queue):
        await query.edit_message_text("مرور امروز تمام شد.", reply_markup=main_menu())
        return
    word = find_word(queue[index])
    if not word:
        await show_review(query, context, index + 1)
        return
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("بلدم", callback_data=f"review:known:{index}"),
        InlineKeyboardButton("یادم نبود", callback_data=f"review:again:{index}"),
    ]])
    await query.edit_message_text(
        f"🔁 مرور {index + 1} از {len(queue)}\n\n"
        f"**{word['word']}**\nمعنی: {word['meaning']}\nمثال: _{word['example']}_",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("conversation", None)
    await update.effective_message.reply_text("تمرین مکالمه متوقف شد.", reply_markup=main_menu())


async def conversation_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("conversation")
    if not state or not update.effective_message or not update.effective_message.text:
        return
    answer = update.effective_message.text.strip()
    if answer.lower() in {"/cancel", "لغو", "خروج"}:
        context.user_data.pop("conversation", None)
        await update.effective_message.reply_text("تمرین مکالمه متوقف شد.", reply_markup=main_menu())
        return
    item = conversation_by_id(state["id"])
    if not item:
        context.user_data.pop("conversation", None)
        return
    index = state["index"]
    turn = item["turns"][index]
    normalized = " ".join(re.sub(r"[^a-z0-9\s]", " ", answer.lower()).split())
    matched = any(
        " ".join(re.sub(r"[^a-z0-9\s]", " ", keyword.lower()).split()) in normalized
        for keyword in turn["keywords"]
    )
    if matched:
        state["matched"] += 1
        repo(context).add_xp(update.effective_user.id, 3)
        repo(context).log_answer(update.effective_user.id, "conversation", f"{item['id']}:{index}", answer, True)
        feedback = "🌟 عالی! پاسخ تو یکی از عبارت‌های مناسب این موقعیت را داشت."
    else:
        repo(context).add_xp(update.effective_user.id, 1)
        repo(context).log_answer(update.effective_user.id, "conversation", f"{item['id']}:{index}", answer, False)
        feedback = "👍 تلاش خوبی بود. برای طبیعی‌تر شدن پاسخ، به نمونه زیر توجه کن."
    next_index = index + 1
    if next_index >= len(item["turns"]):
        total = len(item["turns"])
        matched_count = state["matched"]
        context.user_data.pop("conversation", None)
        await update.effective_message.reply_text(
            f"{feedback}\n\n💬 نمونه پیشنهادی: {turn['sample']}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🏁 مکالمه «{item['title']}» تمام شد!\n"
            f"پاسخ‌های منطبق با عبارت‌های کلیدی: {matched_count} از {total}\n"
            "برای بهتر شدن، همین سناریو را دوباره تمرین کن یا یک موقعیت دیگر انتخاب کن. 🌱",
            reply_markup=conversation_continue(),
        )
        return
    state["index"] = next_index
    next_turn = item["turns"][next_index]
    await update.effective_message.reply_text(
        f"{feedback}\n\n💬 نمونه طبیعی: {turn['sample']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🤝 طرف مقابل: {next_turn['npc']}\n\n"
        f"💡 راهنما: {next_turn['hint']}\n\n"
        "✍️ پاسخ بعدی را به انگلیسی بنویس. (برای خروج بنویس: لغو)"
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.exception("Unhandled bot error", exc_info=context.error)
