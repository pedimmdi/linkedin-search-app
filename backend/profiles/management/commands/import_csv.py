import csv
import json
from django.core.management.base import BaseCommand
from profiles.models import Profile


class Command(BaseCommand):
    help = 'Import LinkedIn profiles from text/CSV/JSON file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the dataset file')

    def handle(self, *args, **options):
        file_path = options['csv_file']
        self.stdout.write(self.style.SUCCESS(f'Reading data from {file_path}...'))

        profiles_to_create = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content.startswith('[') or content.startswith('{'):
                    data = json.loads(content)
                    if isinstance(data, dict):
                        data = [data]
                    for item in data:
                        profiles_to_create.append(Profile(
                            full_name=item.get('full_name') or item.get('name') or item.get('fullName'),
                            job_title=item.get('job_title') or item.get('title') or item.get('jobTitle'),
                            job_title_role=item.get('job_title_role') or item.get('role'),
                            skills=str(item.get('skills', '')),
                            location_country=item.get('location_country') or item.get('country'),
                            location_city=item.get('location_city') or item.get('city'),
                            summary=item.get('summary') or item.get('about'),
                            linkedin_url=item.get('linkedin_url') or item.get('url') or item.get('link')
                        ))
                    Profile.objects.bulk_create(profiles_to_create)
                    self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(profiles_to_create)} profiles from JSON.'))
                    return
        except Exception:
            pass

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                profiles_to_create.append(Profile(
                    full_name=row.get('full_name') or row.get('name') or row.get('fullName'),
                    job_title=row.get('job_title') or row.get('title') or row.get('jobTitle'),
                    job_title_role=row.get('job_title_role') or row.get('role'),
                    skills=row.get('skills', ''),
                    location_country=row.get('location_country') or row.get('country'),
                    location_city=row.get('location_city') or row.get('city'),
                    summary=row.get('summary') or row.get('about'),
                    linkedin_url=row.get('linkedin_url') or row.get('url') or row.get('link')
                ))

        Profile.objects.bulk_create(profiles_to_create)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(profiles_to_create)} profiles.'))
