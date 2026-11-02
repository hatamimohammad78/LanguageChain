from telegram import InlineKeyboardButton, InlineKeyboardMarkup

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗣 مکالمه روزمره", callback_data="menu:conversation")],
        [InlineKeyboardButton("📚 واژگان", callback_data="menu:words"),
         InlineKeyboardButton("🧠 گرامر", callback_data="menu:grammar")],
        [InlineKeyboardButton("✍️ آزمون هوشمند", callback_data="menu:quiz"),
         InlineKeyboardButton("🔁 مرور روزانه", callback_data="menu:review")],
        [InlineKeyboardButton("📈 داشبورد من", callback_data="menu:stats"),
         InlineKeyboardButton("👥 گروه‌های یادگیری", callback_data="menu:groups")],
        [InlineKeyboardButton("🎯 تعیین سطح", callback_data="menu:placement"),
         InlineKeyboardButton("✨ راهنمای مسیر", callback_data="menu:help")],
    ])


def levels_keyboard(prefix):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(level, callback_data=f"{prefix}:{level}")]
        for level in LEVELS
    ] + [[InlineKeyboardButton("⬅️ بازگشت به خانه", callback_data="menu:home")]])


def options_keyboard(prefix, index, options):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(opt, callback_data=f"{prefix}:{index}:{i}")]
        for i, opt in enumerate(options)
    ] + [[InlineKeyboardButton("✕ خروج از تمرین", callback_data="menu:home")]])


def word_keyboard(key):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ بلدم", callback_data=f"word:known:{key}"),
        InlineKeyboardButton("🔁 مرور بیشتر", callback_data=f"word:review:{key}"),
    ], [InlineKeyboardButton("🏠 خانه", callback_data="menu:home")]])


def back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ بازگشت به خانه", callback_data="menu:home")]])


def conversation_categories(conversations, page=0):
    page_size = 8
    total_pages = max(1, (len(conversations) + page_size - 1) // page_size)
    page = max(0, min(page, total_pages - 1))
    start = page * page_size
    rows = []
    for item in conversations[start:start + page_size]:
        rows.append([InlineKeyboardButton(
            f"{item['title']} · {item['level']}",
            callback_data=f"conv:start:{item['id']}"
        )])
    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"conv:page:{page - 1}"))
    if page + 1 < total_pages:
        navigation.append(InlineKeyboardButton("بعدی ➡️", callback_data=f"conv:page:{page + 1}"))
    if navigation:
        rows.append(navigation)
    rows.append([InlineKeyboardButton(f"صفحه {page + 1} از {total_pages}", callback_data="conv:page:0")])
    rows.append([InlineKeyboardButton("🏠 خانه", callback_data="menu:home")])
    return InlineKeyboardMarkup(rows)


def conversation_continue():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 تمرین دوباره", callback_data="menu:conversation")],
        [InlineKeyboardButton("🏠 خانه", callback_data="menu:home")],
    ])
