from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Invoice, Membership

import datetime

CHECK_IN_URL = '/checkin/'


def sample_membership(user, **params):
    """Create and return a sample membership"""
    today = datetime.date.today()
    # Make it a valid membership by default
    defaults = {
        'credits': 4,
        'state': Membership.ACTIVE,
        'start_date': today,
        'end_date': today + datetime.timedelta(days=30)
    }
    defaults.update(params)

    return Membership.objects.create(user=user, **defaults)


def sample_invoice(user, **params):
    """Create and return a sample invoice"""
    defaults = {
        'description': 'test description',
        'status': Invoice.OUTSTANDING,
    }
    defaults.update(params)

    return Invoice.objects.create(user=user, **defaults)


class UserCheckInTests(TestCase):
    """Test the user check in endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@zaf.com',
            password='testpass'
        )

    def test_invalid_user_id(self):
        """Test a check-in request with invalid user id"""
        res = self.client.post(CHECK_IN_URL, {'id': -1})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_user_membership(self):
        """Test a check-in request for a user without a membership"""
        res = self.client.post(CHECK_IN_URL, {'id': self.user.id})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_membership(self):
        """Test that a user with invalid membership can't check-in"""

        # Firstly test for a Cancelled membership
        sample_membership(user=self.user, state=Membership.CANCELLED)
        res = self.client.post(CHECK_IN_URL, {'id': self.user.id})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Next test for a membership that has reached the end date
        self.user.membership.delete()
        sample_membership(
            user=self.user,
            start_date=datetime.date(2021, 10, 5),
            end_date=datetime.date.today()
        )
        res = self.client.post(CHECK_IN_URL, {'id': self.user.id})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Lastly test for a membership that has 0 credits
        self.user.membership.delete()
        sample_membership(user=self.user, credits=0)
        res = self.client.post(CHECK_IN_URL, {'id': self.user.id})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_check_in(self):
        """Test that a user with a valid membership checks in successfully"""

        # Firstly test for a user without an invoice
        sample_membership(user=self.user)
        res = self.client.post(CHECK_IN_URL, {'id': self.user.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.user.invoices.all()), 1)
        invoice = self.user.invoices.get(id=res.data['invoice_id'])
        self.assertEqual(len(invoice.invoice_lines.all()), 1)

        # Get invoice line to ensure that the created invoice line was added
        # to the created invoice. If not, a DoesNotExist exception
        # will be thrown
        invoice.invoice_lines.get(id=res.data['invoice_line_id'])

        # Now test making another check-in and seeing if a
        # new invoice line is added
        res = self.client.post(CHECK_IN_URL, {'id': self.user.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.user.invoices.all()), 1)
        self.assertEqual(len(invoice.invoice_lines.all()), 2)
        invoice.invoice_lines.get(id=res.data['invoice_line_id'])
