"""
Kutuphane Yonetim Sistemi - Uye Modeli
Uye CRUD islemleri
"""

from src.database.db_manager import db_manager
from src.utils.constants import TABLE_UYE, SP_UYE_OZET_RAPOR
from src.utils.validators import validate_required, validate_email, validate_phone


class Member:
    """Uye model sinifi"""
    
    @staticmethod
    def get_all():
        """
        Tum uyeleri getirir
        
        Returns:
            list: Uye listesi
        """
        try:
            query = f"""
                SELECT UyeID, Ad, Soyad, Email, Telefon, Adres, 
                       KayitTarihi, ToplamBorc, AktifMi
                FROM {TABLE_UYE}
                ORDER BY UyeID DESC
            """
            return db_manager.execute_query(query)
        except Exception as e:
            print(f"[MEMBER ERROR] Get all hatasi: {e}")
            return []
    
    @staticmethod
    def get_by_id(uye_id):
        """
        ID'ye gore uye getirir
        
        Args:
            uye_id (int): Uye ID
            
        Returns:
            dict/None: Uye bilgileri
        """
        try:
            query = f"""
                SELECT UyeID, Ad, Soyad, Email, Telefon, Adres, 
                       KayitTarihi, ToplamBorc, AktifMi
                FROM {TABLE_UYE}
                WHERE UyeID = %s
            """
            return db_manager.execute_query(query, (uye_id,), fetch_one=True)
        except Exception as e:
            print(f"[MEMBER ERROR] Get by ID hatasi: {e}")
            return None
    
    @staticmethod
    def search(keyword):
        """
        Uye arama (Ad, Soyad, Email, Telefon)
        
        Args:
            keyword (str): Arama kelimesi
            
        Returns:
            list: Uye listesi
        """
        try:
            query = f"""
                SELECT UyeID, Ad, Soyad, Email, Telefon, Adres, 
                       KayitTarihi, ToplamBorc, AktifMi
                FROM {TABLE_UYE}
                WHERE Ad LIKE %s
                   OR Soyad LIKE %s
                   OR Email LIKE %s
                   OR Telefon LIKE %s
                ORDER BY UyeID DESC
            """
            search_term = f"%{keyword}%"
            return db_manager.execute_query(
                query, (search_term, search_term, search_term, search_term)
            )
        except Exception as e:
            print(f"[MEMBER ERROR] Search hatasi: {e}")
            return []
    
    @staticmethod
    def create(ad, soyad, email, telefon, adres=None):
        """
        Yeni uye olusturur
        
        Args:
            ad (str): Ad
            soyad (str): Soyad
            email (str): Email
            telefon (str): Telefon
            adres (str): Adres
            
        Returns:
            tuple: (bool, str/int) - (Basarili mi, Hata mesaji veya UyeID)
        """
        try:
            # Validasyon
            if not validate_required(ad):
                return False, "Ad zorunlu"
            if not validate_required(soyad):
                return False, "Soyad zorunlu"
            if not validate_required(email):
                return False, "Email zorunlu"
            if not validate_email(email):
                return False, "Gecersiz email formati"
            if not validate_required(telefon):
                return False, "Telefon zorunlu"
            if not validate_phone(telefon):
                return False, "Gecersiz telefon formati (10 haneli, 5 ile baslar)"
            
            # Email benzersiz mi?
            check_query = f"SELECT COUNT(*) as sayi FROM {TABLE_UYE} WHERE Email = %s"
            result = db_manager.execute_query(check_query, (email,), fetch_one=True)
            if result['sayi'] > 0:
                return False, "Bu email adresi zaten kayitli"
            
            # Insert
            query = f"""
                INSERT INTO {TABLE_UYE} (Ad, Soyad, Email, Telefon, Adres)
                VALUES (%s, %s, %s, %s, %s)
            """
            affected, last_id = db_manager.execute_update(
                query, (ad, soyad, email, telefon, adres)
            )
            
            if affected > 0:
                return True, last_id
            return False, "Uye eklenemedi"
            
        except Exception as e:
            print(f"[MEMBER ERROR] Create hatasi: {e}")
            return False, str(e)
    
    @staticmethod
    def update(uye_id, ad=None, soyad=None, email=None, telefon=None, 
               adres=None, aktif_mi=None):
        """
        Uye gunceller
        
        Args:
            uye_id (int): Uye ID
            ... diger alanlar (None ise guncellenmez)
            
        Returns:
            tuple: (bool, str) - (Basarili mi, Mesaj)
        """
        try:
            # Mevcut uye var mi?
            existing = Member.get_by_id(uye_id)
            if not existing:
                return False, "Uye bulunamadi"
            
            # Guncellenecek alanlar
            updates = []
            params = []
            
            if ad is not None:
                updates.append("Ad = %s")
                params.append(ad)
            
            if soyad is not None:
                updates.append("Soyad = %s")
                params.append(soyad)
            
            if email is not None:
                if not validate_email(email):
                    return False, "Gecersiz email formati"
                # Email benzersiz mi?
                check_query = f"""
                    SELECT COUNT(*) as sayi FROM {TABLE_UYE} 
                    WHERE Email = %s AND UyeID != %s
                """
                result = db_manager.execute_query(
                    check_query, (email, uye_id), fetch_one=True
                )
                if result['sayi'] > 0:
                    return False, "Bu email adresi zaten kayitli"
                updates.append("Email = %s")
                params.append(email)
            
            if telefon is not None:
                if not validate_phone(telefon):
                    return False, "Gecersiz telefon formati"
                updates.append("Telefon = %s")
                params.append(telefon)
            
            if adres is not None:
                updates.append("Adres = %s")
                params.append(adres)
            
            if aktif_mi is not None:
                updates.append("AktifMi = %s")
                params.append(aktif_mi)
            
            if not updates:
                return False, "Guncellenecek alan yok"
            
            params.append(uye_id)
            query = f"UPDATE {TABLE_UYE} SET {', '.join(updates)} WHERE UyeID = %s"
            
            affected, _ = db_manager.execute_update(query, tuple(params))
            
            if affected > 0:
                return True, "Uye guncellendi"
            return False, "Guncelleme yapilamadi"
            
        except Exception as e:
            print(f"[MEMBER ERROR] Update hatasi: {e}")
            return False, str(e)
    
    @staticmethod
    def delete(uye_id):
        """
        Uye siler (Trigger engelliyorsa hata doner)
        
        Args:
            uye_id (int): Uye ID
            
        Returns:
            tuple: (bool, str) - (Basarili mi, Mesaj)
        """
        try:
            query = f"DELETE FROM {TABLE_UYE} WHERE UyeID = %s"
            affected, _ = db_manager.execute_update(query, (uye_id,))
            
            if affected > 0:
                return True, "Uye silindi"
            return False, "Uye bulunamadi"
            
        except Exception as e:
            error_msg = str(e)
            # Trigger hatasi mi?
            if "aktif odunc" in error_msg.lower() or "borc" in error_msg.lower():
                return False, "Uyenin aktif odunc kaydi veya borcu var, silinemez"
            print(f"[MEMBER ERROR] Delete hatasi: {e}")
            return False, error_msg
    
    @staticmethod
    def get_summary(uye_id):
        """
        Uye ozet raporu (Stored Procedure)
        
        Args:
            uye_id (int): Uye ID
            
        Returns:
            dict/None: Ozet bilgiler
        """
        try:
            results = db_manager.call_procedure(SP_UYE_OZET_RAPOR, (uye_id,))
            if results:
                return results[0]
            return None
        except Exception as e:
            print(f"[MEMBER ERROR] Summary hatasi: {e}")
            return None
    
    @staticmethod
    def get_active_members():
        """Aktif uyeleri getirir"""
        try:
            query = f"""
                SELECT UyeID, Ad, Soyad, Email, Telefon, ToplamBorc
                FROM {TABLE_UYE}
                WHERE AktifMi = TRUE
                ORDER BY Ad, Soyad
            """
            return db_manager.execute_query(query)
        except Exception as e:
            print(f"[MEMBER ERROR] Active members hatasi: {e}")
            return []
    
    @staticmethod
    def get_members_with_debt():
        """Borcu olan uyeleri getirir"""
        try:
            query = f"""
                SELECT UyeID, Ad, Soyad, Email, Telefon, ToplamBorc
                FROM {TABLE_UYE}
                WHERE ToplamBorc > 0
                ORDER BY ToplamBorc DESC
            """
            return db_manager.execute_query(query)
        except Exception as e:
            print(f"[MEMBER ERROR] Members with debt hatasi: {e}")
            return []
    
    @staticmethod
    def get_full_name(uye_data):
        """
        Uye tam adi
        
        Args:
            uye_data (dict): Uye bilgileri
            
        Returns:
            str: Tam ad
        """
        if uye_data and 'Ad' in uye_data and 'Soyad' in uye_data:
            return f"{uye_data['Ad']} {uye_data['Soyad']}"
        return ""
