from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Invoice, Membership

import datetime

CHECK_OUT_URL = '/checkout/'


def sample_membership(user, **params):
    """Create and return a sample membership"""
    today = datetime.date.today()
    defaults = {
        'credits': 0,
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


class UserCheckoutTests(TestCase):
    """Test the user check out endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@zaf.com',
            password='testpass'
        )

    def test_invalid_user_id(self):
        """Test a check-out request with invalid user id"""
        res = self.client.post(CHECK_OUT_URL, {'id': -1})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_user_membership(self):
        """Test a check-out request for a user without a membership"""
        res = self.client.post(CHECK_OUT_URL, {'id': self.user.id})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_membership(self):
        """Test that a user with invalid membership can't check-out"""

        # Firstly test for a Cancelled membership
        sample_membership(user=self.user, state=Membership.CANCELLED)
        res = self.client.post(CHECK_OUT_URL, {'id': self.user.id})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Next test for a membership that has reached the end date
        self.user.membership.delete()
        sample_membership(
            user=self.user,
            start_date=datetime.date(2021, 10, 5),
            end_date=datetime.date.today()
        )
        res = self.client.post(CHECK_OUT_URL, {'id': self.user.id})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_missing_invoice(self):
        """Test a check-out request for a user without an invoice for the current month"""

        sample_membership(user=self.user)
        res = self.client.post(CHECK_OUT_URL, {'id': self.user.id})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_check_out(self):
        """Test that a user with a valid membership and invoice checks out successfully"""

        # Test check-out and see if a new invoice line is added
        sample_membership(user=self.user)
        invoice = sample_invoice(user=self.user)
        res = self.client.post(CHECK_OUT_URL, {'id': self.user.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(invoice.invoice_lines.all()), 1)
        invoice.invoice_lines.get(id=res.data['invoice_line_id'])
