from rest_framework import viewsets

from lenders.models import Lender
from lenders.serializers import LenderSerializer


class LenderViewSet(viewsets.ModelViewSet):
    queryset = Lender.objects.all()
    serializer_class = LenderSerializer
    resource_name = 'lenders'
