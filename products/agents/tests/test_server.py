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

    def test_api_info_returns_process_meta(self):
        response = self.client.get("/api/info")

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["service"], "golem-agents")
        self.assertIn("pid", body)
        self.assertIn("python", body)
        self.assertIn("uptime", body)

    def test_lab_index_is_served(self):
        response = self.client.get("/apps/researchlab/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"researchlab", response.data.lower())

    def test_lab_static_asset_is_served(self):
        response = self.client.get("/apps/researchlab/js/agent-server.js")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AgentServer", response.data)

    def test_lab_path_traversal_blocked(self):
        response = self.client.get("/../../CLAUDE.md")
        self.assertEqual(response.status_code, 404)

    def test_lab_shutdown_noop_in_testing(self):
        response = self.client.post("/api/lab/shutdown")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["testing"])

    def test_lab_restart_noop_in_testing(self):
        response = self.client.post("/api/lab/restart")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["testing"])

    def test_cors_headers_present_by_default(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")


    @patch("server.write_results")
    @patch("server.read_results", return_value=[])
    @patch("server.execute_named_pipeline", side_effect=ValueError("Неизвестный пайплайн: custom"))
    @patch("server.read_pipelines")
    def test_custom_pipeline_without_runner_falls_back_to_agent_names(self, read_pipelines, execute, _read_results, write_results):
        """Кастомный пайплайн из UI (без Python-раннера) исполняется по русским именам."""
        read_pipelines.return_value = [{
            "id": "custom-ui",
            "runner": "custom-ui",
            "name": "Кастомный",
            "agents": ["Исследователь", "Критик", "Сборщик"],
        }]

        response = self.client.post("/api/pipelines/custom-ui/run", json={"query": "разбор Давар"})

        self.assertEqual(response.status_code, 201)
        body = response.get_json()
        self.assertEqual(body["trace"][0], "researcher")
        self.assertIn("collector", body["trace"])
        write_results.assert_called_once()


if __name__ == "__main__":
    unittest.main()