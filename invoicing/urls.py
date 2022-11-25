from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet)
router.register('invoices', views.InvoiceViewSet)

products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')

products_router.register('stock', views.StockViewSet, basename='product-stock')


urlpatterns = router.urls + products_router.urls
