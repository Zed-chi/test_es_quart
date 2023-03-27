# Тестовое задание для стажера Python

### Само задание - [ссылка](https://karpovilia.notion.site/Python-67777c95bdbe4e59856c59b707349f2d)

Простой поисковик по текстам документов.
Данные хранятся в БД по желанию, поисковый индекс в эластике.

# Запуск

1. Заполнить .env файлик в `./webapp`

```
APP_SQLITE_PATH=./test.db #Как вариант, либо прописать данные базы ПГ
APP_PG_USERNAME=postgres # по дефолту
APP_PG_PASS=postgres # по дефолту
APP_PG_HOST=192.168.99.102 # Например для виндового
APP_PG_PORT=5432 # по дефолту
APP_PG_DB_NAME=postgres # по дефолту
APP_ES_HOST=192.168.99.102 # Например для виндового
APP_ES_PORT=9200
APP_ES_INDEX= # Любое название индекса
APP_CSV_PATH=./posts.csv # В целом так и оставить
APP_SECRET=<...>
APP_DEBUG=False
APP_DB=SQLITE # SQLITE или PG на выбор
```

2)Запустить `docker-compose up` 3)
