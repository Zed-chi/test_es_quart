import logging
import os

from elasticsearch import AsyncElasticsearch
from init_scripts import run_init_check
from models import Document
from quart import Quart, render_template, request, redirect, url_for
from tortoise import Tortoise
from tortoise.contrib.quart import register_tortoise
from environs import Env

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
    text_results = None
    q = None
    if request.method == "POST":
        form = await request.form
        q = form["text"]
        res = await es.search(
            index="documents2", size=20, body={"query": {"match": {"text": q}}}
        )
        print(f'=== {res["hits"]["hits"][0]}')
        text_results = [
            {"text": i["_source"]["text"], "doc_id": i["_source"]["doc_id"]}
            for i in res["hits"]["hits"]
        ]

    return await render_template("index.html", query=q, results=text_results)


@app.post("/delete/<int:doc_id>")
async def delete_document(doc_id):
    db_document = await Document.get_or_none(id=doc_id)
    if db_document:
        db_document.delete()

    es_doc = await es.search(
        index="documents",
        size=20,
        body={"query": {"match": {"doc_id": doc_id}}},
    )

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
    await Tortoise.init(
        db_url="sqlite://./test.db", modules={"models": ["models"]}
    )
    await Tortoise.generate_schemas()
    await run_init_check(Document, es, es_index="documents2")


if __name__ == "__main__":
    app.run()
