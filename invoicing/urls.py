from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet)
router.register('invoices', views.InvoiceViewSet)
router.register('transport', views.TransportViewSet)

products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')

products_router.register('stock', views.StockViewSet, basename='product-stock')


invoices_router = routers.NestedDefaultRouter(
    router, 'invoices', lookup='invoice')

invoices_router.register(
    'items', views.InvoiceItemViewSet, basename='invoice-item')

invoices_router.register(
    'payments', views.PaymentViewSet, basename='invoice-payment')


urlpatterns = router.urls + products_router.urls + invoices_router.urls
