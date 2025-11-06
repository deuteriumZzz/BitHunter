# BitHunter

## Технологический стек

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)  [![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)  [![DRF](https://img.shields.io/badge/DRF-3.14+-orange.svg)](https://www.django-rest-framework.org/)  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)  [![Redis](https://img.shields.io/badge/Redis-6+-red.svg)](https://redis.io/)  [![Celery](https://img.shields.io/badge/Celery-5+-yellow.svg)](https://docs.celeryq.dev/)  [![Channels](https://img.shields.io/badge/Channels-4+-purple.svg)](https://channels.readthedocs.io/)  [![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13+-orange.svg)](https://www.tensorflow.org/)  
[![Stable Baselines3](https://img.shields.io/badge/Stable%20Baselines3-2.0+-green.svg)](https://stable-baselines3.readthedocs.io/)  [![ccxt](https://img.shields.io/badge/ccxt-4+-blue.svg)](https://ccxt.readthedocs.io/)  [![NewsAPI](https://img.shields.io/badge/NewsAPI-1.0+-lightgrey.svg)](https://newsapi.org/)  [![TextBlob](https://img.shields.io/badge/TextBlob-0.17+-yellow.svg)](https://textblob.readthedocs.io/)  [![Cryptography](https://img.shields.io/badge/Cryptography-41+-green.svg)](https://cryptography.io/)  [![PyOTP](https://img.shields.io/badge/PyOTP-2.8+-blue.svg)](https://pyotp.readthedocs.io/)  [![Prometheus](https://img.shields.io/badge/Prometheus-2.40+-orange.svg)](https://prometheus.io/)  [![Sentry](https://img.shields.io/badge/Sentry-1.30+-red.svg)](https://sentry.io/)  [![Docker](https://img.shields.io/badge/Docker-20+-blue.svg)](https://www.docker.com/)  [![Gunicorn](https://img.shields.io/badge/Gunicorn-20+-green.svg)](https://gunicorn.org/)

## Описание

BitHunter — это полнофункциональное веб-приложение на основе Django для автоматизированного трейдинга криптовалют. Проект включает интеграцию машинного обучения (LSTM, reinforcement learning с Stable Baselines3), анализ новостей с sentiment-анализом, реал-тайм алерты через WebSocket, и безопасность с шифрованием и 2FA. Backend построен на Django REST Framework (DRF), с асинхронными задачами через Celery и Redis, а также мониторингом через Prometheus. Проект поддерживает демо-режим для тестирования стратегий без реальных сделок.

Проект разделён на backend (Django-приложения: accounts, alerts, analytics, api, news, trading) и frontend (отдельный интерфейс, не включён в репозиторий). Он предназначен для пользователей, интересующихся AI-поддерживаемым трейдингом на биржах вроде Binance.

**Предупреждение:** Трейдинг криптовалют связан с рисками. Используйте на свой страх и риск. Авторы не несут ответственности за финансовые потери.

**Статус проекта:** Проект находится на стадии разработки и предназначен для демонстрации концепции. MVP готов, но требует дальнейших доработок для продакшена.

## Ключевые функции

- **Аутентификация и безопасность**: JWT-токены, 2FA (TOTP), шифрование API-ключей (Fernet), middleware для защиты от атак.
- **Трейдинг**: Интеграция с биржами через ccxt (Binance и др.), демо-режим, ручные и автоматические стратегии.
- **Машинное обучение**: 
  - LSTM для предсказания цен на основе исторических данных.
  - Reinforcement learning (PPO из Stable Baselines3) для оптимизации стратегий с учётом новостей и sentiment-анализа.
  - Backtesting в кастомной среде TradingEnv с метриками (Sharpe ratio, VaR).
- **Аналитика и новости**: Sentiment-анализ новостей (TextBlob), интеграция с NewsAPI, реал-тайм обновления через WebSocket.
- **Алерты и уведомления**: Настраиваемые алерты по ценам/новостям, отправка через Telegram.
- **API**: RESTful API через DRF с пагинацией, фильтрацией и сериализацией.
- **Асинхронность**: Celery для фоновых задач (обучение моделей, уведомления), Channels для WebSocket.
- **Масштабируемость**: Redis для кэширования и очередей, PostgreSQL для БД, Prometheus для метрик.
- **Мониторинг и логирование**: Структурированные логи, интеграция с Sentry для ошибок.

## Требования

- **Python**: 3.8+
- **База данных**: PostgreSQL (рекомендуется для продакшена; SQLite для разработки)
- **Redis**: Для кэширования, очередей Celery и Channels
- **Зависимости**: См. `requirements.txt` (включает Django, DRF, TensorFlow, ccxt, NewsAPI и др.)
- **Система**: Linux/Windows/Mac (предпочтительно Linux для ML с GPU)
- **API-ключи**: Для бирж (Binance), NewsAPI, Telegram Bot (получите на соответствующих сайтах)
- **Опционально**: Docker для контейнеризации, AWS S3 для хранения моделей

## Установка

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/yourusername/bithunter.git
cd bithunter
```

### 2. Создайте виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения
- Скопируйте `.env.example` в `.env` (если файла нет, создайте его на основе settings.py).
- Заполните `.env`:
  ```
  SECRET_KEY=your-secret-key-here
  DEBUG=True  # False для продакшена
  DATABASE_URL=postgresql://user:password@localhost:5432/bithunter  # Или SQLite для теста
  REDIS_URL=redis://localhost:6379/0
  NEWS_API_KEY=your-newsapi-key
  TELEGRAM_BOT_TOKEN=your-telegram-token
  AWS_ACCESS_KEY_ID=your-aws-key  # Для S3
  AWS_SECRET_ACCESS_KEY=your-aws-secret
  AWS_S3_BUCKET_NAME=your-bucket
  DEMO_MODE=True  # True для демо, False для реального трейдинга
  ENCRYPTION_KEY=your-fernet-key-32-bytes  # Сгенерируйте с python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  PROMETHEUS_URL=http://localhost:9090  # Для мониторинга
  SENTRY_DSN=your-sentry-dsn  # Для логирования ошибок
  ```
- **Генерация ключей**: Для Fernet используйте команду выше. Для SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

### 5. Настройте базу данных
- Установите PostgreSQL и создайте базу данных `bithunter`.
- Или используйте SQLite для быстрого старта (измените DATABASE_URL в .env).
- Запустите миграции:
  ```bash
  python manage.py migrate
  ```

### 6. Создайте суперпользователя
```bash
python manage.py createsuperuser
```
- Следуйте инструкциям для ввода email, username и password.

### 7. (Опционально) Настройте AWS S3
- Если используете S3 для хранения ML-моделей, настройте bucket и ключи в .env.
- Модели сохраняются автоматически после обучения.

## Запуск

### Основной сервер
```bash
python manage.py runserver
```
- Доступно по http://localhost:8000 (admin: http://localhost:8000/admin/).
- Для продакшена используйте Gunicorn или uWSGI:
  ```bash
  gunicorn bithunter.wsgi:application --bind 0.0.0.0:8000
  ```

### Celery Worker (для асинхронных задач)
- Запустите в отдельном терминале (Redis должен быть запущен):
  ```bash
  celery -A bithunter worker -l info
  ```
- Для beat (периодические задачи, например, обучение моделей):
  ```bash
  celery -A bithunter beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
  ```

### WebSocket сервер (Channels)
- Запустите Daphne в отдельном терминале (Redis должен быть запущен):
  ```bash
  daphne -u /tmp/daphne.sock bithunter.asgi:application
  ```
- Или интегрируйте с основным сервером в продакшене.

### Redis
- Установите и запустите Redis:
  ```bash
  redis-server  # Или используйте Docker: docker run -d -p 6379:6379 redis:alpine
  ```

### Prometheus (для мониторинга)
- Скачайте Prometheus с https://prometheus.io/download/.
- Настройте `prometheus.yml` для scraping с http://localhost:8000/metrics.
- Запустите Prometheus:
  - Запустите `./prometheus --config.file=prometheus.yml`.

### Docker (опционально)
- Если есть docker-compose.yml (предполагается):
  ```bash
  docker-compose up -d
  ```
- Иначе создайте compose-файл для Django, Postgres, Redis.

## Использование

### Доступ к API
- API доступно через DRF. Используйте Postman или curl для тестирования.
- **Регистрация/логин**: POST /api/auth/login/ с username/password. Получите JWT-токен.
- **Добавление API-ключа**
