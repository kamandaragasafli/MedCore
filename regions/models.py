from django.db import models


class Region(models.Model):
    """Bölgə (Region) Model"""
    name = models.CharField(max_length=100, verbose_name="Bölgə Adı")
    code = models.CharField(max_length=10, unique=True, verbose_name="Bölgə Kodu")

    class Meta:
        verbose_name = "Bölgə"
        verbose_name_plural = "Bölgələr"
        ordering = ['name']

    def __str__(self):
        return self.name


class City(models.Model):
    """Şəhər (City) Model"""
    name = models.CharField(max_length=100, verbose_name="Şəhər Adı")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities', verbose_name="Bölgə")

    class Meta:
        verbose_name = "Şəhər"
        verbose_name_plural = "Şəhərlər"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class Clinic(models.Model):
    """Klinika/Xəstəxana (Clinic/Hospital) Model"""
    name = models.CharField(max_length=200, verbose_name="Klinika Adı")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='clinics', verbose_name="Bölgə")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='clinics', verbose_name="Şəhər")
    address = models.TextField(verbose_name="Ünvan")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Əlaqə Nömrəsi")
    type = models.CharField(
        max_length=50,
        choices=[
            ('hospital', 'Xəstəxana'),
            ('clinic', 'Klinika'),
            ('polyclinic', 'Poliklinika'),
            ('medical_center', 'Tibb Mərkəzi'),
        ],
        default='clinic',
        verbose_name="Növ"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")
    class Meta:
        verbose_name = "Klinika"
        verbose_name_plural = "Klinikalar"
        ordering = ['name']

    def __str__(self):
        return self.name


class Specialization(models.Model):
    """İxtisas (Specialization) Model"""
    name = models.CharField(max_length=200, verbose_name="İxtisas Adı")

    class Meta:
        verbose_name = "İxtisas"
        verbose_name_plural = "İxtisaslar"
        ordering = ['name']

    def __str__(self):
        return self.name
