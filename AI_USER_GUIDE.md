# MedCore - İstifadəçi Bələdçisi

Bu sənəd MedCore sisteminin istifadəçilər üçün bələdçisini ehtiva edir.

---

## 🎯 Sistem Nədir?

**MedCore** - tibbi idarəetmə sistemidir. Sistemdə həkimlər, dərmanlar, resept qeydiyyatları, satışlar və hesabatlar idarə olunur.

---

## 📋 Əsas Funksiyalar

### 1. Həkim İdarəetməsi

**Həkim Siyahısı (`/doctors/`):**
- Bütün həkimlərin siyahısı
- Bölgə, şəhər, klinika, ixtisas üzrə filtr
- Həkim adına klikləməklə detay səhifəsinə keçid
- Borc rəng kodlaması:
  - Qırmızı: Borc var (> 0)
  - Yaşıl: Kredit var (< 0)
  - Sarı: Borc yoxdur (= 0)

**Həkim Əlavə Etmə:**
- Bölgə, şəhər, klinika, ixtisas seçimi
- Ad Soyad, telefon, email
- Cinsiyyət avtomatik təyin olunur
- Kateqoriya və dərəcə seçimi
- Əvvəlki borc daxil edilə bilər

**Həkim Detay Səhifəsi:**
- Həkimin bütün məlumatları
- Resept sayı və ödənişlər
- Aylıq hesabatlar
- Borc məlumatları

### 2. Dərman İdarəetməsi

**Dərman Siyahısı:**
- Bütün dərmanların siyahısı
- Filtr və axtarış

**Dərman Əlavə Etmə:**
- Ad və Tam ad
- Qiymət və Komissiya (AZN)
- Buraxılış forması, dozaj, barkod

### 3. Resept Qeydiyyatı

**Resept Siyahısı:**
- Bütün reseptlərin siyahısı
- Bölgə, həkim, tarix üzrə filtr
- Həkim adına klikləməklə detay səhifəsinə keçid

**Resept Əlavə Etmə:**
1. Bölgə seçin → həkimlər yüklənir
2. Həkim seçin
3. Tarix seçin (son bağlanmış hesabatdan sonra)
4. Dərmanlar üçün miqdar daxil edin
5. Xəstə adı və qeyd (istəyə bağlı)
6. Göndərin

**Qeyd:** Hesabat bağlandıqdan sonra yeni reseptlər yalnız növbəti ay üçün əlavə edilə bilər.

### 4. Satış İdarəetməsi

**Satış Siyahısı:**
- Bütün satışların siyahısı
- Bölgə və tarix üzrə filtr

**Satış Əlavə Etmə:**
- Bölgə və tarix seçimi
- Dərmanlar üçün miqdar daxil etmə

**Satış Redaktə:**
- Satış məlumatlarının redaktəsi

### 5. Hesabatlar

**Hesabat Siyahısı:**
- Bütün hesabatların siyahısı
- Bölgə və ay/il üzrə filtr
- Bağlanma statusu

**Hesabat Yaratma:**
- Bölgə seçilməlidir
- Ay və il seçimi
- Həkimlər üzrə maliyyə məlumatları
- Excel export

**Hesabat Bağlama:**
- Hesabat bağlandıqdan sonra yeni reseptlər yalnız növbəti ay üçün əlavə edilə bilər

---

## 💰 Maliyyə Hesablamaları

### Həkim Borcları

**Yekun Borc Hesablaması:**
- Yekun Borc = Əvvəlki Borc + Hesablanmış Miqdar - Silinən Miqdar

**Hesablanmış Miqdar:**
- Reseptlər üzrə komissiya
- Satışlar üzrə komissiya
- Həkimin dərəcəsinə görə faktor tətbiq edilir:
  - VIP: 100%
  - I Dərəcə: 90%
  - II Dərəcə: 65%
  - III Dərəcə: 40%

**Qeyd:** Hesablamalar avtomatik aparılır. Resept və ya satış əlavə edildikdə həkimin maliyyə məlumatları avtomatik yenilənir.

---

## 📊 Excel İmport/Export

### Export (Xaricə Çıxarma)

**Dərmanlar:**
- Ad, Tam Ad, Komissiya, Qiymət

**Həkimlər:**
- Bölgə, Həkim adı, Telefon, Email, İxtisas, Dərəcə, Kategoriya, Borc məlumatları

**Borclar:**
- Bölgə, Həkim adı, Yekun Borc

### Import (Daxilə Gətirmə)

**Dərmanlar:**
- Excel faylında: Ad, Tam Ad, Komissiya, Qiymət sütunları olmalıdır

**Borclar:**
- Excel faylında: Bölgə, Həkim adı, Yekun Borc sütunları olmalıdır

---

## 🎨 Rəng Kodlaması

**Həkim Borcları:**
- 🔴 Qırmızı: Borc var (Yekun borc > 0)
- 🟢 Yaşıl: Kredit var (Yekun borc < 0)
- 🟡 Sarı: Borc yoxdur (Yekun borc = 0)

---

## ❓ Tez-tez Verilən Suallar

**S: Resept əlavə edə bilmirəm, nə etməliyəm?**
C: Yoxlayın ki, bölgə seçilib və tarix son bağlanmış hesabatdan sonradır.

**S: Həkimin borcu düzgün hesablanmayıb, nə etməliyəm?**
C: Hesablamalar avtomatikdir. Resept və ya satış əlavə edildikdə avtomatik yenilənir. Əgər problem varsa, həkimin resept və satış məlumatlarını yoxlayın.

**S: Excel import işləmir, nə etməliyəm?**
C: Yoxlayın ki, sütunlar düzgün sırada və adlarla yazılıb. Bölgə və həkim adları düzgün yazılmalıdır.

**S: Hesabat bağlaya bilmirəm, nə etməliyəm?**
C: Yoxlayın ki, bölgə seçilib və hesabat məlumatları doldurulub.

---

## 🔗 Əsas Səhifələr

- `/doctors/` - Həkim siyahısı
- `/doctors/add/` - Həkim əlavə et
- `/drugs/` - Dərman siyahısı
- `/drugs/add/` - Dərman əlavə et
- `/prescriptions/` - Resept siyahısı
- `/prescriptions/add/` - Resept əlavə et
- `/sales/` - Satış siyahısı
- `/sales/add/` - Satış əlavə et
- `/reports/` - Hesabatlar
- `/reports/create/` - Hesabat yarat

---

**Son yenilənmə:** 2026-02-16
