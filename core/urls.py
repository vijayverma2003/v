from django.urls import path
from django.views.generic import TemplateView
from rest_framework_nested import routers
from .views import CountryViewSet, CurrencyViewSet

routers = routers.DefaultRouter()

routers.register('country', CountryViewSet)
routers.register('currency', CurrencyViewSet)


urlpatterns = [
    path('', TemplateView.as_view(template_name='core/index.html'))
] + routers.urls
