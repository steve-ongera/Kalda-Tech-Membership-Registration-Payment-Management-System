"""
Kalda-Tech Systems - Views
Authentication, Dashboards, and Admin Management Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import timedelta
from decimal import Decimal

from .models import (
    User, Member, Payment, MembershipCategory, Country, Region,
    Notification, AuditLog, MembershipRenewal, MembershipCertificate,
    MemberDocument
)


# ============================================================================
# HELPER FUNCTIONS - User Type Checks
# ============================================================================

def is_admin(user):
    """Check if user is an administrator"""
    return user.is_authenticated and user.user_type == 'admin'


def is_staff(user):
    """Check if user is staff"""
    return user.is_authenticated and user.user_type == 'staff'


def is_member(user):
    """Check if user is a member"""
    return user.is_authenticated and user.user_type == 'member'


def is_admin_or_staff(user):
    """Check if user is admin or staff"""
    return user.is_authenticated and user.user_type in ['admin', 'staff']


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def login_view(request):
    """
    Handle user login and redirect to appropriate dashboard
    """
    # Redirect if already authenticated
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user account is active
            if not user.is_active:
                messages.error(request, 'Your account has been deactivated. Please contact support.')
                return render(request, 'accounts/login.html')
            
            # Log the user in
            login(request, user)
            
            # Create audit log
            AuditLog.objects.create(
                user=user,
                action='login',
                model_name='User',
                object_id=str(user.id),
                description=f'User {user.username} logged in',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
            )
            
            # Success message
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect to appropriate dashboard
            return redirect_to_dashboard(user)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            
            # Log failed login attempt
            AuditLog.objects.create(
                user=None,
                action='login',
                model_name='User',
                object_id='failed',
                description=f'Failed login attempt for username: {username}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
            )
    
    return render(request, 'accounts/login.html')


def redirect_to_dashboard(user):
    """
    Redirect user to appropriate dashboard based on user type
    """
    if user.user_type == 'admin':
        return redirect('admin_dashboard')
    elif user.user_type == 'staff':
        return redirect('staff_dashboard')
    elif user.user_type == 'member':
        return redirect('member_dashboard')
    else:
        return redirect('login')


@login_required
def logout_view(request):
    """
    Handle user logout
    """
    # Create audit log before logout
    AuditLog.objects.create(
        user=request.user,
        action='logout',
        model_name='User',
        object_id=str(request.user.id),
        description=f'User {request.user.username} logged out',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
    )
    
    # Log out the user
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')


# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

@login_required
@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    """
    Admin dashboard with comprehensive statistics and management tools
    """
    # Get date ranges for statistics
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Member statistics
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status='approved', expiry_date__gte=today).count()
    pending_members = Member.objects.filter(status='pending').count()
    expired_members = Member.objects.filter(expiry_date__lt=today).count()
    
    # Payment statistics
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    revenue_this_month = Payment.objects.filter(
        status='completed',
        completed_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    pending_payments = Payment.objects.filter(
        status__in=['initiated', 'pending']
    ).count()
    
    # Recent registrations (last 30 days)
    recent_registrations = Member.objects.filter(
        registration_date__gte=thirty_days_ago
    ).count()
    
    # Membership category distribution
    category_distribution = Member.objects.values(
        'membership_category__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Regional distribution
    regional_distribution = Member.objects.values(
        'region__name', 'country__name'
    ).annotate(count=Count('id')).order_by('-count')[:10]
    
    # Recent pending approvals
    pending_approvals = Member.objects.filter(
        status='pending'
    ).order_by('-registration_date')[:5]
    
    # Recent payments
    recent_payments = Payment.objects.filter(
        status='completed'
    ).select_related('member').order_by('-completed_at')[:10]
    
    # Expiring memberships (next 30 days)
    expiring_soon = Member.objects.filter(
        status='approved',
        expiry_date__range=[today, today + timedelta(days=30)]
    ).order_by('expiry_date')[:10]
    
    # Unread notifications
    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    # Recent audit logs
    recent_audits = AuditLog.objects.select_related(
        'user'
    ).order_by('-created_at')[:10]
    
    context = {
        'total_members': total_members,
        'active_members': active_members,
        'pending_members': pending_members,
        'expired_members': expired_members,
        'total_revenue': total_revenue,
        'revenue_this_month': revenue_this_month,
        'pending_payments': pending_payments,
        'recent_registrations': recent_registrations,
        'category_distribution': category_distribution,
        'regional_distribution': regional_distribution,
        'pending_approvals': pending_approvals,
        'recent_payments': recent_payments,
        'expiring_soon': expiring_soon,
        'unread_notifications': unread_notifications,
        'recent_audits': recent_audits,
    }
    
    return render(request, 'admin/dashboard.html', context)


# ============================================================================
# STAFF DASHBOARD
# ============================================================================

@login_required
@user_passes_test(is_staff, login_url='login')
def staff_dashboard(request):
    """
    Staff dashboard for member management and approvals
    """
    today = timezone.now().date()
    
    # Pending approvals
    pending_approvals = Member.objects.filter(
        status='pending'
    ).order_by('-registration_date')
    
    # Recent registrations (last 7 days)
    week_ago = today - timedelta(days=7)
    recent_registrations = Member.objects.filter(
        registration_date__gte=week_ago
    ).count()
    
    # Today's registrations
    today_registrations = Member.objects.filter(
        registration_date__date=today
    ).count()
    
    # Pending payments
    pending_payments = Payment.objects.filter(
        status__in=['initiated', 'pending']
    ).select_related('member').order_by('-created_at')[:10]
    
    # Expiring soon (next 14 days)
    expiring_soon = Member.objects.filter(
        status='approved',
        expiry_date__range=[today, today + timedelta(days=14)]
    ).order_by('expiry_date')
    
    # Recent completed payments
    recent_payments = Payment.objects.filter(
        status='completed'
    ).select_related('member').order_by('-completed_at')[:5]
    
    # Unread notifications
    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    # Statistics
    total_pending = pending_approvals.count()
    total_expiring = expiring_soon.count()
    
    context = {
        'pending_approvals': pending_approvals[:10],
        'recent_registrations': recent_registrations,
        'today_registrations': today_registrations,
        'pending_payments': pending_payments,
        'expiring_soon': expiring_soon[:10],
        'recent_payments': recent_payments,
        'unread_notifications': unread_notifications,
        'total_pending': total_pending,
        'total_expiring': total_expiring,
    }
    
    return render(request, 'staff/dashboard.html', context)


# ============================================================================
# MEMBER DASHBOARD
# ============================================================================

@login_required
@user_passes_test(is_member, login_url='login')
def member_dashboard(request):
    """
    Member dashboard with personal information and membership status
    """
    try:
        member = Member.objects.select_related(
            'membership_category', 'country', 'region'
        ).get(user=request.user)
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found. Please contact support.')
        return redirect('login')
    
    # Check membership status
    is_active = member.is_membership_active()
    days_until_expiry = None
    
    if member.expiry_date:
        days_until_expiry = (member.expiry_date - timezone.now().date()).days
    
    # Payment history
    payment_history = Payment.objects.filter(
        member=member
    ).order_by('-created_at')[:10]
    
    # Recent notifications
    recent_notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:5]
    
    # Unread notifications count
    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    # Membership certificates
    certificates = MembershipCertificate.objects.filter(
        member=member,
        is_active=True
    ).order_by('-issue_date')
    
    # Renewal history
    renewals = MembershipRenewal.objects.filter(
        member=member
    ).order_by('-initiated_at')[:5]
    
    # Documents
    documents = MemberDocument.objects.filter(
        member=member
    ).order_by('-uploaded_at')
    
    context = {
        'member': member,
        'is_active': is_active,
        'days_until_expiry': days_until_expiry,
        'payment_history': payment_history,
        'recent_notifications': recent_notifications,
        'unread_notifications': unread_notifications,
        'certificates': certificates,
        'renewals': renewals,
        'documents': documents,
    }
    
    return render(request, 'member/dashboard.html', context)


# ============================================================================
# ADMIN VIEWS - Member Management
# ============================================================================

@login_required
@user_passes_test(is_admin_or_staff, login_url='login')
def member_list(request):
    """
    List all members with filtering and search
    """
    members = Member.objects.select_related(
        'membership_category', 'country', 'region', 'user'
    ).all()
    
    # Filtering
    status = request.GET.get('status')
    category = request.GET.get('category')
    country = request.GET.get('country')
    search = request.GET.get('search')
    
    if status:
        members = members.filter(status=status)
    
    if category:
        members = members.filter(membership_category_id=category)
    
    if country:
        members = members.filter(country_id=country)
    
    if search:
        members = members.filter(
            Q(membership_id__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(national_id__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(members, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    categories = MembershipCategory.objects.filter(is_active=True)
    countries = Country.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'countries': countries,
        'current_status': status,
        'current_category': category,
        'current_country': country,
        'search_query': search,
    }
    
    return render(request, 'admin/member_list.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url='login')
def member_detail(request, member_id):
    """
    View detailed information about a specific member
    """
    member = get_object_or_404(
        Member.objects.select_related(
            'membership_category', 'country', 'region', 'user', 'approved_by'
        ),
        id=member_id
    )
    
    # Get related data
    payments = Payment.objects.filter(member=member).order_by('-created_at')
    documents = MemberDocument.objects.filter(member=member).order_by('-uploaded_at')
    renewals = MembershipRenewal.objects.filter(member=member).order_by('-initiated_at')
    certificates = MembershipCertificate.objects.filter(member=member).order_by('-issue_date')
    
    context = {
        'member': member,
        'payments': payments,
        'documents': documents,
        'renewals': renewals,
        'certificates': certificates,
    }
    
    return render(request, 'admin/member_detail.html', context)


@login_required
@user_passes_test(is_admin_or_staff, login_url='login')
def approve_member(request, member_id):
    """
    Approve a pending member registration
    """
    if request.method == 'POST':
        member = get_object_or_404(Member, id=member_id, status='pending')
        
        # Update member status
        member.status = 'approved'
        member.approval_date = timezone.now()
        member.approved_by = request.user
        
        # Set expiry date based on membership category
        member.expiry_date = timezone.now().date() + timedelta(
            days=member.membership_category.duration_months * 30
        )
        
        member.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='approve',
            model_name='Member',
            object_id=str(member.id),
            description=f'Approved member {member.membership_id}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
        )
        
        # Create notification for member
        Notification.objects.create(
            recipient=member.user,
            notification_type='approval',
            title='Membership Approved',
            message=f'Congratulations! Your membership application has been approved. Your membership ID is {member.membership_id}.'
        )
        
        messages.success(request, f'Member {member.membership_id} has been approved successfully.')
        return redirect('member_detail', member_id=member.id)
    
    return redirect('member_list')


@login_required
@user_passes_test(is_admin_or_staff, login_url='login')
def reject_member(request, member_id):
    """
    Reject a pending member registration
    """
    if request.method == 'POST':
        member = get_object_or_404(Member, id=member_id, status='pending')
        rejection_reason = request.POST.get('rejection_reason', '')
        
        member.status = 'rejected'
        member.rejection_reason = rejection_reason
        member.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='reject',
            model_name='Member',
            object_id=str(member.id),
            description=f'Rejected member {member.membership_id}. Reason: {rejection_reason}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
        )
        
        # Create notification for member
        Notification.objects.create(
            recipient=member.user,
            notification_type='approval',
            title='Membership Application Rejected',
            message=f'Your membership application has been rejected. Reason: {rejection_reason}'
        )
        
        messages.warning(request, f'Member {member.membership_id} has been rejected.')
        return redirect('member_detail', member_id=member.id)
    
    return redirect('member_list')


# ============================================================================
# ADMIN VIEWS - Payment Management
# ============================================================================

@login_required
@user_passes_test(is_admin_or_staff, login_url='login')
def payment_list(request):
    """
    List all payments with filtering
    """
    payments = Payment.objects.select_related('member').all()
    
    # Filtering
    status = request.GET.get('status')
    payment_type = request.GET.get('payment_type')
    search = request.GET.get('search')
    
    if status:
        payments = payments.filter(status=status)
    
    if payment_type:
        payments = payments.filter(payment_type=payment_type)
    
    if search:
        payments = payments.filter(
            Q(payment_reference__icontains=search) |
            Q(mpesa_receipt_number__icontains=search) |
            Q(member__membership_id__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(payments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_status': status,
        'current_payment_type': payment_type,
        'search_query': search,
    }
    
    return render(request, 'admin/payment_list.html', context)


@login_required
@user_passes_test(is_admin, login_url='login')
def system_settings(request):
    """
    Manage system settings
    """
    from .models import SystemSetting
    
    settings = SystemSetting.objects.all().order_by('key')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'admin/system_settings.html', context)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip