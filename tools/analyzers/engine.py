"""Ядро вертикального анализа текста по слоям подмен.

Метаданные файла:
- Заголовок: движок анализаторов «Голем»
- Описание: токенизация, послойный подсчёт и глубинная диагностика
- Версия: 1.0.0
- Дата создания: 2026-08-02
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


WORD_RE = re.compile(r"[\wёЁ-]+", re.UNICODE)
SENTENCE_RE = re.compile(r"(?<=[.!?…])\s+|\n+")


@dataclass
class MarkerHit:
    term: str
    count: int
    examples: List[str]


@dataclass
class LayerResult:
    id: str
    name: str
    description: str
    hit_count: int
    percentage: float
    markers: List[MarkerHit]
    diagnosis: str
    recommendations: List[str]


@dataclass
class AnalysisResult:
    text: str
    words: List[str]
    sentences: List[str]
    layers: List[LayerResult]
    dominant_layer: Optional[LayerResult]
    deep: Optional[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


class Analyzer:
    """Расширяемый анализатор, управляемый каталогом markers.json."""

    def __init__(self, catalog_path: Optional[Path] = None) -> None:
        path = catalog_path or Path(__file__).with_name("markers.json")
        self.catalog = json.loads(path.read_text(encoding="utf-8"))
        self._compiled = self._compile_catalog(self.catalog["layers"])

    @staticmethod
    def _compile_catalog(layers: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        compiled = []
        for layer in layers:
            current = dict(layer)
            current["markers"] = []
            for marker in layer.get("markers", []):
                item = dict(marker)
                item["regex"] = re.compile(item["pattern"], re.IGNORECASE)
                current["markers"].append(item)
            compiled.append(current)
        return compiled

    @staticmethod
    def tokenize(text: str) -> List[str]:
        return [match.group(0) for match in WORD_RE.finditer(text)]

    @staticmethod
    def split_sentences(text: str) -> List[str]:
        return [part.strip() for part in SENTENCE_RE.split(text) if part.strip()]

    @staticmethod
    def _word_spans(text: str) -> List[tuple[int, int, str]]:
        return [(m.start(), m.end(), m.group(0)) for m in WORD_RE.finditer(text)]

    def _scan_layer(self, layer: Dict[str, Any], text: str, words: List[str]) -> LayerResult:
        normalized_text = text.lower()
        marker_hits: List[MarkerHit] = []
        hit_word_indexes = set()
        for marker in layer["markers"]:
            count = 0
            examples: List[str] = []
            if marker.get("scope", "word") == "text":
                matches = list(marker["regex"].finditer(normalized_text))
                count = len(matches)
                for match in matches:
                    for index, (start, end, value) in enumerate(self._word_spans(text)):
                        if start < match.end() and end > match.start():
                            hit_word_indexes.add(index)
                            if value not in examples and len(examples) < 3:
                                examples.append(value)
            else:
                for index, word in enumerate(words):
                    if marker["regex"].search(word.lower()):
                        count += 1
                        hit_word_indexes.add(index)
                        if word not in examples and len(examples) < 3:
                            examples.append(word)
            if count:
                marker_hits.append(MarkerHit(marker["term"], count, examples))
        total_words = len(words)
        percentage = (len(hit_word_indexes) / total_words * 100) if total_words else 0.0
        return LayerResult(
            id=layer["id"], name=layer["name"], description=layer["description"],
            hit_count=len(hit_word_indexes), percentage=round(percentage, 2),
            markers=marker_hits, diagnosis=layer["diagnosis"],
            recommendations=layer.get("recommendations", []),
        )

    def _deep_analysis(self, words: List[str], layers: List[LayerResult]) -> Dict[str, Any]:
        stopwords = {"и", "в", "во", "на", "с", "со", "к", "из", "что", "это", "как", "для", "по", "а", "но", "не"}
        counts = Counter(word.lower() for word in words if word.lower() not in stopwords)
        repeated = [{"word": word, "count": count} for word, count in counts.most_common(12) if count >= 3]
        active = {layer.id for layer in layers if layer.hit_count}
        tensions = []
        for tension in self.catalog.get("tensions", []):
            if set(tension["layers"]).issubset(active):
                tensions.append(tension["message"])
        recommendations = []
        for layer in sorted(layers, key=lambda item: item.hit_count, reverse=True):
            if layer.hit_count:
                recommendations.extend(layer.recommendations)
        return {
            "trigger": "более 100 слов",
            "repeated_patterns": repeated,
            "contradictions": tensions,
            "recommendations": list(dict.fromkeys(recommendations)),
        }

    def analyze(self, text: str) -> AnalysisResult:
        words = self.tokenize(text)
        sentences = self.split_sentences(text)
        layers = [self._scan_layer(layer, text, words) for layer in self._compiled]
        dominant = max(layers, key=lambda layer: layer.hit_count, default=None)
        if dominant and dominant.hit_count == 0:
            dominant = None
        deep = self._deep_analysis(words, layers) if len(words) > 100 else None
        return AnalysisResult(text, words, sentences, layers, dominant, deep)