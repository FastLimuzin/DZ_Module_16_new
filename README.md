# Домашняя работа - Модуль 16 (Django)

## Задание 1
- Подключение к MS SQL Server, модель `User`.

## Задание 2
- Приложение `posts` с моделями `Post` и `Comment`, `STATIC` и `MEDIA`.

## Задание 3
- CRUD для `Post`, стили, templatetags.

## Задание 4
- Регистрация, вход, профиль, выход.

## Установка
1. Склонируйте: `git clone https://github.com/FastLimuzin/DZ_Module_16_new.git`
2. Создайте venv: `python -m venv .venv`
3. Активируйте: `.venv\Scripts\activate` (Windows)
4. Установите: `pip install -r requirements.txt`
5. Установите драйвер: [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
6. Скопируйте `.env_sample` в `.env` и настройте базу.
7. Создайте базу: `CREATE DATABASE your_db_name;`
8. Миграции: `python manage.py migrate`
9. Суперпользователь: `python manage.py createsuperuser`
10. Запуск: `python manage.py runserver`