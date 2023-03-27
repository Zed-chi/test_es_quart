# Тестовое задание для стажера Python

### Само задание - [ссылка](https://karpovilia.notion.site/Python-67777c95bdbe4e59856c59b707349f2d)

Простой поисковик по текстам документов.
Данные хранятся в БД по желанию, поисковый индекс в эластике.

# Запуск

1. Создать и заполнить `.env` файлик в папке `./webapp`

```
APP_DB=SQLITE               # SQLITE или PG на выбор
APP_SQLITE_PATH=./test.db   # Желаемый путь (в случае выбора SQLITE варианта базы)
APP_PG_USERNAME=postgres    # по дефолту (в случае выбора PG варианта базы)
APP_PG_PASS=postgres        # по дефолту (в случае выбора PG варианта базы)
APP_PG_HOST=db              #алиас на адрес контейнера с БД
APP_PG_PORT=5432            # по дефолту (в случае выбора PG варианта базы)
APP_PG_DB_NAME=postgres     # по дефолту (в случае выбора PG варианта базы)
APP_ES_HOST=elastic         #алиас на адрес контейнера с ES
APP_ES_PORT=9200            # по дефолту
APP_ES_INDEX=               # Любое название индекса
APP_CSV_PATH=./posts.csv    # Путь до csv файла с дампом (В целом так и оставить)
APP_SECRET=<...>
APP_DEBUG=False
APP_INIT_CONTENT_CHECK=True # Начальная проверка наполнености базы

```

2.Запустить `docker-compose up`

Глянуть адрес:
`docker network ls`
`docker inspect <сеть проекта>`

3. Пройти по адресу контейнера с питоно приложением

# Документация

Как смог описал, можно глянуть по адресу `/docs`
