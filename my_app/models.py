from django.db import models

class Repository(models.Model):
    url = models.URLField(unique=True)
    son_analiz_zamani = models.DateTimeField(auto_now=True, verbose_name='Son Analiz Zamanı')

class JavaDosyasi(models.Model):
    depo = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='java_dosyalari', verbose_name='Depo')
    sinif_adi = models.CharField(max_length=255, verbose_name='Sınıf Adı')
    javadoc_yorum_satir_sayisi = models.IntegerField(default=0, verbose_name='Javadoc Yorum Satır Sayısı')
    yorum_satir_sayisi = models.IntegerField(default=0, verbose_name='Yorum Satır Sayısı')
    kod_satir_sayisi = models.IntegerField(default=0, verbose_name='Kod Satır Sayısı')
    toplam_satir_sayisi = models.IntegerField(default=0, verbose_name='Toplam Satır Sayısı (LOC)')
    fonksiyon_sayisi = models.IntegerField(default=0, verbose_name='Fonksiyon Sayısı')
    yorum_sapma_yuzdesi = models.FloatField(default=0.0, verbose_name='Yorum Sapma Yüzdesi')
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
