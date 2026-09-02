from django.db.models import Q
from rest_framework.generics import ListAPIView

from .models import Profile
from .serializers import ProfileSerializer


class ProfileSearchAPIView(ListAPIView):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        queryset = Profile.objects.all()

        q = self.request.query_params.get("q", "").strip()
        job_role = self.request.query_params.get("role", "").strip()
        country = self.request.query_params.get("country", "").strip()

        if q:
            queryset = queryset.filter(
                Q(full_name__icontains=q)
                | Q(job_title__icontains=q)
                | Q(skills__icontains=q)
                | Q(summary__icontains=q)
            )

        if job_role:
            queryset = queryset.filter(
                job_title_role__iexact=job_role
            )

        if country:
            queryset = queryset.filter(
                location_country__iexact=country
            )

        return queryset
