from rest_framework import routers
from apis.shorts_calculation.views import ShortsCalculationViewSet

router = routers.SimpleRouter()
router.register(r'shorts', ShortsCalculationViewSet, basename='shorts')
urlpatterns = router.urls