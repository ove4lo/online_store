from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.get_products),
    path('products/<int:product_id>/', views.get_product_by_id),
    path('products/create/', views.create_product),
    path('products/delete/<int:product_id>/', views.hard_delete_product),
    path('products/update-status/<int:product_id>/', views.update_product_status),
    path('products/edit/<int:product_id>/', views.edit_product),
    path('get_all_parameters/', views.get_all_parameters),
]