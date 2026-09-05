"""Контракт контекста агентов: корни, термины, методология."""
import sys
import unittest
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from utils.context import (  # noqa: E402
    find_root,
    find_term_files,
    load_instruction,
    load_roots,
    root_letters,
)


class RootLettersTest(unittest.TestCase):
    def test_joins_paleo_glyphs(self):
        letters = root_letters({
            "root": "אב",
            "paleo": ["𐤀", "𐤁"],
        })
        self.assertEqual(letters, "𐤀𐤁")

    def test_keeps_explicit_letters(self):
        self.assertEqual(root_letters({"letters": "אב", "paleo": ["𐤀"]}), "אב")

    def test_load_roots_fills_letters(self):
        roots = load_roots()
        self.assertTrue(roots)
        first = roots[0]
        self.assertTrue(first.get("letters"))
        self.assertEqual(first["letters"], root_letters(first))


class FindRootTest(unittest.TestCase):
    def test_finds_hebrew_root(self):
        found = find_root("אב")
        self.assertIsNotNone(found)
        self.assertEqual(found["root"], "אב")
        self.assertEqual(found["letters"], "𐤀𐤁")

    def test_finds_by_translit(self):
        found = find_root("AV")
        self.assertIsNotNone(found)
        self.assertEqual(found["root"], "אב")


class ContentPathsTest(unittest.TestCase):
    def test_find_term_files_returns_markdown(self):
        hits = find_term_files("emet", limit=3)
        self.assertTrue(hits, "ожидались файлы по запросу emet в src/content/md")
        self.assertTrue(all(path.suffix == ".md" for path in hits))
        self.assertTrue(all(path.exists() for path in hits))

    def test_load_instruction_reads_manifest(self):
        text = load_instruction("00-START/MANIFEST.md")
        self.assertIn("ГОЛЕМ", text)

    def test_load_instruction_resolves_basename(self):
        text = load_instruction("PALEO-STANDARD.md")
        self.assertTrue(text)
        self.assertIn("ПАЛЕО", text.upper())


if __name__ == "__main__":
    unittest.main()
