# Tribe - Корпоративный сервис микроблогов

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)

Бэкенд-сервис для корпоративной платформы микроблогов с API для создания твитов, управления подписками и лайками.

## 🚀 Возможности

- ✅ Создание и удаление твитов
- ✅ Загрузка медиафайлов к твитам
- ✅ Система подписок на пользователей
- ✅ Лайки твитов
- ✅ Персональная лента по подпискам
- ✅ Swagger документация API
- ✅ Docker контейнеризация
- ✅ Аутентификация по API-ключу

## 📋 Требования

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.12 (для разработки)

## 🛠️ Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <your-repo-url>
cd Tribe
```

### 2. Настройка переменных окружения
Создайте файл .env в директории backend/, для примера можете воспользоваться файлом .env.example.

### 3. Запуск приложения

```bash
docker compose up -d --build
```

Приложение будет доступно по адресам:

* Frontend: http://localhost

* Backend API: http://localhost/api

* Swagger Docs: http://localhost/api/docs

### 4. Инициализация тестового пользователя и добавление пользователей.

Для тестирования API необходимо создать пользователя в базе данных с полем api_key=test. Без него фронтенд не будет корректно работать. Подключитесь к БД удобным способом и выполните:

```sql
INSERT INTO users (name, api_key) VALUES ('Test User', 'test');
```

Так как подразумевается, что соц.сеть корпоративная, то в эту же таблицу необходимо добавить сотрудников с уникальным API-ключом:

Пример:
```sql
INSERT INTO users (name, api_key) VALUES ('Иван Иванов', 'ExampleUniqueAP1key');
```

### 🔑 Аутентификация

Все эндпоинты требуют API-Ключ в заголовках. Он автоматически добавляется в заголовок через окно авторизации.

### API Endpoints

#### Твиты
* POST /api/tweets - Создать твит
* DELETE /api/tweets/{id} - Удалить твит
* GET /api/tweets - Получить ленту

#### Медиа
* POST /api/medias - Загрузить медиафайл(не используется на прямую)

#### Лайки
* POST /api/tweets/{id}/likes - Поставить лайк
* DELETE /api/tweets/{id}/likes - Убрать лайк

#### Пользователи
* POST /api/users/{id}/follow - Подписаться
* DELETE /api/users/{id}/follow - Отписаться
* GET /api/users/me - Мой профиль
* GET /api/users/{id} - Профиль пользователя

Полная документация доступна в *Swagger*: http://localhost:8000/docs


### Docker сервисы

* nginx: Прокси-сервер (порт 80)
* backend: FastAPI приложение
* db: PostgreSQL база данных


### Запуск тестов
```bash
cd backend
poetry run pytest -v # либо PYTHONPATH=$(pwd) pytest -v, если возникнет проблема с импортом модуля app
```

### Просмотр логов
```bash
docker compose logs backend
docker compose logs nginx
docker compose logs db
```

### Остановка и перезапуск
```bash
docker compose down
docker compose up -d --build
```

### Разработчики:
#### Backend
* Кельвич Богдан
#### Frontend
* Неизвестно


### Лицензия
Этот проект является копроративной разработкой.
