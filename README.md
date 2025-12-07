# 🎫 TicketingHub - Система продажи билетов на транспорт

Простая и надежная система для покупки электронных билетов на общественный транспорт.

## 🚀 Быстрый старт

### Требования
- Docker Desktop
- Git

### Запуск проекта

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd TicketingHub

# Запустите все сервисы
docker-compose up --build

# Откройте браузер
http://localhost/
```

Тестовый аккаунт: `admin` / `admin`

## 📦 Архитектура

Проект состоит из **5 контейнеров**:

1. **nginx** - Веб-сервер и reverse proxy
2. **backend** - Flask REST API (аутентификация, билеты, платежи)
3. **worker** - Фоновые задачи (уведомления)
4. **postgres** - База данных
5. **redis** - Кэш и очередь задач

## 🛠️ Технологии

- **Backend**: Flask + SQLAlchemy
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Proxy**: Nginx
- **Orchestration**: Docker Compose / Docker Swarm

## 📡 API Endpoints

### Аутентификация
- `POST /api/register` - Регистрация
- `POST /api/login` - Вход
- `GET /api/verify` - Проверка токена

### Билеты
- `GET /api/tickets` - Список билетов
- `POST /api/tickets` - Создать билет
- `GET /api/tickets/<id>` - Информация о билете
- `POST /api/tickets/<id>/validate` - Валидация билета

### Платежи
- `POST /api/payments` - Обработать платеж
- `GET /api/payments` - История платежей
- `GET /api/payments/<id>` - Информация о платеже

## 🐳 Docker Swarm

### Инициализация Swarm

```bash
# Инициализировать Swarm
docker swarm init

# Развернуть stack
docker stack deploy -c docker-stack.yml ticketinghub

# Проверить сервисы
docker service ls

# Логи сервиса
docker service logs ticketinghub_backend

# Масштабировать сервис
docker service scale ticketinghub_backend=5

# Удалить stack
docker stack rm ticketinghub
```

## 🔧 Разработка

### Запуск в режиме разработки

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m app

# Worker
cd worker
pip install -r requirements.txt
python worker.py
```

### Переменные окружения

Создайте `.env` файл:

```env
DATABASE_URL=postgresql://user:password@postgres:5432/ticketing_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here
```

## 📋 Функционал

- ✅ Регистрация и аутентификация (JWT)
- ✅ Покупка билетов (разовые, дневные, недельные, месячные)
- ✅ Обработка платежей
- ✅ История покупок
- ✅ Фоновые уведомления
- ✅ Респонсивный интерфейс

## 🧪 Тестирование

```bash
# Запустить тесты
docker-compose run backend pytest

# Проверить линтер
docker-compose run backend flake8
```

## 🔄 CI/CD

GitHub Actions автоматически:
- Проверяет код (flake8)
- Собирает Docker образы
- Запускает тесты

См. `.github/workflows/deploy.yml`

## 📝 Структура проекта

```
TicketingHub/
├── backend/           # Flask API
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── tickets.py
│   │   ├── payments.py
│   │   └── models.py
│   └── Dockerfile
├── worker/            # Background tasks
│   ├── worker.py
│   └── Dockerfile
├── frontend/          # Static files
│   ├── index.html
│   ├── style.css
│   └── app.js
├── nginx/             # Reverse proxy
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml # Local dev
├── docker-stack.yml   # Swarm prod
└── README.md
```

## 🎨 Скриншоты

Интерфейс доступен по адресу `http://localhost/`

- Современный градиентный дизайн
- Адаптивная верстка
- Простой и понятный UX

## 🤝 Вклад

1. Fork репозитория
2. Создайте feature branch
3. Commit изменения
4. Push в branch
5. Создайте Pull Request

## 📄 Лицензия

MIT License

## 👨‍💻 Автор

Ваше имя
