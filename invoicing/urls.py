from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet, basename='product')
router.register('invoices', views.InvoiceViewSet)
router.register('transport', views.TransportViewSet)
router.register('customers', views.CustomerViewSet)
router.register('firms', views.FirmViewSet, basename='firm')

products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')

products_router.register('stock', views.StockViewSet, basename='product-stock')


invoices_router = routers.NestedDefaultRouter(
    router, 'invoices', lookup='invoice')

invoices_router.register(
    'items', views.InvoiceItemViewSet, basename='invoice-item')

invoices_router.register(
    'payments', views.PaymentViewSet, basename='invoice-payment')


firms_router = routers.NestedDefaultRouter(
    router, 'firms', lookup='firm')

firms_router.register(
    'address', views.AddressViewSet, basename='firm-address')


urlpatterns = router.urls + products_router.urls + \
    invoices_router.urls + firms_router.urls
