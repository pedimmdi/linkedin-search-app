import csv
import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from profiles.models import Profile


class Command(BaseCommand):
    help = "Import LinkedIn profiles from CSV or JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "input_file",
            type=str,
            help="Path to the dataset file",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing profiles before importing",
        )

    def handle(self, *args, **options):
        file_path = options["input_file"]
        clear_existing = options["clear"]

        try:
            rows = self._load_rows(file_path)
        except (OSError, UnicodeDecodeError) as exc:
            raise CommandError(
                f"Unable to read file: {exc}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise CommandError(
                f"Invalid JSON file: {exc}"
            ) from exc

        profiles = [
            self._build_profile(row)
            for row in rows
        ]

        profiles = self._deduplicate(profiles)

        with transaction.atomic():
            if clear_existing:
                deleted_count, _ = Profile.objects.all().delete()

                self.stdout.write(
                    self.style.WARNING(
                        f"Deleted {deleted_count} existing records."
                    )
                )

            created_count = self._create_profiles(profiles)

        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed: {created_count} profiles created."
            )
        )

    def _load_rows(self, file_path):
        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as file:
            content = file.read().strip()

        if not content:
            raise CommandError("Input file is empty.")

        if content.startswith("[") or content.startswith("{"):
            data = json.loads(content)

            if isinstance(data, dict):
                data = [data]

            if not isinstance(data, list):
                raise CommandError(
                    "JSON root must be an object or array."
                )

            return data

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore",
            newline="",
        ) as file:
            return list(csv.DictReader(file))

    def _build_profile(self, row):
        return Profile(
            full_name=self._value(
                row,
                "full_name",
                "name",
                "fullName",
            ),
            linkedin_id=self._value(
                row,
                "linkedin_id",
            ),
            job_title=self._value(
                row,
                "job_title",
                "title",
                "jobTitle",
            ),
            job_title_role=self._value(
                row,
                "job_title_role",
                "role",
            ),
            skills=self._string_value(
                row.get("skills", "")
            ),
            location_country=self._value(
                row,
                "location_country",
                "country",
            ),
            location_city=self._value(
                row,
                "location_city",
                "city",
            ),
            summary=self._value(
                row,
                "summary",
                "about",
            ),
            linkedin_url=self._value(
                row,
                "linkedin_url",
                "url",
                "link",
            ),
        )

    @staticmethod
    def _value(row, *keys):
        for key in keys:
            value = row.get(key)

            if value is not None:
                value = str(value).strip()

                if value:
                    return value

        return ""

    @staticmethod
    def _string_value(value):
        if value is None:
            return ""

        if isinstance(value, (list, dict)):
            return json.dumps(
                value,
                ensure_ascii=False,
            )

        return str(value).strip()

    @staticmethod
    def _deduplication_key(profile):
        if profile.linkedin_url:
            return (
                "url",
                profile.linkedin_url.strip().lower(),
            )

        if profile.linkedin_id:
            return (
                "id",
                profile.linkedin_id.strip().lower(),
                profile.full_name.strip().lower(),
            )

        return (
            "fallback",
            profile.full_name.strip().lower(),
            profile.job_title.strip().lower(),
            profile.location_country.strip().lower(),
        )

    def _deduplicate(self, profiles):
        unique_profiles = {}
        duplicate_count = 0

        for profile in profiles:
            key = self._deduplication_key(profile)

            if key in unique_profiles:
                duplicate_count += 1
                continue

            unique_profiles[key] = profile

        if duplicate_count:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped {duplicate_count} duplicate records."
                )
            )

        return list(unique_profiles.values())

    def _create_profiles(self, profiles):
        if not profiles:
            return 0

        Profile.objects.bulk_create(
            profiles,
            batch_size=500,
        )

        return len(profiles)
