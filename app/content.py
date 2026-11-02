"""Starter curriculum. Content is data-driven so lessons can grow without changing bot logic."""

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

VOCABULARY = [
    # A1
    {"key":"a1_hello","level":"A1","word":"hello","pos":"interjection","meaning":"سلام","example":"Hello, how are you?"},
    {"key":"a1_water","level":"A1","word":"water","pos":"noun","meaning":"آب","example":"I drink water every day."},
    {"key":"a1_family","level":"A1","word":"family","pos":"noun","meaning":"خانواده","example":"My family is small."},
    {"key":"a1_book","level":"A1","word":"book","pos":"noun","meaning":"کتاب","example":"This is my book."},
    {"key":"a1_happy","level":"A1","word":"happy","pos":"adjective","meaning":"خوشحال","example":"She is happy today."},
    {"key":"a1_work","level":"A1","word":"work","pos":"verb","meaning":"کار کردن","example":"I work in a shop."},
    # A2
    {"key":"a2_healthy","level":"A2","word":"healthy","pos":"adjective","meaning":"سالم","example":"Walking is a healthy habit."},
    {"key":"a2_invite","level":"A2","word":"invite","pos":"verb","meaning":"دعوت کردن","example":"I want to invite my friends."},
    {"key":"a2_crowded","level":"A2","word":"crowded","pos":"adjective","meaning":"شلوغ","example":"The bus is crowded."},
    {"key":"a2_improve","level":"A2","word":"improve","pos":"verb","meaning":"بهبود دادن","example":"I want to improve my English."},
    {"key":"a2_weather","level":"A2","word":"weather","pos":"noun","meaning":"آب‌وهوا","example":"The weather is cold today."},
    {"key":"a2_usually","level":"A2","word":"usually","pos":"adverb","meaning":"معمولاً","example":"I usually get up early."},
    # B1
    {"key":"b1_achieve","level":"B1","word":"achieve","pos":"verb","meaning":"دستیابی پیدا کردن","example":"You can achieve your goals."},
    {"key":"b1_avoid","level":"B1","word":"avoid","pos":"verb","meaning":"اجتناب کردن","example":"Try to avoid making the same mistake."},
    {"key":"b1_confident","level":"B1","word":"confident","pos":"adjective","meaning":"بااعتمادبه‌نفس","example":"She feels confident speaking English."},
    {"key":"b1_decision","level":"B1","word":"decision","pos":"noun","meaning":"تصمیم","example":"It was a difficult decision."},
    {"key":"b1_effort","level":"B1","word":"effort","pos":"noun","meaning":"تلاش","example":"Learning takes time and effort."},
    {"key":"b1_reliable","level":"B1","word":"reliable","pos":"adjective","meaning":"قابل اعتماد","example":"He is a reliable colleague."},
    # B2
    {"key":"b2_assume","level":"B2","word":"assume","pos":"verb","meaning":"فرض کردن","example":"I assumed the meeting was cancelled."},
    {"key":"b2_consequence","level":"B2","word":"consequence","pos":"noun","meaning":"پیامد","example":"Every choice has a consequence."},
    {"key":"b2_establish","level":"B2","word":"establish","pos":"verb","meaning":"تأسیس کردن؛ برقرار کردن","example":"They established a new company."},
    {"key":"b2_maintain","level":"B2","word":"maintain","pos":"verb","meaning":"حفظ کردن","example":"It is hard to maintain focus."},
    {"key":"b2_significant","level":"B2","word":"significant","pos":"adjective","meaning":"قابل توجه","example":"There was a significant change."},
    {"key":"b2_tend","level":"B2","word":"tend","pos":"verb","meaning":"تمایل داشتن","example":"People tend to learn from experience."},
    # C1
    {"key":"c1_ambiguous","level":"C1","word":"ambiguous","pos":"adjective","meaning":"مبهم؛ دوپهلو","example":"The instructions were ambiguous."},
    {"key":"c1_compelling","level":"C1","word":"compelling","pos":"adjective","meaning":"قانع‌کننده؛ بسیار جذاب","example":"She made a compelling argument."},
    {"key":"c1_facilitate","level":"C1","word":"facilitate","pos":"verb","meaning":"تسهیل کردن","example":"The tool can facilitate communication."},
    {"key":"c1_nuance","level":"C1","word":"nuance","pos":"noun","meaning":"ظرافت معنایی","example":"Translation often misses a cultural nuance."},
    {"key":"c1_undermine","level":"C1","word":"undermine","pos":"verb","meaning":"تضعیف کردن","example":"Constant delays undermine trust."},
    {"key":"c1_viable","level":"C1","word":"viable","pos":"adjective","meaning":"عملی؛ امکان‌پذیر","example":"We need a viable solution."},
    # C2
    {"key":"c2_ephemeral","level":"C2","word":"ephemeral","pos":"adjective","meaning":"زودگذر","example":"Fame can be ephemeral."},
    {"key":"c2_equivocal","level":"C2","word":"equivocal","pos":"adjective","meaning":"دوپهلو؛ نامشخص","example":"His response was deliberately equivocal."},
    {"key":"c2_juxtapose","level":"C2","word":"juxtapose","pos":"verb","meaning":"در کنار هم قرار دادن برای مقایسه","example":"The essay juxtaposes two theories."},
    {"key":"c2_obfuscate","level":"C2","word":"obfuscate","pos":"verb","meaning":"مبهم یا پیچیده جلوه دادن","example":"The report seems to obfuscate the issue."},
    {"key":"c2_ostensible","level":"C2","word":"ostensible","pos":"adjective","meaning":"ظاهری؛ ادعایی","example":"The ostensible reason was cost."},
    {"key":"c2_pervasive","level":"C2","word":"pervasive","pos":"adjective","meaning":"فراگیر","example":"Technology has a pervasive influence."},
]

GRAMMAR = {
    "A1": [
        {"key":"a1_be","title":"فعل to be در زمان حال","explanation":"برای معرفی و توصیف از am / is / are استفاده می‌کنیم. I am، He/She/It is، You/We/They are.","example":"She is a student."},
        {"key":"a1_present_simple","title":"حال ساده","explanation":"برای عادت‌ها و واقعیت‌ها از شکل ساده فعل استفاده می‌کنیم. برای he/she/it معمولاً s اضافه می‌شود.","example":"He works every day."},
    ],
    "A2": [
        {"key":"a2_past_simple","title":"گذشته ساده","explanation":"برای کار تمام‌شده در گذشته از فعل گذشته استفاده می‌کنیم؛ افعال باقاعده معمولاً ed می‌گیرند.","example":"We visited London last year."},
        {"key":"a2_comparatives","title":"صفات تفضیلی","explanation":"برای مقایسه دو چیز معمولاً از -er یا more و سپس than استفاده می‌کنیم.","example":"This book is more interesting than that one."},
    ],
    "B1": [
        {"key":"b1_present_perfect","title":"حال کامل","explanation":"ساختار have/has + past participle برای تجربه یا نتیجه مرتبط با زمان حال استفاده می‌شود.","example":"I have finished my homework."},
        {"key":"b1_first_conditional","title":"شرطی نوع اول","explanation":"برای احتمال واقعی در آینده: If + present simple, will + verb.","example":"If it rains, we will stay home."},
    ],
    "B2": [
        {"key":"b2_passive","title":"مجهول","explanation":"در ساختار مجهول، تمرکز روی عمل یا دریافت‌کننده آن است: be + past participle.","example":"The bridge was built in 1990."},
        {"key":"b2_third_conditional","title":"شرطی نوع سوم","explanation":"برای موقعیت فرضی در گذشته: If + past perfect, would have + past participle.","example":"If I had studied, I would have passed."},
    ],
    "C1": [
        {"key":"c1_inversion","title":"وارونگی برای تأکید","explanation":"پس از برخی قیدهای منفی یا محدودکننده در ابتدای جمله، ترتیب کمکی و فاعل جابه‌جا می‌شود.","example":"Never have I seen such a view."},
        {"key":"c1_cleft","title":"جملات شکافته","explanation":"برای تأکید روی بخشی از جمله از ساختارهایی مانند It is/was ... that استفاده می‌کنیم.","example":"It was John who solved the problem."},
    ],
    "C2": [
        {"key":"c2_subjunctive","title":"وجه التزامی رسمی","explanation":"پس از افعالی مانند recommend و insist، در انگلیسی رسمی می‌توان از شکل پایه فعل استفاده کرد.","example":"They recommended that he be present."},
        {"key":"c2_ellipsis","title":"حذف در ساختارهای موازی","explanation":"برای جلوگیری از تکرار، بخش قابل بازیابی جمله را حذف می‌کنیم؛ به شرط آنکه معنا روشن بماند.","example":"She can play the piano, and he can too."},
    ],
}

QUIZ = [
    {"level":"A1","question":"Choose the correct sentence:","options":["She are happy.","She is happy.","She am happy."],"answer":1,"explanation":"برای she از is استفاده می‌کنیم."},
    {"level":"A1","question":"What is the opposite of 'big'?","options":["small","tall","long"],"answer":0,"explanation":"small یعنی کوچک و متضاد big است."},
    {"level":"A1","question":"I ___ a student.","options":["is","am","are"],"answer":1,"explanation":"با I از am استفاده می‌کنیم."},
    {"level":"A2","question":"Yesterday, we ___ to the park.","options":["go","goes","went"],"answer":2,"explanation":"Yesterday زمان گذشته است؛ شکل گذشته go برابر went است."},
    {"level":"A2","question":"This exercise is ___ than the last one.","options":["easy","easier","easiest"],"answer":1,"explanation":"برای مقایسه دو مورد از صفت تفضیلی easier استفاده می‌شود."},
    {"level":"A2","question":"I ___ drink coffee in the morning.","options":["usually","yesterday","tomorrow"],"answer":0,"explanation":"usually برای بیان عادت به معنی معمولاً است."},
    {"level":"B1","question":"I have ___ my keys.","options":["lose","lost","losing"],"answer":1,"explanation":"در حال کامل از have + قسمت سوم فعل استفاده می‌کنیم: lost."},
    {"level":"B1","question":"If I have time, I ___ you.","options":["call","will call","called"],"answer":1,"explanation":"در شرطی نوع اول، نتیجه با will + verb می‌آید."},
    {"level":"B1","question":"Which word means 'to reach a goal'?","options":["avoid","achieve","assume"],"answer":1,"explanation":"achieve یعنی به هدف رسیدن."},
    {"level":"B2","question":"The building ___ in 1920.","options":["built","was built","has build"],"answer":1,"explanation":"جمله مجهول در گذشته: was + past participle."},
    {"level":"B2","question":"She suggested ___ earlier.","options":["leave","to leave","leaving"],"answer":2,"explanation":"پس از suggest معمولاً فعل ing می‌آید."},
    {"level":"B2","question":"What does 'significant' mean?","options":["unimportant","noticeable/important","temporary"],"answer":1,"explanation":"significant یعنی مهم یا قابل توجه."},
    {"level":"C1","question":"___ had we arrived than it started raining.","options":["No sooner","Hardly","Never"],"answer":0,"explanation":"ساختار ثابت No sooner ... than است."},
    {"level":"C1","question":"Choose the closest meaning of 'ambiguous'.","options":["clear","uncertain or having more than one meaning","brief"],"answer":1,"explanation":"ambiguous یعنی مبهم یا دارای چند برداشت."},
    {"level":"C2","question":"The word 'ephemeral' means:","options":["lasting forever","short-lived","extremely complex"],"answer":1,"explanation":"ephemeral یعنی زودگذر و کوتاه‌مدت."},
    {"level":"C2","question":"Choose the best meaning of 'obfuscate'.","options":["clarify","make unclear","simplify"],"answer":1,"explanation":"obfuscate یعنی مبهم یا نامفهوم کردن."},
]

# Expanded CEFR catalog, kept separate so content can be maintained independently.
from app.content_expansion import EXPANDED_VOCABULARY, EXPANDED_GRAMMAR, CONVERSATIONS, EXPANDED_QUIZ
VOCABULARY.extend(EXPANDED_VOCABULARY)
QUIZ.extend(EXPANDED_QUIZ)
for _level, _lessons in EXPANDED_GRAMMAR.items():
    GRAMMAR[_level].extend(_lessons)


# Extended reference curriculum (v2).
from app.content_reference import EXTRA_VOCABULARY, EXTRA_GRAMMAR, EXTRA_CONVERSATIONS, EXTRA_QUIZ
VOCABULARY.extend(EXTRA_VOCABULARY)
QUIZ.extend(EXTRA_QUIZ)
CONVERSATIONS.extend(EXTRA_CONVERSATIONS)
for _level, _lessons in EXTRA_GRAMMAR.items():
    GRAMMAR[_level].extend(_lessons)

# Remove repeated headwords at the same level while preserving the original stable key.
_seen_vocab = set()
_unique_vocab = []
for _word in VOCABULARY:
    _identity = (_word["level"], _word["word"].strip().casefold())
    if _identity not in _seen_vocab:
        _seen_vocab.add(_identity)
        _unique_vocab.append(_word)
VOCABULARY[:] = _unique_vocab
del _seen_vocab, _unique_vocab, _word, _identity
