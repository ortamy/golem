#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord-бот «Голем» для поиска корней иврита из ТаНаХа.

Команды:
  /root <слово> — ищет корень в базе данных и возвращает смысл с примером.

Использование:
  Установите токен в переменной окружения DISCORD_TOKEN или в файле .env.
  Запустите: python bot.py
"""

import os
import json
import logging

import discord
from discord import app_commands
from discord.ext import commands

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("golem-bot")

# --- Константы ---
ROOTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "roots.json")
TOKEN_ENV_VAR = "DISCORD_TOKEN"
ACTIVITY_NAME = "ТаНаХ | /root"

# Цвета для embed-сообщений
COLOR_FOUND = 0x2ecc71      # зелёный — корень найден
COLOR_NOT_FOUND = 0xe74c3c  # красный — корень не найден
COLOR_INFO = 0x3498db       # синий — информация
COLOR_ERROR = 0xf1c40f      # жёлтый — ошибка


# --- Загрузка базы корней ---
def load_roots() -> dict:
    """
    Загружает базу корней из JSON-файла.

    Returns:
        dict: Словарь {слово: {root, meaning, example}}.
              Возвращает пустой словарь при ошибке загрузки.
    """
    if not os.path.exists(ROOTS_FILE):
        logger.error("Файл базы корней не найден: %s", ROOTS_FILE)
        return {}

    try:
        with open(ROOTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logger.error("Неверный формат базы корней: ожидается dict")
            return {}
        logger.info("Загружено %d корней из %s", len(data), ROOTS_FILE)
        return data
    except json.JSONDecodeError as e:
        logger.error("Ошибка парсинга JSON: %s", e)
        return {}
    except OSError as e:
        logger.error("Ошибка чтения файла: %s", e)
        return {}


# --- Загрузка токена ---
def load_token() -> str | None:
    """
    Загружает токен Discord из .env файла или переменной окружения.

    Returns:
        str | None: Токен или None, если не найден.
    """
    # Попытка загрузить из .env файла
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip("\"'")
                        if key == TOKEN_ENV_VAR and value:
                            return value
        except OSError:
            logger.warning("Не удалось прочитать .env файл")

    # Проверка переменной окружения
    token = os.getenv(TOKEN_ENV_VAR)
    if token:
        return token

    return None


# --- Инициализация бота ---
roots_db = load_roots()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# --- События ---
@bot.event
async def on_ready():
    """Вызывается при успешном подключении бота к Discord."""
    logger.info("Бот «Голем» подключён как %s", bot.user)
    await bot.change_presence(
        activity=discord.Game(name=ACTIVITY_NAME)
    )
    try:
        synced = await bot.tree.sync()
        logger.info("Синхронизировано %d слэш-команд", len(synced))
    except Exception as e:
        logger.error("Ошибка синхронизации команд: %s", e)


# --- Команды ---
@bot.tree.command(
    name="root",
    description="Найти корень ивритского слова в ТаНаХе",
)
@app_commands.describe(
    word="Слово на иврите (например, אהב, ברא, שמר)",
)
async def root_command(
    interaction: discord.Interaction,
    word: str,
):
    """
    Обрабатывает команду /root.

    Ищет слово в базе корней и возвращает:
    - Корень
    - Смысл
    - Пример из ТаНаХа

    Args:
        interaction: Объект взаимодействия Discord.
        word: Слово для поиска (иврит).
    """
    # Деферим ответ сразу, чтобы не было таймаута
    await interaction.response.defer()

    word = word.strip()

    if not word:
        embed = discord.Embed(
            title="❌ Ошибка",
            description="Пожалуйста, укажите слово для поиска.\nПример: `/root אהב`",
            color=COLOR_ERROR,
        )
        await interaction.followup.send(embed=embed)
        return

    # Проверка, загружена ли база
    if not roots_db:
        embed = discord.Embed(
            title="⚠️ База не загружена",
            description="База корней не найдена или повреждена.",
            color=COLOR_ERROR,
        )
        await interaction.followup.send(embed=embed)
        return

    # Поиск слова в базе
    entry = roots_db.get(word)

    if entry is None:
        # Пробуем найти по ключу с другим вариантом написания (например, с добавлением / без огласовок)
        embed = discord.Embed(
            title=f"🔍 «{word}» — пока нет в базе",
            description=(
                f"Слово **{word}** пока не добавлено в базу корней.\n\n"
                "Попробуйте поискать с другим написанием "
                "или предложите добавить это слово в следующих версиях."
            ),
            color=COLOR_NOT_FOUND,
        )
        embed.set_footer(text="Голем — база корней ТаНаХа")
        await interaction.followup.send(embed=embed)
        return

    # Извлекаем данные
    root = entry.get("root", "—")
    meaning = entry.get("meaning", "—")
    example = entry.get("example", "—")

    # Формируем ответ
    embed = discord.Embed(
        title=f"📖 Корень слова «{word}»",
        color=COLOR_FOUND,
    )

    embed.add_field(
        name="🔤 Корень",
        value=root,
        inline=True,
    )
    embed.add_field(
        name="📜 Смысл",
        value=meaning,
        inline=True,
    )
    embed.add_field(
        name="\u200b",  # пустой невидимый разделитель
        value="\u200b",
        inline=True,
    )
    embed.add_field(
        name="📖 Пример из ТаНаХа",
        value=example,
        inline=False,
    )

    embed.set_footer(text="Голем — палео-ивритские корни | /root")
    embed.set_thumbnail(url="https://img.icons8.com/color/48/000000/scroll.png")

    await interaction.followup.send(embed=embed)


@bot.tree.command(
    name="about",
    description="Информация о боте «Голем»",
)
async def about_command(interaction: discord.Interaction):
    """Показывает информацию о боте."""
    embed = discord.Embed(
        title="🤖 Бот «Голем»",
        description=(
            "Поиск корней иврита из ТаНаХа.\n\n"
            "Проект «Голем» — исследование палео-ивритских корней, "
            "восстановление оригинальных образов букв и смыслов ТаНаХа."
        ),
        color=COLOR_INFO,
    )
    embed.add_field(
        name="📊 База корней",
        value=f"{len(roots_db)} корней",
        inline=True,
    )
    embed.add_field(
        name="📝 Команды",
        value="`/root <слово>` — найти корень\n`/about` — информация",
        inline=True,
    )
    embed.add_field(
        name="🔗 Проект",
        value="[Голем на GitHub](https://github.com/ortamy/golem)",
        inline=False,
    )
    embed.set_footer(text="Голем — палео-ивритские корни | /about")
    await interaction.response.send_message(embed=embed)


# --- Точка входа ---
def main():
    """Главная функция запуска бота."""
    token = load_token()

    if not token:
        logger.error(
            "Токен не найден! Укажите DISCORD_TOKEN в файле .env "
            "или в переменной окружения."
        )
        print("=" * 60)
        print("❌ ТОКЕН НЕ НАЙДЕН")
        print("=" * 60)
        print()
        print("Создайте файл .env в папке бота со следующим содержимым:")
        print()
        print("  DISCORD_TOKEN=ваш_токен_здесь")
        print()
        print("Или установите переменную окружения DISCORD_TOKEN.")
        print()
        return

    if not roots_db:
        logger.warning("База корней пуста. Бот будет работать с ограниченной функциональностью.")

    logger.info("Запуск бота «Голем»...")
    bot.run(token)


if __name__ == "__main__":
    main()