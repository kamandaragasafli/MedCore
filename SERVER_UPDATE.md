# Serverdə Kod Yeniləməsi

Serverdə kod yeniləmək üçün addımlar:

## 1. Kod yeniləməsi

```bash
cd ~/var/www/MedCore
source venv/bin/activate
git pull origin main
```

## 2. Cache təmizləmə

```bash
# Python cache təmizlə
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete

# Django cache təmizlə (əgər Redis istifadə edirsinizsə)
# redis-cli FLUSHALL
```

## 3. Serveri yenidən başlat

```bash
# Gunicorn istifadə edirsinizsə
sudo systemctl restart gunicorn
# və ya
pkill -f gunicorn
# Sonra yenidən başlat:
export DJANGO_SETTINGS_MODULE=config.settings_production
export $(grep -v '^#' .env | xargs)
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2

# Nginx istifadə edirsinizsə
sudo systemctl restart nginx
```

## 4. Yoxlama

```bash
# Log-ları yoxla
tail -f logs/django.log

# Və ya Gunicorn log-ları
# journalctl -u gunicorn -f
```

## 5. Database yoxlaması

Əgər problem davam edərsə, database-də subscription status-u yoxla:

```bash
cd ~/var/www/MedCore
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings_production
export $(grep -v '^#' .env | xargs)

python manage.py shell
```

Python shell-də:

```python
from subscription.models import Company, Subscription, ContractAgreement

# Bütün şirkətləri yoxla
companies = Company.objects.all()
for c in companies:
    print(f"{c.name}: {c.db_name}")
    subs = c.subscriptions.all()
    for s in subs:
        print(f"  Subscription: {s.status}, Plan: {s.plan.name}")
    contracts = ContractAgreement.objects.filter(company=c)
    for ct in contracts:
        print(f"  Contract: agreed={ct.agreed}, user={ct.user.username}")

# Müqavilə razılaşdırılmış amma subscription pending olanları aktivləşdir
pending_subs = Subscription.objects.filter(status='pending')
for sub in pending_subs:
    contracts = ContractAgreement.objects.filter(company=sub.company, agreed=True)
    if contracts.exists():
        sub.status = 'active'
        sub.save()
        print(f"Activated subscription for {sub.company.name}")
```

## 6. Əgər hələ də işləmirsə

```bash
# Serveri tam yenidən başlat
sudo reboot

# Və ya yalnız Python proseslərini öldür
pkill -9 python
pkill -9 gunicorn

# Sonra yenidən başlat
```
