FROM python:3.13.11

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade pip wheel uv

COPY uv.lock pyproject.toml ./

RUN uv sync --locked --no-install-project --no-dev

COPY src .

CMD ["uv", "run", "fastapi", "run", "./main.py"]
