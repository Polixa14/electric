from rest_framework import serializers
from references.models import ReferenceMaterial


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceMaterial
        fields = ('id', 'name', 'file', 'slug', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug')
