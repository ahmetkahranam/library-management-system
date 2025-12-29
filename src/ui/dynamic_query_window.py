"""
Dinamik Sorgu Ekrani - Kullanici Filtrelerine Gore SQL Olusturma
Kitap ve Üye arama için opsiyonel filtreler
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QHeaderView, QLineEdit, QComboBox,
                             QCheckBox, QSpinBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from src.database.db_manager import DatabaseManager


class DynamicQueryWindow(QWidget):
    """Dinamik sorgu ekrani - Kullanici filtreleriyle esnek arama"""
    
    def __init__(self, dashboard=None):
        super().__init__()
        self.dashboard = dashboard
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        """UI olustur"""
        # Ana container widget
        from PyQt5.QtWidgets import QScrollArea
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Baslik
        title = QLabel('DİNAMİK SORGU VE RAPORLAMA')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #3B4953;')
        layout.addWidget(title)
        
        # Sorgu Tipi Secimi
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel('Sorgu Tipi:'))
        
        self.query_type_combo = QComboBox()
        self.query_type_combo.addItems(['Kitap Sorgulama', 'Üye Sorgulama'])
        self.query_type_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 2px solid #4A90E2;
                border-radius: 4px;
                font-weight: bold;
                min-width: 200px;
            }
        """)
        self.query_type_combo.currentIndexChanged.connect(self.on_query_type_changed)
        type_layout.addWidget(self.query_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # Aciklama
        self.desc_label = QLabel('İstediğiniz kriterleri seçerek kitapları arayın. Boş bırakılan alanlar sorguya dahil edilmez.')
        self.desc_label.setStyleSheet('font-size: 12px; color: #666; margin-bottom: 10px;')
        layout.addWidget(self.desc_label)
        
        # Filtre Grubu - Scrollable
        from PyQt5.QtWidgets import QScrollArea
        
        self.filter_group = QGroupBox('Arama Kriterleri')
        self.filter_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        self.filter_layout = QGridLayout()
        self.filter_layout.setSpacing(10)
        
        # Kitap filtreleri (varsayilan)
        self.create_book_filters()
        
        self.filter_group.setLayout(self.filter_layout)
        
        # Scroll Area ekle
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.filter_group)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        scroll_area.setMaximumHeight(500)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        layout.addWidget(scroll_area)
        
        # Buton Satiri - Daha belirgin
        button_container = QWidget()
        button_container.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0px;
            }
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 10, 10, 10)
        
        self.search_btn = QPushButton('🔍 SORGULA')
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 40px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
        """)
        self.search_btn.clicked.connect(self.execute_dynamic_query)
        button_layout.addWidget(self.search_btn)
        
        self.clear_btn = QPushButton('🗑️ TEMİZLE')
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 40px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_filters)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        layout.addWidget(button_container)
        
        # Sonuc Ozeti
        self.result_label = QLabel('Arama sonuçları burada görüntülenecek')
        self.result_label.setStyleSheet("""
            font-size: 13px; 
            padding: 10px; 
            background-color: #f8f9fa; 
            border: 1px solid #ddd; 
            border-radius: 5px;
        """)
        layout.addWidget(self.result_label)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(400)
        self.table.setMaximumHeight(700)  # Maksimum yukseklik artırıldı
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # Ana scroll area (tum sayfa icin)
        main_scroll = QScrollArea()
        main_scroll.setWidget(container)
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(main_scroll)
        
        # Kategorileri yukle
        self.load_categories()
    
    def create_book_filters(self):
        """Kitap arama filtreleri olustur"""
        from PyQt5.QtWidgets import QDateEdit
        from PyQt5.QtCore import QDate
        
        # Onceki widget'lari temizle
        self.clear_layout(self.filter_layout)
        
        # Kitap Adi
        self.filter_layout.addWidget(QLabel('Kitap Adı:'), 0, 0)
        self.book_name_input = QLineEdit()
        self.book_name_input.setPlaceholderText('Kitap adında geçen kelime...')
        self.book_name_input.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.filter_layout.addWidget(self.book_name_input, 0, 1)
        
        # Yazar
        self.filter_layout.addWidget(QLabel('Yazar:'), 0, 2)
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText('Yazar adı...')
        self.author_input.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.filter_layout.addWidget(self.author_input, 0, 3)
        
        # Kategori
        self.filter_layout.addWidget(QLabel('Kategori:'), 1, 0)
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px; min-width: 200px;')
        self.filter_layout.addWidget(self.category_combo, 1, 1)
        
        # Yayinevi
        self.filter_layout.addWidget(QLabel('Yayınevi:'), 1, 2)
        self.publisher_input = QLineEdit()
        self.publisher_input.setPlaceholderText('Yayınevi adı...')
        self.publisher_input.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.filter_layout.addWidget(self.publisher_input, 1, 3)
        
        # Basim Yili - Minimum
        self.filter_layout.addWidget(QLabel('Basım Yılı (Min):'), 2, 0)
        self.year_min_spin = QSpinBox()
        self.year_min_spin.setRange(1900, 2100)
        self.year_min_spin.setValue(1900)
        self.year_min_spin.setSpecialValueText('Seçilmedi')
        self.year_min_spin.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.filter_layout.addWidget(self.year_min_spin, 2, 1)
        
        # Basim Yili - Maksimum
        self.filter_layout.addWidget(QLabel('Basım Yılı (Max):'), 2, 2)
        self.year_max_spin = QSpinBox()
        self.year_max_spin.setRange(1900, 2100)
        self.year_max_spin.setValue(2100)
        self.year_max_spin.setSpecialValueText('Seçilmedi')
        self.year_max_spin.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.filter_layout.addWidget(self.year_max_spin, 2, 3)
        
        # Sadece Mevcut Kitaplar
        self.available_only_check = QCheckBox('Sadece Mevcut Kitaplar (Stokta Olanlar)')
        self.available_only_check.setStyleSheet('font-weight: normal; padding: 5px;')
        self.filter_layout.addWidget(self.available_only_check, 3, 0, 1, 2)
        
        # Siralama
        self.filter_layout.addWidget(QLabel('Sıralama:'), 3, 2)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            'Kitap Adı (A-Z)',
            'Kitap Adı (Z-A)',
            'Yazar (A-Z)',
            'Yazar (Z-A)',
            'Basım Yılı (Artan)',
            'Basım Yılı (Azalan)'
        ])
        self.sort_combo.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px; min-width: 180px;')
        self.filter_layout.addWidget(self.sort_combo, 3, 3)
        
        # === ODUNC FILTRELERI ===
        odunc_label = QLabel('--- ÖDÜNÇ DETAYLARI ---')
        odunc_label.setStyleSheet('font-weight: bold; color: #3B4953; margin-top: 10px;')
        self.filter_layout.addWidget(odunc_label, 4, 0, 1, 4)
        
        # Odunc Durumu
        self.filter_layout.addWidget(QLabel('Ödünç Durumu:'), 5, 0)
        self.loan_status_combo = QComboBox()
        self.loan_status_combo.addItems(['Tümü', 'Ödünç Verildi', 'Hiç Ödünç Verilmedi'])
        self.loan_status_combo.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px; min-width: 180px;')
        self.loan_status_combo.currentIndexChanged.connect(self.on_loan_status_changed)
        self.filter_layout.addWidget(self.loan_status_combo, 5, 1)
        
        # Odunc Tarihi Baslangic
        self.filter_layout.addWidget(QLabel('Ödünç Tarihi (Başlangıç):'), 5, 2)
        self.loan_date_start = QDateEdit()
        self.loan_date_start.setDate(QDate.currentDate().addMonths(-12))
        self.loan_date_start.setCalendarPopup(True)
        self.loan_date_start.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.loan_date_start.setEnabled(False)
        self.filter_layout.addWidget(self.loan_date_start, 5, 3)
        
        # Odunc Tarihi Bitis
        self.filter_layout.addWidget(QLabel('Ödünç Tarihi (Bitiş):'), 6, 0)
        self.loan_date_end = QDateEdit()
        self.loan_date_end.setDate(QDate.currentDate())
        self.loan_date_end.setCalendarPopup(True)
        self.loan_date_end.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.loan_date_end.setEnabled(False)
        self.filter_layout.addWidget(self.loan_date_end, 6, 1)
        
        # Teslim Durumu
        self.filter_layout.addWidget(QLabel('Teslim Durumu:'), 6, 2)
        self.return_status_combo = QComboBox()
        self.return_status_combo.addItems(['Tümü', 'Teslim Edildi', 'Teslim Edilmedi'])
        self.return_status_combo.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px; min-width: 160px;')
        self.return_status_combo.setEnabled(False)
        self.return_status_combo.currentIndexChanged.connect(self.on_return_status_changed)
        self.filter_layout.addWidget(self.return_status_combo, 6, 3)
        
        # Gecikme Durumu
        self.filter_layout.addWidget(QLabel('Gecikme Durumu:'), 7, 0)
        self.delay_status_combo = QComboBox()
        self.delay_status_combo.addItems(['Tümü', 'Gecikmiş', 'Gecikmemiş'])
        self.delay_status_combo.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px; min-width: 150px;')
        self.delay_status_combo.setEnabled(False)
        self.delay_status_combo.currentIndexChanged.connect(self.on_delay_status_changed)
        self.filter_layout.addWidget(self.delay_status_combo, 7, 1)
        
        # Gecikme Suresi Min
        self.filter_layout.addWidget(QLabel('Gecikme Süresi (Min Gün):'), 7, 2)
        self.delay_min_spin = QSpinBox()
        self.delay_min_spin.setRange(0, 1000)
        self.delay_min_spin.setValue(0)
        self.delay_min_spin.setSpecialValueText('Seçilmedi')
        self.delay_min_spin.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.delay_min_spin.setEnabled(False)
        self.filter_layout.addWidget(self.delay_min_spin, 7, 3)
        
        # Gecikme Suresi Max
        self.filter_layout.addWidget(QLabel('Gecikme Süresi (Max Gün):'), 8, 0)
        self.delay_max_spin = QSpinBox()
        self.delay_max_spin.setRange(0, 1000)
        self.delay_max_spin.setValue(1000)
        self.delay_max_spin.setSpecialValueText('Seçilmedi')
        self.delay_max_spin.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.delay_max_spin.setEnabled(False)
        self.filter_layout.addWidget(self.delay_max_spin, 8, 1)
        
        self.load_categories()
    
    def on_loan_status_changed(self):
        """Odunc durumu degistiginde alt filtreleri aktif/pasif yap"""
        is_loaned = self.loan_status_combo.currentIndex() == 1  # Odunc Verildi
        
        self.loan_date_start.setEnabled(is_loaned)
        self.loan_date_end.setEnabled(is_loaned)
        self.return_status_combo.setEnabled(is_loaned)
        
        if not is_loaned:
            self.return_status_combo.setCurrentIndex(0)
            self.delay_status_combo.setEnabled(False)
            self.delay_status_combo.setCurrentIndex(0)
            self.delay_min_spin.setEnabled(False)
            self.delay_max_spin.setEnabled(False)
        else:
            # Odunc verildi secildiyse, teslim durumuna gore gecikme aktif olsun
            self.on_return_status_changed()
    
    def on_return_status_changed(self):
        """Teslim durumu degistiginde gecikme filtrelerini aktif/pasif yap"""
        return_status = self.return_status_combo.currentIndex()
        # Teslim Edildi (1) veya Teslim Edilmedi (2) secildiyse gecikme durumu aktif
        has_return_filter = return_status > 0
        
        self.delay_status_combo.setEnabled(has_return_filter)
        if not has_return_filter:
            self.delay_status_combo.setCurrentIndex(0)
            self.delay_min_spin.setEnabled(False)
            self.delay_max_spin.setEnabled(False)
        else:
            # Teslim durumu secildiyse, gecikme durumuna gore min/max aktif olsun
            self.on_delay_status_changed()
    
    def on_delay_status_changed(self):
        """Gecikme durumu degistiginde min/max filtreleri aktif/pasif yap"""
        is_delayed = self.delay_status_combo.currentIndex() == 1  # Gecikmiş
        
        self.delay_min_spin.setEnabled(is_delayed)
        self.delay_max_spin.setEnabled(is_delayed)
    
    def create_member_filters(self):
        """Uye arama filtreleri olustur"""
        from PyQt5.QtWidgets import QDateEdit
        from PyQt5.QtCore import QDate
        
        # Onceki widget'lari temizle
        self.clear_layout(self.filter_layout)
        
        # Ad
        self.filter_layout.addWidget(QLabel('Ad:'), 0, 0)
        self.member_name_input = QLineEdit()
        self.member_name_input.setPlaceholderText('Üye adı...')
        self.member_name_input.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.filter_layout.addWidget(self.member_name_input, 0, 1)
        
        # Soyad
        self.filter_layout.addWidget(QLabel('Soyad:'), 0, 2)
        self.member_surname_input = QLineEdit()
        self.member_surname_input.setPlaceholderText('Üye soyadı...')
        self.member_surname_input.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.filter_layout.addWidget(self.member_surname_input, 0, 3)
        
        # Email
        self.filter_layout.addWidget(QLabel('Email:'), 1, 0)
        self.member_email_input = QLineEdit()
        self.member_email_input.setPlaceholderText('Email adresi...')
        self.member_email_input.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.filter_layout.addWidget(self.member_email_input, 1, 1)
        
        # Telefon
        self.filter_layout.addWidget(QLabel('Telefon:'), 1, 2)
        self.member_phone_input = QLineEdit()
        self.member_phone_input.setPlaceholderText('Telefon numarası...')
        self.member_phone_input.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.filter_layout.addWidget(self.member_phone_input, 1, 3)
        
        # Borcu Olanlar
        self.debt_only_check = QCheckBox('Sadece Borcu Olan Üyeler')
        self.debt_only_check.setStyleSheet('font-weight: normal; padding: 5px;')
        self.filter_layout.addWidget(self.debt_only_check, 2, 0, 1, 2)
        
        # Siralama
        self.filter_layout.addWidget(QLabel('Sıralama:'), 2, 2)
        self.member_sort_combo = QComboBox()
        self.member_sort_combo.addItems([
            'Ad (A-Z)',
            'Ad (Z-A)',
            'Soyad (A-Z)',
            'Soyad (Z-A)',
            'Borç (Artan)',
            'Borç (Azalan)'
        ])
        self.member_sort_combo.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px; min-width: 150px;')
        self.filter_layout.addWidget(self.member_sort_combo, 2, 3)
        
        # === ODUNC FILTRELERI ===
        odunc_label = QLabel('--- ÖDÜNÇ DETAYLARI ---')
        odunc_label.setStyleSheet('font-weight: bold; color: #3B4953; margin-top: 10px;')
        self.filter_layout.addWidget(odunc_label, 3, 0, 1, 4)
        
        # Odunc Aldı mı
        self.filter_layout.addWidget(QLabel('Ödünç Durumu:'), 4, 0)
        self.member_loan_status_combo = QComboBox()
        self.member_loan_status_combo.addItems(['Tümü', 'Ödünç Aldı', 'Hiç Ödünç Almadı'])
        self.member_loan_status_combo.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px; min-width: 180px;')
        self.member_loan_status_combo.currentIndexChanged.connect(self.on_member_loan_status_changed)
        self.filter_layout.addWidget(self.member_loan_status_combo, 4, 1)
        
        # Odunc Tarihi Baslangic
        self.filter_layout.addWidget(QLabel('Ödünç Tarihi (Başlangıç):'), 4, 2)
        self.member_loan_date_start = QDateEdit()
        self.member_loan_date_start.setDate(QDate.currentDate().addMonths(-12))
        self.member_loan_date_start.setCalendarPopup(True)
        self.member_loan_date_start.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.member_loan_date_start.setEnabled(False)
        self.filter_layout.addWidget(self.member_loan_date_start, 4, 3)
        
        # Odunc Tarihi Bitis
        self.filter_layout.addWidget(QLabel('Ödünç Tarihi (Bitiş):'), 5, 0)
        self.member_loan_date_end = QDateEdit()
        self.member_loan_date_end.setDate(QDate.currentDate())
        self.member_loan_date_end.setCalendarPopup(True)
        self.member_loan_date_end.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.member_loan_date_end.setEnabled(False)
        self.filter_layout.addWidget(self.member_loan_date_end, 5, 1)
        
        # Teslim Durumu
        self.filter_layout.addWidget(QLabel('Teslim Durumu:'), 5, 2)
        self.member_return_status_combo = QComboBox()
        self.member_return_status_combo.addItems(['Tümü', 'Teslim Etti', 'Teslim Etmedi'])
        self.member_return_status_combo.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px; min-width: 160px;')
        self.member_return_status_combo.setEnabled(False)
        self.member_return_status_combo.currentIndexChanged.connect(self.on_member_return_status_changed)
        self.filter_layout.addWidget(self.member_return_status_combo, 5, 3)
        
        # Gecikme Durumu
        self.filter_layout.addWidget(QLabel('Gecikme Durumu:'), 6, 0)
        self.member_delay_status_combo = QComboBox()
        self.member_delay_status_combo.addItems(['Tümü', 'Gecikmiş', 'Gecikmemiş'])
        self.member_delay_status_combo.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px; min-width: 150px;')
        self.member_delay_status_combo.setEnabled(False)
        self.member_delay_status_combo.currentIndexChanged.connect(self.on_member_delay_status_changed)
        self.filter_layout.addWidget(self.member_delay_status_combo, 6, 1)
        
        # Gecikme Suresi Min
        self.filter_layout.addWidget(QLabel('Gecikme Süresi (Min Gün):'), 6, 2)
        self.member_delay_min_spin = QSpinBox()
        self.member_delay_min_spin.setRange(0, 1000)
        self.member_delay_min_spin.setValue(0)
        self.member_delay_min_spin.setSpecialValueText('Seçilmedi')
        self.member_delay_min_spin.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.member_delay_min_spin.setEnabled(False)
        self.filter_layout.addWidget(self.member_delay_min_spin, 6, 3)
        
        # Gecikme Suresi Max
        self.filter_layout.addWidget(QLabel('Gecikme Süresi (Max Gün):'), 7, 0)
        self.member_delay_max_spin = QSpinBox()
        self.member_delay_max_spin.setRange(0, 1000)
        self.member_delay_max_spin.setValue(1000)
        self.member_delay_max_spin.setSpecialValueText('Seçilmedi')
        self.member_delay_max_spin.setStyleSheet('padding: 5px; border: 1px solid #ddd; border-radius: 4px;')
        self.member_delay_max_spin.setEnabled(False)
        self.filter_layout.addWidget(self.member_delay_max_spin, 7, 1)
    
    def on_member_loan_status_changed(self):
        """Uye odunc durumu degistiginde alt filtreleri aktif/pasif yap"""
        has_loan = self.member_loan_status_combo.currentIndex() == 1  # Odunc Aldı
        
        self.member_loan_date_start.setEnabled(has_loan)
        self.member_loan_date_end.setEnabled(has_loan)
        self.member_return_status_combo.setEnabled(has_loan)
        
        if not has_loan:
            self.member_return_status_combo.setCurrentIndex(0)
            self.member_delay_status_combo.setEnabled(False)
            self.member_delay_status_combo.setCurrentIndex(0)
            self.member_delay_min_spin.setEnabled(False)
            self.member_delay_max_spin.setEnabled(False)
        else:
            # Odunc aldi secildiyse, teslim durumuna gore gecikme aktif olsun
            self.on_member_return_status_changed()
    
    def on_member_return_status_changed(self):
        """Uye teslim durumu degistiginde gecikme filtrelerini aktif/pasif yap"""
        return_status = self.member_return_status_combo.currentIndex()
        # Teslim Etti (1) veya Teslim Etmedi (2) secildiyse gecikme durumu aktif
        has_return_filter = return_status > 0
        
        self.member_delay_status_combo.setEnabled(has_return_filter)
        if not has_return_filter:
            self.member_delay_status_combo.setCurrentIndex(0)
            self.member_delay_min_spin.setEnabled(False)
            self.member_delay_max_spin.setEnabled(False)
        else:
            # Teslim durumu secildiyse, gecikme durumuna gore min/max aktif olsun
            self.on_member_delay_status_changed()
    
    def on_member_delay_status_changed(self):
        """Uye gecikme durumu degistiginde min/max filtreleri aktif/pasif yap"""
        is_delayed = self.member_delay_status_combo.currentIndex() == 1  # Gecikmiş
        
        self.member_delay_min_spin.setEnabled(is_delayed)
        self.member_delay_max_spin.setEnabled(is_delayed)
    
    def clear_layout(self, layout):
        """Layout icindeki tum widget'lari temizle"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def on_query_type_changed(self):
        """Sorgu tipi degistiginde filtreleri guncelle"""
        query_type = self.query_type_combo.currentIndex()
        
        if query_type == 0:  # Kitap
            self.desc_label.setText('İstediğiniz kriterleri seçerek kitapları arayın. Boş bırakılan alanlar sorguya dahil edilmez.')
            self.create_book_filters()
        else:  # Uye
            self.desc_label.setText('İstediğiniz kriterleri seçerek üyeleri arayın. Boş bırakılan alanlar sorguya dahil edilmez.')
            self.create_member_filters()
        
        # Tabloyu temizle
        self.table.setRowCount(0)
        self.result_label.setText('Arama sonuçları burada görüntülenecek')
    
    def load_categories(self):
        """Kategori combobox'ini doldur"""
        try:
            query = "SELECT KategoriID, KategoriAdi FROM KATEGORI ORDER BY KategoriAdi"
            categories = self.db.execute_query(query)
            
            self.category_combo.clear()
            self.category_combo.addItem('-- Tümü --', None)
            
            for cat in categories:
                self.category_combo.addItem(cat['KategoriAdi'], cat['KategoriID'])
                
        except Exception as e:
            print(f"Kategori yükleme hatası: {e}")
    
    def clear_filters(self):
        """Tum filtreleri temizle"""
        from PyQt5.QtCore import QDate
        
        query_type = self.query_type_combo.currentIndex()
        
        if query_type == 0:  # Kitap
            if hasattr(self, 'book_name_input'):
                self.book_name_input.clear()
                self.author_input.clear()
                self.publisher_input.clear()
                self.category_combo.setCurrentIndex(0)
                self.year_min_spin.setValue(1900)
                self.year_max_spin.setValue(2100)
                self.available_only_check.setChecked(False)
                self.sort_combo.setCurrentIndex(0)
                
                # Odunc filtreleri
                self.loan_status_combo.setCurrentIndex(0)
                self.loan_date_start.setDate(QDate.currentDate().addMonths(-12))
                self.loan_date_end.setDate(QDate.currentDate())
                self.return_status_combo.setCurrentIndex(0)
                self.delay_status_combo.setCurrentIndex(0)
                self.delay_min_spin.setValue(0)
                self.delay_max_spin.setValue(1000)
        else:  # Uye
            if hasattr(self, 'member_name_input'):
                self.member_name_input.clear()
                self.member_surname_input.clear()
                self.member_email_input.clear()
                self.member_phone_input.clear()
                self.debt_only_check.setChecked(False)
                self.member_sort_combo.setCurrentIndex(0)
                
                # Odunc filtreleri
                self.member_loan_status_combo.setCurrentIndex(0)
                self.member_loan_date_start.setDate(QDate.currentDate().addMonths(-12))
                self.member_loan_date_end.setDate(QDate.currentDate())
                self.member_return_status_combo.setCurrentIndex(0)
                self.member_delay_status_combo.setCurrentIndex(0)
                self.member_delay_min_spin.setValue(0)
                self.member_delay_max_spin.setValue(1000)
        
        # Tabloyu temizle
        self.table.setRowCount(0)
        self.result_label.setText('Arama sonuçları burada görüntülenecek')
    
    def execute_dynamic_query(self):
        """Dinamik sorguyu olustur ve calistir"""
        query_type = self.query_type_combo.currentIndex()
        
        if query_type == 0:
            self.execute_book_query()
        else:
            self.execute_member_query()
    
    def execute_book_query(self):
        """Kitap sorgusunu calistir"""
        try:
            # Odunc filtreleri aktif mi kontrol et
            loan_status = self.loan_status_combo.currentIndex()
            has_loan_filter = loan_status > 0
            
            if has_loan_filter:
                # Odunc bilgisi ile detayli sorgu
                query = """
                    SELECT 
                        k.KitapID,
                        k.KitapAdi,
                        k.Yazar,
                        k.Yayinevi,
                        k.BasimYili,
                        kat.KategoriAdi,
                        k.ToplamAdet,
                        k.MevcutAdet,
                        o.OduncID,
                        o.OduncTarihi,
                        o.TeslimTarihi,
                        o.SonTeslimTarihi,
                        CONCAT(u.Ad, ' ', u.Soyad) AS UyeAdi,
                        CASE 
                            WHEN o.TeslimTarihi IS NULL AND CURDATE() > o.SonTeslimTarihi 
                            THEN DATEDIFF(CURDATE(), o.SonTeslimTarihi)
                            WHEN o.TeslimTarihi IS NOT NULL AND o.TeslimTarihi > o.SonTeslimTarihi
                            THEN DATEDIFF(o.TeslimTarihi, o.SonTeslimTarihi)
                            ELSE 0
                        END AS GecikmeSuresi
                    FROM KITAP k
                    LEFT JOIN KATEGORI kat ON k.KategoriID = kat.KategoriID
                    INNER JOIN ODUNC o ON k.KitapID = o.KitapID
                    INNER JOIN UYE u ON o.UyeID = u.UyeID
                    WHERE 1=1
                """
            else:
                # Sadece kitap bilgisi
                query = """
                    SELECT 
                        k.KitapID,
                        k.KitapAdi,
                        k.Yazar,
                        k.Yayinevi,
                        k.BasimYili,
                        kat.KategoriAdi,
                        k.ToplamAdet,
                        k.MevcutAdet
                    FROM KITAP k
                    LEFT JOIN KATEGORI kat ON k.KategoriID = kat.KategoriID
                    WHERE 1=1
                """
            
            params = []
            conditions = []
            
            # Kitap Adi filtresi
            book_name = self.book_name_input.text().strip()
            if book_name:
                conditions.append("k.KitapAdi LIKE %s")
                params.append(f"%{book_name}%")
            
            # Yazar filtresi
            author = self.author_input.text().strip()
            if author:
                conditions.append("k.Yazar LIKE %s")
                params.append(f"%{author}%")
            
            # Yayinevi filtresi
            publisher = self.publisher_input.text().strip()
            if publisher:
                conditions.append("k.Yayinevi LIKE %s")
                params.append(f"%{publisher}%")
            
            # Kategori filtresi
            category_id = self.category_combo.currentData()
            if category_id is not None:
                conditions.append("k.KategoriID = %s")
                params.append(category_id)
            
            # Basim Yili - Minimum
            year_min = self.year_min_spin.value()
            if year_min > 1900:
                conditions.append("k.BasimYili >= %s")
                params.append(year_min)
            
            # Basim Yili - Maksimum
            year_max = self.year_max_spin.value()
            if year_max < 2100:
                conditions.append("k.BasimYili <= %s")
                params.append(year_max)
            
            # Sadece Mevcut Kitaplar
            if self.available_only_check.isChecked():
                conditions.append("k.MevcutAdet > 0")
            
            # Odunc Tarihi Filtresi
            if has_loan_filter:
                loan_date_start = self.loan_date_start.date().toString('yyyy-MM-dd')
                loan_date_end = self.loan_date_end.date().toString('yyyy-MM-dd')
                conditions.append("o.OduncTarihi BETWEEN %s AND %s")
                params.extend([loan_date_start, loan_date_end])
                
                # Teslim Durumu
                return_status = self.return_status_combo.currentIndex()
                if return_status == 1:  # Teslim Edildi
                    conditions.append("o.TeslimTarihi IS NOT NULL")
                elif return_status == 2:  # Teslim Edilmedi
                    conditions.append("o.TeslimTarihi IS NULL")
                    
                    # Gecikme Durumu
                    delay_status = self.delay_status_combo.currentIndex()
                    if delay_status == 1:  # Gecikmiş
                        conditions.append("CURDATE() > o.SonTeslimTarihi")
                        
                        # Gecikme Suresi
                        delay_min = self.delay_min_spin.value()
                        if delay_min > 0:
                            conditions.append("DATEDIFF(CURDATE(), o.SonTeslimTarihi) >= %s")
                            params.append(delay_min)
                        
                        delay_max = self.delay_max_spin.value()
                        if delay_max < 1000:
                            conditions.append("DATEDIFF(CURDATE(), o.SonTeslimTarihi) <= %s")
                            params.append(delay_max)
                    
                    elif delay_status == 2:  # Gecikmemiş
                        conditions.append("CURDATE() <= o.SonTeslimTarihi")
            
            # WHERE kosullarini ekle
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            # Siralama ekle
            sort_index = self.sort_combo.currentIndex()
            if sort_index == 0:
                query += " ORDER BY k.KitapAdi ASC"
            elif sort_index == 1:
                query += " ORDER BY k.KitapAdi DESC"
            elif sort_index == 2:
                query += " ORDER BY k.Yazar ASC"
            elif sort_index == 3:
                query += " ORDER BY k.Yazar DESC"
            elif sort_index == 4:
                query += " ORDER BY k.BasimYili ASC"
            elif sort_index == 5:
                query += " ORDER BY k.BasimYili DESC"
            
            # Sorguyu calistir
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, tuple(params))
                books = cursor.fetchall()
                cursor.close()
            
            # Sonuclari goster
            if has_loan_filter:
                self.populate_book_loan_table(books)
            else:
                self.populate_book_table(books)
            
            # Ozet bilgi
            total_books = len(books)
            if has_loan_filter:
                delayed = sum(1 for b in books if b.get('GecikmeSuresi', 0) > 0 and b.get('TeslimTarihi') is None)
                returned = sum(1 for b in books if b.get('TeslimTarihi') is not None)
                
                self.result_label.setText(
                    f"<b>Toplam Sonuç:</b> {total_books} ödünç kaydı | "
                    f"<b>Teslim Edildi:</b> {returned} | "
                    f"<b>Gecikmiş:</b> {delayed}"
                )
            else:
                available_count = sum(1 for b in books if b['MevcutAdet'] > 0)
                
                self.result_label.setText(
                    f"<b>Toplam Sonuç:</b> {total_books} kitap | "
                    f"<b>Mevcut:</b> {available_count} | "
                    f"<b>Stokta Olmayan:</b> {total_books - available_count}"
                )
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Kitap sorgusu çalıştırılırken hata oluştu:\n{str(e)}')
            import traceback
            print(traceback.format_exc())
    
    def execute_member_query(self):
        """Uye sorgusunu calistir"""
        try:
            # Odunc filtreleri aktif mi kontrol et
            loan_status = self.member_loan_status_combo.currentIndex()
            has_loan_filter = loan_status > 0
            
            if has_loan_filter:
                # Odunc bilgisi ile detayli sorgu
                query = """
                    SELECT 
                        u.UyeID,
                        u.Ad,
                        u.Soyad,
                        u.Email,
                        u.Telefon,
                        u.ToplamBorc,
                        o.OduncID,
                        o.OduncTarihi,
                        o.TeslimTarihi,
                        o.SonTeslimTarihi,
                        k.KitapAdi,
                        CASE 
                            WHEN o.TeslimTarihi IS NULL AND CURDATE() > o.SonTeslimTarihi 
                            THEN DATEDIFF(CURDATE(), o.SonTeslimTarihi)
                            WHEN o.TeslimTarihi IS NOT NULL AND o.TeslimTarihi > o.SonTeslimTarihi
                            THEN DATEDIFF(o.TeslimTarihi, o.SonTeslimTarihi)
                            ELSE 0
                        END AS GecikmeSuresi
                    FROM UYE u
                    INNER JOIN ODUNC o ON u.UyeID = o.UyeID
                    INNER JOIN KITAP k ON o.KitapID = k.KitapID
                    WHERE 1=1
                """
            else:
                # Sadece uye bilgisi
                query = """
                    SELECT 
                        u.UyeID,
                        u.Ad,
                        u.Soyad,
                        u.Email,
                        u.Telefon,
                        u.ToplamBorc,
                        COUNT(DISTINCT o.OduncID) AS ToplamOdunc,
                        COUNT(DISTINCT CASE WHEN o.TeslimTarihi IS NULL THEN o.OduncID END) AS AktifOdunc
                    FROM UYE u
                    LEFT JOIN ODUNC o ON u.UyeID = o.UyeID
                    WHERE 1=1
                """
            
            params = []
            conditions = []
            
            # Ad filtresi
            name = self.member_name_input.text().strip()
            if name:
                conditions.append("u.Ad LIKE %s")
                params.append(f"%{name}%")
            
            # Soyad filtresi
            surname = self.member_surname_input.text().strip()
            if surname:
                conditions.append("u.Soyad LIKE %s")
                params.append(f"%{surname}%")
            
            # Email filtresi
            email = self.member_email_input.text().strip()
            if email:
                conditions.append("u.Email LIKE %s")
                params.append(f"%{email}%")
            
            # Telefon filtresi
            phone = self.member_phone_input.text().strip()
            if phone:
                conditions.append("u.Telefon LIKE %s")
                params.append(f"%{phone}%")
            
            # Odunc Tarihi Filtresi
            if has_loan_filter:
                loan_date_start = self.member_loan_date_start.date().toString('yyyy-MM-dd')
                loan_date_end = self.member_loan_date_end.date().toString('yyyy-MM-dd')
                conditions.append("o.OduncTarihi BETWEEN %s AND %s")
                params.extend([loan_date_start, loan_date_end])
                
                # Teslim Durumu
                return_status = self.member_return_status_combo.currentIndex()
                if return_status == 1:  # Teslim Etti
                    conditions.append("o.TeslimTarihi IS NOT NULL")
                elif return_status == 2:  # Teslim Etmedi
                    conditions.append("o.TeslimTarihi IS NULL")
                    
                    # Gecikme Durumu
                    delay_status = self.member_delay_status_combo.currentIndex()
                    if delay_status == 1:  # Gecikmiş
                        conditions.append("CURDATE() > o.SonTeslimTarihi")
                        
                        # Gecikme Suresi
                        delay_min = self.member_delay_min_spin.value()
                        if delay_min > 0:
                            conditions.append("DATEDIFF(CURDATE(), o.SonTeslimTarihi) >= %s")
                            params.append(delay_min)
                        
                        delay_max = self.member_delay_max_spin.value()
                        if delay_max < 1000:
                            conditions.append("DATEDIFF(CURDATE(), o.SonTeslimTarihi) <= %s")
                            params.append(delay_max)
                    
                    elif delay_status == 2:  # Gecikmemiş
                        conditions.append("CURDATE() <= o.SonTeslimTarihi")
            
            # WHERE kosullarini ekle
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            # GROUP BY (sadece basit sorgu icin)
            if not has_loan_filter:
                query += " GROUP BY u.UyeID"
                
                # Sadece Borcu Olanlar
                if self.debt_only_check.isChecked():
                    query += " HAVING u.ToplamBorc > 0"
            
            # Siralama ekle
            sort_index = self.member_sort_combo.currentIndex()
            if sort_index == 0:
                query += " ORDER BY u.Ad ASC"
            elif sort_index == 1:
                query += " ORDER BY u.Ad DESC"
            elif sort_index == 2:
                query += " ORDER BY u.Soyad ASC"
            elif sort_index == 3:
                query += " ORDER BY u.Soyad DESC"
            elif sort_index == 4:
                query += " ORDER BY u.ToplamBorc ASC"
            elif sort_index == 5:
                query += " ORDER BY u.ToplamBorc DESC"
            
            # Sorguyu calistir
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, tuple(params))
                members = cursor.fetchall()
                cursor.close()
            
            # Sonuclari goster
            if has_loan_filter:
                self.populate_member_loan_table(members)
            else:
                self.populate_member_table(members)
            
            # Ozet bilgi
            total_members = len(members)
            if has_loan_filter:
                delayed = sum(1 for m in members if m.get('GecikmeSuresi', 0) > 0 and m.get('TeslimTarihi') is None)
                returned = sum(1 for m in members if m.get('TeslimTarihi') is not None)
                
                self.result_label.setText(
                    f"<b>Toplam Sonuç:</b> {total_members} ödünç kaydı | "
                    f"<b>Teslim Edildi:</b> {returned} | "
                    f"<b>Gecikmiş:</b> {delayed}"
                )
            else:
                debt_count = sum(1 for m in members if m['ToplamBorc'] > 0)
                total_debt = sum(m['ToplamBorc'] for m in members)
                
                self.result_label.setText(
                    f"<b>Toplam Sonuç:</b> {total_members} üye | "
                    f"<b>Borcu Olan:</b> {debt_count} | "
                    f"<b>Toplam Borç:</b> {total_debt:.2f} TL"
                )
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Üye sorgusu çalıştırılırken hata oluştu:\n{str(e)}')
            import traceback
            print(traceback.format_exc())
    
    def populate_book_table(self, books):
        """Kitap tablosunu doldur"""
        # Tablo boyutunu ayarla
        self.table.setRowCount(len(books) + 1)
        self.table.setColumnCount(8)
        
        # Baslik satiri
        headers = ['ID', 'Kitap Adı', 'Yazar', 'Yayınevi', 'Basım Yılı', 'Kategori', 'Toplam', 'Mevcut']
        
        for col, header in enumerate(headers):
            header_item = QTableWidgetItem(header)
            header_item.setFont(QFont('Arial', 10, QFont.Bold))
            header_item.setForeground(QColor('white'))
            header_item.setBackground(QColor('#1A4D70'))
            header_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, col, header_item)
        
        # Veri satirlari
        for row_idx, book in enumerate(books, start=1):
            # ID
            item = QTableWidgetItem(str(book['KitapID']))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, item)
            
            # Kitap Adi
            item = QTableWidgetItem(book['KitapAdi'])
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 1, item)
            
            # Yazar
            item = QTableWidgetItem(book['Yazar'])
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 2, item)
            
            # Yayinevi
            item = QTableWidgetItem(book.get('Yayinevi', '-'))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 3, item)
            
            # Basim Yili
            item = QTableWidgetItem(str(book.get('BasimYili', '-')))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 4, item)
            
            # Kategori
            item = QTableWidgetItem(book.get('KategoriAdi', '-') or '-')
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 5, item)
            
            # Toplam Adet
            item = QTableWidgetItem(str(book['ToplamAdet']))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 6, item)
            
            # Mevcut Adet
            mevcut = book['MevcutAdet']
            item = QTableWidgetItem(str(mevcut))
            item.setTextAlignment(Qt.AlignCenter)
            
            # Stok durumuna gore renklendirme
            if mevcut == 0:
                item.setBackground(QColor('#ffebee'))  # Kirmizi - Stokta yok
            elif mevcut <= 2:
                item.setBackground(QColor('#fff3e0'))  # Turuncu - Az stok
            else:
                item.setBackground(QColor('#e8f5e9'))  # Yesil - Yeterli stok
            
            self.table.setItem(row_idx, 7, item)
        
        # Sutun genisliklerini ayarla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Kitap
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Yazar
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Yayinevi
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Yil
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Kategori
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Toplam
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Mevcut
    
    def populate_member_table(self, members):
        """Uye tablosunu doldur"""
        # Tablo boyutunu ayarla
        self.table.setRowCount(len(members) + 1)
        self.table.setColumnCount(7)
        
        # Baslik satiri
        headers = ['ID', 'Ad', 'Soyad', 'Email', 'Telefon', 'Toplam Borç', 'Aktif Ödünç']
        
        for col, header in enumerate(headers):
            header_item = QTableWidgetItem(header)
            header_item.setFont(QFont('Arial', 10, QFont.Bold))
            header_item.setForeground(QColor('white'))
            header_item.setBackground(QColor('#1A4D70'))
            header_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, col, header_item)
        
        # Veri satirlari
        for row_idx, member in enumerate(members, start=1):
            # ID
            item = QTableWidgetItem(str(member['UyeID']))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, item)
            
            # Ad
            item = QTableWidgetItem(member['Ad'])
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 1, item)
            
            # Soyad
            item = QTableWidgetItem(member['Soyad'])
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 2, item)
            
            # Email
            item = QTableWidgetItem(member.get('Email', '-'))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 3, item)
            
            # Telefon
            item = QTableWidgetItem(member.get('Telefon', '-'))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 4, item)
            
            # Toplam Borc
            borc = member['ToplamBorc']
            item = QTableWidgetItem(f"{borc:.2f} TL")
            item.setTextAlignment(Qt.AlignCenter)
            
            # Borç durumuna gore renklendirme
            if borc > 0:
                item.setBackground(QColor('#ffebee'))  # Kirmizi - Borcu var
            else:
                item.setBackground(QColor('#e8f5e9'))  # Yesil - Borcu yok
            
            self.table.setItem(row_idx, 5, item)
            
            # Aktif Odunc
            item = QTableWidgetItem(str(member['AktifOdunc']))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 6, item)
        
        # Sutun genisliklerini ayarla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Ad
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Soyad
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Telefon
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Borc
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Odunc
    
    def populate_book_loan_table(self, books):
        """Kitap odunc bilgisi ile tabloyu doldur"""
        # Tablo boyutunu ayarla
        self.table.setRowCount(len(books) + 1)
        self.table.setColumnCount(11)
        
        # Baslik satiri
        headers = ['ID', 'Kitap Adı', 'Yazar', 'Kategori', 'Üye', 'Ödünç Tarihi', 
                   'Beklenen Teslim', 'Teslim Tarihi', 'Gecikme (Gün)', 'Mevcut', 'Durum']
        
        for col, header in enumerate(headers):
            header_item = QTableWidgetItem(header)
            header_item.setFont(QFont('Arial', 10, QFont.Bold))
            header_item.setForeground(QColor('white'))
            header_item.setBackground(QColor('#1A4D70'))
            header_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, col, header_item)
        
        # Veri satirlari
        for row_idx, book in enumerate(books, start=1):
            # ID
            item = QTableWidgetItem(str(book['KitapID']))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, item)
            
            # Kitap Adi
            item = QTableWidgetItem(book['KitapAdi'])
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 1, item)
            
            # Yazar
            item = QTableWidgetItem(book['Yazar'])
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 2, item)
            
            # Kategori
            item = QTableWidgetItem(book.get('KategoriAdi', '-') or '-')
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 3, item)
            
            # Uye Adi
            item = QTableWidgetItem(book.get('UyeAdi', '-'))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 4, item)
            
            # Odunc Tarihi
            odunc_tarihi = book.get('OduncTarihi', '-')
            if odunc_tarihi and odunc_tarihi != '-':
                odunc_tarihi = odunc_tarihi.strftime('%d.%m.%Y')
            item = QTableWidgetItem(str(odunc_tarihi))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 5, item)
            
            # Beklenen Teslim
            beklenen = book.get('SonTeslimTarihi', '-')
            if beklenen and beklenen != '-':
                beklenen = beklenen.strftime('%d.%m.%Y')
            item = QTableWidgetItem(str(beklenen))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 6, item)
            
            # Teslim Tarihi
            teslim = book.get('TeslimTarihi')
            if teslim:
                teslim_str = teslim.strftime('%d.%m.%Y')
            else:
                teslim_str = 'Teslim Edilmedi'
            item = QTableWidgetItem(teslim_str)
            item.setTextAlignment(Qt.AlignCenter)
            if not teslim:
                item.setForeground(QColor('#d32f2f'))
            self.table.setItem(row_idx, 7, item)
            
            # Gecikme Suresi
            gecikme = book.get('GecikmeSuresi', 0)
            item = QTableWidgetItem(str(gecikme))
            item.setTextAlignment(Qt.AlignCenter)
            if gecikme > 0:
                item.setBackground(QColor('#ffebee'))
                item.setForeground(QColor('#d32f2f'))
            self.table.setItem(row_idx, 8, item)
            
            # Mevcut Adet
            mevcut = book['MevcutAdet']
            item = QTableWidgetItem(str(mevcut))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 9, item)
            
            # Durum
            if teslim:
                durum = 'Teslim Edildi'
                renk = QColor('#e8f5e9')
            elif gecikme > 0:
                durum = f'{gecikme} Gün Gecikmiş'
                renk = QColor('#ffebee')
            else:
                durum = 'Aktif'
                renk = QColor('#fff3e0')
            
            item = QTableWidgetItem(durum)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(renk)
            self.table.setItem(row_idx, 10, item)
        
        # Sutun genisliklerini ayarla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents)
    
    def populate_member_loan_table(self, members):
        """Uye odunc bilgisi ile tabloyu doldur"""
        # Tablo boyutunu ayarla
        self.table.setRowCount(len(members) + 1)
        self.table.setColumnCount(10)
        
        # Baslik satiri
        headers = ['Üye ID', 'Ad', 'Soyad', 'Kitap', 'Ödünç Tarihi', 
                   'Beklenen Teslim', 'Teslim Tarihi', 'Gecikme (Gün)', 'Borç', 'Durum']
        
        for col, header in enumerate(headers):
            header_item = QTableWidgetItem(header)
            header_item.setFont(QFont('Arial', 10, QFont.Bold))
            header_item.setForeground(QColor('white'))
            header_item.setBackground(QColor('#1A4D70'))
            header_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, col, header_item)
        
        # Veri satirlari
        for row_idx, member in enumerate(members, start=1):
            # Uye ID
            item = QTableWidgetItem(str(member['UyeID']))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, item)
            
            # Ad
            item = QTableWidgetItem(member['Ad'])
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 1, item)
            
            # Soyad
            item = QTableWidgetItem(member['Soyad'])
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 2, item)
            
            # Kitap Adi
            item = QTableWidgetItem(member.get('KitapAdi', '-'))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row_idx, 3, item)
            
            # Odunc Tarihi
            odunc_tarihi = member.get('OduncTarihi', '-')
            if odunc_tarihi and odunc_tarihi != '-':
                odunc_tarihi = odunc_tarihi.strftime('%d.%m.%Y')
            item = QTableWidgetItem(str(odunc_tarihi))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 4, item)
            
            # Beklenen Teslim
            beklenen = member.get('SonTeslimTarihi', '-')
            if beklenen and beklenen != '-':
                beklenen = beklenen.strftime('%d.%m.%Y')
            item = QTableWidgetItem(str(beklenen))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 5, item)
            
            # Teslim Tarihi
            teslim = member.get('TeslimTarihi')
            if teslim:
                teslim_str = teslim.strftime('%d.%m.%Y')
            else:
                teslim_str = 'Teslim Etmedi'
            item = QTableWidgetItem(teslim_str)
            item.setTextAlignment(Qt.AlignCenter)
            if not teslim:
                item.setForeground(QColor('#d32f2f'))
            self.table.setItem(row_idx, 6, item)
            
            # Gecikme Suresi
            gecikme = member.get('GecikmeSuresi', 0)
            item = QTableWidgetItem(str(gecikme))
            item.setTextAlignment(Qt.AlignCenter)
            if gecikme > 0:
                item.setBackground(QColor('#ffebee'))
                item.setForeground(QColor('#d32f2f'))
            self.table.setItem(row_idx, 7, item)
            
            # Toplam Borc
            borc = member['ToplamBorc']
            item = QTableWidgetItem(f"{borc:.2f} TL")
            item.setTextAlignment(Qt.AlignCenter)
            if borc > 0:
                item.setBackground(QColor('#ffebee'))
            self.table.setItem(row_idx, 8, item)
            
            # Durum
            if teslim:
                durum = 'Teslim Etti'
                renk = QColor('#e8f5e9')
            elif gecikme > 0:
                durum = f'{gecikme} Gün Gecikmiş'
                renk = QColor('#ffebee')
            else:
                durum = 'Aktif'
                renk = QColor('#fff3e0')
            
            item = QTableWidgetItem(durum)
            item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(renk)
            self.table.setItem(row_idx, 9, item)
        
        # Sutun genisliklerini ayarla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)
    
    def refresh_data(self):
        """Sayfa yenilendiginde cagirilir"""
        self.load_categories()
