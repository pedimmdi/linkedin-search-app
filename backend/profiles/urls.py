from django.urls import path

from .views import HealthCheckAPIView, ProfileFiltersAPIView, ProfileSearchAPIView


urlpatterns = [
    path("profiles/search/", ProfileSearchAPIView.as_view(), name="profile-search"),
    path("profiles/filters/", ProfileFiltersAPIView.as_view(), name="profile-filters"),
    path("health/", HealthCheckAPIView.as_view(), name="health-check"),
]
