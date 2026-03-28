from django.urls import path
from . import views

urlpatterns = [
    # Fő funkciók
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('add-category/', views.add_category, name='add_category'),
    path('delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),

    # Fiókkezelés
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]