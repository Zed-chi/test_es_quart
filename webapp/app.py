from elasticsearch import AsyncElasticsearch
from quart import (
    Quart,
    render_template,
    redirect,
    request,
    Response,
    g,
    get_flashed_messages,
    jsonify,
    url_for,
)

es = AsyncElasticsearch("http://192.168.99.102:9200")


def is_es_empty():
    if es.count(index="documents")["count"] > 0:
        return
    populate_es()


def is_db_empty():
    pass


def create_app(mode="Development"):
    app = Quart(__name__, template_folder="./_templates")
    app.config.from_object(f"config.{mode}")
    return app


app = create_app()


@app.route("/")
async def index():
    return await render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
async def search():
    text_results = None
    q = None
    if request.method == "POST":
        form = await request.form
        q = form["text"]
        res = await es.search(
            index="documents", size=20, body={"query": {"match": {"text": q}}}
        )
        print(res)
        text_results = [i["_source"]["text"] for i in res["hits"]["hits"]]

    return await render_template("index.html", query=q, results=text_results)


@app.after_serving
async def app_shutdown():
    await es.close()


if __name__ == "__main__":
    app.run()
