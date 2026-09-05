import ast
import csv
import json
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from profiles.models import Profile


class Command(BaseCommand):
    help = "Import LinkedIn profiles from CSV or JSON file"

    KNOWN_COUNTRIES = {
        "united states",
        "united kingdom",
        "canada",
        "france",
        "germany",
        "australia",
        "singapore",
        "china",
        "mexico",
        "japan",
        "india",
        "iraq",
    }

    KNOWN_JOB_ROLES = {
        "accounting",
        "administrative",
        "arts_and_design",
        "business_development",
        "consulting",
        "customer_service",
        "education",
        "engineering",
        "finance",
        "health",
        "healthcare",
        "human_resources",
        "information_technology",
        "legal",
        "marketing",
        "media",
        "military",
        "operations",
        "product_management",
        "public_relations",
        "real_estate",
        "recruiting",
        "research",
        "sales",
        "software",
        "strategy",
        "support",
        "supply_chain",
        "project_management",
    }

    LINKEDIN_URL_PATTERN = re.compile(
        r"^(https?://)?(www\.)?linkedin\.com/in/[^/\s]+/?$",
        re.IGNORECASE,
    )

    LINKEDIN_ID_PATTERN = re.compile(r"^\d+$")

    DATE_PATTERN = re.compile(
        r"^\d{4}-\d{2}(?:-\d{2})?$"
    )

    NUMERIC_PATTERN = re.compile(
        r"^\d+(?:\.\d+)?$"
    )

    FILE_PATH_PATTERN = re.compile(
        r"^[A-Za-z]:\\",
    )

    GEO_PATTERN = re.compile(
        r"^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$",
    )

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
        try:
            rows = self._load_rows(options["input_file"])
        except (OSError, UnicodeDecodeError) as exc:
            raise CommandError(f"Unable to read file: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON file: {exc}") from exc

        raw_count = len(rows)

        profiles = []
        rejected_reasons = {}

        for row_number, row in enumerate(rows, start=1):
            profile_data = self._extract_profile_data(row)

            if profile_data is None:
                reason = self._get_rejection_reason(row)

                rejected_reasons[reason] = (
                    rejected_reasons.get(reason, 0) + 1
                )

                continue

            profiles.append(
                Profile(**profile_data)
            )

        profiles, duplicate_count = self._deduplicate(profiles)

        with transaction.atomic():
            if options["clear"]:
                deleted_count, _ = Profile.objects.all().delete()

                self.stdout.write(
                    self.style.WARNING(
                        f"Deleted {deleted_count} existing records."
                    )
                )

            created_count, existing_count = self._create_profiles(
                profiles
            )

        rejected_count = raw_count - len(profiles) - duplicate_count

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("Import completed")
        )
        self.stdout.write(
            f"Raw records: {raw_count}"
        )
        self.stdout.write(
            f"Successfully parsed: {raw_count - rejected_count}"
        )
        self.stdout.write(
            f"Rejected records: {rejected_count}"
        )
        self.stdout.write(
            f"Duplicates in input: {duplicate_count}"
        )
        self.stdout.write(
            f"Existing profiles skipped: {existing_count}"
        )
        self.stdout.write(
            f"Profiles created: {created_count}"
        )

        if rejected_reasons:
            self.stdout.write("")
            self.stdout.write("Rejection reasons:")

            for reason, count in sorted(
                rejected_reasons.items(),
                key=lambda item: item[1],
                reverse=True,
            ):
                self.stdout.write(
                    f"- {reason}: {count}"
                )

    def _load_rows(self, file_path):
        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore",
            newline="",
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
            reader = csv.reader(file)

            try:
                header = next(reader)
            except StopIteration:
                return []

            rows = []

            for row in reader:
                rows.append(row)

            return [
                dict(zip(header, row))
                for row in rows
            ]

    def _extract_profile_data(self, row):
        if not isinstance(row, dict):
            return None

        values = list(row.values())

        identity = self._extract_identity(values)

        if identity is None:
            return None

        full_name, linkedin_url, linkedin_id = identity

        if not self._is_valid_name(full_name):
            return None

        experience_index, experience = self._find_experience(values)

        if experience_index is not None:
            skills = self._extract_relative_list(
                values,
                experience_index - 5,
            )

            location_names = self._extract_relative_list(
                values,
                experience_index - 4,
            )

            countries = self._extract_relative_list(
                values,
                experience_index - 2,
            )

            summary = self._extract_summary(
                values,
                experience_index,
            )
        else:
            skills = []
            location_names = []
            countries = []
            summary = ""

        location_city, location_country = self._extract_location(
            location_names,
            countries,
        )

        job_title, job_title_role = self._extract_job_fields(
            experience,
            values,
            experience_index,
        )

        return {
            "full_name": full_name,
            "linkedin_id": linkedin_id,
            "job_title": job_title,
            "job_title_role": job_title_role,
            "skills": self._normalize_skills(skills),
            "location_country": location_country,
            "location_city": location_city,
            "summary": summary,
            "linkedin_url": linkedin_url,
        }

    def _extract_identity(self, values):
        for index, value in enumerate(values):
            value = str(value or "").strip()

            if not self.LINKEDIN_URL_PATTERN.match(value):
                continue

            linkedin_url = self._normalize_linkedin_url(value)

            name_index = index - 4

            if name_index < 0:
                continue

            full_name = str(
                values[name_index] or ""
            ).strip()

            if not self._is_valid_name(full_name):
                continue

            linkedin_id = ""

            for candidate in values[index + 1:index + 5]:
                candidate = str(
                    candidate or ""
                ).strip()

                if self.LINKEDIN_ID_PATTERN.match(candidate):
                    linkedin_id = candidate
                    break

            return (
                full_name,
                linkedin_url,
                linkedin_id,
            )

        return None

    def _extract_skills(self, values):
        for index in range(
            20,
            min(60, len(values) - 3),
        ):
            skills = self._parse_list(values[index])
            location_names = self._parse_list(
                values[index + 1]
            )
            regions = self._parse_list(
                values[index + 2]
            )
            countries = self._parse_list(
                values[index + 3]
            )

            if not isinstance(skills, list):
                continue

            if not isinstance(location_names, list):
                continue

            if not isinstance(regions, list):
                continue

            if not isinstance(countries, list):
                continue

            if not skills:
                continue

            if not all(
                isinstance(item, str)
                for item in skills
            ):
                continue

            if not all(
                isinstance(item, str)
                for item in location_names
            ):
                continue

            if not all(
                isinstance(item, str)
                for item in countries
            ):
                continue

            normalized_countries = {
                item.strip().lower()
                for item in countries
                if item.strip()
            }

            if not normalized_countries:
                continue

            if not normalized_countries.issubset(
                self.KNOWN_COUNTRIES
            ):
                continue

            if not any(
                "," in item
                for item in location_names
            ):
                continue

            return index, skills

        return None, []

    def _find_experience(self, values):
        for index, value in enumerate(values):
            parsed = self._parse_list(value)

            if not isinstance(parsed, list):
                continue

            if not parsed:
                continue

            if not all(
                isinstance(item, dict)
                for item in parsed
            ):
                continue

            first = parsed[0]

            if not isinstance(first.get("title"), dict):
                continue

            if "company" not in first:
                continue

            return index, parsed

        return None, None


    def _extract_relative_list(self, values, index):
        if index is None:
            return []

        if index < 0 or index >= len(values):
            return []

        parsed = self._parse_list(
            values[index]
        )

        if isinstance(parsed, list):
            return parsed

        return []


    def _extract_summary(self, values, experience_index):
        if experience_index is None:
            return ""

        summary_index = experience_index - 9

        if summary_index < 0:
            return ""

        value = str(
            values[summary_index] or ""
        ).strip()

        if not value:
            return ""

        if self._looks_like_phone_list(value):
            return ""

        return value

    def _extract_location(
        self,
        location_names,
        countries,
    ):
        city = ""
        country = ""

        if location_names:
            first_location = str(
                location_names[0] or ""
            ).strip()

            if first_location:
                parts = [
                    part.strip()
                    for part in first_location.split(",")
                    if part.strip()
                ]

                if parts:
                    city = parts[0]

        if countries:
            first_country = str(
                countries[0] or ""
            ).strip().lower()

            if first_country in self.KNOWN_COUNTRIES:
                country = first_country

        return city, country

    def _extract_job_fields(
        self,
        experience,
        values,
        experience_index,
    ):
        if experience:
            primary = next(
                (
                    item
                    for item in experience
                    if item.get("is_primary")
                ),
                experience[0],
            )

            title = primary.get("title") or {}

            job_title = str(
                title.get("name") or ""
            ).strip()

            job_title_role = str(
                title.get("role") or ""
            ).strip().lower()

            if job_title and not self._looks_like_bad_job_title(
                job_title
            ):
                return (
                    job_title,
                    job_title_role,
                )

        fallback_title = self._find_fallback_job_title(
            values,
            experience_index,
        )

        return fallback_title, ""

    @staticmethod
    def _looks_like_phone_list(value):
        parsed = Command._parse_list(value)

        if not isinstance(parsed, list):
            return False

        if not parsed:
            return False

        return all(
            isinstance(item, str)
            and re.fullmatch(
                r"\+?\d[\d\s().-]+",
                item.strip(),
            )
            for item in parsed
        )

    @classmethod
    def _normalize_linkedin_url(cls, value):
        value = str(value or "").strip()

        if not value:
            return ""

        value = value.rstrip("/")

        lower_value = value.lower()

        if lower_value.startswith(
            "http://linkedin.com/"
        ):
            return "https://" + value[
                len("http://") :
            ]

        if lower_value.startswith(
            "https://linkedin.com/"
        ):
            return value

        if lower_value.startswith(
            "https://www.linkedin.com/"
        ):
            return value

        if lower_value.startswith(
            "linkedin.com/"
        ):
            return f"https://{value}"

        if lower_value.startswith(
            "www.linkedin.com/"
        ):
            return f"https://{value}"

        return value

    def _is_valid_name(self, value):
        value = str(value or "").strip()

        if not value:
            return False

        if len(value) > 100:
            return False

        if self.FILE_PATH_PATTERN.match(value):
            return False

        if "part-00001.csv" in value.lower():
            return False

        if self.LINKEDIN_URL_PATTERN.match(value):
            return False

        if self.LINKEDIN_ID_PATTERN.match(value):
            return False

        return True

    @staticmethod
    def _normalize_skills(skills):
        if not skills:
            return ""

        normalized = []

        for skill in skills:
            skill = str(skill).strip()

            if not skill:
                continue

            if skill not in normalized:
                normalized.append(skill)

        return ", ".join(normalized)

    @staticmethod
    def _parse_list(value):
        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return []

        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return None

        if isinstance(parsed, list):
            return parsed

        return None

    def _get_rejection_reason(self, row):
        if not isinstance(row, dict):
            return "invalid row"

        values = list(row.values())

        identity = self._extract_identity(values)

        if identity is None:
            return "missing reliable LinkedIn identity"

        if not self._is_valid_name(identity[0]):
            return "invalid profile name"

        skills_index, _ = self._extract_skills(values)

        if skills_index is None:
            return "unable to validate profile structure"

        return "failed profile extraction"

    @staticmethod
    def _deduplication_key(profile):
        linkedin_url = (
            profile.linkedin_url or ""
        ).strip().lower()

        if linkedin_url:
            return (
                "url",
                linkedin_url,
            )

        linkedin_id = (
            profile.linkedin_id or ""
        ).strip().lower()

        if linkedin_id:
            return (
                "id",
                linkedin_id,
                (
                    profile.full_name or ""
                ).strip().lower(),
            )

        return (
            "fallback",
            (
                profile.full_name or ""
            ).strip().lower(),
            (
                profile.job_title or ""
            ).strip().lower(),
            (
                profile.location_country or ""
            ).strip().lower(),
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

        return (
            list(unique_profiles.values()),
            duplicate_count,
        )

    def _create_profiles(self, profiles):
        if not profiles:
            return 0, 0

        existing_profiles = Profile.objects.only(
            "linkedin_url",
            "linkedin_id",
            "full_name",
            "job_title",
            "location_country",
        ).iterator(
            chunk_size=500
        )

        existing_keys = {
            self._deduplication_key(profile)
            for profile in existing_profiles
        }

        new_profiles = []
        existing_count = 0

        for profile in profiles:
            key = self._deduplication_key(profile)

            if key in existing_keys:
                existing_count += 1
                continue

            new_profiles.append(profile)
            existing_keys.add(key)

        if new_profiles:
            Profile.objects.bulk_create(
                new_profiles,
                batch_size=500,
            )

        return (
            len(new_profiles),
            existing_count,
        )

    def _looks_like_bad_job_title(self, value):
        value = str(value or "").strip().lower()

        if not value:
            return True

        if self.LINKEDIN_ID_PATTERN.match(value):
            return True

        if self.DATE_PATTERN.match(value):
            return True

        if self.NUMERIC_PATTERN.match(value):
            return True

        if value.startswith("gl-"):
            return True

        if value.startswith("part-"):
            return True

        return False


    def _find_fallback_job_title(
        self,
        values,
        experience_index,
    ):
        if experience_index is None:
            return ""

        start = max(
            7,
            experience_index - 15,
        )

        candidates = []

        for index in range(
            start,
            experience_index,
        ):
            value = str(
                values[index] or ""
            ).strip()

            if not value:
                continue

            if self._looks_like_bad_job_title(value):
                continue

            if value.startswith("["):
                continue

            if value.startswith("{"):
                continue

            if value.lower() in self.KNOWN_COUNTRIES:
                continue

            if self.GEO_PATTERN.match(value):
                continue

            candidates.append(
                (index, value)
            )

        if not candidates:
            return ""

        # Prefer a candidate immediately followed
        # by an empty value or a list of job-title levels.
        for index, value in reversed(candidates):
            if index + 1 >= len(values):
                continue

            next_value = str(
                values[index + 1] or ""
            ).strip()

            parsed_next = self._parse_list(
                next_value
            )

            if (
                not next_value
                or isinstance(parsed_next, list)
            ):
                return value

        return candidates[-1][1]
