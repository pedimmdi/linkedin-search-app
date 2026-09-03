from unittest.mock import Mock, patch

from django.urls import reverse
from rest_framework.test import APITestCase

from profiles.models import Profile


class ProfileSupportEndpointTests(APITestCase):
    def setUp(self):
        Profile.objects.create(
            full_name="John Doe",
            job_title_role="engineering",
            location_country="United States",
        )
        Profile.objects.create(
            full_name="Jane Smith",
            job_title_role="product",
            location_country="United Kingdom",
        )

    def test_filters_endpoint_returns_distinct_sorted_values(self):
        response = self.client.get(reverse("profile-filters"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["roles"], ["engineering", "product"])
        self.assertEqual(response.data["countries"], ["United Kingdom", "United States"])

    @patch("profiles.views.get_client")
    def test_health_endpoint_reports_healthy_dependencies(self, get_client):
        client = Mock()
        client.ping.return_value = True
        client.indices.exists.return_value = True
        get_client.return_value = client

        response = self.client.get(reverse("health-check"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ok")
        self.assertEqual(response.data["database"], "ok")
        self.assertEqual(response.data["elasticsearch"], "ok")
