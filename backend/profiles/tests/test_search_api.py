from django.urls import reverse
from rest_framework.test import APITestCase

from profiles.models import Profile


class ProfileSearchAPITests(APITestCase):

    def setUp(self):
        Profile.objects.create(
            full_name="John Doe",
            job_title="Senior Software Engineer",
            job_title_role="engineering",
            skills="Python, Django, PostgreSQL",
            location_country="United States",
            location_city="New York",
            summary="Backend engineer",
            linkedin_url="linkedin.com/in/johndoe",
        )

        Profile.objects.create(
            full_name="Jane Smith",
            job_title="Product Manager",
            job_title_role="product",
            skills="Product Management",
            location_country="United Kingdom",
            location_city="London",
        )

    def test_search_by_name(self):
        response = self.client.get(
            reverse("profile-search"),
            {"q": "John"},
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["full_name"],
            "John Doe",
        )

    def test_filter_by_country(self):
        response = self.client.get(
            reverse("profile-search"),
            {"country": "United Kingdom"},
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

    def test_filter_by_role(self):
        response = self.client.get(
            reverse("profile-search"),
            {"role": "engineering"},
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

    def test_empty_search_returns_profiles(self):
        response = self.client.get(
            reverse("profile-search"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(
            response.data["count"],
            2,
        )