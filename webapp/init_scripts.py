import asyncio
import csv
import logging
from datetime import datetime

from db.models import Document
from elasticsearch import AsyncElasticsearch
from tortoise import Tortoise

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


async def check_db_empty(model, csv_path):
    """Checks row count and fills if empty"""
    db_docs_count = await model.all().count()
    if db_docs_count == 0:
        await populate_db_from_csv(model, csv_path)
    logger.info(db_docs_count)


async def check_es_index(es, es_index):
    """Checks if index exists and creates one"""
    index_exists = await es.indices.exists(index=es_index)
    logger.info(index_exists)

    if not index_exists:
        await create_es_index(es, es_index)


async def check_es_docs(es, es_index, model):
    """Checks docs count and fills with data if empty"""
    es_docs_count = (await es.count(index=es_index))["count"]
    logger.info(es_docs_count)

    db_docs_count = await model.all().count()

    perc_delta_diff_perc = get_diff(db_docs_count, es_docs_count)
    if perc_delta_diff_perc > 50:
        logger.info(f"perc = {perc_delta_diff_perc}")
        await populate_es_from_db(es, es_index, model)
        es_docs_count = (await es.count(index=es_index))["count"]
        logger.info(es_docs_count)


async def run_init_check(
    model, es, es_index="documents", csv_path="./posts.csv"
):
    await check_db_empty(model, csv_path)
    await check_es_index(es, es_index)
    await check_es_docs(es, es_index, model)


def get_diff(db_docs_count, es_docs_count):
    if db_docs_count == es_docs_count:
        return 0
    return (abs(db_docs_count - es_docs_count) / db_docs_count) * 100


async def populate_db_from_csv(model, csv_path):
    logger.info("=> populating db")
    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        # Считывает заголовок
        next(reader)

        for _id, (text, created_date, rubrics) in enumerate(reader):
            logger.info(f"=> post data to db {_id}")
            await model.create(
                text=text,
                rubrics=rubrics,
                created_date=datetime.fromisoformat(created_date),
            )


async def populate_es_from_db(es, index_name, model):
    documents = await model.all()
    for _id, doc in enumerate(documents):
        logger.info(f"=> populating es from db {_id}")
        await es.create(
            index=index_name,
            id=_id,
            document={
                "doc_id": doc.id,
                "text": doc.text,
            },
        )


async def create_es_index(
    es: AsyncElasticsearch,
    name: str,
):
    logger.info("=> creating es ind")
    mappings = {
        "properties": {
            "doc_id": {"type": "integer"},
            "text": {"type": "text"},
        }
    }

    await es.indices.create(index=name, mappings=mappings)


async def main():
    es = AsyncElasticsearch("http://192.168.99.102:9200")
    await Tortoise.init(
        db_url="sqlite://./test.db", modules={"models": ["__main__"]}
    )
    await Tortoise.generate_schemas()
    try:
        await run_init_check(Document, es=es, es_index="documents2")
    finally:
        await es.close()
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
