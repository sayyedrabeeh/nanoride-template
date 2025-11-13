from django.urls import path
from . import views

urlpatterns = [
    
    path('users/', views.users, name='users'),
    path('admin/block_user/<int:user_id>/', views.block_user, name='block_user'),
  
 ]