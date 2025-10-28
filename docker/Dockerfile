# cuz acsylla cant compile on alpine
FROM python:3.13-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential libffi-dev libssl-dev curl bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install uv

COPY pyproject.toml uv.lock* ./

RUN uv sync

COPY src ./src

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--loop", "uvloop"]
