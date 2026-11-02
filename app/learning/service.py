import random
from app.content import VOCABULARY, GRAMMAR, QUIZ, LEVELS

def words_for_level(level):
    return [w for w in VOCABULARY if w["level"] == level]

def grammar_for_level(level):
    return [{**lesson, "level": level} for lesson in GRAMMAR.get(level, [])]

def questions_for_level(level, count=5):
    eligible = [q for q in QUIZ if LEVELS.index(q["level"]) <= LEVELS.index(level)]
    if not eligible:
        eligible = QUIZ[:]
    return random.sample(eligible, min(count, len(eligible)))

def find_word(key):
    return next((w for w in VOCABULARY if w["key"] == key), None)

def placement_questions():
    """A 30-item screening set: five questions from each CEFR band."""
    selected = []
    for level in LEVELS:
        level_questions = [question for question in QUIZ if question["level"] == level]
        selected.extend(level_questions[:5])
    return selected

def placement_level(score):
    """Backward-compatible coarse mapping for older callers."""
    if score <= 1: return "A1"
    if score == 2: return "A2"
    if score == 3: return "B1"
    if score == 4: return "B2"
    if score == 5: return "C1"
    return "C2"

def placement_level_from_breakdown(breakdown):
    """Return the highest band with at least 3/5 correct answers."""
    result = "A1"
    for level in LEVELS:
        if breakdown.get(level, 0) >= 3:
            result = level
        else:
            break
    return result


def conversations_for_level(level=None):
    from app.content import CONVERSATIONS
    if level:
        order = {name: index for index, name in enumerate(LEVELS)}
        current = order.get(level, 0)
        eligible = [item for item in CONVERSATIONS if order.get(item["level"], 0) <= current]
        return eligible or CONVERSATIONS
    return CONVERSATIONS


def conversation_by_id(conversation_id):
    from app.content import CONVERSATIONS
    return next((item for item in CONVERSATIONS if item["id"] == conversation_id), None)
