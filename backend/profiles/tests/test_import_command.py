from django.test import SimpleTestCase

from profiles.management.commands.import_csv import Command


class ImportCommandTests(SimpleTestCase):
    def setUp(self):
        self.command = Command()

    def test_extract_summary_uses_summary_position_relative_to_experience(self):
        values = [""] * 30

        experience_index = 20

        values[11] = "Experienced engineering professional"
        values[16] = "['washington, united states']"

        summary = self.command._extract_summary(
            values,
            experience_index,
        )

        self.assertEqual(
            summary,
            "Experienced engineering professional",
        )

    def test_extract_summary_does_not_return_location_names(self):
        values = [""] * 30

        experience_index = 20

        values[11] = "Experienced engineering professional"
        values[16] = "['washington, united states']"

        summary = self.command._extract_summary(
            values,
            experience_index,
        )

        self.assertNotEqual(
            summary,
            values[16],
        )