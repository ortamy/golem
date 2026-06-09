# tools/generators/generate-graph.py — генерация визуальной карты связей
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, print_header, print_success, print_hint, REPO_ROOT

OUTPUT_FILE = REPO_ROOT / "docs" / "GRAPH.md"
SCAN_DIRS = ["terminology", "researches", "instructions"]


def extract_links(content: str) -> list:
    """Извлекает ссылки на другие файлы проекта."""
    links = []
    for match in re.finditer(r'\[([^\]]*)\]\(((?:terminology|researches|instructions)/[^)]+\.md)\)', content):
        links.append(match.group(2))
    return links


def build_graph():
    """Строит граф связей между файлами."""
    graph = defaultdict(list)  # файл → [связанные файлы]
    all_files = {}
    titles = {}

    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.rglob("*.md")):
            rel_path = str(md_file.relative_to(REPO_ROOT)).replace('\\', '/')
            content = read_file_safe(md_file)
            if not content:
                continue

            # Извлекаем заголовок
            title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else md_file.stem
            title = re.sub(r'[📜🔥🛡️⚔️📖🎯🧭💻👑❤️🏷️📊📋🔍🌐📁📝]\s*', '', title)
            titles[rel_path] = title[:60]

            # Извлекаем ссылки
            links = extract_links(content)
            if links:
                all_files[rel_path] = links
                graph[rel_path].extend(links)

    return graph, titles


def generate_mermaid(graph: dict, titles: dict) -> str:
    """Генерирует диаграмму в формате Mermaid."""
    lines = [
        "# 🗺 ВИЗУАЛЬНАЯ КАРТА СВЯЗЕЙ",
        "",
        "**Метаданные файла**",
        f"- **Файл:** `docs/GRAPH.md`",
        f"- **Версия:** 1.0",
        f"- **Дата создания:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}",
        f"- **Статус:** Активный",
        f"- **Тема:** Визуальная карта связей между файлами проекта",
        "",
        "---",
        "",
        "## 📊 ДИАГРАММА СВЯЗЕЙ",
        "",
        "```mermaid",
        "graph TD",
    ]

    # Группируем по папкам
    folders = defaultdict(list)
    for path in titles:
        folder = path.split('/')[0]
        folders[folder].append(path)

    # Стили для папок
    styles = {
        "terminology": "fill:#e1f5fe",
        "researches": "fill:#f3e5f5",
        "instructions": "fill:#e8f5e9",
    }

    # Генерируем узлы
    node_ids = {}
    for folder, paths in sorted(folders.items()):
        lines.append(f"  subgraph {folder}")
        for path in paths[:30]:  # не больше 30 узлов на папку
            node_id = path.replace('/', '_').replace('.', '_').replace('-', '_')
            node_ids[path] = node_id
            title = titles[path].replace('"', "'")
            lines.append(f'    {node_id}["{title}"]')
        lines.append("  end")

    # Генерируем связи
    for source, targets in graph.items():
        if source not in node_ids:
            continue
        for target in targets[:3]:  # не больше 3 связей на файл
            if target not in node_ids:
                continue
            lines.append(f"  {node_ids[source]} --> {node_ids[target]}")

    lines.append("```")
    lines.append("")
    lines.append("> Диаграмма автоматически сгенерирована. Для просмотра откройте файл в VS Code с плагином Mermaid или на GitHub.")
    lines.append("> Обновить: `python tools/generators/generate-graph.py`")

    return '\n'.join(lines)


def generate_text_map(graph: dict, titles: dict) -> str:
    """Генерирует текстовую карту связей."""
    lines = []

    # Группируем по папкам
    folders = defaultdict(list)
    for path in titles:
        folder = path.split('/')[0]
        folders[folder].append(path)

    for folder in sorted(folders.keys()):
        lines.append(f"## {folder}/")
        lines.append("")
        for path in sorted(folders[folder])[:50]:
            title = titles[path]
            lines.append(f"### {title}")
            lines.append(f"`{path}`")
            if path in graph:
                lines.append("Связан с:")
                for link in graph[path][:5]:
                    link_title = titles.get(link, link)
                    lines.append(f"- [{link_title}]({link})")
            lines.append("")

    return '\n'.join(lines)


def main():
    print_header("ГЕНЕРАЦИЯ КАРТЫ СВЯЗЕЙ", "🗺")

    print("Сканирование файлов...")
    graph, titles = build_graph()

    total_files = len(titles)
    total_links = sum(len(v) for v in graph.values())
    print(f"Файлов: {total_files}")
    print(f"Связей: {total_links}")

    # Генерируем Mermaid-диаграмму
    mermaid = generate_mermaid(graph, titles)
    text_map = generate_text_map(graph, titles)

    full_content = mermaid + "\n\n---\n\n## 📋 ТЕКСТОВАЯ КАРТА\n\n" + text_map

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print_success(f"Карта сохранена: {OUTPUT_FILE}")
    print_hint("Откройте в VS Code с плагином Mermaid для просмотра диаграммы")

    return 0


if __name__ == "__main__":
    sys.exit(main())