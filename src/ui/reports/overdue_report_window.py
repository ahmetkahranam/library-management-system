"""
Geciken Oduncler Raporu
Modernize edilmiş tablo yapısı
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from src.models.loan import Loan
from datetime import datetime


class OverdueReportWindow(QWidget):
    """Geciken oduncler raporu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_overdue_loans()
    
    def init_ui(self):
        """UI olustur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Baslik
        title = QLabel('GECİKEN ÖDÜNÇLER RAPORU')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #3B4953;')
        layout.addWidget(title)
        
        # Ozet Bilgi Kartı (Basit Label yerine stilli frame gibi dursa da label yeterli şimdilik)
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-size: 14px; padding: 10px; background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 5px;")
        layout.addWidget(self.summary_label)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(8) # ID, Üye, Kitap, Ödünç T., Teslim T., Gecikme, Ceza, İletişim
        
        # --- TABLO TASARIMI (Mavi Başlık Kaldırıldı) ---
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(400)
        
        layout.addWidget(self.table)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton('Yenile')
        self.refresh_btn.setStyleSheet("""
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
        self.refresh_btn.clicked.connect(self.load_overdue_loans)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_overdue_loans(self):
        """Geciken oduncleri yukle"""
        try:
            overdue_loans = Loan.get_overdue_loans()
            
            # Ozet bilgi
            total_overdue = len(overdue_loans)
            # TeslimTarihi yerine SonTeslimTarihi kullan
            total_penalty = sum((datetime.now().date() - loan['SonTeslimTarihi']).days * 5 
                              for loan in overdue_loans)
            
            self.summary_label.setText(
                f'<b>Toplam Geciken Ödünç:</b> {total_overdue} | '
                f'<b>Toplam Tahmini Ceza:</b> <span style="color:red">{total_penalty:.2f} TL</span>'
            )
            
            # Satır Sayısı: Veri + 1 (Başlık için)
            self.table.setRowCount(len(overdue_loans) + 1)
            today = datetime.now().date()
            
            # --- 1. BAŞLIK SATIRI (Row 0) ---
            headers = ['Ödünç ID', 'Üye', 'Kitap', 'Ödünç Tarihi', 'Teslim Tarihi', 'Gecikme (Gün)', 'Tahmini Ceza', 'İletişim']
            for col, text in enumerate(headers):
                item = QTableWidgetItem(text)
                item.setBackground(QColor('#1A4D70')) # Mavi Arka Plan
                item.setForeground(QColor('white'))   # Beyaz Yazı
                item.setFont(QFont('Segoe UI', 10, QFont.Bold))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsEnabled)
                self.table.setItem(0, col, item)
            
            # --- 2. VERİ SATIRLARI (Row 1'den başlar) ---
            for row_idx, loan in enumerate(overdue_loans, start=1):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(loan['OduncID'])))
                
                # UyeAdi yerine UyeAd + UyeSoyad
                uye_adi = f"{loan.get('UyeAd', '')} {loan.get('UyeSoyad', '')}"
                self.table.setItem(row_idx, 1, QTableWidgetItem(uye_adi))
                
                self.table.setItem(row_idx, 2, QTableWidgetItem(loan['KitapAdi']))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(loan['OduncTarihi'])))
                
                # TeslimTarihi yerine SonTeslimTarihi
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(loan['SonTeslimTarihi'])))
                
                gecikme = (today - loan['SonTeslimTarihi']).days
                ceza = gecikme * 5
                
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(gecikme)))
                
                ceza_item = QTableWidgetItem(f'{ceza:.2f} TL')
                ceza_item.setForeground(QColor("#dc3545")) # Kırmızı
                ceza_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                self.table.setItem(row_idx, 6, ceza_item)
                
                self.table.setItem(row_idx, 7, QTableWidgetItem(loan.get('Telefon', '') or ''))
                
                # Ortala
                for col in [0, 3, 4, 5, 6, 7]:
                    if self.table.item(row_idx, col):
                        self.table.item(row_idx, col).setTextAlignment(Qt.AlignCenter)
            
            # --- SÜTUN GENİŞLİKLERİ ---
            self.table.resizeColumnsToContents()
            # Kitap sütunu (2. indeks) esnek olsun
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Rapor yüklenemedi: {str(e)}')
    
    def refresh_data(self):
        """Sayfa yenilendiginde cagirilir"""
        self.load_overdue_loans()