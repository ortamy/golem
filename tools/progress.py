# tools/progress.py
import sys

def show_progress(current, total, label="", extra=0):
    """Универсальный прогресс-бар для всех скриптов

    Параметры:
        current: текущий номер итерации
        total: общее количество итераций
        label: текст метки (опционально)
        extra: дополнительное число для отображения (опционально)
    """
    percent = int(current / total * 100) if total > 0 else 0
    bar_len = 40
    filled = int(bar_len * current / total) if total > 0 else 0
    bar = '█' * filled + '░' * (bar_len - filled)

    extra_text = f" | {extra}" if extra else ""
    label_text = f" {label}" if label else ""

    sys.stdout.write(f'\r[{bar}] {percent}% ({current}/{total}){extra_text}{label_text}')
    sys.stdout.flush()


def finish_progress():
    """Завершает строку прогресса"""
    sys.stdout.write('\n')
    sys.stdout.flush()

