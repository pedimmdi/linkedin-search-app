from django.conf import settings

from profiles.models import Profile
from profiles.search_index import ensure_index, get_client


class ProfileSearchService:
    SEARCH_FIELDS = [
        "full_name^4",
        "job_title^3",
        "skills^2",
        "summary",
        "location_city",
    ]

    def __init__(self, client=None):
        self.client = client or get_client()
        self.index = settings.ELASTICSEARCH_INDEX

    def _build_query(self, query="", role="", country=""):
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
                        "fields": self.SEARCH_FIELDS,
                        "fuzziness": "AUTO",
                        "operator": "and",
                    }
                }
            )
        else:
            must.append({"match_all": {}})

        if role:
            filters.append(
                {
                    "term": {
                        "job_title_role": role,
                    }
                }
            )

        if country:
            filters.append(
                {
                    "term": {
                        "location_country": country,
                    }
                }
            )

        return {
            "bool": {
                "must": must,
                "filter": filters,
            }
        }

    def _get_total(self, response):
        total = response["hits"]["total"]

        if isinstance(total, dict):
            return total["value"]

        return total

    def count(self, query="", role="", country=""):
        ensure_index(self.client)

        response = self.client.search(
            index=self.index,
            body={
                "size": 0,
                "track_total_hits": True,
                "query": self._build_query(
                    query=query,
                    role=role,
                    country=country,
                ),
            },
        )

        return self._get_total(response)

    def search(
        self,
        query="",
        role="",
        country="",
        page=1,
        page_size=20,
    ):
        ensure_index(self.client)

        body = {
            "from": max(page - 1, 0) * page_size,
            "size": page_size,
            "track_total_hits": True,
            "query": self._build_query(
                query=query,
                role=role,
                country=country,
            ),
            "sort": [
                {
                    "_score": "desc",
                },
                {
                    "full_name.keyword": "asc",
                },
            ],
            "highlight": {
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"],
                "fields": {
                    "full_name": {},
                    "job_title": {},
                    "skills": {},
                    "summary": {},
                },
            },
        }

        response = self.client.search(
            index=self.index,
            body=body,
        )

        hits = response["hits"]["hits"]
        total = self._get_total(response)

        profiles = []
        highlights = {}
        ids = []

        for hit in hits:
            profile_id = hit["_source"].get("django_id")

            if profile_id is None:
                continue

            ids.append(profile_id)
            highlights[str(profile_id)] = hit.get("highlight", {})

        if ids:
            profiles_by_id = Profile.objects.in_bulk(ids)

            for profile_id in ids:
                profile = profiles_by_id.get(profile_id)

                if profile is not None:
                    profiles.append(profile)

        return profiles, total, highlights