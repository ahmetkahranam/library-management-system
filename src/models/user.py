"""
Kutuphane Yonetim Sistemi - Kullanici Modeli
Kullanici giris, CRUD islemleri
"""

import bcrypt
from src.database.db_manager import db_manager
from src.utils.constants import TABLE_KULLANICI, ROLE_ADMIN, ROLE_GOREVLI
from src.utils.validators import validate_required


class User:
    """Kullanici model sinifi"""
    
    def __init__(self, kullanici_id=None, kullanici_adi=None, sifre=None, 
                 rol=None, ad_soyad=None, email=None, aktif_mi=True):
        self.kullanici_id = kullanici_id
        self.kullanici_adi = kullanici_adi
        self.sifre = sifre
        self.rol = rol
        self.ad_soyad = ad_soyad
        self.email = email
        self.aktif_mi = aktif_mi
    
    @staticmethod
    def login(kullanici_adi, sifre):
        """
        Kullanici girisi yapar
        
        Args:
            kullanici_adi (str): Kullanici adi
            sifre (str): Sifre
            
        Returns:
            User/None: Basarili ise User objesi, degilse None
        """
        try:
            query = f"""
                SELECT * FROM {TABLE_KULLANICI}
                WHERE KullaniciAdi = %s
            """
            result = db_manager.execute_query(query, (kullanici_adi,), fetch_one=True)
            
            if not result:
                return None
            
            # Sifre kontrolu (hash veya duz metin)
            stored_password = result['Sifre']
            
            # Eger hash ile baslarsa bcrypt kontrolu
            if stored_password.startswith('$2b$') or stored_password.startswith('$2a$'):
                if not bcrypt.checkpw(sifre.encode('utf-8'), stored_password.encode('utf-8')):
                    return None
            else:
                # Duz metin karsilastirma
                if sifre != stored_password:
                    return None
            
            # User objesi olustur
            return User(
                kullanici_id=result['KullaniciID'],
                kullanici_adi=result['KullaniciAdi'],
                rol=result['Rol'],
                ad_soyad=result.get('AdSoyad'),
                email=result.get('Email'),
                aktif_mi=result.get('AktifMi', True)
            )
            
        except Exception as e:
            print(f"[USER ERROR] Login hatasi: {e}")
            return None
    
    @staticmethod
    def get_all():
        """
        Tum kullanicilari getirir
        
        Returns:
            list: Kullanici listesi
        """
        try:
            query = f"""
                SELECT KullaniciID, KullaniciAdi, Rol, AdSoyad, Email, AktifMi
                FROM {TABLE_KULLANICI}
                ORDER BY KullaniciID
            """
            return db_manager.execute_query(query)
        except Exception as e:
            print(f"[USER ERROR] Get all hatasi: {e}")
            return []
    
    @staticmethod
    def get_by_id(kullanici_id):
        """
        ID'ye gore kullanici getirir
        
        Args:
            kullanici_id (int): Kullanici ID
            
        Returns:
            dict/None: Kullanici bilgileri
        """
        try:
            query = f"""
                SELECT KullaniciID, KullaniciAdi, Rol, AdSoyad, Email, AktifMi
                FROM {TABLE_KULLANICI}
                WHERE KullaniciID = %s
            """
            return db_manager.execute_query(query, (kullanici_id,), fetch_one=True)
        except Exception as e:
            print(f"[USER ERROR] Get by ID hatasi: {e}")
            return None
    
    @staticmethod
    def search(keyword):
        """
        Kullanici arama
        
        Args:
            keyword (str): Arama kelimesi
            
        Returns:
            list: Kullanici listesi
        """
        try:
            query = f"""
                SELECT KullaniciID, KullaniciAdi, Rol, AdSoyad, Email, AktifMi
                FROM {TABLE_KULLANICI}
                WHERE KullaniciAdi LIKE %s
                   OR AdSoyad LIKE %s
                   OR Email LIKE %s
                ORDER BY KullaniciID
            """
            search_term = f"%{keyword}%"
            return db_manager.execute_query(query, (search_term, search_term, search_term))
        except Exception as e:
            print(f"[USER ERROR] Search hatasi: {e}")
            return []
    
    @staticmethod
    def create(kullanici_adi, sifre, rol, ad_soyad, email=None, hash_password=False):
        """
        Yeni kullanici olusturur
        
        Args:
            kullanici_adi (str): Kullanici adi
            sifre (str): Sifre
            rol (str): Rol (Admin/Gorevli)
            ad_soyad (str): Ad Soyad
            email (str): Email
            hash_password (bool): Sifreyi hash'le mi?
            
        Returns:
            tuple: (bool, str/int) - (Basarili mi, Hata mesaji veya KullaniciID)
        """
        try:
            # Validasyon
            if not validate_required(kullanici_adi):
                return False, "Kullanici adi zorunlu"
            if not validate_required(sifre):
                return False, "Sifre zorunlu"
            if not validate_required(ad_soyad):
                return False, "Ad Soyad zorunlu"
            
            # Kullanici adi benzersiz mi?
            check_query = f"SELECT COUNT(*) as sayi FROM {TABLE_KULLANICI} WHERE KullaniciAdi = %s"
            result = db_manager.execute_query(check_query, (kullanici_adi,), fetch_one=True)
            if result['sayi'] > 0:
                return False, "Bu kullanici adi zaten kullanilmakta"
            
            # Sifre hash'leme
            if hash_password:
                sifre = bcrypt.hashpw(sifre.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert
            query = f"""
                INSERT INTO {TABLE_KULLANICI} 
                (KullaniciAdi, Sifre, Rol, AdSoyad, Email)
                VALUES (%s, %s, %s, %s, %s)
            """
            affected, last_id = db_manager.execute_update(
                query, (kullanici_adi, sifre, rol, ad_soyad, email)
            )
            
            if affected > 0:
                return True, last_id
            return False, "Kullanici eklenemedi"
            
        except Exception as e:
            print(f"[USER ERROR] Create hatasi: {e}")
            return False, str(e)
    
    @staticmethod
    def update(kullanici_id, kullanici_adi=None, sifre=None, rol=None, 
               ad_soyad=None, email=None, aktif_mi=None, hash_password=False):
        """
        Kullanici gunceller
        
        Args:
            kullanici_id (int): Kullanici ID
            ... diger alanlar (None ise guncellenmez)
            
        Returns:
            tuple: (bool, str) - (Basarili mi, Mesaj)
        """
        try:
            # Mevcut kullanici var mi?
            existing = User.get_by_id(kullanici_id)
            if not existing:
                return False, "Kullanici bulunamadi"
            
            # Guncellenecek alanlar
            updates = []
            params = []
            
            if kullanici_adi is not None:
                # Kullanici adi benzersiz mi?
                check_query = f"""
                    SELECT COUNT(*) as sayi FROM {TABLE_KULLANICI} 
                    WHERE KullaniciAdi = %s AND KullaniciID != %s
                """
                result = db_manager.execute_query(check_query, (kullanici_adi, kullanici_id), fetch_one=True)
                if result['sayi'] > 0:
                    return False, "Bu kullanici adi zaten kullanilmakta"
                updates.append("KullaniciAdi = %s")
                params.append(kullanici_adi)
            
            if sifre is not None:
                if hash_password:
                    sifre = bcrypt.hashpw(sifre.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                updates.append("Sifre = %s")
                params.append(sifre)
            
            if rol is not None:
                updates.append("Rol = %s")
                params.append(rol)
            
            if ad_soyad is not None:
                updates.append("AdSoyad = %s")
                params.append(ad_soyad)
            
            if email is not None:
                updates.append("Email = %s")
                params.append(email)
            
            if aktif_mi is not None:
                updates.append("AktifMi = %s")
                params.append(aktif_mi)
            
            if not updates:
                return False, "Guncellenecek alan yok"
            
            params.append(kullanici_id)
            query = f"UPDATE {TABLE_KULLANICI} SET {', '.join(updates)} WHERE KullaniciID = %s"
            
            affected, _ = db_manager.execute_update(query, tuple(params))
            
            if affected > 0:
                return True, "Kullanici guncellendi"
            return False, "Guncelleme yapilamadi"
            
        except Exception as e:
            print(f"[USER ERROR] Update hatasi: {e}")
            return False, str(e)
    
    @staticmethod
    def delete(kullanici_id):
        """
        Kullanici siler
        
        Args:
            kullanici_id (int): Kullanici ID
            
        Returns:
            tuple: (bool, str) - (Basarili mi, Mesaj)
        """
        try:
            query = f"DELETE FROM {TABLE_KULLANICI} WHERE KullaniciID = %s"
            affected, _ = db_manager.execute_update(query, (kullanici_id,))
            
            if affected > 0:
                return True, "Kullanici silindi"
            return False, "Kullanici bulunamadi"
            
        except Exception as e:
            print(f"[USER ERROR] Delete hatasi: {e}")
            return False, str(e)
    
    @staticmethod
    def get_roles():
        """Rol listesi"""
        return [ROLE_ADMIN, ROLE_GOREVLI]
    
    def is_admin(self):
        """Admin mi?"""
        return self.rol == ROLE_ADMIN
    
    def get_full_name(self):
        """Tam ad"""
        if self.ad_soyad:
            return self.ad_soyad
        return self.kullanici_adi
