"""
Kitap Raporlari Ekrani
Modernize edilmiş tablo yapısı
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QComboBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from src.database.db_manager import DatabaseManager


class BookReportWindow(QWidget):
    """Kitap raporlari ekrani"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """UI olustur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Baslik
        title = QLabel('KİTAP RAPORLARI')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #3B4953;')
        layout.addWidget(title)
        
        # Rapor turu sec
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel('Rapor Türü:'))
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            'Tüm Kitaplar',
            'Mevcut Kitaplar',
            'Stokta Olmayan Kitaplar',
            'En Çok Ödünç Verilen Kitaplar'
        ])
        # Seçim değiştiğinde otomatik yenile (İsteğe bağlı, butona da bırakabilirsin)
        self.report_type_combo.currentIndexChanged.connect(self.show_report)
        select_layout.addWidget(self.report_type_combo)
        
        self.show_btn = QPushButton('Rapor Göster')
        self.show_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A4D70;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #153d5a; }
        """)
        self.show_btn.clicked.connect(self.show_report)
        select_layout.addWidget(self.show_btn)
        
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7) # ID, Kitap Adı, Yazar, Kategori, Toplam, Mevcut, Ödünç
        
        # --- TABLO TASARIMI (Mavi Başlık Kaldırıldı) ---
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(400)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        # Baslangicta raporu goster
        self.show_report()
    
    def show_report(self):
        """Secilen raporu goster"""
        report_type = self.report_type_combo.currentIndex()
        
        try:
            db = DatabaseManager()
            
            # --- SORGULAR ---
            if report_type == 0:  # Tum Kitaplar
                query = """
                    SELECT k.KitapID, k.KitapAdi, k.Yazar, kat.KategoriAdi,
                           k.ToplamAdet, k.MevcutAdet,
                           COUNT(o.OduncID) as OduncSayisi
                    FROM KITAP k
                    LEFT JOIN KATEGORI kat ON k.KategoriID = kat.KategoriID
                    LEFT JOIN ODUNC o ON k.KitapID = o.KitapID
                    GROUP BY k.KitapID
                    ORDER BY k.KitapAdi
                """
            elif report_type == 1:  # Mevcut Kitaplar
                query = """
                    SELECT k.KitapID, k.KitapAdi, k.Yazar, kat.KategoriAdi,
                           k.ToplamAdet, k.MevcutAdet,
                           COUNT(o.OduncID) as OduncSayisi
                    FROM KITAP k
                    LEFT JOIN KATEGORI kat ON k.KategoriID = kat.KategoriID
                    LEFT JOIN ODUNC o ON k.KitapID = o.KitapID
                    WHERE k.MevcutAdet > 0
                    GROUP BY k.KitapID
                    ORDER BY k.KitapAdi
                """
            elif report_type == 2:  # Stokta Olmayan
                query = """
                    SELECT k.KitapID, k.KitapAdi, k.Yazar, kat.KategoriAdi,
                           k.ToplamAdet, k.MevcutAdet,
                           COUNT(o.OduncID) as OduncSayisi
                    FROM KITAP k
                    LEFT JOIN KATEGORI kat ON k.KategoriID = kat.KategoriID
                    LEFT JOIN ODUNC o ON k.KitapID = o.KitapID
                    WHERE k.MevcutAdet = 0
                    GROUP BY k.KitapID
                    ORDER BY k.KitapAdi
                """
            else:  # En Cok Odunc Verilen
                query = """
                    SELECT k.KitapID, k.KitapAdi, k.Yazar, kat.KategoriAdi,
                           k.ToplamAdet, k.MevcutAdet,
                           COUNT(o.OduncID) as OduncSayisi
                    FROM KITAP k
                    LEFT JOIN KATEGORI kat ON k.KategoriID = kat.KategoriID
                    LEFT JOIN ODUNC o ON k.KitapID = o.KitapID
                    GROUP BY k.KitapID
                    HAVING COUNT(o.OduncID) > 0
                    ORDER BY OduncSayisi DESC
                    LIMIT 20
                """
            
            books = db.execute_query(query)
            
            # Satır Sayısı: Veri + 1 (Başlık için)
            self.table.setRowCount(len(books) + 1)
            
            # --- 1. BAŞLIK SATIRI (Row 0) ---
            headers = ['ID', 'Kitap Adı', 'Yazar', 'Kategori', 'Toplam', 'Mevcut', 'Ödünç']
            for col, text in enumerate(headers):
                item = QTableWidgetItem(text)
                item.setBackground(QColor('#1A4D70')) # Mavi Arka Plan
                item.setForeground(QColor('white'))   # Beyaz Yazı
                item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsEnabled) # Düzenlenemez
                self.table.setItem(0, col, item)
            
            # --- 2. VERİ SATIRLARI (Row 1'den başlar) ---
            for row_idx, book in enumerate(books, start=1):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(book['KitapID'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(book['KitapAdi']))
                self.table.setItem(row_idx, 2, QTableWidgetItem(book['Yazar']))
                self.table.setItem(row_idx, 3, QTableWidgetItem(book.get('KategoriAdi', '') or '-'))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(book['ToplamAdet'])))
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(book['MevcutAdet'])))
                self.table.setItem(row_idx, 6, QTableWidgetItem(str(book['OduncSayisi'])))
                
                # Ortala (Sayısal alanlar ve ID)
                for col in [0, 4, 5, 6]:
                    self.table.item(row_idx, col).setTextAlignment(Qt.AlignCenter)
            
            # --- SÜTUN GENİŞLİKLERİ ---
            self.table.resizeColumnsToContents()
            # Kitap Adı (1. sütun) esnek olsun
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Rapor oluşturulamadı: {str(e)}')
    
    def refresh_data(self):
        """Sayfa yenilendiginde cagirilir"""
        self.show_report()