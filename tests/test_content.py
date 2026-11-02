import unittest
from app.content import LEVELS, VOCABULARY, GRAMMAR, QUIZ, CONVERSATIONS
from app.learning.service import placement_level, placement_level_from_breakdown, placement_questions, words_for_level, grammar_for_level, conversation_by_id

class ContentTests(unittest.TestCase):
    def test_all_levels_have_substantial_vocabulary_and_grammar(self):
        for level in LEVELS:
            self.assertGreaterEqual(len(words_for_level(level)), 70)
            self.assertGreaterEqual(len(grammar_for_level(level)), 20)

    def test_reference_bank_has_minimum_scale(self):
        self.assertGreaterEqual(len(VOCABULARY), 600)
        self.assertGreaterEqual(len(QUIZ), 90)
        self.assertGreaterEqual(sum(len(items) for items in GRAMMAR.values()), 120)

    def test_vocabulary_keys_are_unique_and_complete(self):
        keys = [word["key"] for word in VOCABULARY]
        self.assertEqual(len(keys), len(set(keys)))
        for word in VOCABULARY:
            self.assertTrue(word["word"])
            self.assertTrue(word["meaning"])
            self.assertTrue(word["example"])

    def test_grammar_keys_are_unique(self):
        keys = [lesson["key"] for level in LEVELS for lesson in GRAMMAR[level]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_quiz_answers_are_valid(self):
        for question in QUIZ:
            self.assertGreaterEqual(question["answer"], 0)
            self.assertLess(question["answer"], len(question["options"]))

    def test_placement_mapping(self):
        self.assertEqual(placement_level(0), "A1")
        self.assertEqual(placement_level(5), "C1")
        self.assertEqual(placement_level(6), "C2")
        self.assertEqual(len(placement_questions()), 30)
        self.assertEqual(placement_level_from_breakdown({"A1": 5, "A2": 4, "B1": 3, "B2": 2}), "B1")

    def test_conversation_catalog(self):
        self.assertGreaterEqual(len(CONVERSATIONS), 50)
        for item in CONVERSATIONS:
            self.assertTrue(item["turns"])
            self.assertIsNotNone(conversation_by_id(item["id"]))
            for turn in item["turns"]:
                self.assertTrue(turn["npc"])
                self.assertTrue(turn["sample"])
                self.assertTrue(turn["keywords"])

if __name__ == "__main__":
    unittest.main()
