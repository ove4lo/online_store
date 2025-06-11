from django.urls import path
from django.contrib import admin
from . import views



urlpatterns = [
    path('products/', views.get_products),
    path('products/<int:product_id>/', views.get_product_by_id),
    path('products/create/', views.create_product),
    path('products/soft-delete/<int:product_id>/', views.soft_delete_product),
    path('products/hard-delete/<int:product_id>/', views.hard_delete_product),
    path('products/edit/<int:product_id>/', views.edit_product),
    path('get_all_parameters/', views.get_all_parameters),
]
