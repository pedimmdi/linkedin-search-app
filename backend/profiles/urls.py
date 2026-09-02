from django.urls import path
from .views import ProfileSearchAPIView


urlpatterns = [
    path('profiles/search/', ProfileSearchAPIView.as_view(), name='profile-search'),
]
