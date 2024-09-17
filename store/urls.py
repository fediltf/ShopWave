from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', StoreView.as_view(), name="store"),
    path('cart/', CartView.as_view(), name="cart"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('update_item/', UpdateitemView.as_view(), name="update-item"),
    path('process_order/', views.processOrder, name="process-order"),
    path('search_product/', SearchProductView.as_view(), name="search-product"),
    path('contact_us/', views.contact_us, name="contact-us"),
    path('add_product/', views.AddProductView.as_view(), name="add-product"),
    path('update_product/<product_id>', views.update_product, name="update-product"),
    path('delete_product/<product_id>', views.delete_product, name="delete-product"),

]
