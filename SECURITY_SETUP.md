# Security Setup Guide for MedAdmin

## Quick Security Fixes

### 1. Install Required Packages

```bash
pip install python-decouple django-ratelimit psycopg2-binary django-redis
pip freeze > requirements.txt
```

### 2. Create `.env` File

Create a `.env` file in your project root (same directory as `manage.py`):

```env
# Django Settings
SECRET_KEY=your-very-long-random-secret-key-here-minimum-50-characters
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost

# Database (PostgreSQL for production)
DB_NAME=medadmin
DB_USER=medadmin_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# n8n Chatbot
N8N_WEBHOOK_URL=https://agsfli.app.n8n.cloud/webhook-test/c37e42bd-56c6-47a1-9f75-47b78923c2a6
N8N_API_KEY=
CHATBOT_API_KEY=your-random-api-key-for-securing-chatbot-api

# Redis (for caching)
REDIS_URL=redis://127.0.0.1:6379/1
```

### 3. Generate Secure Keys

**Generate SECRET_KEY:**
```python
# Run in Python shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

**Generate CHATBOT_API_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 4. Update Settings

The `config/settings.py` has been updated to:
- ✅ Read from environment variables
- ✅ Set secure defaults when `DEBUG=False`
- ✅ Enable security headers in production

### 5. For Production

Use `config/settings_production.py`:

```python
# In your production environment
export DJANGO_SETTINGS_MODULE=config.settings_production
```

Or create a `manage_production.py`:
```python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_production')
```

## Security Features Added

### ✅ Environment Variables
- All secrets now read from `.env` file
- `.env` is in `.gitignore` (won't be committed)

### ✅ Production Security Headers
- `SECURE_SSL_REDIRECT` - Forces HTTPS
- `SESSION_COOKIE_SECURE` - Secure cookies
- `CSRF_COOKIE_SECURE` - Secure CSRF tokens
- `X_FRAME_OPTIONS` - Prevents clickjacking
- `SECURE_HSTS` - HTTP Strict Transport Security

### ✅ API Security
- Chatbot API can be protected with `CHATBOT_API_KEY`
- API key checked via `X-API-Key` header

### ✅ Logging
- Production logging configured
- Error emails to admins
- Log rotation (15MB files, 10 backups)

## Testing Security

### 1. Check Current Settings
```bash
python manage.py check --deploy
```

### 2. Test API Key Protection
```bash
# Without API key (should fail if CHATBOT_API_KEY is set)
curl -X POST http://localhost:8000/chatbot/api/query/ \
  -H "Content-Type: application/json" \
  -d '{"query_type": "doctor_list", "company_id": 1}'

# With API key (should work)
curl -X POST http://localhost:8000/chatbot/api/query/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-chatbot-api-key" \
  -d '{"query_type": "doctor_list", "company_id": 1}'
```

## Production Deployment Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate new `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` with your domain
- [ ] Set `CHATBOT_API_KEY` for API protection
- [ ] Enable HTTPS/SSL certificate
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Configure PostgreSQL database
- [ ] Set up Redis for caching
- [ ] Configure email backend
- [ ] Test all security settings

## Important Notes

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use different keys for dev/staging/production**
3. **Rotate keys periodically** (every 90 days)
4. **Monitor logs** for security issues
5. **Keep Django updated** - `pip install --upgrade django`

## Need Help?

- Check `PROJECT_ASSESSMENT.md` for detailed security recommendations
- Check `PRODUCTION_CHECKLIST.md` for deployment checklist
- Django Security: https://docs.djangoproject.com/en/stable/topics/security/

