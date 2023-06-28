from rest_framework import serializers
from apparatus.models import Transformer, AutoTransformer, SyncMotor,\
    AsyncMotor, Line, Generator
from rest_framework.exceptions import ValidationError
from apis.shorts_calculation.scheme_elements_classes import Load, System


class SystemSerializer(serializers.Serializer):
    nominal_voltage = serializers.FloatField()
    system_short_current = serializers.FloatField()

    def validate(self, attrs):
        return System(attrs['nominal_voltage'], attrs['system_short_current'])


class LoadSerializer(serializers.Serializer):
    power = serializers.FloatField()
    nominal_voltage = serializers.FloatField()

    def validate(self, attrs):
        return Load(attrs['nominal_voltage'], attrs['power'])


class InstanceSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=255)
    id = serializers.UUIDField(required=False)

    def validate(self, attrs):
        type_to_model = {
            'transformer': Transformer,
            'autotransformer': AutoTransformer,
            'generator': Generator,
            'syncmotor': SyncMotor,
            'asyncmotor': AsyncMotor,
            'line': Line
        }
        model = type_to_model.get(attrs['type'])
        try:
            return model.objects.get(id=attrs['id'])
        except model.DoesNotExist:
            raise ValidationError('Invalid instance id')


class CustomSerializer(serializers.Serializer):
    system = SystemSerializer(required=False)
    load = LoadSerializer(required=False)


class NetworkSerializer(serializers.Serializer):
    startpoint = serializers.IntegerField(required=True)
    endpoint = serializers.IntegerField(required=True)
    db_element = InstanceSerializer(required=False)
    custom_element = CustomSerializer(required=False)

    def validate(self, attrs):
        custom_element = attrs.get('custom_element')
        system = None
        load = None
        if custom_element:
            system = custom_element.get('system')
            load = custom_element.get('load')
        data = {
            'startpoint': attrs['startpoint'],
            'endpoint': attrs['endpoint'],
            'element': attrs.get('db_element') or system or load
        }

        if not data.get('element'):
            raise ValidationError(f'You should pass the data for element with '
                                  f'startpoint {attrs.get("startpoint")} and '
                                  f'endpoint {attrs.get("endpoint")}')
        return data


class CalculationDataSerializer(serializers.Serializer):
    calculation_point = serializers.IntegerField(required=True)
    network = NetworkSerializer(many=True, required=True)
