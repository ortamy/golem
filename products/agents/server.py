#!/usr/bin/env python3
# products/agents/server.py — HTTP сервер для запуска агентов из webapp
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

AGENT_NAMES = {"researcher", "exposer", "collector"}
PORT = 8000

_lock = threading.Lock()


class AgentHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[server] {fmt % args}")

    def _send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors()
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/run":
            self.send_response(404)
            self._send_cors()
            self.end_headers()
            self.wfile.write(b'{"error":"not found"}')
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            self._respond(400, {"error": "invalid JSON"})
            return

        agent = data.get("agent", "collector").lower()
        task = (data.get("task") or "").strip()

        if not task:
            self._respond(400, {"error": "task is required"})
            return
        if agent not in AGENT_NAMES:
            self._respond(400, {"error": f"unknown agent '{agent}'. Use: researcher, exposer, collector"})
            return

        with _lock:
            result = _run_agent(agent, task)

        self._respond(200, result)

    def _respond(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self._send_cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _run_agent(agent: str, task: str) -> dict:
    main_py = Path(__file__).parent / "main.py"
    python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    if not python.exists():
        python = sys.executable

    try:
        proc = subprocess.run(
            [str(python), str(main_py), task, "--agent", agent],
            capture_output=True, text=True, timeout=300,
            cwd=str(Path(__file__).parent)
        )
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        # Ищем путь к сохранённому файлу в stdout
        output_path = None
        for line in stdout.splitlines():
            if line.startswith("Готово. Результат сохранён:"):
                output_path = line.split(":", 1)[-1].strip()
                break

        result_text = ""
        if output_path:
            try:
                result_text = Path(output_path).read_text(encoding="utf-8")
            except Exception:
                result_text = stdout
        else:
            result_text = stdout or stderr or "(нет вывода)"

        if proc.returncode != 0 and not result_text:
            return {"error": stderr or "agent exited with error", "returncode": proc.returncode}

        return {"result": result_text, "agent": agent, "task": task}

    except subprocess.TimeoutExpired:
        return {"error": "Timeout: агент не ответил за 5 минут."}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    httpd = HTTPServer(("0.0.0.0", PORT), AgentHandler)
    print(f"[server] AI-агенты доступны на http://localhost:{PORT}/api/run")
    print("[server] Нажмите Ctrl+C для остановки.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("[server] Остановлен.")
