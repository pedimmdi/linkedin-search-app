from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .search_index import INDEX_NAME, get_client
from .serializers import ProfileSerializer
from .services.search import ProfileSearchService


class ProfileSearchAPIView(ListAPIView):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.none()

    def list(self, request, *args, **kwargs):
        query = request.query_params.get("q", "")
        role = request.query_params.get("role", "")
        country = request.query_params.get("country", "")
        try:
            page = max(int(request.query_params.get("page", 1)), 1)
        except (TypeError, ValueError):
            page = 1

        page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE", 20)
        try:
            profiles, total, highlights = ProfileSearchService().search(
                query=query, role=role, country=country,
                page=page, page_size=page_size,
            )
        except Exception:
            return Response(
                {"detail": "Search service is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        data = self.get_serializer(profiles, many=True).data
        for item in data:
            item["highlights"] = highlights.get(str(item["id"]), {})

        return Response({
            "count": total,
            "next": page + 1 if page * page_size < total else None,
            "previous": page - 1 if page > 1 else None,
            "results": data,
        })


class ProfileFiltersAPIView(APIView):
    def get(self, request, *args, **kwargs):
        roles = list(
            Profile.objects.exclude(job_title_role="")
            .values_list("job_title_role", flat=True)
            .distinct().order_by("job_title_role")
        )
        countries = list(
            Profile.objects.exclude(location_country="")
            .values_list("location_country", flat=True)
            .distinct().order_by("location_country")
        )
        return Response({"roles": roles, "countries": countries})


class HealthCheckAPIView(APIView):
    def get(self, request, *args, **kwargs):
        checks = {"database": "ok", "elasticsearch": "ok"}
        try:
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
        except OperationalError:
            checks["database"] = "unavailable"

        try:
            client = get_client()
            if not client.ping() or not client.indices.exists(index=INDEX_NAME):
                checks["elasticsearch"] = "unavailable"
        except Exception:
            checks["elasticsearch"] = "unavailable"

        healthy = all(value == "ok" for value in checks.values())
        return Response(
            {"status": "ok" if healthy else "degraded", **checks},
            status=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
