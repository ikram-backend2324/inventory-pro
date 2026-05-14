from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from inventory.models import Product, Order, Supplier, StockMovement
from forecasting.models import Forecast


@login_required
def dashboard(request):
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(quantity_in_stock__lte=10)
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_suppliers = Supplier.objects.count()
    recent_movements = StockMovement.objects.select_related('product').order_by('-created_at')[:5]
    recent_orders = Order.objects.order_by('-created_at')[:5]
    recent_forecasts = Forecast.objects.select_related('product').order_by('-created_at')[:3]
    
    total_stock_value = sum(p.stock_value for p in Product.objects.all())

    return render(request, 'core/dashboard.html', {
        'total_products': total_products,
        'low_stock_count': low_stock_products.count(),
        'low_stock_products': low_stock_products[:5],
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_suppliers': total_suppliers,
        'recent_movements': recent_movements,
        'recent_orders': recent_orders,
        'recent_forecasts': recent_forecasts,
        'total_stock_value': total_stock_value,
    })
