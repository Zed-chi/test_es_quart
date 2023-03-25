from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


es = Elasticsearch("http://127.0.0.1:9200")

index_name = "documents"
body = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    "mappings": {
        "properties": {
            "doc_id": {"type": "text"},
            "text": {"type": "text"},
        }
    },
}
es.indices.create(index=index_name, mappings=body["mappings"])
es.close()
