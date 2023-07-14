from django.urls import path
from apis.articles.urls import urlpatterns as api_articles_urlpatterns
from apis.shorts_calculation.urls import urlpatterns as api_shorts_urlpatterns
from rest_framework_simplejwt.views import TokenObtainPairView, \
    TokenRefreshView


api_urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='jwt_login'),
    path('refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    *api_articles_urlpatterns,
    *api_shorts_urlpatterns
]
