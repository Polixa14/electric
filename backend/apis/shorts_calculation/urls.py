from rest_framework import routers
from apis.shorts_calculation.views import ShortsCalculationViewSet, \
    ApparatusViewSet

router = routers.SimpleRouter()
router.register(r'shorts', ShortsCalculationViewSet, basename='shorts')
router.register(r'apparatus', ApparatusViewSet, basename='apparatus')
urlpatterns = router.urls
