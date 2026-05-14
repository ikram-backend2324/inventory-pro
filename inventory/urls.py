from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('orders/', views.order_list, name='order_list'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('stock-movements/', views.stock_movements, name='stock_movements'),
]
