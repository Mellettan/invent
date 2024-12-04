from django.utils import timezone
from inventory_management.models import Product, Warehouse, WarehouseProduct, Order, OrderItem
from loguru import logger


def create_mock_data():
    # Создаём несколько продуктов
    product1 = Product.objects.create(
        name="Кирпич",
        description="Прямоугольный глиняный кирпич размера 250x120x65 мм",
        price=100.00
    )
    product2 = Product.objects.create(
        name="Строительная балка",
        description="Стальная строительная балка размера 600х40х40 мм",
        price=200.00
    )
    product3 = Product.objects.create(
        name="Пружина",
        description="Металлическая пружина размера 200х30х30 мм. Упругость 0.5",
        price=300.00
    )

    # Создаём несколько складов
    warehouse1 = Warehouse.objects.create(
        name="Тимирязевский склад",
        location="Москва, ул. Тимирязевская, 52"
    )
    warehouse2 = Warehouse.objects.create(
        name="Главный склад",
        location="Москва, ул. Маяковского, 23 к1"
    )

    # Добавляем продукты на склады
    WarehouseProduct.objects.create(warehouse=warehouse1, product=product1, quantity=50)
    WarehouseProduct.objects.create(warehouse=warehouse1, product=product2, quantity=30)
    WarehouseProduct.objects.create(warehouse=warehouse2, product=product2, quantity=70)
    WarehouseProduct.objects.create(warehouse=warehouse2, product=product3,
                                    quantity=100)

    # Создаём заказы
    order1 = Order.objects.create(status="Pending", created_at=timezone.now(),
                                  updated_at=timezone.now())
    order2 = Order.objects.create(status="Completed", created_at=timezone.now(),
                                  updated_at=timezone.now())

    # Добавляем позиции в заказы
    OrderItem.objects.create(order=order1, product=product1, quantity=5)
    OrderItem.objects.create(order=order1, product=product2, quantity=2)
    OrderItem.objects.create(order=order2, product=product2, quantity=3)
    OrderItem.objects.create(order=order2, product=product3, quantity=1)

    logger.success("Mock data created successfully")


# Запуск функции для создания данных
create_mock_data()
