"""
Kutuphane Yonetim Sistemi - Ceza Modeli
Ceza kayitlari ve odeme islemleri
"""

from src.database.db_manager import db_manager
from src.utils.constants import TABLE_CEZA


class Penalty:
    """Ceza model sinifi"""
    
    @staticmethod
    def get_all():
        """
        Tum ceza kayitlarini getirir
        
        Returns:
            list: Ceza listesi
        """
        try:
            query = f"""
                SELECT c.CezaID, c.OduncID, c.UyeID, c.Tutar, c.OdendiMi, 
                       c.OlusturmaTarihi,
                       u.Ad as UyeAd, u.Soyad as UyeSoyad,
                       o.KitapID, k.KitapAdi
                FROM {TABLE_CEZA} c
                INNER JOIN UYE u ON c.UyeID = u.UyeID
                LEFT JOIN ODUNC o ON c.OduncID = o.OduncID
                LEFT JOIN KITAP k ON o.KitapID = k.KitapID
                ORDER BY c.CezaID DESC
            """
            return db_manager.execute_query(query)
        except Exception as e:
            print(f"[PENALTY ERROR] Get all hatasi: {e}")
            return []
    
    @staticmethod
    def get_by_id(ceza_id):
        """
        ID'ye gore ceza getirir
        
        Args:
            ceza_id (int): Ceza ID
            
        Returns:
            dict/None: Ceza bilgileri
        """
        try:
            query = f"""
                SELECT c.CezaID, c.OduncID, c.UyeID, c.Tutar, c.OdendiMi, 
                       c.OlusturmaTarihi,
                       u.Ad as UyeAd, u.Soyad as UyeSoyad, u.Email,
                       o.KitapID, k.KitapAdi, k.Yazar
                FROM {TABLE_CEZA} c
                INNER JOIN UYE u ON c.UyeID = u.UyeID
                LEFT JOIN ODUNC o ON c.OduncID = o.OduncID
                LEFT JOIN KITAP k ON o.KitapID = k.KitapID
                WHERE c.CezaID = %s
            """
            return db_manager.execute_query(query, (ceza_id,), fetch_one=True)
        except Exception as e:
            print(f"[PENALTY ERROR] Get by ID hatasi: {e}")
            return None
    
    @staticmethod
    def get_by_member(uye_id, odenmemis_only=False):
        """
        Uyeye ait ceza kayitlarini getirir
        
        Args:
            uye_id (int): Uye ID
            odenmemis_only (bool): Sadece odenmemis olanlar mi?
            
        Returns:
            list: Ceza listesi
        """
        try:
            query = f"""
                SELECT c.CezaID, c.OduncID, c.Tutar, c.OdendiMi, 
                       c.OlusturmaTarihi,
                       k.KitapAdi
                FROM {TABLE_CEZA} c
                LEFT JOIN ODUNC o ON c.OduncID = o.OduncID
                LEFT JOIN KITAP k ON o.KitapID = k.KitapID
                WHERE c.UyeID = %s
            """
            if odenmemis_only:
                query += " AND c.OdendiMi = FALSE"
            
            query += " ORDER BY c.OlusturmaTarihi DESC"
            
            return db_manager.execute_query(query, (uye_id,))
        except Exception as e:
            print(f"[PENALTY ERROR] Get by member hatasi: {e}")
            return []
    
    @staticmethod
    def get_unpaid():
        """
        Odenmemis ceza kayitlarini getirir
        
        Returns:
            list: Odenmemis ceza listesi
        """
        try:
            query = f"""
                SELECT c.CezaID, c.OduncID, c.UyeID, c.Tutar, c.OlusturmaTarihi,
                       u.Ad as UyeAd, u.Soyad as UyeSoyad, u.Email, u.Telefon,
                       k.KitapAdi
                FROM {TABLE_CEZA} c
                INNER JOIN UYE u ON c.UyeID = u.UyeID
                LEFT JOIN ODUNC o ON c.OduncID = o.OduncID
                LEFT JOIN KITAP k ON o.KitapID = k.KitapID
                WHERE c.OdendiMi = FALSE
                ORDER BY c.OlusturmaTarihi DESC
            """
            return db_manager.execute_query(query)
        except Exception as e:
            print(f"[PENALTY ERROR] Unpaid hatasi: {e}")
            return []
    
    @staticmethod
    def pay_penalty(ceza_id):
        """
        Ceza odemesi yapar
        
        Args:
            ceza_id (int): Ceza ID
            
        Returns:
            tuple: (bool, str) - (Basarili mi, Mesaj)
        """
        try:
            # Ceza mevcut mu ve odenmemis mi?
            ceza = Penalty.get_by_id(ceza_id)
            if not ceza:
                return False, "Ceza bulunamadi"
            
            if ceza['OdendiMi']:
                return False, "Bu ceza zaten odenmis"
            
            # Odeme yap
            query = f"""
                UPDATE {TABLE_CEZA} 
                SET OdendiMi = TRUE
                WHERE CezaID = %s
            """
            affected, _ = db_manager.execute_update(query, (ceza_id,))
            
            if affected > 0:
                # Uyenin toplam borcunu guncelle
                update_debt_query = """
                    UPDATE UYE 
                    SET ToplamBorc = ToplamBorc - %s
                    WHERE UyeID = %s
                """
                db_manager.execute_update(update_debt_query, (ceza['Tutar'], ceza['UyeID']))
                
                return True, f"Ceza odendi ({ceza['Tutar']} TL)"
            return False, "Odeme yapilamadi"
            
        except Exception as e:
            print(f"[PENALTY ERROR] Pay penalty hatasi: {e}")
            return False, str(e)
    
    @staticmethod
    def create_manual_penalty(uye_id, tutar, aciklama=None):
        """
        Manuel ceza olusturur (Odunc ID olmadan)
        
        Args:
            uye_id (int): Uye ID
            tutar (float): Ceza tutari
            aciklama (str): Aciklama
            
        Returns:
            tuple: (bool, str/int) - (Basarili mi, Hata mesaji veya CezaID)
        """
        try:
            if tutar <= 0:
                return False, "Ceza tutari pozitif olmali"
            
            # Insert - OduncID NULL olabilir (manuel ceza icin)
            query = f"""
                INSERT INTO {TABLE_CEZA} (UyeID, Tutar, OduncID, GecikmeGunu)
                VALUES (%s, %s, NULL, 0)
            """
            affected, last_id = db_manager.execute_update(query, (uye_id, tutar))
            
            if affected > 0:
                # Trigger otomatik olarak UYE.ToplamBorc'u guncelleyecek
                return True, last_id
            return False, "Ceza eklenemedi"
            
        except Exception as e:
            print(f"[PENALTY ERROR] Create manual penalty hatasi: {e}")
            return False, str(e)
    
    @staticmethod
    def delete(ceza_id):
        """
        Ceza siler (Dikkatli kullanilmali - sadece hata durumlarinda)
        
        Args:
            ceza_id (int): Ceza ID
            
        Returns:
            tuple: (bool, str) - (Basarili mi, Mesaj)
        """
        try:
            # Ceza mevcut mu?
            ceza = Penalty.get_by_id(ceza_id)
            if not ceza:
                return False, "Ceza bulunamadi"
            
            # Odenmisse silinemez
            if ceza['OdendiMi']:
                return False, "Odenmis ceza silinemez"
            
            # Once uyenin borcunu azalt
            update_debt_query = """
                UPDATE UYE 
                SET ToplamBorc = ToplamBorc - %s
                WHERE UyeID = %s
            """
            db_manager.execute_update(update_debt_query, (ceza['Tutar'], ceza['UyeID']))
            
            # Cezayi sil
            query = f"DELETE FROM {TABLE_CEZA} WHERE CezaID = %s"
            affected, _ = db_manager.execute_update(query, (ceza_id,))
            
            if affected > 0:
                return True, "Ceza silindi"
            return False, "Ceza silinemedi"
            
        except Exception as e:
            print(f"[PENALTY ERROR] Delete hatasi: {e}")
            return False, str(e)
    
    @staticmethod
    def get_statistics():
        """
        Ceza istatistikleri
        
        Returns:
            dict: Istatistik bilgileri
        """
        try:
            query = f"""
                SELECT 
                    COUNT(*) as ToplamCeza,
                    SUM(Tutar) as ToplamTutar,
                    SUM(CASE WHEN OdendiMi = TRUE THEN Tutar ELSE 0 END) as OdenenTutar,
                    SUM(CASE WHEN OdendiMi = FALSE THEN Tutar ELSE 0 END) as BekleyenTutar,
                    COUNT(CASE WHEN OdendiMi = FALSE THEN 1 END) as OdenmeyenSayisi
                FROM {TABLE_CEZA}
            """
            result = db_manager.execute_query(query, fetch_one=True)
            return result if result else {}
        except Exception as e:
            print(f"[PENALTY ERROR] Statistics hatasi: {e}")
            return {}
    
    @staticmethod
    def get_member_total_debt(uye_id):
        """
        Uyenin toplam odenmemis ceza tutarini hesaplar
        
        Args:
            uye_id (int): Uye ID
            
        Returns:
            float: Toplam borc
        """
        try:
            query = f"""
                SELECT SUM(Tutar) as ToplamBorc
                FROM {TABLE_CEZA}
                WHERE UyeID = %s AND OdendiMi = FALSE
            """
            result = db_manager.execute_query(query, (uye_id,), fetch_one=True)
            if result and result['ToplamBorc']:
                return float(result['ToplamBorc'])
            return 0.0
        except Exception as e:
            print(f"[PENALTY ERROR] Total debt hatasi: {e}")
            return 0.0
