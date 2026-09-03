from django.conf import settings

from profiles.models import Profile
from profiles.search_index import get_client, ensure_index


class ProfileSearchService:
    def __init__(self, client=None):
        self.client = client or get_client()
        self.index = settings.ELASTICSEARCH_INDEX

    def search(self, query="", role="", country="", page=1, page_size=20):
        ensure_index(self.client)

        must = []
        filters = []
        query = query.strip()
        role = role.strip()
        country = country.strip()

        if query:
            must.append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "full_name^4",
                            "job_title^3",
                            "skills^2",
                            "summary",
                            "location_city",
                        ],
                        "fuzziness": "AUTO",
                        "operator": "and",
                    }
                }
            )
        else:
            must.append({"match_all": {}})

        if role:
            filters.append({"term": {"job_title_role": role}})
        if country:
            filters.append({"term": {"location_country": country}})

        body = {
            "from": max(page - 1, 0) * page_size,
            "size": page_size,
            "track_total_hits": True,
            "query": {"bool": {"must": must, "filter": filters}},
            "sort": [{"_score": "desc"}, {"full_name.keyword": "asc"}],
            "highlight": {
                "fields": {
                    "full_name": {},
                    "job_title": {},
                    "skills": {},
                    "summary": {},
                }
            },
        }

        response = self.client.search(index=self.index, body=body)
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]
        total = total["value"] if isinstance(total, dict) else total

        profiles = []
        highlights = {}
        ids = []
        for hit in hits:
            profile_id = hit["_source"].get("django_id")
            if profile_id is not None:
                ids.append(profile_id)
                highlights[str(profile_id)] = hit.get("highlight", {})

        if ids:
            profiles_by_id = Profile.objects.in_bulk(ids)
            for profile_id in ids:
                if profile_id in profiles_by_id:
                    profiles.append(profiles_by_id[profile_id])

        return profiles, total, highlights
