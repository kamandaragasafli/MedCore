# Serverdə MedCore DB quraşdırması

Bu təlimat serverdə (`~/var/www/MedCore`) PostgreSQL və Django DB-ni qurmaq üçündür.

---

## 1. PostgreSQL quraşdırma

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y postgresql postgresql-contrib libpq-dev

# PostgreSQL servisinin işlədiyini yoxla
sudo systemctl status postgresql
```

---

## 2. Default verilənlər bazası və istifadəçi yaratmaq

```bash
sudo -u postgres psql
```

PostgreSQL konsolunda (parolu özünüz əvəz edin):

```sql
CREATE USER medadmin_user WITH PASSWORD 'ÖZ_GÜCLÜ_PAROLUNUZ';
CREATE DATABASE medadmin OWNER medadmin_user;
ALTER USER medadmin_user CREATEDB;
\q
```

Və ya bir sətirdə (parolu əvəz edin):

```bash
sudo -u postgres psql -c "CREATE USER medadmin_user WITH PASSWORD 'ÖZ_PAROL'; CREATE DATABASE medadmin OWNER medadmin_user; ALTER USER medadmin_user CREATEDB;"
```

---

## 3. Environment dəyişənləri (.env)

Layihə qovluğunda `.env` faylı yaradın:

```bash
cd ~/var/www/MedCore
nano .env
```

Aşağıdakıları yazın (qiymətləri öz serverinizə uyğunlaşdırın):

```env
# Django
SECRET_KEY=çox-uzun-təsadüfi-sətir-buraya
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,IP_ADRESINIZ

# PostgreSQL (default DB)
DB_NAME=medadmin
DB_USER=medadmin_user
DB_PASSWORD=ÖZ_GÜCLÜ_PAROLUNUZ
DB_HOST=localhost
DB_PORT=5432

# İstəyə bağlı: OpenAI chatbot üçün
OPENAI_API_KEY=
```

**SECRET_KEY** üçün təsadüfi sətir yaratmaq:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 4. Python bağımlılıqları

```bash
cd ~/var/www/MedCore
source venv/bin/activate
pip install -r requirements.txt
pip install psycopg2-binary
```

---

## 5. Production settings ilə migrate

```bash
cd ~/var/www/MedCore
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings_production

# .env yüklənməsi üçün (python-dotenv istifadə edirsinizsə)
export $(grep -v '^#' .env | xargs)

# Default DB-də cədvəlləri yarat
python manage.py migrate

# Superuser yarat (admin panel üçün)
python manage.py createsuperuser
```

---

## 6. Static fayllar və logs

```bash
export DJANGO_SETTINGS_MODULE=config.settings_production
python manage.py collectstatic --noinput
mkdir -p logs
```

---

## 7. Gunicorn / Nginx (qısa)

Gunicorn ilə işə salmaq üçün:

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Environment-i ötürmək üçün:

```bash
export DJANGO_SETTINGS_MODULE=config.settings_production
export $(grep -v '^#' .env | xargs)
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

---

## 8. Şirkət (tenant) qeydiyyatından sonra

- İstifadəçi **subscription** (qeydiyyat) səhifəsindən şirkət yaradanda sistem avtomatik **tenant database** yaradır (PostgreSQL-da yeni DB).
- Həmin DB üçün migration `create_tenant_database()` tərəfindən icra olunur.
- Əgər şirkətlər artıq varsa və `db_name` boşdursa: `python manage.py populate_db_names` (bu skript varsa) və ya Django admin-dan şirkətə `db_name` (məs. `tenant_slug`) təyin edib tenant DB-ni yaratmaq üçün uyğun funksiyanı/komandanı işə sala bilərsiniz.

---

## Tez-tez verilən xətalar

| Xəta | Həll |
|------|------|
| `FATAL: password authentication failed` | `.env`-də `DB_PASSWORD`-u postgres-də verdiyiniz parolla eyni edin. |
| `relation "subscription_company" does not exist` | `python manage.py migrate` default DB üçün işlədildiyindən əmin olun. |
| `ModuleNotFoundError: psycopg2` | `pip install psycopg2-binary` edin. |
| `SECRET_KEY` / `ALLOWED_HOSTS` | `.env`-də düzgün təyin edin və app server (gunicorn) bu env ilə işə düşsün. |

---

## Bir sətirdə (xülasə)

```bash
cd ~/var/www/MedCore && source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings_production
export $(grep -v '^#' .env | xargs)
pip install -r requirements.txt psycopg2-binary
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

Bundan sonra Gunicorn və ya Nginx ilə tətbiqi işə sala bilərsiniz.
