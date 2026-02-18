# MedCore - AI Sistem Bələdçisi

Bu sənəd MedCore sisteminin tam təsvirini ehtiva edir və AI asistanlarının sistem haqqında məlumat verməsi üçün nəzərdə tutulub.

---

## 📋 Mündəricat

1. [Sistemin Ümumi Təsviri](#sistemin-ümumi-təsviri)
2. [Arxitektura](#arxitektura)
3. [Modellər və Əlaqələr](#modellər-və-əlaqələr)
4. [Əsas Funksionallıq](#əsas-funksionallıq)
5. [URL Strukturu](#url-strukturu)
6. [İstifadəçi Rolları](#istifadəçi-rolları)
7. [Məlumat Axını](#məlumat-axını)
8. [Hesablama Məntiqi](#hesablama-məntiqi)
9. [İmport/Export Funksionallığı](#importexport-funksionallığı)
10. [Texniki Detallar](#texniki-detallar)

---

## 🎯 Sistemin Ümumi Təsviri

**MedCore** - çox tenantlı (multi-tenant) SaaS tibbi idarəetmə sistemidir. Sistem həkimlərin, dərmanların, reseptlərin, satışların və hesabatların idarə edilməsi üçün nəzərdə tutulub.

### Əsas Xüsusiyyətlər:
- **Multi-tenant arxitektura**: Hər şirkətin öz ayrı verilənlər bazası var
- **Dual Session sistemi**: Admin və istifadəçi sessiyaları eyni brauzerdə müstəqil işləyir
- **Həkim maliyyə hesablamaları**: Avtomatik borc və komissiya hesablamaları
- **Aylıq hesabatlar**: Region və həkim üzrə aylıq hesabatlar
- **Excel import/export**: Dərmanlar, həkimlər və borclar üçün Excel import/export
- **AI Chatbot**: Professional və Enterprise planlar üçün OpenAI inteqrasiyası

---

## 🏗️ Arxitektura

### Multi-Tenant Strukturu

Sistem Django-nun database router mexanizmi ilə çox tenantlı arxitektura istifadə edir:

- **Default Database**: Şirkətlər, abunəliklər, istifadəçilər (superuser)
- **Tenant Databases**: Hər şirkətin öz verilənlər bazası (həkimlər, dərmanlar, reseptlər, satışlar)

### Database Router

`subscription/db_router.py` - `TenantDatabaseRouter`:
- `/admin/` və `/master-admin/` üçün default database istifadə edir
- Digər URL-lər üçün tenant database istifadə edir
- `request.user.profile.company.db_name` əsasında database seçir

### Dual Session Sistemi

`core/middleware.py` - `DualSessionMiddleware`:
- `/admin/` üçün `admin_sessionid` cookie istifadə edir
- Digər URL-lər üçün `sessionid` cookie istifadə edir
- İki sessiya eyni brauzerdə müstəqil işləyir

---

## 📊 Modellər və Əlaqələr

### 1. Subscription App (`subscription/models.py`)

#### Company
- `name`: Şirkət adı
- `slug`: URL üçün slug
- `email`: Email
- `db_name`: Verilənlər bazası adı
- `is_active`: Aktiv status

#### SubscriptionPlan
- `plan_type`: 'basic', 'professional', 'enterprise'
- `price_monthly`, `price_yearly`: Qiymətlər
- `max_users`, `max_doctors`, `max_patients`: Limitlər
- `features`: JSONField - xüsusiyyətlər siyahısı

#### Subscription
- `company`: Company ForeignKey
- `plan`: SubscriptionPlan ForeignKey
- `status`: 'active', 'cancelled', 'expired'
- `start_date`, `end_date`: Tarixlər

#### UserProfile
- `user`: User OneToOneField
- `company`: Company ForeignKey
- `role`: 'owner', 'admin', 'doctor', 'staff', 'user'

### 2. Regions App (`regions/models.py`)

#### Region
- `name`: Bölgə adı
- `code`: Unikal kod (avtomatik yaradılır)

#### City
- `region`: Region ForeignKey
- `name`: Şəhər adı

#### Clinic
- `region`: Region ForeignKey
- `city`: City ForeignKey (optional)
- `name`: Klinika adı
- `address`: Ünvan (optional)

#### Specialization
- `name`: İxtisas adı

### 3. Doctors App (`doctors/models.py`)

#### Doctor
**Əsas Məlumatlar:**
- `ad`: Ad Soyad
- `code`: 6 simvollu unikal kod (avtomatik yaradılır)
- `telefon`: Telefon nömrəsi
- `email`: Email (optional)
- `gender`: 'male', 'female', '' (ad soyada görə avtomatik təyin olunur)

**Yer və Təşkilat:**
- `region`: Region ForeignKey
- `city`: City ForeignKey (optional)
- `clinic`: Clinic ForeignKey (optional)

**Peşəkar Məlumatlar:**
- `ixtisas`: Specialization ForeignKey
- `category`: 'A*', 'A', 'B', 'C', 'I ' (Kateqoriya)
- `degree`: 'VIP', 'I', 'II', 'III' (Dərəcə)

**Maliyyə Məlumatları:**
- `evvelki_borc`: Əvvəlki borc (Decimal)
- `hesablanmish_miqdar`: Hesablanmış miqdar (Decimal)
- `silinen_miqdar`: Silinən miqdar (Decimal)
- `yekun_borc`: Yekun borc (avtomatik hesablanır: evvelki_borc + hesablanmish_miqdar - silinen_miqdar)

**Xüsusiyyətlər:**
- `save()` metodu: `yekun_borc` avtomatik hesablanır
- `gender_from_name()` statik metodu: Ad soyadın ilk sözünün sonuna görə cinsiyyət təyin edir ('a' → 'female', 'v' → 'male')

### 4. Drugs App (`drugs/models.py`)

#### Drug
**Əsas Məlumatlar:**
- `ad`: Qısa ad
- `tam_ad`: Tam ad
- `qiymet`: Qiymət (AZN)
- `komissiya`: Komissiya məbləği (AZN, faiz deyil!)
- `buraxilis_formasi`: Buraxılış forması (tablet, capsule, syrup, və s.)
- `dozaj`: Dozaj (optional)
- `barkod`: Barkod (optional, unique)

**Qeyd:** Excel import zamanı yalnız `ad`, `tam_ad`, `komissiya`, `qiymet` sütunları istifadə olunur.

### 5. Prescriptions App (`prescriptions/models.py`)

#### Prescription
- `region`: Region ForeignKey
- `doctor`: Doctor ForeignKey
- `date`: Tarix
- `patient_name`: Xəstə adı (optional)
- `notes`: Qeyd (optional)
- `is_active`: Aktiv status

**Property-lər:**
- `total_amount`: Bütün dərmanların ümumi məbləği
- `drug_count`: Dərman sayı

#### PrescriptionItem
- `prescription`: Prescription ForeignKey
- `drug`: Drug ForeignKey
- `quantity`: Say
- `unit_price`: Vahid qiyməti (resept yaradılanda dərmanın qiyməti)
- `dosage`: Dozaj (optional)
- `duration`: Müddət (optional)

**Property-lər:**
- `total_price`: quantity * unit_price

**Signal-lər:**
- `prescription_item_saved`: PrescriptionItem yaradılanda/deyişdiriləndə həkimin maliyyə məlumatları yenilənir
- `prescription_item_deleted`: PrescriptionItem silinəndə həkimin maliyyə məlumatları yenilənir

### 6. Sales App (`sales/models.py`)

#### Sale
- `region`: Region ForeignKey
- `date`: Tarix
- `notes`: Qeyd (optional)

#### SaleItem
- `sale`: Sale ForeignKey
- `drug`: Drug ForeignKey
- `quantity`: Say
- `unit_price`: Vahid qiyməti

**Signal-lər:**
- `sale_saved`: Sale yaradılanda/deyişdiriləndə regiondakı həkimlərin maliyyə məlumatları yenilənir
- `sale_deleted`: Sale silinəndə regiondakı həkimlərin maliyyə məlumatları yenilənir

### 7. Reports App (`reports/models.py`)

#### Report
- `region`: Region ForeignKey
- `month`: Ay (1-12)
- `year`: İl
- `is_closed`: Bağlanıb mı?
- `closed_at`: Bağlanma tarixi (optional)
- `notes`: Qeyd (optional)

**Qeyd:** Hesabat bağlandıqdan sonra yeni reseptlər yalnız növbəti ay üçün əlavə edilə bilər.

---

## ⚙️ Əsas Funksionallıq

### 1. Həkim İdarəetməsi

**Siyahı (`/doctors/`):**
- Bölgə, şəhər, klinika, ixtisas üzrə filtr
- Həkim adları kliklənə bilər → detay səhifəsinə keçir
- Borc rəng kodlaması:
  - Qırmızı: Yekun borc > 0
  - Yaşıl: Yekun borc < 0
  - Sarı: Yekun borc = 0

**Əlavə Et (`/doctors/add/`):**
- Region, City, Clinic, Specialization seçimi
- Ad Soyad, telefon, email
- Cinsiyyət avtomatik təyin olunur (ad soyadın ilk sözünün sonuna görə)
- Kateqoriya, Dərəcə seçimi
- Əvvəlki Borc (yalnız superadmin görür)

**Detay (`/doctors/<id>/`):**
- Həkim məlumatları
- Resept sayı, ödənişlər
- Aylıq hesabatlar
- Borc məlumatları

### 2. Dərman İdarəetməsi

**Siyahı (`/drugs/`):**
- Dərmanların siyahısı
- Filtr və axtarış

**Əlavə Et (`/drugs/add/`):**
- Ad, Tam ad
- Qiymət, Komissiya
- Buraxılış forması, Dozaj, Barkod (optional)

**Excel Import (`/master-admin/companies/<id>/import-drugs/`):**
- Yalnız 4 sütun: Ad, Tam Ad, Komissiya, Qiymət
- Digər sütunlar nəzərə alınmır

### 3. Resept İdarəetməsi

**Siyahı (`/prescriptions/`):**
- Bölgə, həkim, tarix üzrə filtr
- Həkim adları kliklənə bilər → detay səhifəsinə keçir

**Əlavə Et (`/prescriptions/add/`):**
- Bölgə seçimi → həkimlər yüklənir
- Tarix seçimi (son bağlanmış hesabatdan sonra)
- Dərmanların siyahısı və miqdar daxil etmə
- Xəstə adı və qeyd (optional)

**Qeyd:** Input sahələri üçün CSS-də `pointer-events: auto` və `z-index: 10` təyin edilib.

### 4. Satış İdarəetməsi

**Siyahı (`/sales/`):**
- Satışların siyahısı
- Region və tarix üzrə filtr

**Əlavə Et (`/sales/add/`):**
- Region və tarix seçimi
- Dərmanların siyahısı və miqdar

**Redaktə (`/sales/<id>/edit/`):**
- Satış məlumatlarının redaktəsi

### 5. Hesabatlar (`/reports/`)

**Siyahı:**
- Region və ay/il üzrə filtr
- Hesabatların siyahısı
- Bağlanma statusu

**Yarat/Bax:**
- Region seçilməlidir
- Ay və il seçimi
- Həkimlər üzrə maliyyə məlumatları
- Excel export

**Bağlama:**
- Hesabat bağlandıqdan sonra yeni reseptlər yalnız növbəti ay üçün əlavə edilə bilər

### 6. Master Admin Panel (`/master-admin/`)

**Şirkətlər (`/master-admin/companies/`):**
- Bütün şirkətlərin siyahısı
- Şirkət detalları
- Şirkətə keçid (impersonation)

**Şirkət Detalları (`/master-admin/companies/<id>/`):**
- Şirkət məlumatları
- Həkimlər siyahısı (borc rəng kodlaması ilə)
- Excel Export:
  - Dərmanlar (`/export-drugs/`)
  - Həkimlər (`/export-doctors/`)
  - Borclar (`/export-debts/`)
- Excel Import:
  - Dərmanlar (`/import-drugs/`)
  - Borclar (`/import-debts/`) - Sütunlar: Bölgə, Həkim adı, Yekun borc
  - Tam həkim məlumatları (`/import-doctors-full/`) - Sütunlar: Bölgə, Həkim adı, İxtisas, Dərəcə, Kategoriya, Müəssisə, Borcu
- Borcları sıfırlama (`/zero-debts/`)

**Analitika (`/master-admin/analytics/`):**
- Platforma statistikası
- Şirkətlər, istifadəçilər, abunəliklər

**İstifadəçi İdarəetməsi (`/master-admin/users/`):**
- Bütün istifadəçilərin siyahısı
- Rollar və icazələr

---

## 🔗 URL Strukturu

### Əsas URL-lər (`config/urls.py`)

```
/admin/                    → Django Admin (superuser)
/master-admin/            → Master Admin Panel (superuser)
/subscription/             → Abunəlik idarəetməsi
/                          → Dashboard
/doctors/                  → Həkim idarəetməsi
/drugs/                    → Dərman idarəetməsi
/prescriptions/            → Resept idarəetməsi
/reports/                  → Hesabatlar
/sales/                    → Satış idarəetməsi
/regions/                  → Bölgə idarəetməsi
/chatbot/                  → AI Chatbot
```

### Core App (`core/urls.py`)

```
/login/                    → Giriş
/logout/                   → Çıxış
/                          → Dashboard
/notifications/            → Bildirişlər
/profile/                  → Profil
/settings/                 → Parametrlər
/help/                     → Kömək
```

### Doctors App (`doctors/urls.py`)

```
/doctors/                  → Siyahı
/doctors/add/              → Əlavə et
/doctors/<id>/             → Detay
/doctors/<id>/edit/        → Redaktə
/doctors/<id>/delete/      → Sil
```

### Prescriptions App (`prescriptions/urls.py`)

```
/prescriptions/            → Siyahı
/prescriptions/add/        → Əlavə et
/prescriptions/<id>/       → Detay
/prescriptions/api/doctors/<region_id>/ → API: Region həkimləri
/prescriptions/api/last-closed-report/<region_id>/ → API: Son bağlanmış hesabat
```

### Reports App (`reports/urls.py`)

```
/reports/                  → Siyahı
/reports/create/           → Yarat
/reports/<id>/             → Detay
/reports/<id>/close/       → Bağla
/reports/<id>/export/      → Excel export
```

### Master Admin (`master_admin/urls.py`)

```
/master-admin/             → Dashboard
/master-admin/companies/   → Şirkətlər siyahısı
/master-admin/companies/<id>/ → Şirkət detalları
/master-admin/companies/<id>/switch/ → Şirkətə keçid
/master-admin/companies/<id>/export-doctors/ → Excel export: Həkimlər
/master-admin/companies/<id>/export-debts/ → Excel export: Borclar
/master-admin/companies/<id>/zero-debts/ → Borcları sıfırla
/master-admin/companies/<id>/import-debts/ → Excel import: Borclar
/master-admin/companies/<id>/import-doctors-full/ → Excel import: Tam həkim məlumatları
/master-admin/companies/<id>/import-drugs/ → Excel import: Dərmanlar
/master-admin/analytics/    → Analitika
/master-admin/users/       → İstifadəçi idarəetməsi
```

---

## 👥 İstifadəçi Rolları

### Superuser (Admin)
- Django Admin (`/admin/`) və Master Admin (`/master-admin/`) girişi
- Bütün şirkətləri görür və idarə edir
- Şirkətə keçid (impersonation) edə bilir
- Abunəlikləri idarə edir

### Company Owner
- Şirkət dashboard-una giriş
- Bütün şirkət məlumatlarını görür
- Həkimlər, dərmanlar, reseptlər, satışlar, hesabatlar idarə edir

### Company Admin
- Şirkət dashboard-una giriş
- Şirkət məlumatlarını idarə edir

### Doctor
- Öz məlumatlarını görür
- Reseptlər əlavə edə bilir

### Staff/User
- Məhdud icazələr

---

## 🔄 Məlumat Axını

### Resept Əlavə Etmə Prosesi

1. İstifadəçi `/prescriptions/add/` səhifəsinə gedir
2. Bölgə seçir → JavaScript region həkimlərini yükləyir
3. Həkim seçir
4. Tarix seçir → JavaScript son bağlanmış hesabatı yoxlayır və minimum tarix təyin edir
5. Dərmanlar üçün miqdar daxil edir
6. Form göndərilir
7. `Prescription` və `PrescriptionItem` yaradılır
8. Signal (`prescription_item_saved`) işə düşür
9. `recalculate_doctor_financials()` çağırılır (reseptin ayı və ili ilə)
10. Həkimin `hesablanmish_miqdar` yenilənir
11. Həkimin `yekun_borc` avtomatik yenilənir (`save()` metodu)

### Satış Əlavə Etmə Prosesi

1. İstifadəçi `/sales/add/` səhifəsinə gedir
2. Region və tarix seçir
3. Dərmanlar üçün miqdar daxil edir
4. Form göndərilir
5. `Sale` və `SaleItem` yaradılır
6. Signal (`sale_saved`) işə düşür
7. `recalculate_doctor_financials()` çağırılır (satışın ayı və ili ilə, region_id ilə)
8. Regiondakı bütün həkimlərin `hesablanmish_miqdar` yenilənir
9. Həkimlərin `yekun_borc` avtomatik yenilənir

### Hesabat Bağlama Prosesi

1. İstifadəçi `/reports/<id>/close/` səhifəsinə gedir
2. Hesabat bağlanır (`is_closed = True`, `closed_at = now()`)
3. Yeni reseptlər yalnız növbəti ay üçün əlavə edilə bilər
4. JavaScript `/prescriptions/add/` səhifəsində minimum tarixi təyin edir

---

## 🧮 Hesablama Məntiqi

### Həkim Maliyyə Hesablamaları

**Fayl:** `doctors/services/financial_calculator.py`

**Funksiya:** `recalculate_doctor_financials(doctor_ids=None, region_ids=None, month=None, year=None)`

**Hesablama Məntiqi:**

1. **Reseptlər üzrə hesablama:**
   - Həkimin reseptləri filtr edilir (ay və il üzrə, əgər verilibsə)
   - Hər resept elementi üçün:
     - `drug.komissiya` (AZN) götürülür
     - Həkimin `degree`-inə görə faktor tətbiq edilir:
       - VIP: 1.00
       - I: 0.90
       - II: 0.65
       - III: 0.40
     - Komissiya = `drug.komissiya * degree_factor`
     - Ümumi komissiya = `komissiya * quantity`

2. **Satışlar üzrə hesablama:**
   - Regiondakı satışlar filtr edilir (ay və il üzrə, əgər verilibsə)
   - Hər satış elementi üçün:
     - `drug.komissiya` (AZN) götürülür
     - Regiondakı bütün həkimlər üçün:
       - Həkimin `degree`-inə görə faktor tətbiq edilir
       - Komissiya = `drug.komissiya * degree_factor`
       - Ümumi komissiya = `komissiya * quantity`

3. **Yekun:**
   - `hesablanmish_miqdar` = Reseptlər üzrə komissiya + Satışlar üzrə komissiya
   - `yekun_borc` = `evvelki_borc` + `hesablanmish_miqdar` - `silinen_miqdar`

**Qeyd:** Hesablamalar aylıq əsasda aparılır. Satış və ya resept hansı aya aid edilibsə, o ay üçün hesablama aparılır.

### Dərəcə Faktorları

```python
DEGREE_FACTORS = {
    'VIP': Decimal('1.00'),
    'I': Decimal('0.90'),
    'II': Decimal('0.65'),
    'III': Decimal('0.40'),
}
```

### Yekun Borc Hesablaması

`Doctor.save()` metodu:
```python
self.yekun_borc = self.evvelki_borc + self.hesablanmish_miqdar - self.silinen_miqdar
```

---

## 📥📤 İmport/Export Funksionallığı

### Excel Export

#### 1. Dərmanlar (`/master-admin/companies/<id>/export-drugs/`)
**Sütunlar:**
- Ad
- Tam Ad
- Komissiya
- Qiymət

#### 2. Həkimlər (`/master-admin/companies/<id>/export-doctors/`)
**Sütunlar:**
- Bölgə
- Həkim adı
- Telefon
- Email
- İxtisas
- Dərəcə
- Kategoriya
- Əvvəlki Borc
- Hesablanmış Miqdar
- Silinən Miqdar
- Yekun Borc

#### 3. Borclar (`/master-admin/companies/<id>/export-debts/`)
**Sütunlar:**
- Bölgə
- Həkim adı
- Yekun Borc

### Excel Import

#### 1. Dərmanlar (`/master-admin/companies/<id>/import-drugs/`)
**Tələb olunan sütunlar:**
- **A sütunu:** Ad
- **B sütunu:** Tam Ad
- **C sütunu:** Komissiya
- **D sütunu:** Qiymət

**Qeyd:** Digər sütunlar (Buraxılış Forması, Dozaj, Barkod) nəzərə alınmır.

#### 2. Borclar (`/master-admin/companies/<id>/import-debts/`)
**Tələb olunan sütunlar:**
- **A sütunu:** Bölgə
- **B sütunu:** Həkim adı
- **C sütunu:** Yekun Borc

**Məntiq:**
- Bölgə adına görə `Region` tapılır
- Həkim adına və bölgəyə görə `Doctor` tapılır
- `doctor.evvelki_borc = yekun_borc` təyin edilir
- `doctor.hesablanmish_miqdar = 0` və `doctor.silinen_miqdar = 0` təyin edilir
- `doctor.save()` çağırılır → `yekun_borc` avtomatik yenilənir

#### 3. Tam Həkim Məlumatları (`/master-admin/companies/<id>/import-doctors-full/`)
**Tələb olunan sütunlar:**
- **B sütunu:** Bölgə
- **C sütunu:** Həkim adı
- **D sütunu:** İxtisas
- **E sütunu:** Dərəcə
- **F sütunu:** Kategoriya
- **G sütunu:** Müəssisə (Klinika)
- **I sütunu:** Borcu

**Məntiq:**
- Bölgə yoxdursa yaradılır (case-insensitive yoxlama)
- İxtisas yoxdursa yaradılır (case-insensitive yoxlama)
- Şəhər yoxdursa yaradılır (default: bölgə adı)
- Klinika yoxdursa yaradılır (address="" təyin edilir)
- Həkim yoxdursa yaradılır:
  - `telefon = "-"`
  - `evvelki_borc = borcu`
  - `hesablanmish_miqdar = 0`
  - `silinen_miqdar = 0`
- Həkim varsa, yenilənmir (duplicate yoxlaması)

### Borcları Sıfırlama

**URL:** `/master-admin/companies/<id>/zero-debts/`

**Məntiq:**
- Şirkətdəki bütün həkimlərin `evvelki_borc = 0` təyin edilir
- `doctor.save()` çağırılır → `yekun_borc` avtomatik yenilənir

---

## 🔧 Texniki Detallar

### Database Konfiqurasiyası

**Local (Development):**
- SQLite istifadə olunur
- `config/settings.py` istifadə olunur

**Production:**
- PostgreSQL istifadə olunur
- `DJANGO_SETTINGS_MODULE=config.settings_production` təyin edilməlidir
- `.env` faylında:
  ```
  DB_NAME=medcore_db
  DB_USER=medcore_user
  DB_PASSWORD=your_password
  DB_HOST=localhost
  DB_PORT=5432
  ```

### Environment Variables

`.env` faylında:
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
OPENAI_API_KEY=your-openai-api-key
USE_POSTGRESQL=True
DB_NAME=medcore_db
DB_USER=medcore_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Signal-lər

#### Prescriptions App (`prescriptions/signals.py`)

**`prescription_item_saved`:**
- `PrescriptionItem` yaradılanda/deyişdiriləndə işə düşür
- `recalculate_doctor_financials()` çağırılır (reseptin ayı və ili ilə)

**`prescription_item_deleted`:**
- `PrescriptionItem` silinəndə işə düşür
- `recalculate_doctor_financials()` çağırılır (reseptin ayı və ili ilə)

#### Sales App (`sales/signals.py`)

**`sale_saved`:**
- `Sale` yaradılanda/deyişdiriləndə işə düşür
- `recalculate_doctor_financials()` çağırılır (satışın ayı və ili ilə, region_id ilə)

**`sale_deleted`:**
- `Sale` silinəndə işə düşür
- `recalculate_doctor_financials()` çağırılır (satışın ayı və ili ilə, region_id ilə)

### AI Chatbot

**URL:** `/chatbot/`

**Xüsusiyyətlər:**
- Professional və Enterprise planlar üçün
- OpenAI API inteqrasiyası
- Sistem mesajı Azərbaycan dilində
- `OPENAI_API_KEY` `.env` faylından oxunur

**Frontend (`templates/base.html`):**
- Chatbot widget (sağ alt küncdə)
- JavaScript Fetch API ilə backend-ə sorğu göndərir
- CSRF token avtomatik əlavə edilir

**Backend (`chatbot/views.py`):**
- `send_message` view-i
- OpenAI API çağırışı
- Sistem mesajı: "Sən MedCore tibbi idarəetmə sisteminin köməkçi asistanısan..."

### CSS və JavaScript

**Əsas CSS faylları:**
- `static/css/dashboard.css`
- `static/css/styles.css`
- `static/js/theme-manager.js`

**Prescription Add Page CSS:**
- `.drug-qty-input`: `pointer-events: auto`, `z-index: 10`
- `.drug-input`: `pointer-events: auto`, `z-index: 10`
- `.drug-item`: `position: relative`

### Rəng Kodlaması

**Həkim Borcları:**
- Qırmızı (`#dc2626`): Yekun borc > 0
- Yaşıl (`#22c55e`): Yekun borc < 0
- Sarı (`#eab308`): Yekun borc = 0

---

## 📝 Qeydlər

1. **Cinsiyyət Avtomatik Təyini:**
   - Həkimin ad soyadının ilk sözünün sonuna görə:
     - 'a' ilə bitirsə → 'female'
     - 'v' ilə bitirsə → 'male'
     - Digər halda → ''

2. **Hesabat Bağlama:**
   - Hesabat bağlandıqdan sonra yeni reseptlər yalnız növbəti ay üçün əlavə edilə bilər
   - JavaScript minimum tarixi avtomatik təyin edir

3. **Multi-Tenant:**
   - Hər şirkətin öz verilənlər bazası var
   - Database router avtomatik database seçir
   - Superuser bütün şirkətləri görür

4. **Dual Session:**
   - Admin və istifadəçi sessiyaları eyni brauzerdə müstəqil işləyir
   - `/admin/` üçün `admin_sessionid` cookie
   - Digər URL-lər üçün `sessionid` cookie

---

## 🆘 Problemlərin Həlli

### Input sahəsi işləmir (Prescription Add)
- CSS-də `pointer-events: auto` və `z-index: 10` təyin edilməlidir

### Hesablama düzgün işləmir
- Signal-lərin düzgün işlədiyini yoxlayın
- `recalculate_doctor_financials()` funksiyasının çağırıldığını yoxlayın
- Ay və il parametrlərinin düzgün ötürüldüyünü yoxlayın

### Excel import işləmir
- Sütunların düzgün sırada olduğunu yoxlayın
- Bölgə və həkim adlarının düzgün yazıldığını yoxlayın
- Case-insensitive yoxlama aparılır

### Database xətası
- Local: SQLite istifadə olunur
- Production: PostgreSQL istifadə olunur və `.env` faylında konfiqurasiya olunmalıdır

---

## 📚 Əlavə Məlumat

Daha ətraflı məlumat üçün:
- `HOW_IT_WORKS.txt` - Dual Session sistemi haqqında
- `PRODUCTION_SETUP.md` - Production konfiqurasiyası
- `SECURITY_SETUP.md` - Təhlükəsizlik konfiqurasiyası

---

**Son yenilənmə:** 2026-02-16
**Versiya:** 1.0
