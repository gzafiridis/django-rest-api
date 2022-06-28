from rest_framework import viewsets, status, views

from rest_framework.response import Response

from core.models import Invoice, InvoiceLine

from invoice import serializers


class InvoiceViewSet(viewsets.ModelViewSet):
    """Manage invoices in the database"""
    authentication_classes = []
    permission_classes = []
    serializer_class = serializers.InvoiceSerializer
    queryset = Invoice.objects.all()

    def retrieve(self, request, pk=None):
        """Manage a single invoice"""
        try:
            invoice = Invoice.objects.get(pk=pk)
        except Invoice.DoesNotExist:
            return Response('Invoice does not exist',
                            status.HTTP_404_NOT_FOUND)
        serializer = serializers.InvoiceDetailSerializer(invoice)
        return Response(serializer.data)


class InvoiceLinesViewSet(viewsets.ModelViewSet):
    """Manage an invoice's invoice lines in the database"""
    authentication_classes = []
    permission_classes = []
    queryset = InvoiceLine.objects.all()
    serializer_class = serializers.InvoiceLinesSerializer

    def get_queryset(self):
        """Retreive the invoice lines of a specific invoice"""
        invoice_id = self.request.query_params.get('invoice')
        queryset = self.queryset
        if invoice_id:
            queryset = queryset.filter(invoice__id=int(invoice_id))
        return queryset.order_by('id')


class UserCheckInView(views.APIView):
    """
    Implement a user's check-in. It returns the associated invoice id
    and invoice line id.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = serializers.UserCheckInSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.save()
            return Response(data, status=status.HTTP_200_OK)

class UserCheckOutView(views.APIView):
    """
    Implement a user's check-out. It returns the associated invoice id
    and invoice line id.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = serializers.UserCheckOutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            data = serializer.save()
            return Response(data, status=status.HTTP_200_OK)
