# CrazyFroot Shop Project

Магазин продажи цифровых аккаунтов GTA 5 (Epic Games и Rockstar Club)


## Локальный запуск
1) Создать новую БД PostgreSQL
2) Настроить вебхуки (Ngrok или аналогичные сервисы)
3) Создать новый .env файл (используя .env.example)
4) Запустить redis на локальной машине
5) Запустить первый терминал и прописать `celery -A src.utils.celery.celery worker --loglevel=info --pool=solo`
6) Запустить второй терминал и прописать `fastapi dev .\src\main.py`


## Запуск в Docker-контейнере
1) Выполнить шаги 2 и 3 из предыдущего пункта
2) Установить docker на свою систему
3) Прописать в консоли `docker compose up`, можно добавить флаг `-d`, если вам нужен терминал
