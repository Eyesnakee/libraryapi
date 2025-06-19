Library Management API
RESTful API для управления библиотечным каталогом с аутентификацией JWT. 
Реализован на FastAPI с использованием PostgreSQL и SQLAlchemy.
https://docs.google.com/document/d/1ej6Qdhf65VP6d8rPCti2wdiD680p91UKu6GQS7i-IKs/edit?tab=t.0

=== Требования:
- Python 3.8+
- PostgreSQL
- Установленные зависимостей

=== Инструкция запуска:
1. Создание виртуального окружения
2. Установка зависимостей 'pip install -r requirements.txt'
3. Настройка базы данных:
- createdb library_db
- psql -c "CREATE USER library_user WITH PASSWORD '3569';"
- psql -c "GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;"
4. Применение миграций 
- alembic upgrade head
5. Запуск сервера
- python main.py
Сервер запустится на http://localhost:8000. Документация API на http://localhost:8000/docs

=== Регистрация первого пользователя
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@library.com", "password": "securepassword"}'

=== Краткое описание структуры проекта:
-migrations/ # Миграции Alembic
-src/        # Исходный код приложения
--app/       # Основное приложение
---api/      # Эндпоинты
---core/     # Конфигурация и утилиты
---crud/     # Операции с БД
---db/       # Модели и сессии
---schemas/  # Pydantic схемы
---main.py   # FastAPI app
--tests/     # Тесты (Pytest)
-.env        # переменные окружения
-alembic.ini # Конфигурация Alembic
-main.py     # Точка входа (запуск сервера)

=== Таблицы
1. users - Библиотекари
- id, email (unique), hashed_password, created_at

2. books - Книги
- id, title, author, year, isbn (unique), copies_available, description

3. readers - Читатели
- id, name, email (unique)

4. borrowed_books - История выдачи
- id, book_id, reader_id, borrow_date, return_date

== Бизнес-логика
4.1: Выдача книги (POST /borrow)

Проверки:
Наличие доступных экземпляров (copies_available > 0)
У читателя < 3 активных выдач

Действия:
Уменьшение copies_available на 1
Создание записи в borrowed_books

4.2: Возврат книги (POST /borrow/return/{borrow_id})

Проверки:
Запись о выдаче существует
Книга ещё не возвращена (return_date = NULL)

Действия:
Увеличение copies_available на 1
Установка return_date

4.3: Защита от невалидных возвратов

Решение: Проверка статуса возврата в базе перед обработкой.


Сложности и решения:

Проблема: Конкурентное обновление copies_available.
Решение: Транзакции SQLAlchemy + блокировка записей.

Проблема: Проверка лимита книг у читателя.
Решение: Отдельный запрос подсчёта активных выдач.

== Аутентификация

Библиотеки:
1. python-jose для JWT
2. passlib[bcrypt] для хеширования паролей

Эндпоинты:
/auth/register - регистрация
/auth/login - получение токена

Механика:
Пароль хешируется bcrypt при регистрации.
При логине проверяется хеш.
Генерируется JWT с user_id в payload.
Токен проверяется в get_current_user.
Защищённые эндпоинты: Все, кроме /auth/* и / (управление данными требует прав библиотекаря).

Почему эти библиотеки?
python-jose - стандарт для JWT в Python
passlib - поддерживает современные алгоритмы (bcrypt)

== Творческая часть
Я бы добавил бронирование. Т.е. очереди на книги. 
Для этого нужно создать таблицу book_reservations, 
добавить модель в app/db/models.py. Создать 
app/crud/reservation.py, app/schemas/reservation.py,
app/api/reservation.py. И обновить app/crud/borrow.py,
а также app/main.py.
