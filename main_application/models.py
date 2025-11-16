"""
Kalda-Tech Systems - Membership Registration & Payment Management System
Django Models Structure
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from decimal import Decimal


# ============================================================================
# USER & AUTHENTICATION MODELS
# ============================================================================

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    USER_TYPE_CHOICES = [
        ('member', 'Member'),
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='member'
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?254\d{9}$',
            message='Phone number must be in format: +254XXXXXXXXX'
        )],
        unique=True
    )
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"


# ============================================================================
# LOCATION MODELS
# ============================================================================

class Country(models.Model):
    """
    Country model for organizing members geographically
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(
        max_length=3,
        unique=True,
        help_text="ISO 3166-1 alpha-3 country code"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'countries'
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['name']

    def __str__(self):
        return self.name


class Region(models.Model):
    """
    Region/County model within countries
    """
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name='regions'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'regions'
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'
        ordering = ['country', 'name']
        unique_together = ['country', 'name']

    def __str__(self):
        return f"{self.name}, {self.country.name}"


# ============================================================================
# MEMBERSHIP MODELS
# ============================================================================

class MembershipCategory(models.Model):
    """
    Different membership tiers/categories with pricing
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    registration_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    annual_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    benefits = models.TextField(
        help_text="List membership benefits"
    )
    duration_months = models.IntegerField(
        default=12,
        help_text="Membership validity period in months"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'membership_categories'
        verbose_name = 'Membership Category'
        verbose_name_plural = 'Membership Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Member(models.Model):
    """
    Core Member model with registration details
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    # Relationships
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='member_profile'
    )
    membership_category = models.ForeignKey(
        MembershipCategory,
        on_delete=models.PROTECT,
        related_name='members'
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name='members'
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name='members'
    )

    # Unique Membership ID
    membership_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Auto-generated unique membership ID"
    )

    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    national_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="National ID or Passport Number"
    )
    
    # Contact Information
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    alternative_phone = models.CharField(max_length=15, blank=True)
    postal_address = models.CharField(max_length=200, blank=True)
    physical_address = models.TextField()

    # Professional Information
    occupation = models.CharField(max_length=200, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    
    # Membership Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Approval workflow
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_members'
    )
    rejection_reason = models.TextField(blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'members'
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['membership_id']),
            models.Index(fields=['status']),
            models.Index(fields=['national_id']),
        ]

    def __str__(self):
        return f"{self.membership_id} - {self.get_full_name()}"

    def get_full_name(self):
        """Return member's full name"""
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.first_name}{middle} {self.last_name}"

    def is_membership_active(self):
        """Check if membership is currently active"""
        if self.status != 'approved':
            return False
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return False
        return True

    def save(self, *args, **kwargs):
        """Override save to generate membership ID"""
        if not self.membership_id:
            # Generate unique membership ID (e.g., KTS-2024-0001)
            year = timezone.now().year
            last_member = Member.objects.filter(
                membership_id__startswith=f'KTS-{year}'
            ).order_by('-membership_id').first()
            
            if last_member:
                last_number = int(last_member.membership_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.membership_id = f'KTS-{year}-{new_number:04d}'
        
        super().save(*args, **kwargs)


class MemberDocument(models.Model):
    """
    Documents uploaded by members during registration
    """
    DOCUMENT_TYPE_CHOICES = [
        ('id_copy', 'ID/Passport Copy'),
        ('passport_photo', 'Passport Photo'),
        ('certificate', 'Certificate'),
        ('recommendation', 'Recommendation Letter'),
        ('other', 'Other'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES
    )
    document_file = models.FileField(
        upload_to='member_documents/%Y/%m/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']
        )]
    )
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'member_documents'
        verbose_name = 'Member Document'
        verbose_name_plural = 'Member Documents'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.member.membership_id} - {self.get_document_type_display()}"


# ============================================================================
# PAYMENT MODELS
# ============================================================================

class Payment(models.Model):
    """
    Payment transactions for registration and renewals
    """
    PAYMENT_TYPE_CHOICES = [
        ('registration', 'Registration Fee'),
        ('renewal', 'Renewal Fee'),
        ('late_fee', 'Late Payment Fee'),
    ]

    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    # Relationships
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    # Payment Details
    payment_reference = models.CharField(
        max_length=100,
        unique=True,
        editable=False
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    
    # M-Pesa Details
    mpesa_receipt_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="M-Pesa confirmation code"
    )
    phone_number = models.CharField(max_length=15)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    
    # Status and Timestamps
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='initiated'
    )
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    description = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_reference']),
            models.Index(fields=['mpesa_receipt_number']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.payment_reference} - {self.member.membership_id}"

    def save(self, *args, **kwargs):
        """Override save to generate payment reference"""
        if not self.payment_reference:
            # Generate unique payment reference (e.g., PAY-20240115-UUID)
            date_str = timezone.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:8].upper()
            self.payment_reference = f'PAY-{date_str}-{unique_id}'
        
        super().save(*args, **kwargs)


class PaymentReceipt(models.Model):
    """
    Digital receipts generated for successful payments
    """
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='receipt'
    )
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )
    receipt_file = models.FileField(
        upload_to='receipts/%Y/%m/',
        blank=True,
        help_text="PDF receipt"
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)

    class Meta:
        db_table = 'payment_receipts'
        verbose_name = 'Payment Receipt'
        verbose_name_plural = 'Payment Receipts'
        ordering = ['-generated_at']

    def __str__(self):
        return f"Receipt {self.receipt_number}"

    def save(self, *args, **kwargs):
        """Override save to generate receipt number"""
        if not self.receipt_number:
            # Generate unique receipt number (e.g., RCT-2024-0001)
            year = timezone.now().year
            last_receipt = PaymentReceipt.objects.filter(
                receipt_number__startswith=f'RCT-{year}'
            ).order_by('-receipt_number').first()
            
            if last_receipt:
                last_number = int(last_receipt.receipt_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.receipt_number = f'RCT-{year}-{new_number:04d}'
        
        super().save(*args, **kwargs)


# ============================================================================
# RENEWAL MODELS
# ============================================================================

class MembershipRenewal(models.Model):
    """
    Track membership renewals
    """
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='renewals'
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='renewal',
        null=True,
        blank=True
    )
    
    previous_expiry_date = models.DateField()
    new_expiry_date = models.DateField()
    renewal_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_payment'
    )
    
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'membership_renewals'
        verbose_name = 'Membership Renewal'
        verbose_name_plural = 'Membership Renewals'
        ordering = ['-initiated_at']

    def __str__(self):
        return f"{self.member.membership_id} - Renewal {self.initiated_at.date()}"


# ============================================================================
# CERTIFICATE MODELS
# ============================================================================

class MembershipCertificate(models.Model):
    """
    Digital membership certificates
    """
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )
    certificate_file = models.FileField(
        upload_to='certificates/%Y/',
        blank=True,
        help_text="PDF certificate"
    )
    issue_date = models.DateField(auto_now_add=True)
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)
    
    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_certificates'
    )

    class Meta:
        db_table = 'membership_certificates'
        verbose_name = 'Membership Certificate'
        verbose_name_plural = 'Membership Certificates'
        ordering = ['-issue_date']

    def __str__(self):
        return f"Certificate {self.certificate_number}"

    def save(self, *args, **kwargs):
        """Override save to generate certificate number"""
        if not self.certificate_number:
            year = timezone.now().year
            last_cert = MembershipCertificate.objects.filter(
                certificate_number__startswith=f'CERT-{year}'
            ).order_by('-certificate_number').first()
            
            if last_cert:
                last_number = int(last_cert.certificate_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.certificate_number = f'CERT-{year}-{new_number:04d}'
        
        super().save(*args, **kwargs)


# ============================================================================
# NOTIFICATION MODELS
# ============================================================================

class Notification(models.Model):
    """
    System notifications for members and admins
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('registration', 'Registration'),
        ('approval', 'Approval'),
        ('payment', 'Payment'),
        ('renewal', 'Renewal'),
        ('expiry_reminder', 'Expiry Reminder'),
        ('system', 'System'),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    is_sent_email = models.BooleanField(default=False)
    is_sent_sms = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"


# ============================================================================
# AUDIT LOG MODEL
# ============================================================================

class AuditLog(models.Model):
    """
    System audit trail for tracking important actions
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('payment', 'Payment'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    description = models.TextField()
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['model_name', 'object_id']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name}"


# ============================================================================
# SYSTEM SETTINGS MODEL
# ============================================================================

class SystemSetting(models.Model):
    """
    Configurable system settings
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['key']

    def __str__(self):
        return self.key