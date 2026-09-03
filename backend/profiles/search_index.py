from django.conf import settings
from elasticsearch import Elasticsearch


INDEX_NAME = settings.ELASTICSEARCH_INDEX

PROFILE_MAPPING = {
    "properties": {
        "full_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "linkedin_id": {"type": "keyword"},
        "job_title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "job_title_role": {"type": "keyword"},
        "skills": {"type": "text"},
        "location_country": {"type": "keyword"},
        "location_city": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "summary": {"type": "text"},
        "linkedin_url": {"type": "keyword"},
    }
}


def get_client():
    return Elasticsearch(settings.ELASTICSEARCH_URL, request_timeout=5)


def ensure_index(client=None):
    client = client or get_client()

    if client.indices.exists(index=INDEX_NAME):
        return False

    client.indices.create(
        index=INDEX_NAME,
        settings={"number_of_shards": 1, "number_of_replicas": 0},
        mappings=PROFILE_MAPPING,
    )
    return True
