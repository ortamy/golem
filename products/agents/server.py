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
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

AGENT_NAMES = {"researcher", "exposer", "collector"}
_lock = threading.Lock()
CORS_ENABLED = True

METHODOLOGY_CARDS_PATH = (
    Path(__file__).parent.parent / "website" / "apps" / "researchlab" / "data" / "methodology" / "cards.json"
)
_cards_lock = threading.Lock()


class AgentHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[server] {fmt % args}")

    def _send_cors(self):
        if not CORS_ENABLED:
            return
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors()
        self.end_headers()

    def do_GET(self):
        if self.path != "/api/methodology/cards":
            self.send_response(404)
            self._send_cors()
            self.end_headers()
            self.wfile.write(b'{"error":"not found"}')
            return

        try:
            data = json.loads(METHODOLOGY_CARDS_PATH.read_text(encoding="utf-8"))
        except FileNotFoundError:
            self._respond(404, {"error": "cards.json not found"})
            return
        except Exception as e:
            self._respond(500, {"error": str(e)})
            return

        self._respond(200, data)

    def do_POST(self):
        if self.path == "/api/methodology/cards":
            self._handle_save_cards()
            return

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

    def _handle_save_cards(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            self._respond(400, {"error": "invalid JSON"})
            return

        error = _validate_cards_payload(payload)
        if error:
            self._respond(400, {"error": error})
            return

        with _cards_lock:
            try:
                _write_cards_atomic(payload)
            except Exception as e:
                self._respond(500, {"error": str(e)})
                return

        self._respond(200, payload)


def _validate_cards_payload(payload) -> str:
    if not isinstance(payload, dict):
        return "payload must be an object"
    if "categories" not in payload or not isinstance(payload["categories"], dict):
        return "'categories' must be an object"
    cards = payload.get("cards")
    if not isinstance(cards, list):
        return "'cards' must be an array"
    for card in cards:
        if not isinstance(card, dict):
            return "each card must be an object"
        for field in ("id", "category", "title", "text"):
            if not isinstance(card.get(field), str):
                return f"card.{field} must be a string"
    return ""


def _write_cards_atomic(payload):
    METHODOLOGY_CARDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = METHODOLOGY_CARDS_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(METHODOLOGY_CARDS_PATH)


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
    parser = argparse.ArgumentParser(description="HTTP сервер для запуска агентов Голема")
    parser.add_argument("--host", default="0.0.0.0", help="Адрес привязки сервера")
    parser.add_argument("--port", type=int, default=8000, help="Порт сервера")
    parser.add_argument("--no-cors", action="store_true", help="Не добавлять CORS-заголовки")
    args = parser.parse_args()
    CORS_ENABLED = not args.no_cors
    httpd = HTTPServer((args.host, args.port), AgentHandler)
    display_host = "localhost" if args.host in ("0.0.0.0", "::") else args.host
    print(f"[server] AI-агенты доступны на http://{display_host}:{args.port}/api/run")
    print("[server] Нажмите Ctrl+C для остановки.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("[server] Остановлен.")
