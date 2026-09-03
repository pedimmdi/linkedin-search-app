from elasticsearch.helpers import bulk
from django.core.management.base import BaseCommand

from profiles.models import Profile
from profiles.search_index import INDEX_NAME, PROFILE_MAPPING, get_client


class Command(BaseCommand):
    help = "Rebuild the Elasticsearch index from PostgreSQL profiles"

    def handle(self, *args, **options):
        client = get_client()

        if client.indices.exists(index=INDEX_NAME):
            client.indices.delete(index=INDEX_NAME)

        client.indices.create(
            index=INDEX_NAME,
            settings={"number_of_shards": 1, "number_of_replicas": 0},
            mappings=PROFILE_MAPPING,
        )

        actions = (
            {
                "_index": INDEX_NAME,
                "_id": profile.pk,
                "_source": {
                    "django_id": profile.pk,
                    "full_name": profile.full_name or "",
                    "linkedin_id": profile.linkedin_id or "",
                    "job_title": profile.job_title or "",
                    "job_title_role": profile.job_title_role or "",
                    "skills": profile.skills or "",
                    "location_country": profile.location_country or "",
                    "location_city": profile.location_city or "",
                    "summary": profile.summary or "",
                    "linkedin_url": profile.linkedin_url or "",
                },
            }
            for profile in Profile.objects.iterator(chunk_size=500)
        )

        success, errors = bulk(client, actions, chunk_size=500)
        client.indices.refresh(index=INDEX_NAME)

        if errors:
            self.stdout.write(self.style.ERROR(f"Indexed {success} profiles with errors."))
            raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS(f"Indexed {success} profiles."))
