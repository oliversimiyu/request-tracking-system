from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('requests/', views.request_list, name='request_list'),
    path('requests/<int:request_id>/', views.request_detail, name='request_detail'),
    path('requests/<int:request_id>/update-status/', views.update_request_status, name='update_request_status'),
    path('status/<int:request_id>/', views.request_status_check, name='request_status_check'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Department management URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_add, name='department_add'),
    path('departments/<int:department_id>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:department_id>/delete/', views.department_delete, name='department_delete'),
    path('departments/sync-api/', views.sync_departments_api, name='sync_departments_api'),
]