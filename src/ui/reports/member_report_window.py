"""
Uye Raporlari
Detaylı ödünç ve ceza geçmişi raporlama ekranı
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QComboBox, QFrame, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from src.database.db_manager import db_manager


class MemberReportWindow(QWidget):
    """Uye raporlari ekrani"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_members()
    
    def init_ui(self):
        """UI olustur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Sayfa Başlığı
        title = QLabel('ÜYE RAPORLARI')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #3B4953;')
        layout.addWidget(title)
        
        # --- 1. ARAMA VE SEÇİM ALANI ---
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #D0D8E2;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("Üye Seçin:"))
        
        # Normal ComboBox
        self.member_combo = QComboBox()
        self.member_combo.setMinimumWidth(350)
        self.member_combo.setStyleSheet("padding: 6px; font-size: 14px;")
        self.member_combo.currentIndexChanged.connect(self.show_member_report)
        search_layout.addWidget(self.member_combo)
        
        # Yenile Butonu
        refresh_btn = QPushButton("Yenile")
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.refresh_data)
        search_layout.addWidget(refresh_btn)
        
        search_layout.addStretch()
        search_frame.setLayout(search_layout)
        layout.addWidget(search_frame)
        
        # --- 2. ÖZET BİLGİ KARTI ---
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 5px;
            }
        """)
        self.info_layout = QHBoxLayout()
        
        # Başlangıç etiketleri
        self.lbl_ad = QLabel("<b>Üye:</b> -")
        self.lbl_toplam = QLabel("<b>Toplam Ödünç:</b> 0")
        self.lbl_teslim = QLabel("<b>Teslim Edilmiş:</b> 0")
        self.lbl_aktif = QLabel("<b>Aktif Ödünç:</b> 0")
        self.lbl_borc = QLabel("<b>Toplam Borç:</b> <span style='color:red'>0.00 TL</span>")
        
        self.info_layout.addWidget(self.lbl_ad)
        self.info_layout.addWidget(self.lbl_toplam)
        self.info_layout.addWidget(self.lbl_teslim)
        self.info_layout.addWidget(self.lbl_aktif)
        self.info_layout.addWidget(self.lbl_borc)
        
        self.info_frame.setLayout(self.info_layout)
        self.info_frame.hide()
        layout.addWidget(self.info_frame)
        
        # --- 3. DETAY TABLOSU ---
        self.table = QTableWidget()
        self.table.setColumnCount(6) # Sütun Sayısı
        
        # Tablo Görünüm Ayarları (Mavi Başlık Kaldırıldı)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(400)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def refresh_data(self):
        """Sayfa yenilendiğinde çağrılır"""
        self.load_members()
        self.info_frame.hide()
        self.table.setRowCount(0)
    
    def load_members(self):
        """Uyeleri yukle"""
        try:
            query = "SELECT UyeID, Ad, Soyad, Email FROM UYE ORDER BY Ad, Soyad"
            members = db_manager.execute_query(query)
            
            self.member_combo.clear()
            self.member_combo.addItem("-- Üye Seçin --", None)
            
            for m in members:
                display_text = f"{m['Ad']} {m['Soyad']} ({m['Email']})"
                self.member_combo.addItem(display_text, m['UyeID'])
                
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Üyeler yüklenemedi: {str(e)}')
    
    def show_member_report(self):
        """Uye raporu goster"""
        index = self.member_combo.currentIndex()
        if index <= 0:  # 0 = "-- Üye Seçin --"
            self.info_frame.hide()
            self.table.setRowCount(0)
            return
            
        uye_id = self.member_combo.itemData(index)
        if not uye_id:
            return

        self.info_frame.show()
        
        try:
            # 1. ÖZET BİLGİLER
            uye_query = "SELECT Ad, Soyad, ToplamBorc FROM UYE WHERE UyeID = %s"
            uye_data = db_manager.execute_query(uye_query, (uye_id,), fetch_one=True)
            
            stats_query = """
                SELECT 
                    COUNT(*) as Toplam,
                    COUNT(CASE WHEN TeslimTarihi IS NULL THEN 1 END) as Aktif,
                    COUNT(CASE WHEN TeslimTarihi IS NOT NULL THEN 1 END) as Teslim
                FROM ODUNC 
                WHERE UyeID = %s
            """
            stats = db_manager.execute_query(stats_query, (uye_id,), fetch_one=True)
            
            if uye_data and stats:
                ad_soyad = f"{uye_data['Ad']} {uye_data['Soyad']}"
                borc = float(uye_data['ToplamBorc'])
                
                self.lbl_ad.setText(f"<b>Üye:</b> {ad_soyad}")
                self.lbl_toplam.setText(f"<b>Toplam Ödünç:</b> {stats['Toplam']}")
                self.lbl_teslim.setText(f"<b>Teslim Edilmiş:</b> {stats['Teslim']}")
                self.lbl_aktif.setText(f"<b>Aktif Ödünç:</b> {stats['Aktif']}")
                
                borc_color = "red" if borc > 0 else "green"
                self.lbl_borc.setText(f"<b>Toplam Borç:</b> <span style='color:{borc_color}'>{borc:.2f} TL</span>")
            
            # 2. DETAY TABLOSU
            table_query = """
                SELECT 
                    k.KitapID, 
                    k.KitapAdi, 
                    o.OduncTarihi, 
                    o.TeslimTarihi,
                    c.Tutar as CezaTutar,
                    c.OdendiMi
                FROM ODUNC o
                INNER JOIN KITAP k ON o.KitapID = k.KitapID
                LEFT JOIN CEZA c ON o.OduncID = c.OduncID
                WHERE o.UyeID = %s
                ORDER BY o.OduncTarihi DESC
            """
            loans = db_manager.execute_query(table_query, (uye_id,))
            
            # Satır sayısı: Data + 1 (Başlık için)
            self.table.setRowCount(len(loans) + 1)
            
            # --- TABLO BAŞLIĞI (ROW 0) ---
            headers = ['Kitap ID', 'Kitap Adı', 'Ödünç Tarihi', 'Teslim Tarihi', 'Ceza Tutarı', 'Ceza Durumu']
            for col, text in enumerate(headers):
                item = QTableWidgetItem(text)
                item.setBackground(QColor('#1A4D70')) # Koyu Mavi Arka Plan
                item.setForeground(QColor('white'))   # Beyaz Yazı
                item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsEnabled) # Tıklanamaz
                self.table.setItem(0, col, item)
            
            # --- VERİ SATIRLARI ---
            for row_idx, item in enumerate(loans, start=1):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(item['KitapID'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(item['KitapAdi'])))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(item['OduncTarihi'])))
                
                # Teslim Tarihi
                if item['TeslimTarihi']:
                    teslim_item = QTableWidgetItem(str(item['TeslimTarihi']))
                else:
                    teslim_item = QTableWidgetItem("Teslim Edilmedi")
                    teslim_item.setForeground(QColor("#E67E22")) # Turuncu
                    teslim_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                self.table.setItem(row_idx, 3, teslim_item)
                
                # Ceza
                if item['CezaTutar'] is not None:
                    ceza_str = f"{float(item['CezaTutar']):.2f} TL"
                else:
                    ceza_str = "-"
                self.table.setItem(row_idx, 4, QTableWidgetItem(ceza_str))
                
                # Durum
                if item['CezaTutar'] is None:
                    durum = "-"
                    color = QColor("black")
                elif item['OdendiMi']:
                    durum = "Ödendi"
                    color = QColor("#28a745") # Yeşil
                else:
                    durum = "Ödenmedi"
                    color = QColor("#dc3545") # Kırmızı
                
                durum_item = QTableWidgetItem(durum)
                if durum != "-":
                    durum_item.setForeground(color)
                    durum_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                self.table.setItem(row_idx, 5, durum_item)
                
                # Hizalama
                for col in range(6):
                    if self.table.item(row_idx, col):
                        self.table.item(row_idx, col).setTextAlignment(Qt.AlignCenter)
            
            self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # Kitap Adı esnek
                
        except Exception as e:
            print(f"Rapor hatasi: {e}")
            QMessageBox.critical(self, 'Hata', f'Rapor oluşturulamadı: {str(e)}')