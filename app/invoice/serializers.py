from rest_framework import serializers

from core.models import Invoice, InvoiceLine, Membership

from django.contrib.auth import get_user_model

import datetime


class InvoiceSerializer(serializers.ModelSerializer):
    """Serialize an invoice object"""
    class Meta:
        model = Invoice
        fields = (
            'id', 'user', 'date', 'status', 'description', 'amount',
            'invoice_lines'
        )
        read_only_fields = ('id',)
        extra_kwargs = {'invoice_lines': {'required': False}}


class InvoiceLinesSerializer(serializers.ModelSerializer):
    """Serialize an invoice line object"""

    class Meta:
        model = InvoiceLine
        fields = ('id', 'invoice', 'amount', 'description')
        read_only_fields = ('id',)


class InvoiceDetailSerializer(InvoiceSerializer):
    """Serialize an invoice and its lines"""
    invoice_lines = InvoiceLinesSerializer(many=True, read_only=True)


class UserCheckInSerializer(serializers.Serializer):
    """Custom serializer that implements a user's check-in"""
    id = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        """
        See if the id is valid and if the user with this id
        has a valid membership
        """
        try:
            user = get_user_model().objects.get(id=value)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError('User id does not exist')
        try:
            membership = user.membership
        except get_user_model().membership.RelatedObjectDoesNotExist:
            raise serializers.ValidationError('User membership does not exist')

        current_date = datetime.date.today()
        if membership.state == Membership.CANCELLED \
                or membership.credits == 0 \
                or membership.end_date <= current_date:
            raise serializers.ValidationError('User membership invalid')

        return value

    def save(self):
        """
        Create a new invoice line for the user's monthly invoice.
        If the invoice for this month doesn't exist, it gets created.
        Returns the associated invoice id and invoice line id.
        """
        id = self.validated_data.get('id')
        user = get_user_model().objects.get(id=id)
        current_month = datetime.date.today().month

        try:
            target_invoice = user.invoices.get(date__month=current_month)
        except Invoice.DoesNotExist:
            target_invoice = user.invoices.create(
                user=user,
                description='Invoice for month number '+str(current_month),
                status=Invoice.OUTSTANDING
            )

        new_invoice_line = target_invoice.invoice_lines.create(
            invoice=target_invoice,
            amount=1,
            description='Check-in'
        )
        user.membership.credits -= 1
        user.membership.save(update_fields=['credits'])
        data = {
            'invoice_id': target_invoice.id,
            'invoice_line_id': new_invoice_line.id
        }
        return data

class UserCheckOutSerializer(serializers.Serializer):
    """Custom serializer that implements a user's check-out"""
    id = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        """
        See if the id is valid and if the user with this id
        has a valid membership
        """
        try:
            user = get_user_model().objects.get(id=value)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError('User id does not exist')
        try:
            membership = user.membership
        except get_user_model().membership.RelatedObjectDoesNotExist:
            raise serializers.ValidationError('User membership does not exist')

        current_date = datetime.date.today()
        if membership.state == Membership.CANCELLED \
                or membership.credits < 0 \
                or membership.end_date <= current_date:
            raise serializers.ValidationError('User membership invalid')

        return value

    def save(self):
        """
        Create a new invoice line for the user's monthly invoice.
        Returns the associated invoice id and invoice line id.
        """
        id = self.validated_data.get('id')
        user = get_user_model().objects.get(id=id)
        current_month = datetime.date.today().month

        try:
            target_invoice = user.invoices.get(date__month=current_month)
        except Invoice.DoesNotExist:
            raise serializers.ValidationError('User membership invalid')

        new_invoice_line = target_invoice.invoice_lines.create(
            invoice=target_invoice,
            amount=1,
            description='Check-out'
        )
        user.membership.credits += 1
        user.membership.save(update_fields=['credits'])
        data = {
            'invoice_id': target_invoice.id,
            'invoice_line_id': new_invoice_line.id
        }
        return data