#!/usr/bin/env python3
# products/agents/agents/collector.py — агент-собиратель: сборка итогового файла
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

TEMPLATE = """# {title}

**Метаданные файла**
- **Тема:** {query}
- **Статус:** Черновик (сгенерирован агентами Голема)

---

## ИССЛЕДОВАНИЕ

{research}

---

## РАЗОБЛАЧЕНИЕ ПОДМЕН

{exposure}

---
"""


def assemble_markdown(query: str, research: str, exposure: str) -> str:
    """Собирает результаты researcher + exposer в единый Markdown-документ."""
    title = query.strip()
    return TEMPLATE.format(
        title=title,
        query=query.strip(),
        research=research.strip() or "(нет результата)",
        exposure=exposure.strip() or "(нет результата)",
    )


def save_output(markdown: str, output_dir: Path, slug: str) -> Path:
    """Сохраняет итоговый Markdown в output_dir/slug.md, создавая папку при нужде."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{slug}.md"
    out_path.write_text(markdown, encoding="utf-8")
    return out_path
