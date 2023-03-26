import logging

from elasticsearch import AsyncElasticsearch
from environs import Env
from quart import Quart, redirect, render_template, request
from tortoise import Tortoise

from init_scripts import run_init_check
from models import Document

env = Env()
env.read_env()

logging.basicConfig(level=logging.DEBUG)
es = None

app = Quart(
    __name__,
    template_folder="./_templates",
    static_folder="_static",
    static_url_path="/static",
)
app.config.from_prefixed_env("APP")


@app.route("/")
async def index():
    return await render_template("index.html")


@app.post("/search")
async def search():
    form = await request.form
    query = form["text"]
    doc_ids = await get_doc_ids_by_query(query)
    docs = await Document.filter(id__in=doc_ids).order_by("created_date")
    serialized_docs = serialize_docs(docs)

    return await render_template(
        "index.html", query=query, results=serialized_docs
    )


def serialize_docs(docs):
    return [
        {"id": doc.id, "text": doc.text, "date": doc.created_date}
        for doc in docs
    ]


async def get_doc_ids_by_query(query):
    res = await es.search(
        index=app.config["ES_INDEX"],
        size=20,
        body={"query": {"match": {"text": query}}},
    )
    return [i["_source"]["doc_id"] for i in res["hits"]["hits"]]


@app.post("/delete/<int:doc_id>")
async def delete_document(doc_id):
    db_document = await Document.get_or_none(id=doc_id)
    if db_document:
        db_document.delete()

    es_doc = await es.search(
        index=app.config["ES_INDEX"],
        size=1,
        body={"query": {"match": {"doc_id": doc_id}}},
    )
    if es_doc["hits"]["hits"]:
        _id = es_doc["hits"]["hits"][0]["_id"]
        await es.delete(index=app.config["ES_INDEX"], id=_id)

    return redirect("/")


@app.after_serving
async def app_shutdown():
    await Tortoise.close_connections()
    await es.close()


@app.before_serving
async def app_start():
    global es
    if app.config["SQLITE_PATH"]:
        db_url = f"sqlite://{app.config['SQLITE_PATH']}"
    else:
        db_url = "postgresql://{}:{}@{}:{}/{}".format(
            app.config["PG_USERNAME"],
            app.config["PG_PASS"],
            app.config["PG_HOST"],
            app.config["PG_PORT"],
            app.config["PG_DB_NAME"],
        )

    es = AsyncElasticsearch(
        f"http://{app.config['ES_HOST']}:{app.config['ES_PORT']}"
    )
    await Tortoise.init(db_url=db_url, modules={"models": ["models"]})
    await Tortoise.generate_schemas()
    await run_init_check(Document, es, es_index=app.config["ES_INDEX"])


if __name__ == "__main__":
    app.run()
