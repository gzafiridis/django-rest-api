from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin

import datetime


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """"Creates and saves a new user"""
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Membership(models.Model):
    """Membership object"""
    ACTIVE = 'ACT'
    CANCELLED = 'CANC'
    STATE_CHOICES = (
        (ACTIVE, 'Active'),
        (CANCELLED, 'Cancelled')
    )

    user = models.OneToOneField(
        'User',
        related_name='membership',
        on_delete=models.CASCADE,
    )
    state = models.CharField(
        max_length=4,
        choices=STATE_CHOICES,
        default=ACTIVE,
    )
    credits = models.PositiveIntegerField(default=0)
    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField()

    def __str__(self):
        return 'User: ' + str(self.user)


class Invoice(models.Model):
    """
    Invoice object. The amount field of an invoice is the sum of its invoice
    lines' amounts.
    """
    OUTSTANDING = 'OUT'
    PAID = 'PAID'
    VOID = 'VOID'
    STATUS_CHOICES = (
        (OUTSTANDING, 'Outstanding'),
        (PAID, 'Paid'),
        (VOID, 'Void')
    )

    user = models.ForeignKey(
        'User',
        unique_for_month='date',
        related_name='invoices',
        on_delete=models.CASCADE
    )
    date = models.DateField(default=datetime.date.today)
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=4, choices=STATUS_CHOICES)
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.id)


class InvoiceLine(models.Model):
    """Invoice line object"""
    invoice = models.ForeignKey(
        'Invoice',
        related_name='invoice_lines',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=255, blank=True)

    # This function adds an invoice line's amount to the invoice amount
    # when this line is saved for the first time in the database
    # (which means when the line is created)
    def save(self, *args, **kwargs):
        if not self.pk:
            self.invoice.amount += self.amount
            self.invoice.save(update_fields=['amount'])
        super(InvoiceLine, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)
