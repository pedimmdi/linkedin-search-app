from django.test import TestCase

from profiles.models import Profile


class ProfileModelTests(TestCase):
    def test_profile_string_representation(self):
        profile = Profile(
            full_name="John Doe",
        )

        self.assertEqual(
            str(profile),
            "John Doe",
        )

    def test_profile_without_name(self):
        profile = Profile()

        self.assertEqual(
            str(profile),
            "Unknown Profile",
        )