"""
Kalda-Tech Systems - Membership Registration & Payment Management System
Django Admin Configuration
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.contrib import messages
from .models import (
    User, Country, Region, MembershipCategory, Member, MemberDocument,
    Payment, PaymentReceipt, MembershipRenewal, MembershipCertificate,
    Notification, AuditLog, SystemSetting
)


# ============================================================================
# CUSTOM ADMIN SITE
# ============================================================================

class KaldaTechAdminSite(admin.AdminSite):
    site_header = 'Kalda-Tech Membership System'
    site_title = 'Kalda-Tech Admin'
    index_title = 'System Administration Dashboard'


admin_site = KaldaTechAdminSite(name='kalda_admin')


# ============================================================================
# INLINE ADMIN CLASSES
# ============================================================================

class MemberDocumentInline(admin.TabularInline):
    model = MemberDocument
    extra = 0
    fields = ('document_type', 'document_file', 'is_verified', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
    can_delete = True


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('payment_reference', 'payment_type', 'amount', 'status', 'created_at')
    readonly_fields = ('payment_reference', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class MembershipRenewalInline(admin.TabularInline):
    model = MembershipRenewal
    extra = 0
    fields = ('previous_expiry_date', 'new_expiry_date', 'renewal_fee', 'status', 'initiated_at')
    readonly_fields = ('initiated_at',)
    can_delete = False


class RegionInline(admin.TabularInline):
    model = Region
    extra = 1
    fields = ('name', 'code', 'is_active')


# ============================================================================
# USER ADMIN
# ============================================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'phone_number', 'user_type', 
        'is_verified', 'is_active', 'date_joined'
    )
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'email')
        }),
    )
    
    actions = ['verify_users', 'deactivate_users']
    
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} users verified successfully.')
    verify_users.short_description = 'Verify selected users'
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'


# ============================================================================
# LOCATION ADMIN
# ============================================================================

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)
    inlines = [RegionInline]
    
    def region_count(self, obj):
        return obj.regions.count()
    region_count.short_description = 'Regions'


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'code', 'member_count', 'is_active')
    list_filter = ('country', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'country__name')
    ordering = ('country', 'name')
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


# ============================================================================
# MEMBERSHIP CATEGORY ADMIN
# ============================================================================

@admin.register(MembershipCategory)
class MembershipCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'registration_fee', 'annual_fee', 
        'duration_months', 'member_count', 'is_active'
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'benefits')
        }),
        ('Pricing', {
            'fields': ('registration_fee', 'annual_fee', 'duration_months')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def member_count(self, obj):
        count = obj.members.count()
        url = reverse('admin:membership_member_changelist') + f'?membership_category__id__exact={obj.id}'
        return format_html('<a href="{}">{} members</a>', url, count)
    member_count.short_description = 'Members'


# ============================================================================
# MEMBER ADMIN
# ============================================================================

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'membership_id', 'get_full_name', 'status_badge', 
        'membership_category', 'country', 'registration_date', 
        'expiry_date', 'payment_status'
    )
    list_filter = (
        'status', 'membership_category', 'country', 'region',
        'gender', 'registration_date', 'expiry_date'
    )
    search_fields = (
        'membership_id', 'first_name', 'last_name', 'email',
        'phone_number', 'national_id'
    )
    ordering = ('-registration_date',)
    date_hierarchy = 'registration_date'
    
    readonly_fields = (
        'membership_id', 'registration_date', 'created_at', 
        'updated_at', 'approval_date'
    )
    
    fieldsets = (
        ('Membership Information', {
            'fields': (
                'membership_id', 'user', 'membership_category',
                'status', 'registration_date', 'approval_date',
                'expiry_date', 'approved_by', 'rejection_reason'
            )
        }),
        ('Personal Information', {
            'fields': (
                'first_name', 'middle_name', 'last_name',
                'date_of_birth', 'gender', 'national_id'
            )
        }),
        ('Contact Information', {
            'fields': (
                'email', 'phone_number', 'alternative_phone',
                'postal_address', 'physical_address'
            )
        }),
        ('Location', {
            'fields': ('country', 'region')
        }),
        ('Professional Information', {
            'fields': ('occupation', 'organization'),
            'classes': ('collapse',)
        }),
        ('Additional Details', {
            'fields': ('notes', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MemberDocumentInline, PaymentInline, MembershipRenewalInline]
    
    actions = [
        'approve_members', 'reject_members', 'suspend_members',
        'send_expiry_reminders', 'export_to_csv'
    ]
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'suspended': '#6c757d',
            'expired': '#f8d7da',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_status(self, obj):
        completed_payments = obj.payments.filter(status='completed').count()
        total_amount = obj.payments.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        return format_html(
            '{} payments<br/>KES {:,.2f}',
            completed_payments, total_amount
        )
    payment_status.short_description = 'Payments'
    
    def approve_members(self, request, queryset):
        pending_members = queryset.filter(status='pending')
        updated = 0
        
        for member in pending_members:
            member.status = 'approved'
            member.approved_by = request.user
            member.approval_date = timezone.now()
            
            # Set expiry date based on membership category
            member.expiry_date = timezone.now().date() + timezone.timedelta(
                days=member.membership_category.duration_months * 30
            )
            member.save()
            updated += 1
        
        self.message_user(
            request, 
            f'{updated} members approved successfully.',
            messages.SUCCESS
        )
    approve_members.short_description = 'Approve selected members'
    
    def reject_members(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            approved_by=request.user
        )
        self.message_user(
            request,
            f'{updated} members rejected.',
            messages.WARNING
        )
    reject_members.short_description = 'Reject selected members'
    
    def suspend_members(self, request, queryset):
        updated = queryset.exclude(status='pending').update(status='suspended')
        self.message_user(
            request,
            f'{updated} members suspended.',
            messages.WARNING
        )
    suspend_members.short_description = 'Suspend selected members'
    
    def send_expiry_reminders(self, request, queryset):
        # Logic to send expiry reminders would go here
        count = queryset.count()
        self.message_user(
            request,
            f'Expiry reminders sent to {count} members.',
            messages.INFO
        )
    send_expiry_reminders.short_description = 'Send expiry reminders'
    
    def export_to_csv(self, request, queryset):
        # CSV export logic would go here
        self.message_user(
            request,
            f'{queryset.count()} members exported to CSV.',
            messages.SUCCESS
        )
    export_to_csv.short_description = 'Export to CSV'


# ============================================================================
# MEMBER DOCUMENT ADMIN
# ============================================================================

@admin.register(MemberDocument)
class MemberDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'member', 'document_type', 'document_preview', 
        'is_verified', 'uploaded_at'
    )
    list_filter = ('document_type', 'is_verified', 'uploaded_at')
    search_fields = ('member__membership_id', 'member__first_name', 'member__last_name')
    ordering = ('-uploaded_at',)
    date_hierarchy = 'uploaded_at'
    
    readonly_fields = ('uploaded_at',)
    
    actions = ['verify_documents']
    
    def document_preview(self, obj):
        if obj.document_file:
            return format_html(
                '<a href="{}" target="_blank">View Document</a>',
                obj.document_file.url
            )
        return '-'
    document_preview.short_description = 'Document'
    
    def verify_documents(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(
            request,
            f'{updated} documents verified successfully.',
            messages.SUCCESS
        )
    verify_documents.short_description = 'Verify selected documents'


# ============================================================================
# PAYMENT ADMIN
# ============================================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'payment_reference', 'member', 'payment_type', 
        'amount', 'status_badge', 'mpesa_receipt_number',
        'phone_number', 'initiated_at'
    )
    list_filter = (
        'status', 'payment_type', 'currency', 
        'initiated_at', 'completed_at'
    )
    search_fields = (
        'payment_reference', 'mpesa_receipt_number', 
        'phone_number', 'member__membership_id'
    )
    ordering = ('-initiated_at',)
    date_hierarchy = 'initiated_at'
    
    readonly_fields = (
        'payment_reference', 'initiated_at', 'completed_at',
        'created_at', 'updated_at'
    )
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'payment_reference', 'member', 'payment_type',
                'amount', 'currency', 'status'
            )
        }),
        ('M-Pesa Details', {
            'fields': (
                'mpesa_receipt_number', 'phone_number',
                'checkout_request_id', 'merchant_request_id'
            )
        }),
        ('Additional Information', {
            'fields': ('description', 'failure_reason')
        }),
        ('Timestamps', {
            'fields': ('initiated_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def status_badge(self, obj):
        colors = {
            'initiated': '#17a2b8',
            'pending': '#FFA500',
            'completed': '#28a745',
            'failed': '#dc3545',
            'cancelled': '#6c757d',
            'refunded': '#ffc107',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} payments marked as completed.',
            messages.SUCCESS
        )
    mark_as_completed.short_description = 'Mark as completed'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.filter(status__in=['initiated', 'pending']).update(
            status='failed'
        )
        self.message_user(
            request,
            f'{updated} payments marked as failed.',
            messages.WARNING
        )
    mark_as_failed.short_description = 'Mark as failed'


# ============================================================================
# PAYMENT RECEIPT ADMIN
# ============================================================================

@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_number', 'payment', 'generated_at',
        'sent_via_email', 'sent_via_sms', 'receipt_link'
    )
    list_filter = ('sent_via_email', 'sent_via_sms', 'generated_at')
    search_fields = ('receipt_number', 'payment__payment_reference')
    ordering = ('-generated_at',)
    date_hierarchy = 'generated_at'
    
    readonly_fields = ('receipt_number', 'generated_at')
    
    def receipt_link(self, obj):
        if obj.receipt_file:
            return format_html(
                '<a href="{}" target="_blank">Download Receipt</a>',
                obj.receipt_file.url
            )
        return '-'
    receipt_link.short_description = 'Receipt'


# ============================================================================
# MEMBERSHIP RENEWAL ADMIN
# ============================================================================

@admin.register(MembershipRenewal)
class MembershipRenewalAdmin(admin.ModelAdmin):
    list_display = (
        'member', 'previous_expiry_date', 'new_expiry_date',
        'renewal_fee', 'status', 'initiated_at'
    )
    list_filter = ('status', 'initiated_at', 'completed_at')
    search_fields = ('member__membership_id', 'member__first_name', 'member__last_name')
    ordering = ('-initiated_at',)
    date_hierarchy = 'initiated_at'
    
    readonly_fields = ('initiated_at', 'completed_at')


# ============================================================================
# MEMBERSHIP CERTIFICATE ADMIN
# ============================================================================

@admin.register(MembershipCertificate)
class MembershipCertificateAdmin(admin.ModelAdmin):
    list_display = (
        'certificate_number', 'member', 'issue_date',
        'valid_until', 'is_active', 'certificate_link'
    )
    list_filter = ('is_active', 'issue_date', 'valid_until')
    search_fields = (
        'certificate_number', 'member__membership_id',
        'member__first_name', 'member__last_name'
    )
    ordering = ('-issue_date',)
    date_hierarchy = 'issue_date'
    
    readonly_fields = ('certificate_number', 'issue_date')
    
    def certificate_link(self, obj):
        if obj.certificate_file:
            return format_html(
                '<a href="{}" target="_blank">Download Certificate</a>',
                obj.certificate_file.url
            )
        return '-'
    certificate_link.short_description = 'Certificate'


# ============================================================================
# NOTIFICATION ADMIN
# ============================================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'recipient', 'notification_type', 'title',
        'is_read', 'is_sent_email', 'is_sent_sms', 'created_at'
    )
    list_filter = (
        'notification_type', 'is_read', 'is_sent_email',
        'is_sent_sms', 'created_at'
    )
    search_fields = ('recipient__username', 'title', 'message')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'read_at')
    
    actions = ['mark_as_read', 'mark_as_sent_email']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(
            request,
            f'{updated} notifications marked as read.',
            messages.SUCCESS
        )
    mark_as_read.short_description = 'Mark as read'
    
    def mark_as_sent_email(self, request, queryset):
        updated = queryset.update(is_sent_email=True)
        self.message_user(
            request,
            f'{updated} notifications marked as sent via email.',
            messages.SUCCESS
        )
    mark_as_sent_email.short_description = 'Mark as sent via email'


# ============================================================================
# AUDIT LOG ADMIN
# ============================================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'action', 'model_name', 'object_id',
        'ip_address', 'created_at'
    )
    list_filter = ('action', 'model_name', 'created_at')
    search_fields = ('user__username', 'description', 'ip_address', 'object_id')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================================
# SYSTEM SETTINGS ADMIN
# ============================================================================

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_preview', 'is_active', 'updated_at', 'updated_by')
    list_filter = ('is_active', 'updated_at')
    search_fields = ('key', 'description', 'value')
    ordering = ('key',)
    
    readonly_fields = ('updated_at',)
    
    def value_preview(self, obj):
        if len(obj.value) > 50:
            return f"{obj.value[:50]}..."
        return obj.value
    value_preview.short_description = 'Value'
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)