import csv
from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

es = Elasticsearch("http://192.168.99.102:9200")
if es.ping():
    with open("posts.csv", "r", encoding="utf-8") as file:
        print("=> CSV opened")
        reader = csv.reader(file)

        # Считывает заголовок
        next(reader)

        for _id, (text, created_date, rubrics) in enumerate(reader, start=10):
            print(f"=> post doc {_id} to es")
            es.create(
                index="documents",
                id=_id,
                document={
                    "text": text,
                    "created_date": datetime.fromisoformat(created_date),
                    "rubrics": rubrics,
                },
            )
    es.close()

else:
    raise ConnectionError("Connection error with es instance while ping")
