"""Проверка сохранённого, а не скрытого, следа агентов."""
import sys
import unittest
from pathlib import Path


AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from agents.common import packet, record  # noqa: E402


class AgentTraceTest(unittest.TestCase):
    def test_record_keeps_input_and_explicit_output(self):
        data = record(packet("проверка", source="локальный корпус"), "collector", result={"title": "Итог"})

        step = data["agentTrace"][0]
        self.assertEqual(step["agentId"], "collector")
        self.assertEqual(step["input"]["source"], "локальный корпус")
        self.assertEqual(step["output"]["result"]["title"], "Итог")
        self.assertEqual(step["observations"][0]["field"], "result")


if __name__ == "__main__":
    unittest.main()