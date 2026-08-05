#!/usr/bin/env python3
"""Минимальная Flask API-точка входа для оркестратора."""
from flask import Flask, jsonify, request
from orchestrator import dispatch

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    """Разрешает Research Lab, открытой на другом локальном порту, вызвать API."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
