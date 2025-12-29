"""
Kutuphane Yonetim Sistemi - Veritabani Yoneticisi
Connection pool ve veritabani islemleri
"""

import mysql.connector
from mysql.connector import pooling, Error
from contextlib import contextmanager
from src.config.database import DatabaseConfig


class DatabaseManager:
    """Veritabani baglanti ve islem yoneticisi"""
    
    _pool = None
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Connection pool'u baslatir"""
        if DatabaseManager._pool is None:
            try:
                pool_config = DatabaseConfig.get_pool_config()
                DatabaseManager._pool = pooling.MySQLConnectionPool(**pool_config)
                print("[DB] Connection pool olusturuldu")
            except Error as e:
                print(f"[DB ERROR] Pool olusturma hatasi: {e}")
                raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager ile baglanti al
        
        Yields:
            connection: MySQL baglantisi
            
        Example:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                # islemler...
        """
        connection = None
        try:
            connection = DatabaseManager._pool.get_connection()
            yield connection
        except Error as e:
            if connection:
                connection.rollback()
            print(f"[DB ERROR] Baglanti hatasi: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_query(self, query, params=None, fetch_one=False):
        """
        SELECT sorgusu calistirir
        
        Args:
            query (str): SQL sorgusu
            params (tuple): Parametre degerleri
            fetch_one (bool): Tek satir mi donsun?
            
        Returns:
            list/dict: Sorgu sonucu
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                
                if fetch_one:
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchall()
                
                cursor.close()
                return result
                
        except Error as e:
            print(f"[DB ERROR] Sorgu hatasi: {e}")
            print(f"[DB ERROR] Query: {query}")
            raise
    
    def execute_update(self, query, params=None):
        """
        INSERT, UPDATE, DELETE sorgusu calistirir
        
        Args:
            query (str): SQL sorgusu
            params (tuple): Parametre degerleri
            
        Returns:
            tuple: (affected_rows, last_insert_id)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                
                affected_rows = cursor.rowcount
                last_id = cursor.lastrowid
                
                cursor.close()
                return affected_rows, last_id
                
        except Error as e:
            print(f"[DB ERROR] Update hatasi: {e}")
            print(f"[DB ERROR] Query: {query}")
            raise
    
    def execute_many(self, query, params_list):
        """
        Toplu INSERT/UPDATE islemi
        
        Args:
            query (str): SQL sorgusu
            params_list (list): Parametre listesi
            
        Returns:
            int: Etkilenen satir sayisi
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
                
        except Error as e:
            print(f"[DB ERROR] Bulk update hatasi: {e}")
            raise
    
    def call_procedure(self, proc_name, params=None):
        """
        Stored procedure calistirir
        
        Args:
            proc_name (str): Procedure adi
            params (tuple): Parametre degerleri
            
        Returns:
            list: Procedure sonuclari
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.callproc(proc_name, params or ())
                
                # Tum result setleri al
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                
                conn.commit()
                cursor.close()
                return results
                
        except Error as e:
            print(f"[DB ERROR] Procedure hatasi: {e}")
            print(f"[DB ERROR] Procedure: {proc_name}")
            raise
    
    def test_connection(self):
        """
        Veritabani baglantisini test eder
        
        Returns:
            tuple: (bool, str) - (Basarili mi, Mesaj)
        """
        try:
            with self.get_connection() as conn:
                if conn.is_connected():
                    cursor = conn.cursor()
                    cursor.execute("SELECT DATABASE(), VERSION()")
                    db_name, version = cursor.fetchone()
                    cursor.close()
                    
                    message = f"Baglanti basarili! DB: {db_name}, Version: {version}"
                    return True, message
                else:
                    return False, "Baglanti kurulamadi"
                    
        except Error as e:
            return False, f"Baglanti hatasi: {e}"
    
    def begin_transaction(self):
        """Transaction baslatir"""
        connection = DatabaseManager._pool.get_connection()
        connection.start_transaction()
        return connection
    
    def commit_transaction(self, connection):
        """Transaction'i commit eder"""
        if connection and connection.is_connected():
            connection.commit()
            connection.close()
    
    def rollback_transaction(self, connection):
        """Transaction'i geri alir"""
        if connection and connection.is_connected():
            connection.rollback()
            connection.close()
    
    def close_pool(self):
        """Connection pool'u kapatir"""
        if DatabaseManager._pool:
            print("[DB] Connection pool kapatiliyor...")
            DatabaseManager._pool = None
    
    def get_table_info(self, table_name):
        """
        Tablo bilgilerini getirir
        
        Args:
            table_name (str): Tablo adi
            
        Returns:
            list: Kolon bilgileri
        """
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)


# Singleton instance
db_manager = DatabaseManager()
