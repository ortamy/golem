"""Контрактные тесты локального API пайплайнов."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from server import app  # noqa: E402
from ollama_adapter import OllamaError  # noqa: E402


class PipelineApiTest(unittest.TestCase):
    """Проверяет API без запуска отдельного Flask-процесса."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.pipeline = {
            "id": "word_analyzer",
            "runner": "word_analyzer",
            "name": "Разбор слова",
            "defaultQuery": "разбери слово Берешит",
        }
        self.output = {
            "trace": ["researcher", "collector"],
            "agentTrace": [{"agentId": "researcher", "status": "done", "input": {}, "observations": [], "decisions": [], "hypotheses": [], "limitations": [], "output": {}}],
            "result": {"title": "Исследование", "summary": "Базовый результат"},
        }

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    @patch("server.write_results")
    @patch("server.read_results", return_value=[{"pipelineId": "word_analyzer", "id": "previous"}])
    @patch("server.execute_named_pipeline")
    @patch("server.read_pipelines")
    def test_run_saves_agent_result_without_ollama(self, read_pipelines, execute, _read_results, write_results):
        read_pipelines.return_value = [self.pipeline]
        execute.return_value = self.output

        response = self.client.post("/api/pipelines/word_analyzer/run", json={"query": "тест"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["result"]["summary"], "Базовый результат")
        self.assertEqual(response.get_json()["agentTrace"][0]["agentId"], "researcher")
        write_results.assert_called_once()
        self.assertEqual(write_results.call_args.args[0][1]["id"], "previous")

    @patch("server.read_results")
    def test_pipeline_history_returns_only_requested_pipeline(self, read_results):
        read_results.return_value = [{"pipelineId": "word_analyzer"}, {"pipelineId": "research_builder"}]

        response = self.client.get("/api/pipelines/word_analyzer/results")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [{"pipelineId": "word_analyzer"}])

    @patch("server.write_results")
    @patch("server.read_results", return_value=[])
    @patch("server.ollama_summarize", side_effect=OllamaError("unexpected"))
    @patch("server.execute_named_pipeline")
    @patch("server.read_pipelines")
    def test_agent_result_survives_ollama_error(self, read_pipelines, execute, _ollama, _read_results, write_results):
        read_pipelines.return_value = [self.pipeline]
        execute.return_value = self.output

        response = self.client.post(
            "/api/pipelines/word_analyzer/run",
            json={"query": "тест", "useOllama": True},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["ollama"]["status"], "error")
        write_results.assert_called_once()


if __name__ == "__main__":
    unittest.main()