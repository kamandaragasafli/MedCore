from django.urls import path

from .views import monthly_sales, add_sale

app_name = 'sales'

urlpatterns = [
    path('', monthly_sales, name='list'),
    path('add/', add_sale, name='add'),
]

