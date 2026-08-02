"""Тесты движка анализаторов.

Метаданные файла:
- Заголовок: тесты анализаторов «Голем»
- Описание: проверки токенизации, слоёв и глубинного прохода
- Версия: 1.0.0
- Дата создания: 2026-08-02
"""

import unittest

from engine import Analyzer


class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = Analyzer()

    def test_tokenization_and_sentences(self):
        result = self.analyzer.analyze("Дверь открывает поток. Тело движется!")
        self.assertEqual(len(result.words), 5)
        self.assertEqual(len(result.sentences), 2)

    def test_layers_and_dominant_layer(self):
        result = self.analyzer.analyze("Алгоритм системы оптимизирует ресурс и контролирует данные.")
        technology = next(layer for layer in result.layers if layer.id == "technology")
        self.assertGreaterEqual(technology.hit_count, 5)
        self.assertEqual(result.dominant_layer.id, "technology")

    def test_short_markers_do_not_match_inside_unrelated_words(self):
        result = self.analyzer.analyze("Алгоритм управляет потоком.")
        paleo = next(layer for layer in result.layers if layer.id == "paleo")
        juridical = next(layer for layer in result.layers if layer.id == "juridization")
        self.assertEqual([hit.term for hit in paleo.markers], ["поток"])
        self.assertEqual(juridical.hit_count, 0)

    def test_deep_pass_after_one_hundred_words(self):
        text = ("Поток открывает дверь и возвращается в дом. " * 21)
        result = self.analyzer.analyze(text)
        self.assertGreater(len(result.words), 100)
        self.assertIsNotNone(result.deep)
        self.assertTrue(result.deep["repeated_patterns"])

    def test_empty_text_has_no_dominant_layer(self):
        result = self.analyzer.analyze("")
        self.assertEqual(result.words, [])
        self.assertIsNone(result.dominant_layer)


if __name__ == "__main__":
    unittest.main()