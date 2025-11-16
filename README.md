# Kalda-Tech Membership Registration & Payment Management System

![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)
![License](https://img.shields.io/badge/License-Proprietary-red.svg)

A comprehensive Django-based web system for managing member registrations, secure M-Pesa payments, renewals, and administrative operations with advanced analytics.

---

##  Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [M-Pesa Integration](#mpesa-integration)
- [Deployment](#deployment)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Security](#security)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

##  Features

### Member Management
-  **Online Registration** - Digital member registration with document uploads
-  **Unique Membership IDs** - Auto-generated membership numbers (e.g., KTS-2024-0001)
-  **Member Profiles** - Comprehensive member information management
-  **Document Management** - Upload and verify ID copies, photos, certificates
-  **Approval Workflow** - Multi-step approval process (Pending → Approved → Active)
-  **Geographic Organization** - Country and region-based member categorization

### Payment System
-  **M-Pesa Integration** - Secure STK Push payments via Daraja API
-  **Digital Receipts** - Auto-generated PDF receipts with unique numbers
-  **Multiple Payment Types** - Registration fees, renewals, late payments
-  **Payment Verification** - Automatic payment status tracking
-  **Payment Notifications** - Email and SMS confirmations

### Member Portal
-  **Dashboard** - Personal member dashboard with quick actions
-  **Self-Service Renewals** - Online membership renewal with M-Pesa
-  **Payment History** - Complete transaction history
-  **Certificate Downloads** - Downloadable membership certificates
-  **Notifications** - Real-time updates and reminders

### Admin Dashboard
-  **User Management** - Comprehensive member approval and management
-  **Analytics & Reports** - Real-time statistics and data visualization
-  **Advanced Search** - Filter by status, location, dates, payment status
-  **Data Export** - CSV/Excel export capabilities
- **Role-Based Access** - Admin, staff, and member roles
- **Audit Trail** - Complete activity logging

### Security Features
-  **HTTPS/SSL** - Secure data transmission
-  **CSRF Protection** - Cross-site request forgery prevention
-  **Strong Authentication** - Secure user authentication system
-  **Activity Logging** - Complete audit trail
-  **Access Control** - Role-based permissions

---

##  Technology Stack

### Backend
- **Framework**: Django 4.2+
- **API**: Django REST Framework 3.14+
- **Database**: PostgreSQL 14+
- **Task Queue**: Celery (for background tasks)
- **Cache**: Redis

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with animations
- **Bootstrap 5** - Responsive framework
- **JavaScript** - Interactive features
- **jQuery** - DOM manipulation

### Payment Integration
- **Safaricom Daraja API** - M-Pesa STK Push
- **Requests** - HTTP library for API calls

### Deployment
- **Server**: Ubuntu 22.04 LTS
- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **SSL**: Let's Encrypt (Certbot)

### Development Tools
- **Version Control**: Git
- **Environment Management**: virtualenv/venv
- **Code Quality**: Black, Flake8, isort
- **Testing**: pytest, coverage

---

##  System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Python**: 3.10+
- **PostgreSQL**: 14+
- **Redis**: 6.0+

### Recommended Requirements
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **Python**: 3.11+
- **PostgreSQL**: 15+
- **Redis**: 7.0+

---

##  Installation

### 1. Clone Repository

```bash
git clone https://github.com/kalda-tech/membership-system.git
cd membership-system
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### 4. Install System Dependencies (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3-dev postgresql postgresql-contrib \
    libpq-dev redis-server nginx supervisor
```

---

##  Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Database Configuration
DB_NAME=membership_db
DB_USER=membership_user
DB_PASSWORD=your-secure-database-password
DB_HOST=localhost
DB_PORT=5432

# M-Pesa Daraja API Configuration
MPESA_ENVIRONMENT=sandbox  # Change to 'production' for live
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=174379  # Your business shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback/

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# SMS Configuration (Africa's Talking or similar)
SMS_API_KEY=your-sms-api-key
SMS_USERNAME=your-sms-username

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Static & Media Files
STATIC_URL=/static/
MEDIA_URL=/media/
STATIC_ROOT=/var/www/membership/static/
MEDIA_ROOT=/var/www/membership/media/
```

### 2. Django Settings

Update `settings.py` with your configuration:

```python
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Static files
STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(BASE_DIR, 'staticfiles'))
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))
```

---

##  Database Setup

### 1. Create PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE membership_db;
CREATE USER membership_user WITH PASSWORD 'your-secure-password';
ALTER ROLE membership_user SET client_encoding TO 'utf8';
ALTER ROLE membership_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE membership_user SET timezone TO 'Africa/Nairobi';
GRANT ALL PRIVILEGES ON DATABASE membership_db TO membership_user;

# Exit
\q
```

### 2. Run Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 3. Load Initial Data (Optional)

```bash
# Load countries and regions
python manage.py loaddata fixtures/countries.json
python manage.py loaddata fixtures/regions.json
python manage.py loaddata fixtures/membership_categories.json
```

---

##  M-Pesa Integration

### 1. Get Daraja API Credentials

1. Visit [Safaricom Daraja Portal](https://developer.safaricom.co.ke/)
2. Create an account and log in
3. Create a new app
4. Get your Consumer Key and Consumer Secret
5. Generate a Passkey for STK Push

### 2. Configure M-Pesa Settings

Update your `.env` file with M-Pesa credentials:

```bash
MPESA_ENVIRONMENT=sandbox  # or 'production'
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=174379  # Test shortcode for sandbox
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback/
```

### 3. Test M-Pesa Integration

```bash
# Test in sandbox mode
python manage.py test_mpesa

# Use test credentials:
# Phone: 254708374149
# Amount: Any amount
# Account Reference: TEST
```

### 4. Go Live

1. Submit your app for review on Daraja Portal
2. Get production credentials
3. Update `.env` with production credentials
4. Change `MPESA_ENVIRONMENT=production`
5. Test thoroughly before full deployment

---

##  Deployment

### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx postgresql \
    postgresql-contrib redis-server supervisor git
```

### 2. Deploy Application

```bash
# Create application directory
sudo mkdir -p /var/www/membership
sudo chown $USER:$USER /var/www/membership

# Clone and setup
cd /var/www/membership
git clone your-repo-url .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate
```

### 3. Configure Gunicorn

Create `/etc/supervisor/conf.d/membership.conf`:

```ini
[program:membership]
directory=/var/www/membership
command=/var/www/membership/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/membership/membership.sock \
    config.wsgi:application
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/membership/gunicorn.log
stderr_logfile=/var/log/membership/gunicorn_error.log
```

### 4. Configure Nginx

Create `/etc/nginx/sites-available/membership`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/membership/staticfiles/;
    }

    location /media/ {
        alias /var/www/membership/media/;
    }

    location / {
        proxy_pass http://unix:/var/www/membership/membership.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/membership /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Install SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 6. Start Services

```bash
# Start Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start membership

# Start Celery (for background tasks)
celery -A config worker -l info
```

---

##  Usage

### Admin Access

1. Navigate to `https://yourdomain.com/admin/`
2. Log in with superuser credentials
3. Access the full admin dashboard

### Member Registration

1. Visit `https://yourdomain.com/register/`
2. Fill in registration form
3. Upload required documents
4. Make payment via M-Pesa
5. Wait for admin approval

### Member Portal

1. Log in at `https://yourdomain.com/login/`
2. Access personal dashboard
3. View membership status
4. Renew membership
5. Download certificates

---

##  API Documentation

### Authentication

```bash
# Get JWT Token
POST /api/auth/login/
{
    "username": "member@example.com",
    "password": "password123"
}

# Response
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Member Endpoints

```bash
# Get member profile
GET /api/members/profile/
Authorization: Bearer <token>

# Update member profile
PATCH /api/members/profile/
Authorization: Bearer <token>
{
    "phone_number": "+254712345678",
    "physical_address": "New address"
}

# Get payment history
GET /api/payments/history/
Authorization: Bearer <token>
```

### Payment Endpoints

```bash
# Initiate M-Pesa payment
POST /api/payments/mpesa/initiate/
Authorization: Bearer <token>
{
    "amount": 1000,
    "phone_number": "254712345678",
    "payment_type": "renewal"
}

# Check payment status
GET /api/payments/<payment_reference>/status/
Authorization: Bearer <token>
```

---

##  Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test members

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test M-Pesa Integration

```bash
# Test STK Push
python manage.py test_mpesa_stk

# Test callback handling
python manage.py test_mpesa_callback
```

---

##  Security

### Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **Strong Passwords**: Use complex database and admin passwords
3. **SSL/HTTPS**: Always use SSL in production
4. **Regular Updates**: Keep Django and dependencies updated
5. **Backup Database**: Daily automated backups
6. **Monitor Logs**: Regular log review for suspicious activity
7. **Rate Limiting**: Implement API rate limiting
8. **CSRF Protection**: Enabled by default in Django

### Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Enable SSL/HTTPS
- [ ] Secure cookie settings
- [ ] Regular security audits
- [ ] Keep dependencies updated
- [ ] Monitor failed login attempts
- [ ] Implement 2FA for admin accounts
- [ ] Regular database backups

---

##  Maintenance

### Daily Tasks
- Monitor system logs
- Check payment processing
- Review failed transactions

### Weekly Tasks
- Database backup verification
- Security updates
- Performance monitoring

### Monthly Tasks
- Full system backup
- Security audit
- Dependency updates
- Generate analytics reports

### Database Backup

```bash
# Manual backup
pg_dump -U membership_user membership_db > backup_$(date +%Y%m%d).sql

# Automated daily backup (crontab)
0 2 * * * pg_dump -U membership_user membership_db > /backups/db_$(date +\%Y\%m\%d).sql
```

---

##  Troubleshooting

### Common Issues

**Issue**: M-Pesa payment not processing
```bash
# Check logs
tail -f /var/log/membership/mpesa.log

# Verify credentials
python manage.py verify_mpesa_config

# Test connectivity
curl https://sandbox.safaricom.co.ke/
```

**Issue**: Static files not loading
```bash
# Collect static files
python manage.py collectstatic --clear --noinput

# Check permissions
sudo chown -R www-data:www-data /var/www/membership/staticfiles/
```

**Issue**: Database connection error
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U membership_user -d membership_db -h localhost
```

---

##  Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8
- Write unit tests
- Document new features
- Update README

---

##  License

**Proprietary License**

Copyright © 2024 Kalda-Tech Systems. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use of this software is strictly prohibited.

---

##  Support

### Contact Information

**Kalda-Tech Systems**
-  Email: info@kalda-techsystems.com
-  Website: www.kalda-techsystems.com
-  Location: Rongai, Kenya
-  Phone: +254 XXX XXX XXX

### Support Hours
- Monday - Friday: 8:00 AM - 6:00 PM EAT
- Saturday: 9:00 AM - 1:00 PM EAT
- Sunday: Closed (Emergency support available)

### Reporting Issues

For bug reports or feature requests, please email support with:
1. Detailed description
2. Steps to reproduce
3. Screenshots (if applicable)
4. System information

---

##  Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Safaricom Daraja API Docs](https://developer.safaricom.co.ke/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

**Built with Love  by Steve Ongera for  Kalda-Tech Systems**

*Empowering organizations through innovative technology solutions*