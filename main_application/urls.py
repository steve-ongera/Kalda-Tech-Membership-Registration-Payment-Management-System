"""
Kalda-Tech Systems - URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    # ============================================================================
    # AUTHENTICATION URLs
    # ============================================================================
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ============================================================================
    # DASHBOARD URLs
    # ============================================================================
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('member/dashboard/', views.member_dashboard, name='member_dashboard'),
    
    # ============================================================================
    # ADMIN - Member Management URLs
    # ============================================================================
    path('admin/members/', views.member_list, name='member_list'),
    path('admin/members/<int:member_id>/', views.member_detail, name='member_detail'),
    path('admin/members/<int:member_id>/approve/', views.approve_member, name='approve_member'),
    path('admin/members/<int:member_id>/reject/', views.reject_member, name='reject_member'),
    
    # ============================================================================
    # ADMIN - Payment Management URLs
    # ============================================================================
    path('admin/payments/', views.payment_list, name='payment_list'),
    
    # ============================================================================
    # ADMIN - System Settings URLs
    # ============================================================================
    path('admin/settings/', views.system_settings, name='system_settings'),
]