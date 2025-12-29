"""
Kutuphane Yonetim Sistemi - Odunc Modeli
Odunc verme ve teslim alma islemleri (Stored Procedures kullanir)
"""

from datetime import datetime, timedelta
from src.database.db_manager import db_manager
from src.utils.constants import (
    TABLE_ODUNC, SP_YENI_ODUNC_VER, SP_KITAP_TESLIM_AL, 
    SP_AKTIF_ODUNC_SAYISI, ODUNC_SURE_GUN
)
from src.utils.helpers import format_date_for_display, calculate_days_between


class Loan:
    """Odunc model sinifi"""
    
    @staticmethod
    def get_all():
        """
        Tum odunc kayitlarini getirir
        
        Returns:
            list: Odunc listesi
        """
        try:
            query = f"""
                SELECT o.OduncID, o.UyeID, o.KitapID, o.OduncTarihi, 
                       o.SonTeslimTarihi, o.TeslimTarihi, o.KullaniciID,
                       u.Ad as UyeAd, u.Soyad as UyeSoyad,
                       k.KitapAdi, k.Yazar,
                       kul.KullaniciAdi
                FROM {TABLE_ODUNC} o
                INNER JOIN UYE u ON o.UyeID = u.UyeID
                INNER JOIN KITAP k ON o.KitapID = k.KitapID
                LEFT JOIN KULLANICI kul ON o.KullaniciID = kul.KullaniciID
                ORDER BY o.OduncID DESC
            """
            return db_manager.execute_query(query)
        except Exception as e:
            print(f"[LOAN ERROR] Get all hatasi: {e}")
            return []
    
    @staticmethod
    def get_by_id(odunc_id):
        """
        ID'ye gore odunc getirir
        
        Args:
            odunc_id (int): Odunc ID
            
        Returns:
            dict/None: Odunc bilgileri
        """
        try:
            query = f"""
                SELECT o.OduncID, o.UyeID, o.KitapID, o.OduncTarihi, 
                       o.SonTeslimTarihi, o.TeslimTarihi, o.KullaniciID,
                       u.Ad as UyeAd, u.Soyad as UyeSoyad, u.Email,
                       k.KitapAdi, k.Yazar, k.ISBN,
                       kul.KullaniciAdi
                FROM {TABLE_ODUNC} o
                INNER JOIN UYE u ON o.UyeID = u.UyeID
                INNER JOIN KITAP k ON o.KitapID = k.KitapID
                LEFT JOIN KULLANICI kul ON o.KullaniciID = kul.KullaniciID
                WHERE o.OduncID = %s
            """
            return db_manager.execute_query(query, (odunc_id,), fetch_one=True)
        except Exception as e:
            print(f"[LOAN ERROR] Get by ID hatasi: {e}")
            return None
    
    @staticmethod
    def get_active_loans():
        """
        Aktif odunc kayitlarini getirir (TeslimTarihi NULL)
        
        Returns:
            list: Aktif odunc listesi
        """
        try:
            query = f"""
                SELECT o.OduncID, o.UyeID, o.KitapID, o.OduncTarihi, 
                       o.SonTeslimTarihi,
                       u.Ad as UyeAd, u.Soyad as UyeSoyad,
                       k.KitapAdi, k.Yazar,
                       DATEDIFF(CURDATE(), o.SonTeslimTarihi) as GecikmeGun
                FROM {TABLE_ODUNC} o
                INNER JOIN UYE u ON o.UyeID = u.UyeID
                INNER JOIN KITAP k ON o.KitapID = k.KitapID
                WHERE o.TeslimTarihi IS NULL
                ORDER BY o.SonTeslimTarihi ASC
            """
            return db_manager.execute_query(query)
        except Exception as e:
            print(f"[LOAN ERROR] Active loans hatasi: {e}")
            return []
    
    @staticmethod
    def get_by_member(uye_id, aktif_only=False):
        """
        Uyeye ait odunc kayitlarini getirir
        
        Args:
            uye_id (int): Uye ID
            aktif_only (bool): Sadece aktif olanlar mi?
            
        Returns:
            list: Odunc listesi
        """
        try:
            query = f"""
                SELECT o.OduncID, o.KitapID, o.OduncTarihi, 
                       o.SonTeslimTarihi, o.TeslimTarihi,
                       k.KitapAdi, k.Yazar,
                       DATEDIFF(CURDATE(), o.SonTeslimTarihi) as GecikmeGun
                FROM {TABLE_ODUNC} o
                INNER JOIN KITAP k ON o.KitapID = k.KitapID
                WHERE o.UyeID = %s
            """
            if aktif_only:
                query += " AND o.TeslimTarihi IS NULL"
            
            query += " ORDER BY o.OduncTarihi DESC"
            
            return db_manager.execute_query(query, (uye_id,))
        except Exception as e:
            print(f"[LOAN ERROR] Get by member hatasi: {e}")
            return []
    
    @staticmethod
    def create_loan(uye_id, kitap_id, kullanici_id):
        """
        Yeni odunc verir (Stored Procedure: sp_YeniOduncVer)
        
        Args:
            uye_id (int): Uye ID
            kitap_id (int): Kitap ID
            kullanici_id (int): Islem yapan kullanici ID
            
        Returns:
            tuple: (bool, str) - (Basarili mi, Mesaj)
        """
        try:
            # sp_YeniOduncVer(UyeID, KitapID, IslemYapanKullaniciID)
            results = db_manager.call_procedure(
                SP_YENI_ODUNC_VER, 
                (uye_id, kitap_id, kullanici_id)
            )
            return True, "Odunc verme basarili"
            
        except Exception as e:
            error_msg = str(e)
            
            # Hata mesajlarini anlamli hale getir
            if "limit" in error_msg.lower() or "5" in error_msg:
                return False, "Uye maksimum odunc limitine ulasti (5 kitap)"
            elif "stok" in error_msg.lower() or "mevcut" in error_msg.lower():
                return False, "Kitap stokta yok"
            elif "bulunamadi" in error_msg.lower():
                return False, "Uye veya kitap bulunamadi"
            else:
                print(f"[LOAN ERROR] Create loan hatasi: {e}")
                return False, f"Odunc verme hatasi: {error_msg[:100]}"
    
    @staticmethod
    def return_loan(odunc_id, teslim_tarihi=None):
        """
        Kitap teslim alir (Stored Procedure: sp_KitapTeslimAl)
        
        Args:
            odunc_id (int): Odunc ID
            teslim_tarihi (date): Teslim tarihi (None ise bugun)
            
        Returns:
            tuple: (bool, str, float) - (Basarili mi, Mesaj, Ceza tutari)
        """
        try:
            # Teslim tarihi yoksa bugun
            if teslim_tarihi is None:
                teslim_tarihi = datetime.now().date()
            
            # sp_KitapTeslimAl(OduncID, TeslimTarihi)
            results = db_manager.call_procedure(
                SP_KITAP_TESLIM_AL, 
                (odunc_id, teslim_tarihi)
            )
            
            # Procedure'den ceza tutarini al
            ceza_tutari = 0.0
            if results and len(results) > 0 and 'CezaTutari' in results[0]:
                ceza_tutari = float(results[0]['CezaTutari'])
            
            if ceza_tutari > 0:
                return True, f"Kitap teslim alindi. Gecikme cezasi: {ceza_tutari} TL", ceza_tutari
            else:
                return True, "Kitap basariyla teslim alindi", 0.0
            
        except Exception as e:
            print(f"[LOAN ERROR] Return loan hatasi: {e}")
            return False, f"Teslim alma hatasi: {str(e)[:100]}", 0.0
    
    @staticmethod
    def get_active_loan_count(uye_id):
        """
        Uyenin aktif odunc sayisini getirir (Stored Procedure)
        
        Args:
            uye_id (int): Uye ID
            
        Returns:
            int: Aktif odunc sayisi
        """
        try:
            results = db_manager.call_procedure(SP_AKTIF_ODUNC_SAYISI, (uye_id,))
            if results and len(results) > 0:
                return results[0].get('AktifOduncSayisi', 0)
            return 0
        except Exception as e:
            print(f"[LOAN ERROR] Active count hatasi: {e}")
            return 0
    
    @staticmethod
    def get_overdue_loans():
        """
        Geciken odunc kayitlarini getirir
        
        Returns:
            list: Geciken odunc listesi
        """
        try:
            query = f"""
                SELECT o.OduncID, o.UyeID, o.KitapID, o.OduncTarihi, 
                       o.SonTeslimTarihi,
                       u.Ad as UyeAd, u.Soyad as UyeSoyad, u.Email, u.Telefon,
                       k.KitapAdi, k.Yazar,
                       DATEDIFF(CURDATE(), o.SonTeslimTarihi) as GecikmeGun
                FROM {TABLE_ODUNC} o
                INNER JOIN UYE u ON o.UyeID = u.UyeID
                INNER JOIN KITAP k ON o.KitapID = k.KitapID
                WHERE o.TeslimTarihi IS NULL 
                  AND o.SonTeslimTarihi < CURDATE()
                ORDER BY o.SonTeslimTarihi ASC
            """
            return db_manager.execute_query(query)
        except Exception as e:
            print(f"[LOAN ERROR] Overdue loans hatasi: {e}")
            return []
    
    @staticmethod
    def get_statistics():
        """
        Odunc istatistikleri
        
        Returns:
            dict: Istatistik bilgileri
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as ToplamOdunc,
                    SUM(CASE WHEN TeslimTarihi IS NULL THEN 1 ELSE 0 END) as AktifOdunc,
                    SUM(CASE WHEN TeslimTarihi IS NOT NULL THEN 1 ELSE 0 END) as TeslimEdilen,
                    SUM(CASE WHEN TeslimTarihi IS NULL AND SonTeslimTarihi < CURDATE() 
                        THEN 1 ELSE 0 END) as Geciken
                FROM ODUNC
            """
            result = db_manager.execute_query(query, fetch_one=True)
            return result if result else {}
        except Exception as e:
            print(f"[LOAN ERROR] Statistics hatasi: {e}")
            return {}
    
    @staticmethod
    def format_loan_info(loan_data):
        """
        Odunc bilgilerini formatli string olarak dondurur
        
        Args:
            loan_data (dict): Odunc bilgileri
            
        Returns:
            str: Formatli bilgi
        """
        if not loan_data:
            return ""
        
        info = f"{loan_data.get('KitapAdi', '')} - {loan_data.get('Yazar', '')}\n"
        info += f"Odunc Tarihi: {format_date_for_display(loan_data.get('OduncTarihi'))}\n"
        info += f"Son Teslim: {format_date_for_display(loan_data.get('SonTeslimTarihi'))}"
        
        if loan_data.get('TeslimTarihi'):
            info += f"\nTeslim Tarihi: {format_date_for_display(loan_data.get('TeslimTarihi'))}"
        else:
            # Gecikme var mi?
            if loan_data.get('GecikmeGun'):
                gecikme = loan_data['GecikmeGun']
                if gecikme > 0:
                    info += f"\n⚠️ Gecikme: {gecikme} gun"
        
        return info
