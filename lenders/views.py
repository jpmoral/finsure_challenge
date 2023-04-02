import csv

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from lenders.models import Lender
from lenders.serializers import LenderSerializer


class LenderViewSet(viewsets.ModelViewSet):
    queryset = Lender.objects.all()
    serializer_class = LenderSerializer
    resource_name = 'lenders'

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        raw_file = request.FILES['file']
        decoded_file = raw_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        to_create = []
        for row in reader:
            row['is_active'] = row['is_active'].lower() == 'true'
            row['is_hidden'] = row['is_hidden'].lower() == 'true'
            to_create.append(Lender(**row))
        lenders = Lender.objects.bulk_create(to_create)

        data = self.serializer_class(lenders, many=True).data

        return Response({'data': data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def download_csv(self, request):
        lenders = Lender.objects.all()
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="lenders.csv"'},
        )
        writer = csv.writer(response)
        writer.writerow(['id', 'name', 'code', 'upfront_commission', 'high_trail_commission', 'low_trail_commission', 'is_active', 'is_hidden', 'balance_multiplier'])
        for lender in lenders:
            writer.writerow([
                lender.id,
                lender.name,
                lender.code,
                lender.upfront_commission,
                lender.high_trail_commission,
                lender.low_trail_commission,
                str(lender.is_active).lower(),
                str(lender.is_hidden).lower(),
                lender.balance_multiplier,
            ])
        return response
