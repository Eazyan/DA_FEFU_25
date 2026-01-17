# Система сбора и анализа данных с погодной станции

Полнофункциональная система мониторинга погоды с генерацией реалистичных данных, хранением в PostgreSQL и двумя дашбордами: кастомным в стиле неоморфизм и Redash для детальной аналитики.

## Функционал

- **Реалистичная генерация погодных данных** с корреляциями между параметрами
- **Красивый кастомный дашборд** в стиле неоморфизм с обновлениями в реальном времени
- **Redash для детальной аналитики** с SQL запросами и визуализациями
- **Jupyter Notebook** с глубоким анализом данных, статистикой и визуализациями
- **Docker Compose** - запуск всей системы одной командой
- **Интерактивные графики** температуры за 24 часа
- **Автоматическое обновление** данных каждые 5 секунд

## Архитектура

```
┌─────────────────┐
│  Генератор      │ ──> Генерирует реалистичные данные каждые 5 секунд
│  данных (Python)│
└────────┬────────┘
         │
         v
┌─────────────────┐
│   PostgreSQL    │ ──> Хранит все измерения
│   База данных   │
└────┬────────┬───┘
     │        │
     v        v
┌─────────┐ ┌──────────────────┐
│ Redash  │ │ Кастомный дашборд│ ──> localhost:8080
│         │ │  (Flask + HTML)  │
└─────────┘ └──────────────────┘
     ▲
     │ Кнопка "Подробная аналитика"
     │ ведет на localhost:5001
```

## Требования

- Docker 20.10+
- Docker Compose 2.0+

## Быстрый старт

1. **Клонировать репозиторий**
```bash
git clone https://github.com/eazyan/da_fefu_25
cd da_fefu_25
```

2. **Запустить систему**
```bash
docker compose up -d
```

3. **Дождаться инициализации** (30-60 секунд)

4. **Открыть дашборды**
   - Кастомный дашборд: http://localhost:8080
   - Redash аналитика: http://localhost:5001 (изменен с 5000 из-за конфликта с macOS Control Center)

## Доступ к сервисам

| Сервис | URL | Описание |
|--------|-----|----------|
| Кастомный дашборд | http://localhost:8080 | Главный интерфейс |
| Redash | http://localhost:5001 | Детальная аналитика и SQL запросы |
| PostgreSQL | localhost:5432 | База данных (credentials в .env) |

## Структура проекта

```
DA_FEFU_25/
├── docker-compose.yml           # Оркестрация всех сервисов
├── .env                         # Переменные окружения
├── README.md                    # Эта документация
├── .gitignore                   # Git ignore файл
│
├── data_generator/              # Генератор погодных данных
│   ├── Dockerfile
│   ├── requirements.txt
│   └── generator.py
│
├── database/                    # База данных
│   └── init.sql                 # SQL схема
│
└── dashboard/                   # Кастомный дашборд
    ├── Dockerfile
    ├── requirements.txt
    ├── app.py                   # Flask API
    ├── static/
    │   ├── css/
    │   │   └── neumorphism.css
    │   └── js/
    │       └── app.js
    └── templates/
        └── index.html
```

## Схема базы данных

### Таблица `weather_data`

| Поле | Тип | Диапазон | Описание |
|------|-----|----------|----------|
| id | SERIAL | - | Первичный ключ |
| timestamp | TIMESTAMP | - | Время измерения |
| temperature | DECIMAL(5,2) | -50°C до +50°C | Температура |
| humidity | DECIMAL(5,2) | 0% до 100% | Влажность |
| pressure | DECIMAL(6,2) | 950 до 1050 гПа | Давление |
| wind_speed | DECIMAL(5,2) | 0 до 50 м/с | Скорость ветра |
| wind_direction | INTEGER | 0 до 360° | Направление ветра |
| weather_condition | VARCHAR(50) | см. ниже | Состояние погоды |

**Погодные условия:**
- `sunny` - Солнечно
- `partly_cloudy` - Переменная облачность
- `cloudy` - Облачно
- `rainy` - Дождь
- `snowy` - Снег
- `foggy` - Туман

## API Endpoints (Кастомный дашборд)

### GET `/api/latest`
Получить последнее измерение погоды.

**Ответ:**
```json
{
  "id": 123,
  "timestamp": "2026-01-17T12:00:00+00:00",
  "temperature": 24.5,
  "humidity": 65.3,
  "pressure": 1013.2,
  "wind_speed": 12.5,
  "wind_direction": 135,
  "weather_condition": "partly_cloudy"
}
```

### GET `/api/history?hours=24`
Получить исторические данные.

**Параметры:**
- `hours` (опционально) - количество часов истории (по умолчанию 24)

### GET `/api/stats`
Получить статистику за 24 часа (мин/макс/средн).

## Генерация данных

Данные генерируются с реалистичными паттернами:

1. **Температура**: суточный цикл на основе синусоидальной волны
2. **Влажность**: обратно пропорциональна температуре
3. **Давление**: медленные градуальные изменения
4. **Погодные условия**: зависят от температуры и влажности
   - Снег: высокая влажность (>80%) + низкая температура (<5°C)
   - Дождь: высокая влажность (>70%)
   - Солнечно: низкая влажность (<40%)
   - Облачно: средняя влажность

## Настройка Redash

### Первый запуск

1. Откройте http://localhost:5001
2. Создайте учетную запись администратора
3. Добавьте источник данных PostgreSQL:
   - **Type**: PostgreSQL
   - **Name**: Weather Station
   - **Host**: postgres
   - **Port**: 5432
   - **Database**: weather_station
   - **User**: admin
   - **Password**: (из .env файла)

### Примеры SQL запросов

#### Тренд температуры за 24 часа
```sql
SELECT timestamp, temperature
FROM weather_data
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp;
```

#### Распределение погодных условий
```sql
SELECT weather_condition, COUNT(*) as count
FROM weather_data
GROUP BY weather_condition;
```

#### Статистика по всем параметрам
```sql
SELECT
  AVG(temperature) as avg_temp,
  MIN(temperature) as min_temp,
  MAX(temperature) as max_temp,
  AVG(humidity) as avg_humidity,
  AVG(pressure) as avg_pressure
FROM weather_data
WHERE timestamp > NOW() - INTERVAL '24 hours';
```

#### Корреляция температуры и влажности
```sql
SELECT temperature, humidity
FROM weather_data
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp;
```

## Управление системой

### Просмотр логов
```bash
# Все сервисы
docker compose logs -f

# Только генератор
docker compose logs -f data_generator

# Только дашборд
docker compose logs -f custom_dashboard
```

### Проверка статуса
```bash
docker compose ps
```

### Остановка системы
```bash
docker compose down
```

### Остановка с удалением данных
```bash
docker compose down -v
```

### Перезапуск сервиса
```bash
docker compose restart data_generator
```

## Проверка работоспособности

### 1. Проверка генерации данных
```bash
docker compose logs data_generator --tail 10
```

Ожидаемый вывод:
```
[2026-01-17 12:00:00] Generated: 24.5°C, 65.3%, 1013.2 hPa, 12.5 m/s, partly_cloudy
```

### 2. Проверка базы данных
```bash
docker compose exec postgres psql -U admin -d weather_station -c "SELECT COUNT(*) FROM weather_data;"
```

### 3. Проверка API
```bash
curl http://localhost:8080/api/latest
```

## Технические детали

### Используемые технологии

- **Backend**: Python 3.11, Flask 3.0
- **Database**: PostgreSQL 17
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Charts**: Chart.js 4.4
- **Analytics**: Redash (latest)
- **Orchestration**: Docker Compose

### Переменные окружения (.env)

```env
POSTGRES_DB=weather_station
POSTGRES_USER=admin
POSTGRES_PASSWORD=securepassword123
DATABASE_URL=postgresql://admin:securepassword123@postgres:5432/weather_station

GENERATION_INTERVAL=5

REDASH_DATABASE_URL=postgresql://admin:securepassword123@postgres:5432/redash
REDASH_SECRET_KEY=change_me_to_random_string_please
REDASH_COOKIE_SECRET=change_me_to_another_random_string
```

## Скриншоты

### Кастомный дашборд (Neumorphism)
![Основной дашборд](image.png)

### Redash Dashboard
![Дашборд с подробной аналитикой](image-1.png)

## Jupyter Notebook с анализом данных

В проекте включен [weather_analysis.ipynb](weather_analysis.ipynb) - подробный анализ погодных данных.

### Что включает notebook:

1. **Подключение к базе данных** - прямые SQL запросы к PostgreSQL
2. **Статистический анализ** - описательная статистика всех параметров
3. **Визуализация временных рядов** - динамика температуры, влажности, давления, ветра
4. **Корреляционный анализ** - матрица корреляций, scatter plots
5. **Анализ погодных условий** - распределение типов погоды, box plots
6. **Роза ветров** - визуализация направлений ветра
7. **Суточные паттерны** - анализ изменений по часам суток

### Запуск notebook:

```bash
# Установить зависимости
pip install -r notebook_requirements.txt

# Запустить Jupyter Notebook
jupyter notebook weather_analysis.ipynb
```

**Примечание:** Убедитесь, что система запущена (`docker-compose up -d`), чтобы notebook мог подключиться к базе данных.

## Возможные проблемы

### Порты заняты
Если порты 5001, 5432 или 8080 уже используются:
1. Остановите конфликтующие сервисы
2. Или измените порты в `docker-compose.yml`

### Redash не запускается
Подождите 1-2 минуты после запуска - Redash требует времени на инициализацию схемы базы данных.

### Данные не генерируются
Проверьте логи генератора:
```bash
docker-compose logs data_generator
```

## Разработка

### Изменение интервала генерации
В файле `.env` измените значение `GENERATION_INTERVAL` (в секундах).

### Изменение стилей
Отредактируйте `dashboard/static/css/neumorphism.css` и перезапустите:
```bash
docker-compose restart custom_dashboard
```

## Авторство

Проект создан в рамках курса по анализу данных в ДВФУ.

## Лицензия

MIT
