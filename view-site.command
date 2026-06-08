#!/bin/bash
# Двойной клик в Finder → поднимает локальный сайт и открывает его в браузере.
# Остановить: закрыть это окно Терминала или нажать Ctrl+C.
cd "$(dirname "$0")" || exit 1
if [ ! -x .venv/bin/mkdocs ]; then
  echo "Настраиваю окружение (один раз, ~1 минута)…"
  python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt
fi
echo "Открою сайт в браузере через пару секунд…"
( sleep 3; open "http://localhost:8000/docusketch-help/" ) &
echo "Сайт запущен. Чтобы остановить — закрой это окно или нажми Ctrl+C."
exec .venv/bin/mkdocs serve
