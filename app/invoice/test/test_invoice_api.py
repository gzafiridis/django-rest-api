from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Invoice, InvoiceLine
from invoice.serializers import InvoiceSerializer, InvoiceDetailSerializer

INVOICES_URL = reverse('invoice:invoice-list')


def single_invoice_url(invoice_id):
    """Return the URL for an invoice with specific id"""
    return reverse('invoice:invoice-detail', args=[invoice_id])


def sample_invoice_line(invoice, amount=10):
    """Create and return a sample invoice_line"""
    return InvoiceLine.objects.create(invoice=invoice, amount=amount)


def sample_invoice(user, **params):
    """Create and return a sample invoice"""
    defaults = {
        'description': 'test description',
        'status': Invoice.OUTSTANDING,
    }
    defaults.update(params)

    return Invoice.objects.create(user=user, **defaults)


class InvoiceApiTests(TestCase):
    """Test the invoice API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@zaf.com'
            'password123'
        )
        self.client = APIClient()

    def test_retrieve_invoices(self):
        """Test endpoint for retrieving a list of invoices"""
        sample_invoice(user=self.user)
        sample_invoice(user=self.user)

        res = self.client.get(INVOICES_URL)

        invoices = Invoice.objects.all().order_by('id')
        serializer = InvoiceSerializer(invoices, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_invoice(self):
        """Test endpoint for creating invoice"""
        payload = {
            'user': self.user.id,
            'status': Invoice.OUTSTANDING,
        }
        res = self.client.post(INVOICES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        invoice = Invoice.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key == 'user':
                self.assertEqual(payload[key], invoice.user.id)
            else:
                self.assertEqual(payload[key], getattr(invoice, key))

    def test_view_single_invoice(self):
        """Test viewing a single invoice"""
        invoice = sample_invoice(user=self.user)
        invoice.invoice_lines.add(sample_invoice_line(invoice=invoice))
        invoice.refresh_from_db()

        url = single_invoice_url(invoice.id)
        res = self.client.get(url)

        serializer = InvoiceDetailSerializer(invoice)
        self.assertEqual(res.data, serializer.data)

    def test_update_invoice(self):
        """Test endpoint for updating an invoice"""
        invoice = sample_invoice(user=self.user, status=Invoice.VOID)
        invoice.invoice_lines.add(sample_invoice_line(invoice=invoice))

        payload = {
            'user': self.user.id,
            'status': Invoice.PAID, 'description': 'Update: check',
            }
        url = single_invoice_url(invoice.id)
        self.client.put(url, payload)

        invoice.refresh_from_db()
        self.assertEqual(invoice.status, payload['status'])
        self.assertEqual(invoice.description, payload['description'])
