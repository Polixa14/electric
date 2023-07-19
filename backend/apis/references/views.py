from references.models import ReferenceMaterial
from apis.references.serializers import ReferenceSerializer
from rest_framework import viewsets
from apis.permissions import IsAdminUserOrReadOnly


class ReferencesViewSet(viewsets.ModelViewSet):
    serializer_class = ReferenceSerializer
    queryset = ReferenceMaterial.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)

