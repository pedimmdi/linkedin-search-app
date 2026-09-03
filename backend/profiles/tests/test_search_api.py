from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase

from profiles.models import Profile


class ProfileSearchAPITests(APITestCase):
    def setUp(self):
        self.john = Profile.objects.create(
            full_name="John Doe",
            job_title="Senior Software Engineer",
            job_title_role="engineering",
            skills="Python, Django, PostgreSQL",
            location_country="United States",
            location_city="New York",
            summary="Backend engineer",
            linkedin_url="https://linkedin.com/in/johndoe",
        )
        self.jane = Profile.objects.create(
            full_name="Jane Smith",
            job_title="Product Manager",
            job_title_role="product",
            skills="Product Management",
            location_country="United Kingdom",
            location_city="London",
        )

    def _mock_search(self, profiles, total=None, highlights=None):
        return patch(
            "profiles.views.ProfileSearchService.search",
            return_value=(
                profiles,
                total if total is not None else len(profiles),
                highlights or {},
            ),
        )

    def test_search_by_name(self):
        with self._mock_search([self.john], 1):
            response = self.client.get(reverse("profile-search"), {"q": "John"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["full_name"], "John Doe")

    def test_filter_by_country(self):
        with self._mock_search([self.jane], 1):
            response = self.client.get(
                reverse("profile-search"), {"country": "United Kingdom"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_by_role(self):
        with self._mock_search([self.john], 1):
            response = self.client.get(
                reverse("profile-search"), {"role": "engineering"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_empty_search_returns_profiles(self):
        with self._mock_search([self.john, self.jane], 2):
            response = self.client.get(reverse("profile-search"))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data["count"], 2)

    def test_search_returns_highlights(self):
        highlights = {str(self.john.pk): {"full_name": ["<em>John</em> Doe"]}}
        with self._mock_search([self.john], 1, highlights):
            response = self.client.get(reverse("profile-search"), {"q": "John"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["results"][0]["highlights"]["full_name"][0],
            "<em>John</em> Doe",
        )

    def test_search_service_error_returns_503(self):
        with patch(
            "profiles.views.ProfileSearchService.search",
            side_effect=RuntimeError("Elasticsearch unavailable"),
        ):
            response = self.client.get(reverse("profile-search"), {"q": "John"})
        self.assertEqual(response.status_code, 503)
