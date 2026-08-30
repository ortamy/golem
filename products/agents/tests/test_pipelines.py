"""Контрактные тесты движка: линейные цепочки, циклы, новые пайплайны."""
import sys
import unittest
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from agents.common import packet, record  # noqa: E402
from agents.convergence import converge  # noqa: E402
from agents.paleo_translator import translate  # noqa: E402
from agents.critic import critique  # noqa: E402
from agents.verifier import verify  # noqa: E402
from pipelines.core import run_steps, run_loop  # noqa: E402


class EmptyStepTest(unittest.TestCase):
    """Линейная цепочка останавливается на пустом результате."""

    def test_stops_on_none(self):
        def dead(_data):
            return None

        data = run_steps(packet("тест"), [dead, critique])
        self.assertIsNone(data)

    def test_stops_on_empty_dict(self):
        def dead(_data):
            return {}

        data = run_steps(packet("тест"), [dead, critique])
        self.assertEqual(data, {})

    def test_runs_until_finish(self):
        data = run_steps(packet("тест"), [critique])
        self.assertIn("critique_notes", data)
        self.assertIn("critic", data["trace"])


class LoopEngineTest(unittest.TestCase):
    """Цикл сходится, не сходится со stall, уважает max_iterations."""

    def test_converges_on_stable_signature(self):
        steps = (critique, verify)
        data = run_loop(packet("тест", term="тест"),
                        cycle_steps=steps, converge_step=converge, max_iterations=5)
        self.assertTrue(data["converged"])
        self.assertFalse(data["convergence"]["stalled"])
        self.assertGreaterEqual(len(data["convergence_history"]), 2)

    def test_stalls_when_never_converging(self):
        def restless(data):
            # Каждый виток меняет поле, входящее в подпись → подпись вечно новая.
            data["critique"] = "шум №%d" % data.get("iteration", 0)
            return data

        data = run_loop(packet("тест"),
                        cycle_steps=(restless,), converge_step=converge, max_iterations=3)
        self.assertFalse(data["converged"])
        self.assertTrue(data["convergence"]["stalled"])
        self.assertEqual(len(data["convergence_history"]), 3)

    def test_shmita_reset_keeps_protected_fields(self):
        steps = (critique, verify)
        data = run_loop(packet("тест", term="схема", gaps=["A"]),
                        cycle_steps=steps, converge_step=converge, max_iterations=5,
                        shmita_every=2, reset_fields=["exposures"])
        self.assertGreaterEqual(data.get("shmita_resets"), 1)
        self.assertIn("query", data)
        self.assertIn("trace", data)

    def test_agent_trace_has_iteration(self):
        steps = (critique, verify)
        data = run_loop(packet("тест"),
                        cycle_steps=steps, converge_step=converge, max_iterations=3)
        iterations = {item.get("iteration") for item in data["agentTrace"]}
        self.assertTrue(iterations.intersection({1, 2}))
class LinearityWithPaleoTest(unittest.TestCase):
    """Новые линейные пайплайны возвращают след и результат."""

    def _assert_ok(self, output):
        self.assertTrue(output.get("trace"))
        self.assertTrue(output.get("agentTrace"))
        self.assertIn("result", output)
        self.assertIn("title", output["result"])

    def test_paleo_translation(self):
        from pipelines.paleo_translation import run
        self._assert_ok(run("обратный перевод Давар"))

    def test_research_audit(self):
        from pipelines.research_audit import run
        self._assert_ok(run("проверь отчёт Давар"))

    def test_mechanism_scanner(self):
        from pipelines.mechanism_scanner import run
        self._assert_ok(run("сканер подмен Давар"))

    def test_verse_reconstruction(self):
        from pipelines.verse_reconstruction import run
        self._assert_ok(run("реконструируй стих Берешит 1:1"))


class LoopPipelinesTest(unittest.TestCase):
    """Циклические пайплайны возвращают iteration-след."""

    def _assert_loop(self, output):
        self.assertIn("iterations", output["result"])
        self.assertIn("converged", output["result"])

    def test_critique_loop(self):
        from pipelines.critique_loop import run
        output = run("самокритика Давар")
        self.assertTrue(output["trace"])
        self._assert_loop(output)

    def test_gap_cycle(self):
        from pipelines.gap_cycle import run
        output = run("карантин пропусков Слово")
        self.assertIn("gaps", output["result"])
        self._assert_loop(output)

    def test_spiral_swiva(self):
        from pipelines.spiral_swiva import run
        output = run("хук свива Давар")
        # Спираль сходится: горизонт исчерпан и подпись стабилизируется.
        self.assertTrue(output["result"]["converged"])
        self.assertIn("horizon", output["result"]["data"])
        self._assert_loop(output)

    def test_dialectic_loop(self):
        from pipelines.dialectic_loop import run
        self._assert_loop(run("диалектика стиха Берешит 1:1"))

    def test_midrash_recursion(self):
        from pipelines.midrash_recursion import run
        output = run("мидраш слова Берешит")
        # Палео-образ лежит в data результата; цикл сходится на стабильном образе.
        self.assertIn("paleo_image", output["result"]["data"])
        self.assertTrue(output["result"]["converged"])
        self._assert_loop(output)

    def test_shmita_loop(self):
        from pipelines.shmita_loop import run
        output = run("шмита слова Давар")
        self._assert_loop(output)
        self.assertIn("shmita_resets", output["result"])


class OrchestratorTest(unittest.TestCase):
    def test_unknown_query_raises(self):
        from orchestrator import dispatch
        with self.assertRaises(ValueError):
            dispatch("почини принтер")

    def test_known_routes_exist(self):
        from orchestrator import PIPELINES
        for pipeline_id in ("paleo_translation", "research_audit", "mechanism_scanner",
                            "verse_reconstruction", "critique_loop", "gap_cycle",
                            "spiral_swiva", "dialectic_loop", "midrash_recursion", "shmita_loop"):
            self.assertIn(pipeline_id, PIPELINES)


if __name__ == "__main__":
    unittest.main()