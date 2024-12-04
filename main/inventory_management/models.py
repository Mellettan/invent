from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField(max_length=200, help_text="Название склада")
    location = models.CharField(
        max_length=300, help_text="Адрес или место расположения склада"
    )
    products = models.ManyToManyField(
        Product, through="WarehouseProduct", related_name="warehouses"
    )

    def __str__(self):
        return self.name


class WarehouseProduct(models.Model):
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="warehouse_products"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="warehouse_products"
    )
    quantity = models.PositiveIntegerField(help_text="Количество продукта на складе")

    def __str__(self):
        return f"{self.product.name} ({self.quantity}) in {self.warehouse.name}"


class Order(models.Model):
    status = models.CharField(
        max_length=50, choices=[("Pending", "Ожидание"), ("Completed", "Завершён")]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order №{self.pk}"

    def total_price(self):
        """Вычисление общей стоимости заказа."""
        return sum(item.total_price() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        help_text="Количество этого продукта в заказе"
    )

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) in Order №{self.order.pk}"

    def total_price(self):
        """Общая стоимость этой позиции в заказе."""
        return self.product.price * self.quantity
