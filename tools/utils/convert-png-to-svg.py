#!/usr/bin/env python3
# tools/utils/convert-png-to-svg.py — конвертация PNG/JPEG/GIF/BMP иконок в SVG (v1.1)

import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = ROOT / "web" / "icons" / "source"
OUTPUT_DIR = ROOT / "web" / "icons" / "32"

# Настройки
TARGET_SIZE = 32
STROKE_COLOR = "#d4a843"
STROKE_WIDTH = 2

# Все поддерживаемые форматы
SUPPORTED_FORMATS = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.webp", "*.tiff"]


def png_to_svg(image_path, svg_path):
    """Конвертирует изображение в простой SVG через трассировку контура."""
    img = Image.open(image_path).convert("RGBA")
    img = img.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
    
    pixels = img.load()
    width, height = img.size
    
    # Находим непрозрачные пиксели
    paths = []
    visited = set()
    
    for y in range(height):
        for x in range(width):
            if (x, y) in visited:
                continue
            
            r, g, b, a = pixels[x, y]
            if a < 128:  # прозрачный
                continue
            
            # Начинаем новый путь с этой точки
            path = f"M{x},{y}"
            visited.add((x, y))
            
            # Идём вправо пока есть непрозрачные пиксели
            run_x = x + 1
            while run_x < width and (run_x, y) not in visited:
                _, _, _, a2 = pixels[run_x, y]
                if a2 >= 128:
                    visited.add((run_x, y))
                    run_x += 1
                else:
                    break
            
            if run_x - x > 1:
                path += f"h{run_x - x - 1}"
            
            paths.append(path)
    
    if not paths:
        print(f"⚠️ Не найдено контуров в {image_path.name}")
        return False
    
    # Собираем SVG
    paths_d = " ".join(paths)
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TARGET_SIZE} {TARGET_SIZE}" width="{TARGET_SIZE}" height="{TARGET_SIZE}">
  <path d="{paths_d}" stroke="{STROKE_COLOR}" stroke-width="{STROKE_WIDTH}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''
    
    svg_path.write_text(svg, encoding="utf-8")
    return True


def main():
    if not SOURCE_DIR.exists():
        print(f"❌ Папка не найдена: {SOURCE_DIR}")
        print("Поместите изображения в web/icons/source/")
        return
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Собираем все поддерживаемые форматы
    image_files = []
    for fmt in SUPPORTED_FORMATS:
        image_files.extend(sorted(SOURCE_DIR.glob(fmt)))
    
    if not image_files:
        print(f"❌ Нет изображений в {SOURCE_DIR}")
        print(f"   Поддерживаемые форматы: {', '.join(SUPPORTED_FORMATS)}")
        return
    
    converted = 0
    failed = 0
    
    for image_file in image_files:
        svg_name = image_file.stem + ".svg"
        svg_path = OUTPUT_DIR / svg_name
        
        print(f"🔄 {image_file.name} → {svg_name}...", end=" ")
        if png_to_svg(image_file, svg_path):
            print("✅")
            converted += 1
        else:
            print("❌")
            failed += 1
    
    print(f"\n✅ Конвертировано: {converted}")
    print(f"❌ Не удалось: {failed}")
    print(f"📁 Результат: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()