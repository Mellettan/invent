from django.contrib import admin
from .models import Product, Warehouse, WarehouseProduct, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')


@admin.register(WarehouseProduct)
class WarehouseProductAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'quantity')
    search_fields = ('warehouse__name', 'product__name')
    list_filter = ('warehouse', 'product')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'created_at', 'updated_at', 'total_price')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)

    def total_price(self, obj):
        """Отображает общую стоимость заказа."""
        return obj.total_price()
    total_price.short_description = 'Общая стоимость'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'total_price')
    search_fields = ('order__id', 'product__name')
    list_filter = ('order',)

    def total_price(self, obj):
        """Отображает стоимость этой позиции в заказе."""
        return obj.total_price()
    total_price.short_description = 'Стоимость позиции'
