from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View

from .models import Product, WarehouseProduct, Warehouse, Order, OrderItem


class MainView(LoginRequiredMixin, View):

    def get(self, request):
        products_amount = Product.objects.count()
        warehouses_amount = Warehouse.objects.count()
        active_orders_amount = Order.objects.filter(status="Pending").count()
        completed_orders_amount = Order.objects.filter(status="Completed").count()

        most_popular_product = (
            Product.objects.annotate(order_count=Count("orderitem"))
            .order_by("-order_count")
            .first()
        )
        if most_popular_product:
            most_popular_quantity = most_popular_product.orderitem_set.count()
        else:
            most_popular_quantity = 0

        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Создаем префетч-запрос для OrderItem, чтобы сразу получить все позиции заказа
        order_items_prefetch = Prefetch(
            "items", queryset=OrderItem.objects.select_related("product")
        )

        # Получаем заказы с предзагруженными данными о позициях заказов
        orders_this_month = Order.objects.prefetch_related(order_items_prefetch).filter(
            created_at__gte=start_of_month, status="Completed"
        )

        total_month_income = sum(order.total_price() for order in orders_this_month)

        low_stock_products = WarehouseProduct.objects.filter(quantity__lt=10).count()

        total_users = User.objects.count()

        context = {
            "products_amount": products_amount,
            "warehouses_amount": warehouses_amount,
            "active_orders_amount": active_orders_amount,
            "most_popular_product": most_popular_product,
            "most_popular_quantity": most_popular_quantity,
            "total_month_income": total_month_income,
            "low_stock_products": low_stock_products,
            "total_users": total_users,
            "completed_orders_amount": completed_orders_amount,
        }
        return render(request, "inventory_management/main.html", context)


class OrderView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order_items_prefetch = Prefetch(
            "items", queryset=OrderItem.objects.select_related("product")
        )

        # Получаем заказы с предзагруженными данными о позициях заказов
        order = (
            Order.objects.prefetch_related(order_items_prefetch).filter(pk=pk).first()
        )

        # Получаем все позиции в заказе
        order_items = OrderItem.objects.filter(order=order)

        # Если нужен шаблон для просмотра заказа
        return render(
            request,
            "inventory_management/order.html",
            {
                "order": order,
                "order_items": order_items,
                "total_price": order.total_price(),
            },
        )

    def post(self, request, pk):
        # Получаем заказ по ID (pk)
        order = get_object_or_404(Order, pk=pk)

        # В зависимости от формы вы можете менять статус или обновлять позиции
        if "update_status" in request.POST:
            # Например, обновляем статус заказа
            new_status = request.POST.get("status")
            order.status = new_status
            order.save()

            # Перенаправляем на страницу с деталями заказа после обновления
            return redirect("inventory_management:order", pk=order.pk)

        elif "update_items" in request.POST:
            # Обновляем позиции заказа (например, изменяем количество товаров)
            for item in order.items.all():
                new_quantity = int(
                    request.POST.get(f"quantity_{item.pk}", item.quantity)
                )
                item.quantity = new_quantity
                item.save()

            # Перенаправляем на страницу с деталями заказа после обновления
            return redirect("inventory_management:order", pk=order.pk)

        return HttpResponseNotAllowed("Метод не разрешен")


class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        # Создаем префетч-запрос для OrderItem, чтобы сразу получить все позиции заказа
        order_items_prefetch = Prefetch(
            "items", queryset=OrderItem.objects.select_related("product")
        )

        # Получаем заказы с предзагруженными данными о позициях заказов
        orders = Order.objects.prefetch_related(order_items_prefetch).all()

        # Создаем список для отправки в шаблон
        orders_data = []
        for order in orders:
            order_info = {
                "order": order,
                "items": order.items.all(),  # Используем предзагруженные данные
                "total_price": order.total_price(),
            }
            orders_data.append(order_info)

        # Отправляем данные в шаблон
        return render(
            request, "inventory_management/orders.html", {"orders_data": orders_data}
        )


class ProductView(LoginRequiredMixin, View):
    def get(self, request, pk):
        # Получаем продукт по первичному ключу (pk) или возвращаем 404, если продукт не найден
        product = get_object_or_404(Product, pk=pk)

        # Предзагружаем связанные объекты WarehouseProduct для этого продукта
        warehouse_products = WarehouseProduct.objects.filter(
            product=product
        ).select_related("warehouse")

        # Считаем общее количество продукта на складах
        total_quantity = sum(
            warehouse_product.quantity for warehouse_product in warehouse_products
        )

        warehouses = Warehouse.objects.all()

        # Отправляем данные в шаблон
        return render(
            request,
            "inventory_management/product.html",
            {
                "product": product,
                "warehouse_products": warehouse_products,
                "total_quantity": total_quantity,
                "warehouses": warehouses,
            },
        )

    def post(self, request, pk):
        # Получаем продукт по ID (pk)
        product = get_object_or_404(Product, pk=pk)

        # Обрабатываем изменение количества товара на складе
        if "update_quantity" in request.POST:
            for warehouse_product in product.warehouse_products.all():
                # Изменяем количество товара на складе
                new_quantity = int(
                    request.POST.get(
                        f"quantity_{warehouse_product.pk}", warehouse_product.quantity
                    )
                )
                warehouse_product.quantity = new_quantity
                warehouse_product.save()

            # Перенаправляем на страницу с деталями продукта после обновления
            return redirect("inventory_management:product", pk=product.pk)

        # Обрабатываем изменение цены продукта
        elif "update_price" in request.POST:
            new_price = request.POST.get("price")
            if new_price:
                product.price = new_price
                product.save()

            # Перенаправляем на страницу с деталями продукта после обновления
            return redirect("inventory_management:product", pk=product.pk)

        elif "add_warehouse" in request.POST:
            # Получаем выбранный склад и количество
            warehouse_id = request.POST.get("warehouse")
            quantity = int(request.POST.get("new_quantity"))

            # Получаем склад по ID
            warehouse = get_object_or_404(Warehouse, pk=warehouse_id)

            # Создаем новую запись WarehouseProduct
            WarehouseProduct.objects.create(
                product=product, warehouse=warehouse, quantity=quantity
            )

            # Перенаправляем на страницу с деталями продукта после добавления склада
            return redirect("inventory_management:product", pk=product.pk)

        return HttpResponseNotAllowed("Метод не разрешен")


class ProductListView(LoginRequiredMixin, View):
    def get(self, request):
        # Создаем префетч-запрос для WarehouseProduct, чтобы сразу получить все продукты на складах
        warehouse_products_prefetch = Prefetch(
            "warehouse_products",
            queryset=WarehouseProduct.objects.select_related("warehouse"),
        )

        # Получаем все продукты с предзагруженными данными о складах
        products = Product.objects.prefetch_related(warehouse_products_prefetch).all()

        # Создаем список для отправки в шаблон
        products_data = []
        for product in products:
            product_info = {
                "product": product,
                "warehouses": product.warehouse_products.all(),
                # Используем предзагруженные данные
                "total_quantity": sum(
                    warehouse_product.quantity
                    for warehouse_product in product.warehouse_products.all()
                ),
                # Сумма всех количеств товара на складах
            }
            products_data.append(product_info)

        # Отправляем данные в шаблон
        return render(
            request,
            "inventory_management/products.html",
            {"products_data": products_data},
        )


class WarehouseView(LoginRequiredMixin, View):
    def get(self, request, pk):
        # Получаем склад по ID (pk) или возвращаем 404, если склад не найден
        warehouse = get_object_or_404(Warehouse, pk=pk)

        # Отправляем данные о складе в шаблон для отображения
        return render(
            request, "inventory_management/warehouse.html", {"warehouse": warehouse}
        )

    def post(self, request, pk):
        # Получаем склад по ID (pk)
        warehouse = get_object_or_404(Warehouse, pk=pk)

        # Если были изменены данные о складе
        if "update_warehouse" in request.POST:
            # Извлекаем данные из формы
            new_name = request.POST.get("name")
            new_location = request.POST.get("location")

            # Обновляем данные о складе
            warehouse.name = new_name
            warehouse.location = new_location
            warehouse.save()

            # Перенаправляем на страницу с деталями склада после обновления
            return redirect("inventory_management:warehouse", pk=warehouse.pk)

        return HttpResponseNotAllowed("Метод не разрешен")


class WarehouseListView(LoginRequiredMixin, View):
    def get(self, request):
        # Получаем все склады и предзагружаем данные о продуктах на складах
        warehouses = Warehouse.objects.all()

        # Для каждого склада получаем его продукты и количество
        warehouses_data = []
        for warehouse in warehouses:
            warehouse_products = WarehouseProduct.objects.filter(
                warehouse=warehouse
            ).select_related("product")
            warehouses_data.append(
                {
                    "warehouse": warehouse,
                    "warehouse_products": warehouse_products,
                    "total_quantity": sum(
                        warehouse_product.quantity
                        for warehouse_product in warehouse_products
                    ),
                }
            )

        # Отправляем данные в шаблон
        return render(
            request,
            "inventory_management/warehouses.html",
            {"warehouses_data": warehouses_data},
        )


class ProductCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "inventory_management/product_create.html")

    def post(self, request):
        # Получаем данные из формы
        product_name = request.POST.get("name")
        product_price = request.POST.get("price")
        product_description = request.POST.get("description")

        if product_name and product_price:
            # Создаем новый продукт
            product = Product.objects.create(
                name=product_name, price=product_price, description=product_description
            )
            return redirect("inventory_management:product", pk=product.pk)
        return HttpResponseNotAllowed("Метод не разрешен")


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        products = Product.objects.all()  # Получаем все продукты
        return render(
            request, "inventory_management/order_create.html", {"products": products}
        )

    def post(self, request):
        # Получаем данные из формы
        product_ids = request.POST.getlist("product_ids")  # Список ID продуктов
        quantities = request.POST.getlist("quantities")  # Список количеств товаров

        if product_ids and quantities:
            # Создаем новый заказ
            order = Order.objects.create(status="Pending")

            # Добавляем товары в заказ
            for product_id, quantity in zip(product_ids, quantities):
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order, product=product, quantity=quantity
                )

            return redirect("inventory_management:order", pk=order.pk)

        return HttpResponseNotAllowed("Метод не разрешен")


class WarehouseCreateView(LoginRequiredMixin, View):
    def get(self, request):
        # Отображаем форму для создания нового склада
        return render(request, "inventory_management/warehouse_create.html")

    def post(self, request):
        # Получаем данные из формы
        warehouse_name = request.POST.get("name")
        warehouse_location = request.POST.get("location")

        if warehouse_name and warehouse_location:
            # Создаем новый склад
            warehouse = Warehouse.objects.create(
                name=warehouse_name, location=warehouse_location
            )

            return redirect("inventory_management:warehouse", pk=warehouse.pk)

        return HttpResponseNotAllowed("Метод не разрешен")


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("inventory_management:main")

        form = AuthenticationForm()
        return render(request, "inventory_management/login.html", {"form": form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("inventory_management:main")

        # Создаем форму из POST данных
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("inventory_management:main")
        else:
            return render(request, "inventory_management/login.html", {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("inventory_management:login")
