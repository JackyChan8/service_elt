# Проект ELT Сервис

### [Документация Swagger](http://127.0.0.1:8000/swagger_docs)
### [Логи](./logs/file_1.log)
### [Переменное окружение](./.env)
### [Зависимости](./requirements.txt)

## Запуск Проекта:
```shell
docker compose -f docker-compose.yml up -d
```

## Миграции:

### Создать миграцию:
```shell
alembic revision --autogenerate -m "Comment"
```

### Применить миграцию:
```shell
alembic upgrade heed
```

## Python Версия: ```3.12.0```
