from dataclasses import dataclass

from db.models import Document
from quart import Blueprint, current_app, redirect, render_template, request
from quart_schema import validate_request
from quart_schema.validation import DataSource

blueprint = Blueprint("main", __name__)


@dataclass
class SearchQuery:
    text: str


@blueprint.route("/")
async def index():
    """Main page"""
    return await render_template("index.html")


@blueprint.post("/search")
@validate_request(SearchQuery, source=DataSource.FORM)
async def search():
    """Search endpoint for browser

    Receives 'text' from the form, returns
    page with result list.
    """
    form = await request.form
    query = form["text"]
    doc_ids = await get_doc_ids_by_query(query)
    docs = await Document.filter(id__in=doc_ids).order_by("created_date")
    serialized_docs = serialize_docs(docs)

    return await render_template(
        "index.html", query=query, results=serialized_docs
    )


@blueprint.post("/delete/<int:doc_id>")
async def delete_document(doc_id):
    """Delete endpoint for browser

    Receives 'doc_id' param from post request,
    deletes document from db, elastic index and
    returns to the home page.
    """
    db_document = await Document.get_or_none(id=doc_id)
    if db_document:
        db_document.delete()

    es_doc = await current_app.store["es"].search(
        index=current_app.config["ES_INDEX"],
        size=1,
        body={"query": {"match": {"doc_id": doc_id}}},
    )
    if es_doc["hits"]["hits"]:
        _id = es_doc["hits"]["hits"][0]["_id"]
        await current_app.store["es"].delete(
            index=current_app.config["ES_INDEX"], id=_id
        )

    return redirect("/")


def serialize_docs(docs):
    return [
        {
            "id": doc.id,
            "text": doc.text,
            "date": doc.created_date,
            "rubrics": doc.rubrics,
        }
        for doc in docs
    ]


async def get_doc_ids_by_query(query):
    res = await current_app.store["es"].search(
        index=current_app.config["ES_INDEX"],
        size=20,
        body={"query": {"match": {"text": query}}},
    )
    return [i["_source"]["doc_id"] for i in res["hits"]["hits"]]
