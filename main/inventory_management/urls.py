from django.urls import path
from . import views

app_name = "inventory_management"

urlpatterns = [
    path("", views.MainView.as_view(), name="main"),
    path("orders/", views.OrderListView.as_view(), name="orders"),
    path("orders/<int:pk>", views.OrderView.as_view(), name="order"),
    path("create_order/", views.OrderCreateView.as_view(), name="create_order"),
    path("products/", views.ProductListView.as_view(), name="products"),
    path("products/<int:pk>", views.ProductView.as_view(), name="product"),
    path("create_product/", views.ProductCreateView.as_view(), name="create_product"),
    path("warehouses/", views.WarehouseListView.as_view(), name="warehouses"),
    path("warehouses/<int:pk>", views.WarehouseView.as_view(), name="warehouse"),
    path("create_warehouse/", views.WarehouseCreateView.as_view(), name="create_warehouse"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
