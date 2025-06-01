from django.urls import path, include
from django.contrib import admin
from order.views import *


urlpatterns = [
    path('orders/create/', create_order),
    path('orders/<int:order_id>/', get_order_by_id),
    path('orders/', get_all_orders),
    path('orders/<int:order_id>/status/', update_order_status)
]
