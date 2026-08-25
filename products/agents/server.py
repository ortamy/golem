#!/usr/bin/env python3
"""Минимальная Flask API-точка входа для оркестратора."""
import json
from pathlib import Path

from flask import Flask, jsonify, request
from orchestrator import dispatch

app = Flask(__name__)
PIPELINES_PATH = Path(__file__).resolve().parents[2] / "products" / "website" / "apps" / "researchlab" / "data" / "pipelines.json"


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


@app.get("/api/pipelines")
def list_pipelines():
    return jsonify(read_pipelines())


@app.post("/api/pipelines")
def create_pipeline():
    payload = request.get_json(silent=True) or {}
    pipeline, error = validate_pipeline(payload)
    if error:
        return jsonify({"error": error[0]}), error[1]
    pipelines = read_pipelines()
    pipeline["id"] = make_pipeline_id(pipelines, pipeline["name"])
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
    return {"name": name, "description": description, "agents": [str(agent).strip() for agent in agents]}, None


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
