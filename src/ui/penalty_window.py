"""
Ceza Goruntuleme ve Odeme Ekrani
Modernize edilmis tablo yapisi ve hata duzeltmeleri
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QComboBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from src.models.penalty import Penalty

class PenaltyWindow(QWidget):
    """Ceza yonetim ekrani"""
    
    def __init__(self, dashboard=None):
        super().__init__()
        self.dashboard = dashboard
        self.init_ui()
        self.load_penalties()
    
    def init_ui(self):
        """UI olustur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Baslik
        title = QLabel('CEZA YÖNETİMİ')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #3B4953;')
        layout.addWidget(title)
        
        # Filtre
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Durum:'))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['Tüm Cezalar', 'Ödenmemiş', 'Ödenmiş'])
        self.filter_combo.currentIndexChanged.connect(self.load_penalties)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7) # ID, Üye, Kitap, Tutar, Durum, Tarih, CezaID (Gizli)
        
        # --- TABLO AYARLARI (Mavi Başlık Kaldırıldı) ---
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(400)
        
        layout.addWidget(self.table)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.pay_btn = QPushButton('Ceza Öde')
        self.pay_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        self.pay_btn.clicked.connect(self.pay_penalty)
        button_layout.addWidget(self.pay_btn)
        
        self.refresh_btn = QPushButton('Yenile')
        self.refresh_btn.clicked.connect(self.load_penalties)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def update_table_content(self, penalties):
        """Tabloyu doldur"""
        self.table.setRowCount(len(penalties) + 1)
        
        # 1. BAŞLIK SATIRI (Row 0)
        headers = ['ID', 'Üye', 'Kitap / İşlem', 'Ceza Tutarı', 'Durum', 'Tarih']
        for col, header_text in enumerate(headers):
            item = QTableWidgetItem(header_text)
            item.setBackground(QColor('#1A4D70')) # Mavi Arka Plan
            item.setForeground(QColor('#FFFFFF')) # Beyaz Yazı
            font = QFont('Segoe UI', 11, QFont.Bold)
            item.setFont(font)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(0, col, item)
            
        # 2. VERİ SATIRLARI
        for row_idx, penalty in enumerate(penalties, start=1):
            # ID
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(penalty.get('CezaID', ''))))
            
            # Üye
            uye_adi = f"{penalty.get('UyeAd', '')} {penalty.get('UyeSoyad', '')}"
            self.table.setItem(row_idx, 1, QTableWidgetItem(uye_adi))
            
            # Kitap Adı (Eğer kitap yoksa Manuel Ceza olabilir veya join boş gelmiş olabilir)
            kitap = penalty.get('KitapAdi')
            if not kitap:
                kitap = "Diğer / Manuel" if not penalty.get('OduncID') else "Kitap Silinmiş"
            self.table.setItem(row_idx, 2, QTableWidgetItem(kitap))
            
            # Tutar
            tutar = float(penalty.get('Tutar', 0))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{tutar:.2f} TL"))
            
            # --- HATA DUZELTME NOKTASI (OdendiMi Hatasi) ---
            # get_unpaid() sorgusunda 'OdendiMi' sütunu gelmiyor olabilir.
            # .get('OdendiMi', False) diyerek, eğer gelmezse varsayılan olarak False (Ödenmedi) kabul et diyoruz.
            odendi_mi = penalty.get('OdendiMi', False)
            
            durum_str = 'Ödendi' if odendi_mi else 'Ödenmedi'
            durum_item = QTableWidgetItem(durum_str)
            
            # Ödenmemişleri kırmızı yap
            if not odendi_mi:
                durum_item.setForeground(QColor('#dc3545'))
                durum_item.setFont(QFont('Segoe UI', 9, QFont.Bold))
            else:
                durum_item.setForeground(QColor('#28a745')) # Yeşil
                
            self.table.setItem(row_idx, 4, durum_item)
            
            # Tarih
            tarih = str(penalty.get('OlusturmaTarihi', ''))
            self.table.setItem(row_idx, 5, QTableWidgetItem(tarih))
            
            # Hücreleri ortala
            for col in [0, 3, 4, 5]:
                if self.table.item(row_idx, col):
                    self.table.item(row_idx, col).setTextAlignment(Qt.AlignCenter)

        # Genişlik ayarları
        self.table.resizeColumnsToContents()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch) # Üye adı esnek
        header.setSectionResizeMode(2, QHeaderView.Stretch) # Kitap adı esnek

    def load_penalties(self):
        """Cezalari yukle"""
        try:
            filter_index = self.filter_combo.currentIndex()
            
            if filter_index == 1:  # Odenmemis
                penalties = Penalty.get_unpaid()
            elif filter_index == 2:  # Odenmis
                all_penalties = Penalty.get_all()
                penalties = [p for p in all_penalties if p.get('OdendiMi')]
            else:  # Tumu
                penalties = Penalty.get_all()
            
            self.update_table_content(penalties)
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Cezalar yüklenemedi: {str(e)}')
    
    def refresh_data(self):
        """Sayfa yenilendiğinde çağrılır"""
        self.load_penalties()
    
    def pay_penalty(self):
        """Ceza ode"""
        selected = self.table.currentRow()
        
        # --- CRASH FIX: Seçim kontrolü ---
        if selected <= 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen ödenecek cezayı seçin!')
            return
        
        # Sütun indeksleri değiştiği için dikkatli alıyoruz
        # 0: ID, 1: Üye, 2: Kitap, 3: Tutar, 4: Durum
        ceza_id = int(self.table.item(selected, 0).text())
        durum = self.table.item(selected, 4).text()
        
        if durum == 'Ödendi':
            if self.dashboard:
                self.dashboard.show_toast('Bu ceza zaten ödenmiş!', 'info')
            return
        
        uye = self.table.item(selected, 1).text()
        tutar = self.table.item(selected, 3).text()
        
        reply = QMessageBox.question(
            self,
            'Ödeme Onayı',
            f'{uye} için {tutar} cezayı ödemek istediğinize emin misiniz?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                Penalty.pay_penalty(ceza_id)
                if self.dashboard:
                    self.dashboard.show_toast('Ceza başarıyla ödendi!', 'success')
                self.load_penalties()
                
                # İstatistikleri güncelle (dashboard açıksa)
                if self.dashboard:
                    self.dashboard.refresh_statistics()
                    
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Ödeme hatası: {str(e)}')