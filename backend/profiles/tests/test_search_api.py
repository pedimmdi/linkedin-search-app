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

    def _mock_count(self, total):
        return patch(
            "profiles.views.ProfileSearchService.count",
            return_value=total,
        )

    def test_search_by_name(self):
        with self._mock_count(1), self._mock_search([self.john], 1):
            response = self.client.get(
                reverse("profile-search"),
                {"q": "John"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["full_name"],
            "John Doe",
        )

    def test_filter_by_country(self):
        with self._mock_count(1), self._mock_search([self.jane], 1):
            response = self.client.get(
                reverse("profile-search"),
                {"country": "United Kingdom"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["location_country"],
            "United Kingdom",
        )

    def test_filter_by_role(self):
        with self._mock_count(1), self._mock_search([self.john], 1):
            response = self.client.get(
                reverse("profile-search"),
                {"role": "engineering"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["job_title_role"],
            "engineering",
        )

    def test_empty_search_returns_profiles(self):
        with self._mock_count(2), self._mock_search(
            [self.john, self.jane],
            2,
        ):
            response = self.client.get(
                reverse("profile-search"),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_combined_filters(self):
        with self._mock_count(1), self._mock_search([self.john], 1):
            response = self.client.get(
                reverse("profile-search"),
                {
                    "q": "engineer",
                    "role": "engineering",
                    "country": "United States",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["full_name"],
            "John Doe",
        )

    def test_pagination_returns_navigation_metadata(self):
        with self._mock_count(25), self._mock_search(
            [self.john],
            25,
        ):
            response = self.client.get(
                reverse("profile-search"),
                {"page": 1},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 25)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_second_page_has_previous_link(self):
        with self._mock_count(25), self._mock_search(
            [self.jane],
            25,
        ):
            response = self.client.get(
                reverse("profile-search"),
                {"page": 2},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 25)
        self.assertIsNone(response.data["next"])
        self.assertEqual(response.data["previous"], 1)

    def test_out_of_range_page_returns_400(self):
        with self._mock_count(20):
            response = self.client.get(
                reverse("profile-search"),
                {"page": 2},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "Requested page is out of range.",
        )
        self.assertEqual(response.data["count"], 20)
        self.assertEqual(response.data["results"], [])
        self.assertEqual(response.data["previous"], 1)

    def test_out_of_range_page_does_not_execute_search(self):
        with (
            self._mock_count(20),
            patch(
                "profiles.views.ProfileSearchService.search"
            ) as search_mock,
        ):
            response = self.client.get(
                reverse("profile-search"),
                {"page": 2},
            )

        self.assertEqual(response.status_code, 400)
        search_mock.assert_not_called()

    def test_search_returns_highlights(self):
        highlights = {
            str(self.john.pk): {
                "full_name": ["<em>John</em> Doe"],
            }
        }

        with self._mock_count(1), self._mock_search(
            [self.john],
            1,
            highlights,
        ):
            response = self.client.get(
                reverse("profile-search"),
                {"q": "John"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["results"][0]["highlights"]["full_name"][0],
            "<em>John</em> Doe",
        )

    def test_count_error_returns_503(self):
        with patch(
            "profiles.views.ProfileSearchService.count",
            side_effect=RuntimeError("Elasticsearch unavailable"),
        ):
            response = self.client.get(
                reverse("profile-search"),
                {"q": "John"},
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.data["detail"],
            "Search service is temporarily unavailable.",
        )

    def test_search_error_returns_503(self):
        with (
            self._mock_count(1),
            patch(
                "profiles.views.ProfileSearchService.search",
                side_effect=RuntimeError(
                    "Elasticsearch unavailable"
                ),
            ),
        ):
            response = self.client.get(
                reverse("profile-search"),
                {"q": "John"},
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.data["detail"],
            "Search service is temporarily unavailable.",
        )

    def test_response_contains_expected_structure(self):
        with self._mock_count(1), self._mock_search(
            [self.john],
            1,
        ):
            response = self.client.get(
                reverse("profile-search"),
                {"q": "John"},
            )

        self.assertEqual(response.status_code, 200)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        result = response.data["results"][0]

        self.assertIn("id", result)
        self.assertIn("full_name", result)
        self.assertIn("job_title", result)
        self.assertIn("job_title_role", result)
        self.assertIn("skills", result)
        self.assertIn("location_country", result)
        self.assertIn("highlights", result)