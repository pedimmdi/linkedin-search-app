from django.conf import settings
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from .models import Profile
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
        profiles, total, highlights = ProfileSearchService().search(
            query=query,
            role=role,
            country=country,
            page=page,
            page_size=page_size,
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
