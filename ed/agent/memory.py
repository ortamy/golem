#!/usr/bin/env python3
# ed/agent/memory.py — memory
# ed-agent/memory.py — память агента «Эд»
import json
from pathlib import Path
from datetime import datetime
from collections import deque

MEMORY_FILE = Path(__file__).parent / "memory.json"
MAX_ACTIONS = 100
MAX_HISTORY = 20


class AgentMemory:
    def __init__(self):
        self.data = self._load()

    def _load(self) -> dict:
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "actions": [],
            "history": [],
            "last_task": None,
            "stats": {
                "tasks_completed": 0,
                "tools_used": {},
                "errors": 0,
                "started_at": datetime.now().isoformat(),
            },
            "context": {
                "current_branch": None,
                "last_check": None,
                "pending_tasks": [],
            }
        }

    def save(self):
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_action(self, task: str, plan: dict, success_count: int, total_count: int):
        action = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "plan": plan,
            "success": success_count,
            "total": total_count,
        }
        self.data["actions"].append(action)
        self.data["history"].append(f"[{success_count}/{total_count}] {task}")

        # Ограничиваем размер
        if len(self.data["actions"]) > MAX_ACTIONS:
            self.data["actions"] = self.data["actions"][-MAX_ACTIONS:]
        if len(self.data["history"]) > MAX_HISTORY:
            self.data["history"] = self.data["history"][-MAX_HISTORY:]

        # Обновляем статистику
        self.data["stats"]["tasks_completed"] += 1
        for tool in plan.get("tools", []):
            self.data["stats"]["tools_used"][tool] = self.data["stats"]["tools_used"].get(tool, 0) + 1

        self.data["last_task"] = task

    def add_error(self, error: str):
        self.data["stats"]["errors"] += 1
        self.data["history"].append(f"❌ {error}")

    def get_stats(self) -> dict:
        return self.data["stats"]

    def get_history(self, n: int = 5) -> list:
        return self.data["history"][-n:]

    def get_favorite_tools(self, n: int = 5) -> list:
        tools = self.data["stats"]["tools_used"]
        return sorted(tools.items(), key=lambda x: x[1], reverse=True)[:n]

    def add_pending_task(self, task: str):
        self.data["context"]["pending_tasks"].append(task)

    def pop_pending_task(self) -> str | None:
        if self.data["context"]["pending_tasks"]:
            return self.data["context"]["pending_tasks"].pop(0)
        return None

    def clear_pending(self):
        self.data["context"]["pending_tasks"] = []

    def set_context(self, key: str, value):
        self.data["context"][key] = value

    def get_context(self, key: str):
        return self.data["context"].get(key)