"""
Kutuphane Yonetim Sistemi - Kitap Modeli
Kitap CRUD islemleri
"""

from src.database.db_manager import db_manager
from src.utils.constants import TABLE_KITAP, TABLE_KATEGORI, SP_KITAP_ARA
from src.utils.validators import validate_required, validate_positive_number, validate_year, validate_isbn


class Book:
    """Kitap model sinifi"""
    
    @staticmethod
    def get_all():
        """
        Tum kitaplari getirir
        
        Returns:
            list: Kitap listesi
        """
        try:
            query = f"""
                SELECT k.KitapID, k.KitapAdi, k.Yazar, k.ISBN, k.Yayinevi, 
                       k.BasimYili, k.ToplamAdet, k.MevcutAdet, k.KategoriID,
                       kat.KategoriAdi
                FROM {TABLE_KITAP} k
                LEFT JOIN {TABLE_KATEGORI} kat ON k.KategoriID = kat.KategoriID
                ORDER BY k.KitapID DESC
            """
            return db_manager.execute_query(query)
        except Exception as e:
            print(f"[BOOK ERROR] Get all hatasi: {e}")
            return []
    
    @staticmethod
    def get_by_id(kitap_id):
        """
        ID'ye gore kitap getirir
        
        Args:
            kitap_id (int): Kitap ID
            
        Returns:
            dict/None: Kitap bilgileri
        """
        try:
            query = f"""
                SELECT k.KitapID, k.KitapAdi, k.Yazar, k.ISBN, k.Yayinevi, 
                       k.BasimYili, k.ToplamAdet, k.MevcutAdet, k.KategoriID,
                       kat.KategoriAdi
                FROM {TABLE_KITAP} k
                LEFT JOIN {TABLE_KATEGORI} kat ON k.KategoriID = kat.KategoriID
                WHERE k.KitapID = %s
            """
            return db_manager.execute_query(query, (kitap_id,), fetch_one=True)
        except Exception as e:
            print(f"[BOOK ERROR] Get by ID hatasi: {e}")
            return None
    
    @staticmethod
    def search(keyword=None, kategori_id=None, yazar=None):
        """
        Kitap arama (Stored Procedure kullanir)
        
        Args:
            keyword (str): Kitap adi arama
            kategori_id (int): Kategori filtresi
            yazar (str): Yazar filtresi
            
        Returns:
            list: Kitap listesi
        """
        try:
            # sp_KitapAra 4 parametre aliyor: KitapAdi, Yazar, ISBN, KategoriID
            results = db_manager.call_procedure(
                SP_KITAP_ARA, 
                (keyword, yazar, None, kategori_id)
            )
            return results
        except Exception as e:
            print(f"[BOOK ERROR] Search hatasi: {e}")
            # SP hatasi varsa normal sorgu ile dene
            try:
                query = f"""
                    SELECT k.KitapID, k.KitapAdi, k.Yazar, k.ISBN, k.Yayinevi, 
                           k.BasimYili, k.ToplamAdet, k.MevcutAdet, k.KategoriID,
                           kat.KategoriAdi
                    FROM {TABLE_KITAP} k
                    LEFT JOIN {TABLE_KATEGORI} kat ON k.KategoriID = kat.KategoriID
                    WHERE 1=1
                """
                params = []
                
                if keyword:
                    query += " AND k.KitapAdi LIKE %s"
                    params.append(f"%{keyword}%")
                
                if kategori_id:
                    query += " AND k.KategoriID = %s"
                    params.append(kategori_id)
                
                if yazar:
                    query += " AND k.Yazar LIKE %s"
                    params.append(f"%{yazar}%")
                
                query += " ORDER BY k.KitapID DESC"
                
                return db_manager.execute_query(query, tuple(params) if params else None)
            except Exception as e2:
                print(f"[BOOK ERROR] Fallback search hatasi: {e2}")
                return []
    
    @staticmethod
    def create(kitap_adi, yazar, isbn, yayinevi, basim_yili, toplam_adet, kategori_id):
        """
        Yeni kitap olusturur
        
        Args:
            kitap_adi (str): Kitap adi
            yazar (str): Yazar
            isbn (str): ISBN
            yayinevi (str): Yayinevi
            basim_yili (int): Basim yili
            toplam_adet (int): Toplam adet
            kategori_id (int): Kategori ID
            
        Returns:
            tuple: (bool, str/int) - (Basarili mi, Hata mesaji veya KitapID)
        """
        try:
            # Validasyon
            if not validate_required(kitap_adi):
                return False, "Kitap adi zorunlu"
            if not validate_required(yazar):
                return False, "Yazar zorunlu"
            if not validate_required(isbn):
                return False, "ISBN zorunlu"
            if not validate_isbn(isbn):
                return False, "Gecersiz ISBN formati"
            if not validate_required(yayinevi):
                return False, "Yayinevi zorunlu"
            if not validate_year(basim_yili):
                return False, "Gecersiz basim yili"
            if not validate_positive_number(toplam_adet):
                return False, "Toplam adet pozitif olmali"
            
            # ISBN benzersiz mi?
            check_query = f"SELECT COUNT(*) as sayi FROM {TABLE_KITAP} WHERE ISBN = %s"
            result = db_manager.execute_query(check_query, (isbn,), fetch_one=True)
            if result['sayi'] > 0:
                return False, "Bu ISBN zaten kayitli"
            
            # MevcutAdet baslangicta ToplamAdet ile ayni
            mevcut_adet = toplam_adet
            
            # Insert
            query = f"""
                INSERT INTO {TABLE_KITAP} 
                (KitapAdi, Yazar, ISBN, Yayinevi, BasimYili, ToplamAdet, MevcutAdet, KategoriID)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            affected, last_id = db_manager.execute_update(
                query, (kitap_adi, yazar, isbn, yayinevi, basim_yili, 
                       toplam_adet, mevcut_adet, kategori_id)
            )
            
            if affected > 0:
                return True, last_id
            return False, "Kitap eklenemedi"
            
        except Exception as e:
            print(f"[BOOK ERROR] Create hatasi: {e}")
            return False, str(e)
    
    @staticmethod
    def update(kitap_id, kitap_adi=None, yazar=None, isbn=None, yayinevi=None, 
               basim_yili=None, toplam_adet=None, kategori_id=None):
        """
        Kitap gunceller
        
        Args:
            kitap_id (int): Kitap ID
            ... diger alanlar (None ise guncellenmez)
            
        Returns:
            tuple: (bool, str) - (Basarili mi, Mesaj)
        """
        try:
            # Mevcut kitap var mi?
            existing = Book.get_by_id(kitap_id)
            if not existing:
                return False, "Kitap bulunamadi"
            
            # Guncellenecek alanlar
            updates = []
            params = []
            
            if kitap_adi is not None:
                updates.append("KitapAdi = %s")
                params.append(kitap_adi)
            
            if yazar is not None:
                updates.append("Yazar = %s")
                params.append(yazar)
            
            if isbn is not None:
                if not validate_isbn(isbn):
                    return False, "Gecersiz ISBN formati"
                # ISBN benzersiz mi?
                check_query = f"""
                    SELECT COUNT(*) as sayi FROM {TABLE_KITAP} 
                    WHERE ISBN = %s AND KitapID != %s
                """
                result = db_manager.execute_query(
                    check_query, (isbn, kitap_id), fetch_one=True
                )
                if result['sayi'] > 0:
                    return False, "Bu ISBN zaten kayitli"
                updates.append("ISBN = %s")
                params.append(isbn)
            
            if yayinevi is not None:
                updates.append("Yayinevi = %s")
                params.append(yayinevi)
            
            if basim_yili is not None:
                if not validate_year(basim_yili):
                    return False, "Gecersiz basim yili"
                updates.append("BasimYili = %s")
                params.append(basim_yili)
            
            if toplam_adet is not None:
                if not validate_positive_number(toplam_adet):
                    return False, "Toplam adet pozitif olmali"
                updates.append("ToplamAdet = %s")
                params.append(toplam_adet)
                
                # MevcutAdet'i de ayarla (fark kadar ekle/cikar)
                fark = int(toplam_adet) - existing['ToplamAdet']
                yeni_mevcut = existing['MevcutAdet'] + fark
                if yeni_mevcut < 0:
                    yeni_mevcut = 0
                updates.append("MevcutAdet = %s")
                params.append(yeni_mevcut)
            
            if kategori_id is not None:
                updates.append("KategoriID = %s")
                params.append(kategori_id)
            
            if not updates:
                return False, "Guncellenecek alan yok"
            
            params.append(kitap_id)
            query = f"UPDATE {TABLE_KITAP} SET {', '.join(updates)} WHERE KitapID = %s"
            
            affected, _ = db_manager.execute_update(query, tuple(params))
            
            if affected > 0:
                return True, "Kitap guncellendi"
            return False, "Guncelleme yapilamadi"
            
        except Exception as e:
            print(f"[BOOK ERROR] Update hatasi: {e}")
            return False, str(e)
    
    @staticmethod
    def delete(kitap_id):
        """
        Kitap siler
        
        Args:
            kitap_id (int): Kitap ID
            
        Returns:
            tuple: (bool, str) - (Basarili mi, Mesaj)
        """
        try:
            # Aktif odunc var mi kontrol et
            check_query = """
                SELECT COUNT(*) as sayi FROM ODUNC 
                WHERE KitapID = %s AND TeslimTarihi IS NULL
            """
            result = db_manager.execute_query(check_query, (kitap_id,), fetch_one=True)
            if result['sayi'] > 0:
                return False, "Kitabin aktif odunc kaydi var, silinemez"
            
            query = f"DELETE FROM {TABLE_KITAP} WHERE KitapID = %s"
            affected, _ = db_manager.execute_update(query, (kitap_id,))
            
            if affected > 0:
                return True, "Kitap silindi"
            return False, "Kitap bulunamadi"
            
        except Exception as e:
            print(f"[BOOK ERROR] Delete hatasi: {e}")
            return False, str(e)
    
    @staticmethod
    def get_available_books():
        """Mevcut stoku olan kitaplari getirir"""
        try:
            query = f"""
                SELECT k.KitapID, k.KitapAdi, k.Yazar, k.MevcutAdet,
                       kat.KategoriAdi
                FROM {TABLE_KITAP} k
                LEFT JOIN {TABLE_KATEGORI} kat ON k.KategoriID = kat.KategoriID
                WHERE k.MevcutAdet > 0
                ORDER BY k.KitapAdi
            """
            return db_manager.execute_query(query)
        except Exception as e:
            print(f"[BOOK ERROR] Available books hatasi: {e}")
            return []
