# 🎨 Онлайн-рисовалка (Python + FastAPI)

## ⚡ Быстрый старт (Windows)

```batch
install.bat venv
start.bat
```

Или вручную (любая ОС):

```bash
# 1. Создать виртуальное окружение
python -m venv .venv

# 2. Активировать
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить
python main.py
```

Открой http://localhost:8000

## ⚠️ Важно: версия Python

**Требуется Python 3.11, 3.12 или 3.13.**

Python 3.14 (предрелизный) пока НЕ поддерживается, потому что `pydantic-core`
не выпустил готовых сборок (wheels) под него. Сборка из исходников требует Rust.

Скачай стабильный Python: https://www.python.org/downloads/

При установке на Windows **обязательно поставь галочку** `Add Python to PATH`.

## Структура проекта

```
risovalka-python/
├── main.py              # FastAPI приложение (точка входа)
├── database.py          # SQLite + WAL, инициализация таблиц
├── auth.py              # JWT + bcrypt
├── routes/
│   ├── __init__.py
│   ├── auth.py          # Регистрация / вход / выход / me
│   └── drawings.py      # CRUD рисунков (сохранение/загрузка)
├── static/
│   └── index.html       # Фронтенд (рисовалка)
├── data/                # Папка для базы SQLite (создаётся автоматически)
├── requirements.txt     # Зависимости Python
├── Dockerfile           # Для деплоя на Render (Docker runtime, опционально)
├── render.yaml          # Конфиг Render (Blueprint, Python runtime)
├── runtime.txt          # Версия Python для Render
├── install.bat          # Помощник установки (Windows)
└── start.bat            # Быстрый запуск (Windows)
```

## Почему нет __pycache__ и venv в архиве?

- **`__pycache__/`** — создаётся автоматически при запуске Python, не нужен в Git
- **`.venv/`** — виртуальное окружение создаёшь сам командой `python -m venv .venv`
- **`data/*.db`** — база данных создаётся автоматически при первом запуске

## Оптимизации фронтенда

- **Unified Pointer Events** — мышь, тач и стилус единообразно
- **requestAnimationFrame** — плавное рисование без лагов
- **High-DPI** — чёткий холст на Retina/AMOLED
- **Горизонтальный скролл панелей** — удобно на телефонах
- **Touch-action: none** — блокирует случайные жесты браузера
- **Крупные тач-зоны (44px+)** — все элементы управления
- **Lazy-load** миниатюр галереи
- **Адаптивные размеры** — clamp(), aspect-ratio, dvh
- **ResizeObserver** — холст всегда точно совпадает с размером контейнера

## Деплой на Render

Проект настроен на **Python runtime** через `render.yaml` (см. `buildCommand`/`startCommand`) —
Render соберёт и запустит его без Docker. `Dockerfile` в репозитории оставлен на случай,
если вы захотите переключиться на `runtime: docker` в `render.yaml`.

1. Залей код на GitHub
2. На Render выбери **New + → Blueprint**, подключи репозиторий — Render сам прочитает `render.yaml`
3. Проверь переменную `JWT_SECRET` — она генерируется автоматически (`generateValue: true`)
4. Нажми **Apply / Deploy**

Если диск (`disk:` в `render.yaml`) недоступен на вашем тарифе — удали секцию `disk` и
переменную `DATA_DIR`, база будет локальной (данные сотрутся при перезапуске контейнера).
