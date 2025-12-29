"""
Kutuphane Yonetim Sistemi - Sabitler
Uygulamada kullanilan tum sabit degerler
"""

# Kullanici Rolleri
ROLE_ADMIN = 'Admin'
ROLE_GOREVLI = 'Gorevli'

# Odunc Alma Kurallari
MAX_AKTIF_ODUNC = 5
ODUNC_SURE_GUN = 15

# Ceza Hesaplama
GUNLUK_CEZA_TUTARI = 5.00

# Veritabanı Tablo Isimleri
TABLE_KULLANICI = 'KULLANICI'
TABLE_UYE = 'UYE'
TABLE_KATEGORI = 'KATEGORI'
TABLE_KITAP = 'KITAP'
TABLE_ODUNC = 'ODUNC'
TABLE_CEZA = 'CEZA'
TABLE_LOG_ISLEM = 'LOG_ISLEM'

# Stored Procedure Isimleri
SP_YENI_ODUNC_VER = 'sp_YeniOduncVer'
SP_KITAP_TESLIM_AL = 'sp_KitapTeslimAl'
SP_UYE_OZET_RAPOR = 'sp_UyeOzetRapor'
SP_KITAP_ARA = 'sp_KitapAra'
SP_AKTIF_ODUNC_SAYISI = 'sp_AktifOduncSayisi'

# UI Mesajlari
MSG_SUCCESS = 'Islem basarili!'
MSG_ERROR = 'Bir hata olustu!'
MSG_DELETE_CONFIRM = 'Silmek istediginizden emin misiniz?'
MSG_INVALID_INPUT = 'Lutfen tum alanlari dogru doldurun!'
MSG_LOGIN_FAILED = 'Kullanici adi veya sifre hatali!'
MSG_LOGIN_SUCCESS = 'Giris basarili!'

# Tarih Formatlari
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DISPLAY_DATE_FORMAT = '%d.%m.%Y'
DISPLAY_DATETIME_FORMAT = '%d.%m.%Y %H:%M'
