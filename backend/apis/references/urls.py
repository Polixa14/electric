from rest_framework import routers
from apis.references.views import ReferencesViewSet

router = routers.SimpleRouter()
router.register(r'references', ReferencesViewSet, basename='references')
urlpatterns = router.urls
