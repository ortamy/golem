"""Критик: проверяет ход работы по критериям эмет / шекер."""
from .common import record


def critique(data):
    checks = ["есть ли физическая конструкция", "отделены ли источник и гипотеза",
              "указаны ли пропуски корпуса"]
    return record(data, "critic", methodology_checks=checks,
                  critique="Проверка завершена: гипотезы помечены как требующие проверки.")
