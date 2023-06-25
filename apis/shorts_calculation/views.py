
from apis.shorts_calculation.serializers import NetworkSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from apis.shorts_calculation.calculation_helpers import make_equivalent_circuit, calculate_shorts
from rest_framework.response import Response


class ShortsCalculationViewSet(viewsets.GenericViewSet):
    serializer_class = NetworkSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['many'] = True
        return serializer_class(*args, **kwargs)

    @action(detail=False, methods=['post'])
    def shorts(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            equivalent_circuit, result = calculate_shorts(serializer.validated_data)
            return Response({'equivalent_circuit': equivalent_circuit, 'result': result}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)