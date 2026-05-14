from django.contrib import admin
from .models import Category, Supplier, Product, Order, OrderItem, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_email', 'phone', 'created_at']
    search_fields = ['name', 'contact_email']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'supplier', 'unit_price', 'quantity_in_stock', 'is_low_stock']
    list_filter = ['category', 'supplier']
    search_fields = ['name', 'sku']
    list_per_page = 20


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'order_type', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'order_type']
    search_fields = ['order_number']
    inlines = [OrderItemInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'reference', 'created_at']
    list_filter = ['movement_type']
    search_fields = ['product__name', 'reference']
