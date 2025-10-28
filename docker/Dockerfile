FROM python:3.13-alpine

RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    openssl-dev \
    curl \
    bash \
    make \
    linux-headers

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install uv

COPY pyproject.toml uv.lock* ./

RUN uv sync

COPY src ./src

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--loop", "uvloop"]