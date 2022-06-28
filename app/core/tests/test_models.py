from django.test import TestCase
from django.contrib.auth import get_user_model

from datetime import date

from core import models


def sample_user(email='test@zaf.com', password='testpass'):
    """Create and return a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@zaf.com'
        password = 'Password123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
            )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@zaf.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_mempership_str(self):
        """Test the membership string representation"""
        membership = models.Membership.objects.create(
            user=sample_user(),
            state=models.Membership.CANCELLED,
            credits=0,
            start_date=date(2022, 4, 13),
            end_date=date(2022, 6, 13)
        )

        self.assertEqual(
            str(membership),
            'User: ' + str(membership.user)
            )

    def test_invoice_str(self):
        """Test the invoice string representation"""
        invoice = models.Invoice.objects.create(
            user=sample_user(),
            status=models.Invoice.OUTSTANDING,
        )

        self.assertEqual(
            str(invoice), str(invoice.id)
        )

    def test_invoice_line_str(self):
        """Test the invoice line string representation"""
        test_invoice = models.Invoice.objects.create(
            user=sample_user(),
            status=models.Invoice.OUTSTANDING,
            amount=0
        )
        invoice_line = models.InvoiceLine.objects.create(
            invoice=test_invoice,
            amount=3,
            description='test description'
        )

        self.assertEqual(
            str(invoice_line), str(invoice_line.id))

    def test_invoice_line_save(self):
        """
        Test that when an instance of invoice line is saved for the
        first time, its amount is added to its invoice amount
        """
        test_invoice = models.Invoice.objects.create(
            user=sample_user(),
            status=models.Invoice.OUTSTANDING,
            amount=0
        )
        invoice_line = models.InvoiceLine.objects.create(
            invoice=test_invoice,
            amount=3,
            description='test description'
        )

        test_invoice.refresh_from_db()
        self.assertEqual(test_invoice.amount, invoice_line.amount)
