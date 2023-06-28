
from apis.shorts_calculation.serializers import CalculationDataSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from apis.shorts_calculation.calculation_helpers import ShortsCalculation, \
    make_substitution_scheme
from rest_framework.response import Response


class ShortsCalculationViewSet(viewsets.GenericViewSet):
    serializer_class = CalculationDataSerializer

    @action(detail=False, methods=['post'])
    def shorts(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            network = serializer.validated_data['network']
            vertices = []
            for elem in network:
                vertices.append(elem['startpoint'])
                vertices.append(elem['endpoint'])
            scheme = ShortsCalculation(len(set(vertices)))
            equivalent_circuit = make_substitution_scheme(network)
            result = scheme.calculate_short_circuit(
                network,
                serializer.validated_data['calculation_point']
            )
            return Response(
                {'equivalent_circuit': equivalent_circuit, 'result': result},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
