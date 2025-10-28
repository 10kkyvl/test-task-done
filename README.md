# 📊 Сервіс інгесту подій та аналітики

## 🧩 Огляд
Це асинхронний сервіс для збору подій (event ingestion) і побудови простих аналітичних метрик (DAU, top events, retention).
Побудований на Litestar, з чергою NATS JetStream, гарячим шаром у ScyllaDB і холодним у ClickHouse.

---

## ⚙️ Архітектура
POST /events
   ↓
Backend (Litestar + msgspec)
   ↓
NATS JetStream (черга подій)
   ↓
Worker (консюмер)
   ↓
ScyllaDB ← гарячий шар (швидкий запис)
   ↓
ClickHouse ← холодний шар (аналітика)

Prometheus збирає метрики з backend’а (/metrics).

---

## 🚀 Запуск
docker-compose -f docker-compose-dev up -d

### Сервіси
- backend: REST API (інгест подій, аналітика)
- worker: Споживач із NATS, запис у ScyllaDB і ClickHouse
- nats: Черга повідомлень JetStream
- scylla: OLTP база для швидких записів
- clickhouse: OLAP база для аналітики
- prometheus: Збір метрик
- scylla-init / clickhouse-init: Ініціалізація схем баз
- data-importer: Імпорт історичних CSV-даних

### Порти
- Backend API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/schema/swagger
- Prometheus: http://127.0.0.1:9090
- Scylla: 9042
- ClickHouse: 8123

---

## 🔌 API

### POST /events
Приймає масив подій для запису.
Ідемпотентність забезпечується через event_id.

Приклад:
  [
    {
      "event_id": "uuid",
      "occurred_at": "2025-10-28T12:00:00Z",
      "user_id": 1,
      "event_type": "view_item",
      "properties": {"country": "UA"}
    }
  ]

201 Created — події прийнято у чергу

---

### GET /stats/dau?from=YYYY-MM-DD&to=YYYY-MM-DD
Повертає кількість унікальних користувачів (DAU) по днях.
Аналітичний запит у ClickHouse.

---

### GET /stats/top-events?from=YYYY-MM-DD&to=YYYY-MM-DD&limit=10
Повертає топ типів подій за кількістю.

---

### GET /stats/retention?start_date=YYYY-MM-DD&windows=3
Простий когортний ретеншн за днями.
Обчислюється безпосередньо у ClickHouse.

---

## 📦 Імпорт історичних даних
CSV-імпорт автоматично запускається у контейнері data-importer.
Можна виконати вручну:
  python import-events.py /data/events_sample.csv

Формат CSV:
  - event_id: UUID
  - occurred_at: ISO-8601
  - user_id: UInt64
  - event_type: String
  - properties: JSON-об’єкт

---

## 🧪 Тестування
Запуск юніт- та інтеграційних тестів:
  pytest -v

Інтеграційний шлях:
  POST /events → NATS → Worker → ClickHouse → GET /stats/dau

Unit-тест перевіряє ідемпотентність подій (один event_id — одна вставка).

---

## 📈 Продуктивність

### Методика
Навантаження через Vegeta:
  150 RPS, тривалість 30s, середній розмір батчу — 1 подія.

### Результати
- analytics_backend: 42.95% CPU, 114.7 MiB RAM — обробка HTTP
- analytics_worker: 55.81% CPU, 39.8 MiB RAM — запис у БД
- analytics_nats: 20.7% CPU, 35.6 MiB RAM — активна передача
- analytics_clickhouse: 0.75% CPU, 337.1 MiB RAM — аналітичні вставки
- analytics_scylla: 7.42% CPU, 93.8 MiB RAM — гарячий шар
- prometheus: 0.12% CPU, 21.4 MiB RAM — метрики

Середня латентність: 3.45 мс
Мінімум: 2.1 мс
Максимум: 29.82 мс

### Вузькі місця
- CPU backend і worker при пікових RPS
- ClickHouse і Scylla залишались стабільними

### Оптимізація
- Інсерт подій у Scylla батчами
- Горизонтальне масштабування backend/worker
- Перепис ingestion-частини та апі на Go або Rust

---

## 🔍 Спостережуваність
- Структуровані логи: timestamp, level, route, status_code, latency_ms
- Метрики Prometheus:
  - REQUEST_COUNT{status="<code>"} — кількість запитів по статусах
  - RPS — запити/секунда (оновлюється у middleware)

---

## 🛡️ Безпека та стабільність
- Валідація даних через msgspec (швидше за Pydantic)
- Rate-limit реалізовано middleware-ом у пам’яті (Litestar)
- Акуратна обробка кодів помилок (400, 429)

---
