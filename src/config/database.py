"""
Kutuphane Yonetim Sistemi - Veritabani Konfigurasyonu
.env dosyasindan veritabani bilgilerini yukler
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Proje root dizinini bul
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# .env dosyasini yukle
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)


class DatabaseConfig:
    """Veritabani konfigurasyonu"""
    
    HOST = os.getenv('DB_HOST', 'localhost')
    PORT = int(os.getenv('DB_PORT', 3306))
    NAME = os.getenv('DB_NAME', 'kutuphane_db')
    USER = os.getenv('DB_USER', 'root')
    PASSWORD = os.getenv('DB_PASSWORD', '')
    
    @classmethod
    def get_config(cls):
        """
        Veritabani baglanti bilgilerini dict olarak dondurur
        
        Returns:
            dict: Baglanti bilgileri
        """
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'database': cls.NAME,
            'user': cls.USER,
            'password': cls.PASSWORD,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_turkish_ci',
            'autocommit': False,
            'raise_on_warnings': True
        }
    
    @classmethod
    def get_pool_config(cls):
        """
        Connection pool icin konfigurasyonu dondurur
        
        Returns:
            dict: Pool konfigurasyonu
        """
        config = cls.get_config()
        config.update({
            'pool_name': 'kutuphane_pool',
            'pool_size': 5,
            'pool_reset_session': True
        })
        return config
    
    @classmethod
    def validate_config(cls):
        """
        Konfigurasyonun gecerli olup olmadigini kontrol eder
        
        Returns:
            tuple: (bool, str) - (Gecerli mi, Hata mesaji)
        """
        if not cls.HOST:
            return False, "DB_HOST tanimlanmamis"
        
        if not cls.NAME:
            return False, "DB_NAME tanimlanmamis"
        
        if not cls.USER:
            return False, "DB_USER tanimlanmamis"
        
        return True, "Konfigurasi gecerli"


class AppConfig:
    """Uygulama konfigurasyonu"""
    
    DEBUG = os.getenv('APP_DEBUG', 'False').lower() == 'true'
    TIMEZONE = os.getenv('APP_TIMEZONE', 'Europe/Istanbul')
    
    @classmethod
    def is_debug(cls):
        """Debug modu aktif mi?"""
        return cls.DEBUG


# Singleton instance
db_config = DatabaseConfig()
app_config = AppConfig()
