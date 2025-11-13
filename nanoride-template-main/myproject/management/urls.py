from django.urls import path
from . import views

urlpatterns = [
    
    path('users/', views.users, name='users'),
    path('admin_projects/', views.admin_projects, name='admin_projects'),
    path('service_admin/', views.service_admin, name='service_admin'),
    path('contact_management/', views.contact_management, name='contact_management'),
    path('admin/block_user/<int:user_id>/', views.block_user, name='block_user'),
  
 ]