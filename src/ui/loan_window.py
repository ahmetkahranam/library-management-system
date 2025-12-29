"""
Odunc ve Teslim Islemleri Ekrani
Tek bir pencerede hem ödünç verme hem teslim alma işlemleri
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                             QMessageBox, QDialog, QFormLayout, QComboBox, 
                             QDateEdit, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from src.models.loan import Loan
from src.models.member import Member
from src.models.book import Book
from datetime import datetime

class LoanWindow(QWidget):
    """Odunc ve Teslim yonetim ekrani"""
    
    def __init__(self, user, dashboard=None):
        super().__init__()
        self.user = user
        self.dashboard = dashboard
        self.all_loans = [] # Arama yapabilmek için veriyi hafızada tutacağız
        self.init_ui()
        self.load_active_loans()
    
    def init_ui(self):
        """UI olustur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Baslik
        title = QLabel('ÖDÜNÇ & TESLİM İŞLEMLERİ')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #3B4953;')
        layout.addWidget(title)
        
        # --- ARAMA BÖLÜMÜ ---
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Üye adı veya Kitap adı ile ara...')
        self.search_input.textChanged.connect(self.search_loans)
        search_layout.addWidget(QLabel('Ara:'))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7) # ID, Üye, Kitap, Ödünç T., İade T., Durum, Ceza
        
        # Header gizle (0. satırı başlık yapacağız)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(400)
        
        layout.addWidget(self.table)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.new_loan_btn = QPushButton('Yeni Ödünç Ver')
        self.new_loan_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        self.new_loan_btn.clicked.connect(self.new_loan)
        button_layout.addWidget(self.new_loan_btn)
        
        self.return_btn = QPushButton('Teslim Al')
        self.return_btn.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")
        self.return_btn.clicked.connect(self.return_book)
        button_layout.addWidget(self.return_btn)
        
        self.refresh_btn = QPushButton('Yenile')
        self.refresh_btn.clicked.connect(self.load_active_loans)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_table_content(self, loans):
        """Tabloyu doldur"""
        self.table.setRowCount(len(loans) + 1)
        
        # 1. BAŞLIK SATIRI
        headers = ['ID', 'Üye', 'Kitap', 'Ödünç Tarihi', 'Son Teslim', 'Durum', 'Tahmini Ceza']
        for col, header_text in enumerate(headers):
            item = QTableWidgetItem(header_text)
            item.setBackground(QColor('#1A4D70'))
            item.setForeground(QColor('#FFFFFF'))
            font = QFont('Segoe UI', 11, QFont.Bold)
            item.setFont(font)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(0, col, item)
            
        today = datetime.now().date()
        
        # 2. VERİ SATIRLARI
        for row_idx, loan in enumerate(loans, start=1):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(loan['OduncID'])))
            
            # Üye Adı
            uye_adi = f"{loan.get('UyeAd', '')} {loan.get('UyeSoyad', '')}"
            self.table.setItem(row_idx, 1, QTableWidgetItem(uye_adi))
            
            # Kitap Adı
            self.table.setItem(row_idx, 2, QTableWidgetItem(loan['KitapAdi']))
            
            # Tarihler
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(loan['OduncTarihi'])))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(loan['SonTeslimTarihi'])))
            
            # Durum ve Ceza Hesaplama
            teslim_tarihi = loan['SonTeslimTarihi']
            if teslim_tarihi < today:
                gecikme = (today - teslim_tarihi).days
                ceza = gecikme * 5.0  # Günlük 5 TL
                durum = f'GECİKMİŞ ({gecikme} gün)'
                ceza_str = f"{ceza:.2f} TL"
                
                # Gecikenleri kırmızı yapalım
                durum_item = QTableWidgetItem(durum)
                durum_item.setForeground(QColor('#dc3545')) # Kırmızı
                self.table.setItem(row_idx, 5, durum_item)
            else:
                self.table.setItem(row_idx, 5, QTableWidgetItem('Normal'))
                ceza_str = "-"
            
            self.table.setItem(row_idx, 6, QTableWidgetItem(ceza_str))
            
            # Ortala
            for col in [0, 3, 4, 6]:
                if self.table.item(row_idx, col):
                    self.table.item(row_idx, col).setTextAlignment(Qt.AlignCenter)

        # Genişlik ayarları
        self.table.resizeColumnsToContents()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch) # Üye adı esnek
        header.setSectionResizeMode(2, QHeaderView.Stretch) # Kitap adı esnek

    def load_active_loans(self):
        """Aktif ödünçleri veritabanından çek"""
        try:
            self.all_loans = Loan.get_active_loans()
            self.update_table_content(self.all_loans)
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Ödünçler yüklenemedi: {str(e)}')
    
    def search_loans(self):
        """Client-side arama"""
        text = self.search_input.text().lower().strip()
        if not text:
            self.update_table_content(self.all_loans)
            return
            
        filtered = []
        for loan in self.all_loans:
            # Üye adı, kitap adı veya ID içinde ara
            uye = f"{loan.get('UyeAd', '')} {loan.get('UyeSoyad', '')}".lower()
            kitap = loan.get('KitapAdi', '').lower()
            
            if text in uye or text in kitap:
                filtered.append(loan)
        
        self.update_table_content(filtered)
    
    def refresh_data(self):
        self.load_active_loans()
        if self.dashboard:
            self.dashboard.load_statistics()
    
    def new_loan(self):
        """Yeni ödünç verme penceresi"""
        dialog = NewLoanDialog(self, self.user)
        if dialog.exec_() == QDialog.Accepted:
            if hasattr(dialog, 'success_message') and self.dashboard:
                self.dashboard.show_toast(dialog.success_message[0], dialog.success_message[1])
            self.load_active_loans()
            if self.dashboard:
                self.dashboard.refresh_statistics()

    def return_book(self):
        """Kitap teslim alma penceresi"""
        selected = self.table.currentRow()
        
        # --- CRASH FIX: Seçim kontrolü ---
        if selected <= 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen teslim alınacak işlemi seçin!')
            return
            
        odunc_id = int(self.table.item(selected, 0).text())
        uye_adi = self.table.item(selected, 1).text()
        kitap_adi = self.table.item(selected, 2).text()
        
        dialog = ReturnDialog(self, odunc_id, uye_adi, kitap_adi)
        if dialog.exec_() == QDialog.Accepted:
            if hasattr(dialog, 'success_message') and self.dashboard:
                self.dashboard.show_toast(dialog.success_message[0], dialog.success_message[1])
            self.load_active_loans()
            if self.dashboard:
                self.dashboard.refresh_statistics()


class NewLoanDialog(QDialog):
    """Yeni ödünç verme dialogu"""
    
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.members = []
        self.books = []
        self.success_message = None
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle('Yeni Ödünç Ver')
        # Soru işaretini kaldır
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(500)
        
        layout = QFormLayout()
        
        self.uye_combo = QComboBox()
        layout.addRow('Üye Seçin:', self.uye_combo)
        
        self.kitap_combo = QComboBox()
        layout.addRow('Kitap Seçin:', self.kitap_combo)
        
        info_label = QLabel('Not: Ödünç süresi 15 gündür. Gecikmede günlük 5 TL ceza uygulanır.')
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addRow(info_label)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Ödünç Ver')
        save_btn.clicked.connect(self.create_loan)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('İptal')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def load_data(self):
        try:
            self.members = Member.get_active_members()
            self.uye_combo.clear()
            self.uye_combo.addItem("Seçiniz...", None)
            for member in self.members:
                self.uye_combo.addItem(f"{member['Ad']} {member['Soyad']} ({member['Email']})", member['UyeID'])
            
            self.books = Book.get_available_books()
            self.kitap_combo.clear()
            self.kitap_combo.addItem("Seçiniz...", None)
            for book in self.books:
                self.kitap_combo.addItem(f"{book['KitapAdi']} - {book['Yazar']}", book['KitapID'])
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Veriler yüklenemedi: {str(e)}')
    
    def create_loan(self):
        uye_id = self.uye_combo.currentData()
        kitap_id = self.kitap_combo.currentData()
        
        if not uye_id or not kitap_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen üye ve kitap seçin!')
            return
        
        try:
            result = Loan.create_loan(uye_id, kitap_id, self.user.kullanici_id)
            if result:
                self.success_message = (f'Ödünç işlemi başarılı! (ID: {result})', 'success')
                self.accept()
            else:
                QMessageBox.warning(self, 'Uyarı', 'Ödünç işlemi gerçekleştirilemedi!')
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Ödünç verme hatası: {str(e)}')


class ReturnDialog(QDialog):
    """Kitap teslim alma dialogu (Eski ReturnWindow'dan taşındı)"""
    
    def __init__(self, parent, odunc_id, uye_adi, kitap_adi):
        super().__init__(parent)
        self.odunc_id = odunc_id
        self.uye_adi = uye_adi
        self.kitap_adi = kitap_adi
        self.success_message = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Kitap Teslim Al')
        # Soru işaretini kaldır
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        layout.addRow('Ödünç ID:', QLabel(str(self.odunc_id)))
        layout.addRow('Üye:', QLabel(self.uye_adi))
        layout.addRow('Kitap:', QLabel(self.kitap_adi))
        
        self.teslim_tarihi_input = QDateEdit()
        self.teslim_tarihi_input.setCalendarPopup(True)
        self.teslim_tarihi_input.setDate(QDate.currentDate())
        layout.addRow('Teslim Tarihi:', self.teslim_tarihi_input)
        
        info = QLabel('Not: Gecikme varsa otomatik ceza hesaplanır.')
        info.setStyleSheet("color: #666; font-style: italic;")
        layout.addRow(info)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Teslim Al')
        save_btn.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")
        save_btn.clicked.connect(self.process_return)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('İptal')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def process_return(self):
        teslim_tarihi = self.teslim_tarihi_input.date().toPyDate()
        
        # Standart QMessageBox yerine custom helper kullanılabilir ama burada hızlı çözüm için standart kullanıyoruz.
        # İstersen ask_yes_no_tr ile değiştirebilirsin.
        reply = QMessageBox.question(
            self,
            'Teslim Onayı',
            f'Kitabı teslim almak istediğinize emin misiniz?\nTeslim Tarihi: {teslim_tarihi}',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = Loan.return_loan(self.odunc_id, teslim_tarihi)
                if result:
                    self.success_message = ('Kitap teslim alındı!', 'success')
                    self.accept()
                else:
                    QMessageBox.warning(self, 'Uyarı', 'Teslim işlemi başarısız!')
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Hata: {str(e)}')