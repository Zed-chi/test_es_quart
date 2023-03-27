from dataclasses import dataclass
from datetime import datetime
from typing import List

from apps.main.views import get_doc_ids_by_query, serialize_docs
from db.models import Document
from quart import Blueprint, current_app, request
from quart_schema import validate_request, validate_response
from quart_schema.validation import DataSource


@dataclass
class SearchAPIQuery:
    text: str


@dataclass
class FoundedDocument:
    id: int
    text: str
    created_date: datetime
    rubrics: str


@dataclass
class SearchAPIResult:
    status: int
    results: List[FoundedDocument]


blueprint = Blueprint("api", __name__)


@blueprint.post("/documents/search")
@validate_request(SearchAPIQuery, source=DataSource.JSON)
@validate_response(SearchAPIResult, 201)
async def api_search():
    """API search documents endpoint"""
    data = await request.get_json()
    query = data["text"]
    doc_ids = await get_doc_ids_by_query(query)
    docs = await Document.filter(id__in=doc_ids).order_by("created_date")
    serialized_docs = serialize_docs(docs)

    return {"status": 201, "results": serialized_docs}


@blueprint.delete("/documents/<int:doc_id>")
async def api_delete_document(doc_id):
    """API delete document endpoint"""
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

    return {"status": 200, "message": "deleted"}
