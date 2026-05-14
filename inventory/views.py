from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Supplier, StockMovement, Category


@login_required
def product_list(request):
    products = Product.objects.select_related('category', 'supplier').all()
    categories = Category.objects.all()
    cat_id = request.GET.get('category')
    if cat_id:
        products = products.filter(category_id=cat_id)
    low_stock = request.GET.get('low_stock')
    if low_stock:
        products = products.filter(quantity_in_stock__lte=10)
    return render(request, 'inventory/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_cat': cat_id,
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    movements = product.movements.all()[:10]
    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'movements': movements,
    })


@login_required
def order_list(request):
    orders = Order.objects.prefetch_related('items').all()
    return render(request, 'inventory/order_list.html', {'orders': orders})


@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})


@login_required
def stock_movements(request):
    movements = StockMovement.objects.select_related('product').all()[:50]
    return render(request, 'inventory/stock_movements.html', {'movements': movements})
