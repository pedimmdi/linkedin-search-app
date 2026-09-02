from django.db import models


class Profile(models.Model):
    full_name = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=255, blank=True)
    job_title_role = models.CharField(max_length=255, blank=True, db_index=True)
    skills = models.TextField(blank=True)
    location_country = models.CharField(max_length=100, blank=True, db_index=True)
    location_city = models.CharField(max_length=100, blank=True, db_index=True)
    summary = models.TextField(blank=True)
    linkedin_url = models.URLField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["job_title_role"]),
            models.Index(fields=["location_country"]),
            models.Index(fields=["location_city"]),
        ]

    def __str__(self):
        return self.full_name or "Unknown Profile"
