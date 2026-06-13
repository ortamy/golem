#!/usr/bin/env python3
# tools/checkers/check-countries.py — проверка стран по критериям ТаНаХа (v1.0)

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = ROOT / "tools" / "cache"
DATA_FILE = CACHE_DIR / "cache-countries.json"
OUTPUT_FILE = CACHE_DIR / "cache-countries-results.json"

# 7 уровней, 35 параметров, каждый 0-10 баллов
LEVELS = {
    "roots": {
        "label": "Корни — отношение к Яхве и Израилю",
        "params": [
            "recognizes_yhwh",
            "supports_israel",
            "torah_above_law",
            "no_state_religion",
        ]
    },
    "trunk": {
        "label": "Ствол — законы и власть",
        "params": [
            "laws_near_torah",
            "low_pietism",
            "freedom_of_speech",
            "separation_of_powers",
        ]
    },
    "branches": {
        "label": "Ветви — экономика и налоги",
        "params": [
            "debt_forgiveness",
            "land_return",
            "tax_burden",
            "no_usury",
            "property_rights",
            "autonomous_life",
        ]
    },
    "fruits": {
        "label": "Плоды — общество и культура",
        "params": [
            "family_protection",
            "child_protection",
            "chastity_culture",
            "elder_respect",
            "low_crime",
            "protection_of_weak",
        ]
    },
    "soil": {
        "label": "Почва — география и климат",
        "params": [
            "agriculture_suitable",
            "clean_water",
            "low_disasters",
            "mild_climate",
            "sea_access",
        ]
    },
    "seed": {
        "label": "Семя — история и основание",
        "params": [
            "founded_without_blood",
            "clean_history",
            "constitution_stable",
            "neutral_in_wars",
        ]
    },
    "breath": {
        "label": "Дыхание — дух народа",
        "params": [
            "openness_to_truth",
            "mutual_help",
            "low_fear_of_authority",
            "remnant_presence",
        ]
    },
}


def load_data():
    if not DATA_FILE.exists():
        print(f"❌ Файл данных не найден: {DATA_FILE}")
        print("Создайте JSON с данными стран в этом файле.")
        return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_score(country_data):
    """Считает баллы для одной страны."""
    scores = {}
    total = 0
    max_total = 0
    
    for level_key, level_data in LEVELS.items():
        level_score = 0
        level_max = 0
        
        for param in level_data["params"]:
            value = country_data.get(level_key, {}).get(param, 0)
            level_score += value
            level_max += 10
        
        scores[level_key] = {
            "score": level_score,
            "max": level_max,
            "label": level_data["label"],
            "pct": round(level_score / level_max * 100) if level_max > 0 else 0,
        }
        total += level_score
        max_total += level_max
    
    return {
        "name": country_data.get("name", "Unknown"),
        "code": country_data.get("code", "XX"),
        "scores": scores,
        "total": total,
        "max": max_total,
        "pct": round(total / max_total * 100) if max_total > 0 else 0,
    }


def color_for_pct(pct):
    if pct >= 70:
        return "🟢"
    elif pct >= 40:
        return "🟡"
    else:
        return "🔴"


def run():
    data = load_data()
    if not data:
        return
    
    countries = data.get("countries", [])
    if not countries:
        print("❌ Нет данных о странах в JSON.")
        return
    
    results = []
    for country in countries:
        result = calculate_score(country)
        results.append(result)
    
    # Сортировка по общему баллу
    results.sort(key=lambda r: r["total"], reverse=True)
    
    # Вывод таблицы
    print(f"\n{'🌍 Страна':25} {'Корни':>6} {'Ствол':>6} {'Ветви':>6} {'Плоды':>6} {'Почва':>6} {'Семя':>6} {'Дых.':>6} {'Итог':>8}")
    print("-" * 85)
    
    for r in results:
        name = r["name"][:24]
        parts = []
        for level in ["roots", "trunk", "branches", "fruits", "soil", "seed", "breath"]:
            s = r["scores"].get(level, {})
            pct = s.get("pct", 0)
            color = color_for_pct(pct)
            parts.append(f"{color}{pct:3}%")
        
        line = "  ".join(parts)
        print(f"{r['code']} {name:22} {line}  {color_for_pct(r['pct'])}{r['pct']:3}% ({r['total']}/{r['max']})")
    
    # Вывод топ-10
    print(f"\n🏆 Топ-10:")
    for i, r in enumerate(results[:10], 1):
        print(f"  {i:2}. {r['code']} {r['name']} — {r['total']}/{r['max']} ({r['pct']}%)")
    
    # Вывод худших 5
    print(f"\n💀 Худшие 5:")
    for i, r in enumerate(results[-5:], 1):
        print(f"  {i:2}. {r['code']} {r['name']} — {r['total']}/{r['max']} ({r['pct']}%)")
    
    # Сохранить результаты
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Результаты сохранены: {OUTPUT_FILE}")


if __name__ == "__main__":
    run()