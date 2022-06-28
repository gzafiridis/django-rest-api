from django.urls import path, include
from rest_framework.routers import DefaultRouter

from invoice import views


router = DefaultRouter()
router.register('invoices', views.InvoiceViewSet)
router.register('invoice_lines', views.InvoiceLinesViewSet)

app_name = 'invoice'

urlpatterns = [
    path('', include(router.urls))
]
