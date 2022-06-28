from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Invoice, InvoiceLine
from invoice.serializers import InvoiceLinesSerializer

INVOICE_LINES_URL = reverse('invoice:invoiceline-list')


def single_invoice_line_url(invoice_line_id):
    """Return the URL for an invoice line with specific id"""
    return reverse('invoice:invoiceline-detail', args=[invoice_line_id])


class InvoiceLineApiTests(TestCase):
    """Test the invoice lines API"""

    def setUp(self):
        test_user = get_user_model().objects.create_user(
            'test@zaf.com',
            'password123'
        )
        self.invoice = Invoice.objects.create(
            user=test_user,
            status=Invoice.OUTSTANDING
        )
        self.invoice2 = Invoice.objects.create(
            user=test_user,
            status=Invoice.VOID
        )
        self.client = APIClient()

    def test_retrieve_invoice_lines(self):
        """Test retrieving invoice lines"""
        InvoiceLine.objects.create(invoice=self.invoice)
        InvoiceLine.objects.create(invoice=self.invoice, amount=10)

        res = self.client.get(INVOICE_LINES_URL)

        invoice_lines = InvoiceLine.objects.all().order_by('id')
        serializer = InvoiceLinesSerializer(invoice_lines, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_invoice_line(self):
        """Test creating a new invoice line"""
        payload = {'invoice': self.invoice.id, 'amount': 3}
        self.client.post(INVOICE_LINES_URL, payload)

        exists = InvoiceLine.objects.filter(
            invoice=payload['invoice'],
            amount=payload['amount']
        ).exists()
        self.assertTrue(exists)

    def test_view_single_invoice_line(self):
        """Test viewing a single invoice line"""
        invoice_line = InvoiceLine.objects.create(
            invoice=self.invoice,
            amount=5,
            description='test description'
        )

        url = single_invoice_line_url(invoice_line.id)
        res = self.client.get(url)

        serializer = InvoiceLinesSerializer(invoice_line)
        self.assertEqual(res.data, serializer.data)

    def test_update_invoice_line(self):
        """Test endpoint for updating an invoice line"""
        invoice_line = InvoiceLine.objects.create(invoice=self.invoice)

        payload = {
            'invoice': self.invoice.id,
            'amount': 5, 'description': 'Update: check',
            }
        url = single_invoice_line_url(invoice_line.id)
        self.client.put(url, payload)

        invoice_line.refresh_from_db()
        self.assertEqual(invoice_line.amount, payload['amount'])
        self.assertEqual(invoice_line.description, payload['description'])

    def test_filter_invoice_lines_by_invoice(self):
        """Test returning the invoice lines of a specific invoice"""
        invoice_line1 = InvoiceLine.objects.create(invoice=self.invoice)
        invoice_line2 = InvoiceLine.objects.create(invoice=self.invoice2)
        invoice_line3 = InvoiceLine.objects.create(
            invoice=self.invoice,
            description='This should not be in the filtered list'
        )
        invoice_line4 = InvoiceLine.objects.create(
            invoice=self.invoice2,
            description='This should be in the filtered list'
        )

        res = self.client.get(INVOICE_LINES_URL, {'invoice': self.invoice2.id})
        serializer1 = InvoiceLinesSerializer(invoice_line1)
        serializer2 = InvoiceLinesSerializer(invoice_line2)
        serializer3 = InvoiceLinesSerializer(invoice_line3)
        serializer4 = InvoiceLinesSerializer(invoice_line4)

        self.assertNotIn(serializer1.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertIn(serializer4.data, res.data)
