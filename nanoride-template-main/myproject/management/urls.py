from django.urls import path
from . import views

urlpatterns = [   
    path('users/', views.users, name='users'),
    path('admin_projects/', views.admin_projects, name='admin_projects'),
    path('projects/add/', views.add_project, name='add_project'),
    path('Project_list/', views.Project_list, name='Project_list'),
    path('projects/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('projects/delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('projects/view/<int:project_id>/', views.view_project, name='view_project'),
    path('projects/toggle-featured/<int:project_id>/', views.toggle_featured, name='toggle_featured'),
    path('service_admin/', views.service_admin, name='service_admin'),
    path('service_list/', views.service_list, name='service_list'),
    path('services/add/', views.add_service, name='add_service'),
    path('services/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    path('services/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    path('services/toggle/<int:service_id>/', views.toggle_service, name='toggle_service'),
    path('services/view/<int:service_id>/', views.view_service, name='view_service'),
    path('contact_management/', views.contact_management, name='contact_management'),
    path('contact-forms/reply/<int:contact_id>/', views.reply_contact, name='reply_contact'),
    path('contact-forms/delete/<int:contact_id>/', views.delete_contact, name='delete_contact'),
    path('contact-forms/view/<int:contact_id>/', views.view_contact, name='view_contact'),
    path('admin/block_user/<int:user_id>/', views.block_user, name='block_user'),
 ]