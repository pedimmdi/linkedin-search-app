from unittest.mock import Mock

from django.test import TestCase

from profiles.models import Profile
from profiles.services.search import ProfileSearchService


class ProfileSearchServiceTests(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create(
            full_name="John Doe",
            job_title="Senior Software Engineer",
            job_title_role="engineering",
            skills="Python, Django",
            location_country="United States",
            location_city="New York",
        )

    def _client(self, hits=None, total=1):
        client = Mock()
        client.indices.exists.return_value = True
        client.search.return_value = {
            "hits": {
                "total": {"value": total},
                "hits": hits or [],
            }
        }
        return client

    def test_search_builds_fuzzy_ranked_query(self):
        client = self._client(
            [{
                "_source": {"django_id": self.profile.pk},
                "highlight": {"full_name": ["<em>John</em> Doe"]},
            }]
        )

        profiles, total, highlights = ProfileSearchService(client).search(
            query="Jon", role="engineering", country="United States", page=2, page_size=20
        )

        body = client.search.call_args.kwargs["body"]
        query = body["query"]["bool"]["must"][0]["multi_match"]

        self.assertEqual(profiles, [self.profile])
        self.assertEqual(total, 1)
        self.assertIn("full_name^4", query["fields"])
        self.assertEqual(query["fuzziness"], "AUTO")
        self.assertEqual(body["from"], 20)
        self.assertEqual(body["query"]["bool"]["filter"], [
            {"term": {"job_title_role": "engineering"}},
            {"term": {"location_country": "United States"}},
        ])
        self.assertEqual(
            highlights[str(self.profile.pk)]["full_name"][0],
            "<em>John</em> Doe",
        )

    def test_empty_query_uses_match_all(self):
        client = self._client(
            [{"_source": {"django_id": self.profile.pk}], total=1
        )
        ProfileSearchService(client).search()
        body = client.search.call_args.kwargs["body"]
        self.assertEqual(body["query"]["bool"]["must"], [{"match_all": {}}])
