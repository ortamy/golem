#!/usr/bin/env python3
"""Минимальная Flask API-точка входа для оркестратора."""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request
from orchestrator import dispatch, run_pipeline as execute_named_pipeline
from pipelines.core import run_steps
from agents.common import packet
from agents import ai_engineer, code_reviewer, collector, comparator, critic, editor, exposer, \
    flow_architect, frontend, liaison, paleo_translator, researcher, semitologist, verifier, writer
from ollama_adapter import OllamaError, status as ollama_status, summarize as ollama_summarize

app = Flask(__name__)
PIPELINES_PATH = Path(__file__).resolve().parents[2] / "products" / "website" / "apps" / "researchlab" / "data" / "pipelines.json"
RESULTS_PATH = PIPELINES_PATH.with_name("pipeline-results.json")

# Русские имена агентов из UI (getAgentMapData) → их функции.
# Позволяет исполнять кастомные пайплайны, созданные в Research Lab,
# даже если для них не зарегистрирован Python-раннер.
AGENT_FUNCTIONS = {
    "Исследователь": researcher.research,
    "Семитолог": semitologist.compare,
    "Разоблачитель": exposer.expose,
    "Редактор": editor.edit,
    "Сборщик": collector.collect,
    "Компаратор": comparator.compare,
    "Критик": critic.critique,
    "Проверяющий": verifier.verify,
    "Переводчик палео-иврита": paleo_translator.translate,
    "Архитектор потока": flow_architect.design,
    "Связной": liaison.relay,
    "Технический писатель": writer.write,
    "Ревьюер кода": code_reviewer.review,
    "AI-инженер": ai_engineer.prepare,
    "Фронтенд-разработчик": frontend.prepare,
}


def read_pipelines():
    if not PIPELINES_PATH.exists():
        return []
    with PIPELINES_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, list) else payload.get("pipelines", [])


def write_pipelines(pipelines):
    PIPELINES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PIPELINES_PATH.open("w", encoding="utf-8") as handle:
        json.dump(pipelines, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def read_results():
    if not RESULTS_PATH.exists():
        return []
    with RESULTS_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, list) else []


def write_results(results):
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


@app.after_request
def add_cors_headers(response):
    """Разрешает Research Lab, открытой на другом локальном порту, вызвать API."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@app.route("/run", methods=["OPTIONS"])
def run_options():
    return ("", 204)


@app.post("/run")
@app.post("/api/run")
def run_pipeline():
    payload = request.get_json(silent=True) or {}
    query = (payload.get("query") or payload.get("task") or "").strip()
    if not query:
        return jsonify({"error": "query is required"}), 400
    try:
        return jsonify(dispatch(query))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "golem-agents"})


@app.get("/api/ollama/status")
def get_ollama_status():
    return jsonify(ollama_status())


@app.get("/api/pipelines")
def list_pipelines():
    return jsonify(read_pipelines())


@app.get("/api/pipeline-results")
def list_pipeline_results():
    return jsonify(read_results())


@app.post("/api/pipelines/<pipeline_id>/run")
def run_named_pipeline(pipeline_id):
    payload = request.get_json(silent=True) or {}
    query = (payload.get("query") or "").strip()
    use_ollama = bool(payload.get("useOllama"))
    ollama_model = str(payload.get("model") or "").strip() or None
    ollama_temperature = payload.get("temperature", 0.2)
    try:
        ollama_temperature = float(ollama_temperature)
        if not math.isfinite(ollama_temperature):
            ollama_temperature = 0.2
    except (TypeError, ValueError):
        ollama_temperature = 0.2
    pipeline = next((item for item in read_pipelines() if item.get("id") == pipeline_id), None)
    if pipeline is None:
        return jsonify({"error": "pipeline not found"}), 404
    if not query:
        query = str(pipeline.get("defaultQuery") or "").strip()
    if not query:
        return jsonify({"error": "query is required"}), 400
    try:
        output = execute_named_pipeline(str(pipeline.get("runner") or pipeline_id), query)
    except ValueError as error:
        # Для пайплайнов, созданных в UI и не имеющих Python-раннера,
        # собираем линейную цепочку из русских имён агентов.
        steps = [AGENT_FUNCTIONS[name] for name in pipeline.get("agents", []) if name in AGENT_FUNCTIONS]
        if not steps:
            return jsonify({"error": str(error)}), 400
        output = run_steps(packet(query), steps)
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    result = {
        "id": pipeline_id + "-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        "pipelineId": pipeline_id,
        "title": output.get("result", {}).get("title", pipeline.get("name", pipeline_id)),
        "query": query,
        "createdAt": created_at,
        "source": "local-agents",
        "status": "ready",
        "trace": output.get("trace", []),
        "agentTrace": output.get("agentTrace", []),
        "result": output.get("result", {}),
    }
    if use_ollama:
        try:
            result["ollama"] = ollama_summarize(query, result["result"], ollama_model, ollama_temperature)
            result["result"]["aiSummary"] = result["ollama"]["text"]
        except OllamaError as error:
            # Ошибка редакторского слоя не отменяет результат агентов.
            result["ollama"] = {
                "status": "error",
                "model": ollama_model,
                "error": str(error),
            }
    results = read_results()
    results.insert(0, result)
    write_results(results)
    return jsonify(result), 201


@app.get("/api/pipelines/<pipeline_id>/results")
def list_pipeline_history(pipeline_id):
    results = [item for item in read_results() if item.get("pipelineId") == pipeline_id]
    return jsonify(results)


@app.post("/api/pipelines")
def create_pipeline():
    payload = request.get_json(silent=True) or {}
    pipeline, error = validate_pipeline(payload)
    if error:
        return jsonify({"error": error[0]}), error[1]
    pipelines = read_pipelines()
    pipeline["id"] = make_pipeline_id(pipelines, pipeline["name"])
    pipeline.setdefault("runner", pipeline["id"])
    pipelines.append(pipeline)
    write_pipelines(pipelines)
    return jsonify(pipeline), 201


@app.put("/api/pipelines/<pipeline_id>")
def update_pipeline(pipeline_id):
    payload = request.get_json(silent=True) or {}
    pipeline, error = validate_pipeline(payload)
    if error:
        return jsonify({"error": error[0]}), error[1]
    pipelines = read_pipelines()
    for index, current in enumerate(pipelines):
        if current.get("id") == pipeline_id:
            pipeline["id"] = pipeline_id
            pipelines[index] = pipeline
            write_pipelines(pipelines)
            return jsonify(pipeline)
    return jsonify({"error": "pipeline not found"}), 404


@app.delete("/api/pipelines/<pipeline_id>")
def delete_pipeline(pipeline_id):
    pipelines = read_pipelines()
    filtered = [item for item in pipelines if item.get("id") != pipeline_id]
    if len(filtered) == len(pipelines):
        return jsonify({"error": "pipeline not found"}), 404
    write_pipelines(filtered)
    return jsonify({"deleted": pipeline_id})


def validate_pipeline(payload):
    name = str(payload.get("name") or "").strip()
    description = str(payload.get("description") or "").strip()
    agents = payload.get("agents")
    if not name:
        return None, ("name is required", 400)
    if not isinstance(agents, list) or not agents or not all(str(agent).strip() for agent in agents):
        return None, ("at least one agent is required", 400)
    pipeline_type = str(payload.get("type") or "linear").strip().lower()
    if pipeline_type not in ("linear", "loop", "spiral"):
        pipeline_type = "linear"
    pipeline = {"name": name, "description": description, "agents": [str(agent).strip() for agent in agents],
                "type": pipeline_type}
    try:
        max_iterations = int(payload.get("maxIterations") or 0)
    except (TypeError, ValueError):
        max_iterations = 0
    if max_iterations > 0:
        pipeline["maxIterations"] = max_iterations
    return pipeline, None


def make_pipeline_id(pipelines, name):
    base = "pipeline-" + "-".join("".join(char.lower() if char.isalnum() else "-" for char in name).split())
    base = base.strip("-") or "pipeline"
    candidate = base
    suffix = 2
    used = {item.get("id") for item in pipelines}
    while candidate in used:
        candidate = base + "-" + str(suffix)
        suffix += 1
    return candidate


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
