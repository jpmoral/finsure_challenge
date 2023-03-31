from rest_framework_json_api import serializers

from lenders.models import Lender


class LenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lender
        fields = '__all__'
