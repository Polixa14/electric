
from apis.shorts_calculation.serializers import CalculationDataSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from apis.shorts_calculation.calculation_helpers import ShortsScheme
from rest_framework.response import Response


class ShortsCalculationViewSet(viewsets.GenericViewSet):
    serializer_class = CalculationDataSerializer

    @action(detail=False, methods=('post',))
    def calculate_shorts(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            network = serializer.validated_data['network']
            vertices = set()
            for elem in network:
                vertices.add(elem['startpoint'])
                vertices.add(elem['endpoint'])
            scheme = ShortsScheme(len(set(vertices)))
            equivalent_circuit = scheme.make_substitution_scheme(network)
            result_scheme, short_current = scheme.calculate_short_circuit(
                network,
                serializer.validated_data['calculation_point']
            )
            return Response(
                {'equivalent_circuit': equivalent_circuit,
                 'result_scheme': result_scheme,
                 'short_current': short_current},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
