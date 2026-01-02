"""
Kutuphane Yonetim Sistemi - Dinamik Sorgu ve Raporlama Ekranı
Kitap ve üye için dinamik filtreler ile arama ve raporlama
(Tablo Görünümü Modernize Edildi)
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QComboBox, QCheckBox, QGroupBox,
                             QRadioButton, QButtonGroup, QScrollArea, QFrame,
                             QSpinBox, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from src.database.db_manager import DatabaseManager
from datetime import datetime


class DynamicQueryWindow(QWidget):
    """Dinamik sorgu ve raporlama ekranı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_query_type = 'KITAP'  # KITAP veya UYE
        self.init_ui()
    
    def init_ui(self):
        """UI başlangıç"""
        # Ana scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #F5F6FA; }")
        
        # Ana widget
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title = QLabel('Dinamik Sorgu ve Raporlama')
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #1A4D70;
            background: transparent;
            padding: 10px;
        """)
        main_layout.addWidget(title)
        
        # Sorgu türü seçimi
        type_frame = self.create_query_type_selection()
        main_layout.addWidget(type_frame)
        
        # Filtre bölümü (dinamik)
        self.filter_container = QWidget()
        self.filter_layout = QVBoxLayout()
        self.filter_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_container.setLayout(self.filter_layout)
        main_layout.addWidget(self.filter_container)
        
        # İlk olarak kitap filtrelerini göster
        self.show_book_filters()
        
        # Sorgu butonları
        button_layout = QHBoxLayout()
        
        search_btn = QPushButton('🔍 Sorgula')
        search_btn.setMinimumHeight(50)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
        """)
        search_btn.clicked.connect(self.execute_query)
        
        clear_btn = QPushButton('🗑️ Temizle')
        clear_btn.setMinimumHeight(50)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        clear_btn.clicked.connect(self.clear_filters)
        
        button_layout.addWidget(search_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Sonuç tablosu başlığı
        result_header = QHBoxLayout()
        
        result_title = QLabel('Sorgu Sonuçları')
        result_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1A4D70;
            background: transparent;
        """)
        result_header.addWidget(result_title)
        
        self.result_count_label = QLabel('0 sonuç')
        self.result_count_label.setStyleSheet("""
            font-size: 14px;
            color: #666666;
            background: transparent;
        """)
        result_header.addWidget(self.result_count_label)
        
        result_header.addStretch()
        
        main_layout.addLayout(result_header)
        
        # --- TABLO YAPILANDIRMASI (GÜNCELLENDİ) ---
        self.results_table = QTableWidget()
        
        # Mavi header'ı gizle
        self.results_table.horizontalHeader().setVisible(False)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #D0D8E2;
                border-radius: 8px;
                gridline-color: #E8EEF5;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #EEEEEE;
            }
        """)
        self.results_table.setMinimumHeight(400)
        
        main_layout.addWidget(self.results_table)
        
        main_widget.setLayout(main_layout)
        scroll.setWidget(main_widget)
        
        # Ana layout
        final_layout = QVBoxLayout()
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.addWidget(scroll)
        self.setLayout(final_layout)
    
    def create_query_type_selection(self):
        """Sorgu türü seçim bölümü (Kitap/Üye)"""
        frame = QGroupBox('Sorgu Türü')
        frame.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #D0D8E2;
                border-radius: 10px;
                padding: 15px;
                margin-top: 10px;
                font-weight: bold;
                font-size: 14px;
                color: #1A4D70;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Radio button grup
        self.type_group = QButtonGroup()
        
        self.book_radio = QRadioButton('📚 Kitap Sorgulama')
        self.book_radio.setChecked(True)
        self.book_radio.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
                color: #333333;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        self.book_radio.toggled.connect(self.on_type_changed)
        
        self.member_radio = QRadioButton('👤 Üye Sorgulama')
        self.member_radio.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
                color: #333333;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        self.member_radio.toggled.connect(self.on_type_changed)
        
        self.type_group.addButton(self.book_radio)
        self.type_group.addButton(self.member_radio)
        
        layout.addWidget(self.book_radio)
        layout.addWidget(self.member_radio)
        layout.addStretch()
        
        frame.setLayout(layout)
        return frame
    
    def on_type_changed(self):
        """Sorgu türü değiştiğinde filtreleri güncelle"""
        if self.book_radio.isChecked():
            self.current_query_type = 'KITAP'
            self.show_book_filters()
        else:
            self.current_query_type = 'UYE'
            self.show_member_filters()
        
        # Sonuç tablosunu temizle
        self.results_table.clearContents()
        self.results_table.setRowCount(0)
        self.result_count_label.setText('0 sonuç')
    
    def show_book_filters(self):
        """Kitap filtreleme bölümünü göster"""
        # Mevcut filtreleri temizle
        self.clear_filter_layout()
        
        # Filtre frame'i
        filter_frame = QGroupBox('Kitap Filtreleri')
        filter_frame.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #D0D8E2;
                border-radius: 10px;
                padding: 20px;
                margin-top: 10px;
                font-weight: bold;
                font-size: 14px;
                color: #1A4D70;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Grid layout for filters
        from PyQt5.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Kitap Adı
        grid.addWidget(QLabel('Kitap Adı:'), 0, 0)
        self.book_name_input = QLineEdit()
        self.book_name_input.setPlaceholderText('Kitap adı giriniz (kısmi eşleşme)')
        self.book_name_input.setStyleSheet(self.get_input_style())
        grid.addWidget(self.book_name_input, 0, 1)
        
        # Yazar
        grid.addWidget(QLabel('Yazar:'), 1, 0)
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText('Yazar adı giriniz')
        self.author_input.setStyleSheet(self.get_input_style())
        grid.addWidget(self.author_input, 1, 1)
        
        # Kategori
        grid.addWidget(QLabel('Kategori:'), 2, 0)
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(self.get_input_style())
        self.load_categories()
        grid.addWidget(self.category_combo, 2, 1)
        
        # Yayınevi
        grid.addWidget(QLabel('Yayınevi:'), 3, 0)
        self.publisher_input = QLineEdit()
        self.publisher_input.setPlaceholderText('Yayınevi adı giriniz')
        self.publisher_input.setStyleSheet(self.get_input_style())
        grid.addWidget(self.publisher_input, 3, 1)
        
        # Basım Yılı Min
        grid.addWidget(QLabel('Basım Yılı (Min):'), 4, 0)
        self.year_min_spin = QSpinBox()
        self.year_min_spin.setRange(1800, 2100)
        self.year_min_spin.setValue(1900)
        self.year_min_spin.setSpecialValueText('Belirsiz')
        self.year_min_spin.setStyleSheet(self.get_input_style())
        grid.addWidget(self.year_min_spin, 4, 1)
        
        # Basım Yılı Max
        grid.addWidget(QLabel('Basım Yılı (Max):'), 5, 0)
        self.year_max_spin = QSpinBox()
        self.year_max_spin.setRange(1800, 2100)
        self.year_max_spin.setValue(2100)
        self.year_max_spin.setSpecialValueText('Belirsiz')
        self.year_max_spin.setStyleSheet(self.get_input_style())
        grid.addWidget(self.year_max_spin, 5, 1)
        
        layout.addLayout(grid)
        
        # Checkbox - Sadece mevcut kitaplar
        self.available_only_check = QCheckBox('Sadece mevcut kitapları göster (MevcutAdet > 0)')
        self.available_only_check.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #333333;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        layout.addWidget(self.available_only_check)
        
        # Sıralama seçenekleri
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel('Sıralama:'))
        
        self.book_sort_combo = QComboBox()
        self.book_sort_combo.addItems([
            'Kitap Adı (A-Z)',
            'Kitap Adı (Z-A)',
            'Yazar (A-Z)',
            'Yazar (Z-A)',
            'Basım Yılı (Eskiden Yeniye)',
            'Basım Yılı (Yeniden Eskiye)',
            'Mevcut Adet (Artan)',
            'Mevcut Adet (Azalan)'
        ])
        self.book_sort_combo.setStyleSheet(self.get_input_style())
        sort_layout.addWidget(self.book_sort_combo)
        sort_layout.addStretch()
        
        layout.addLayout(sort_layout)
        
        filter_frame.setLayout(layout)
        self.filter_layout.addWidget(filter_frame)
    
    def show_member_filters(self):
        """Üye filtreleme bölümünü göster"""
        # Mevcut filtreleri temizle
        self.clear_filter_layout()
        
        # Filtre frame'i
        filter_frame = QGroupBox('Üye Filtreleri')
        filter_frame.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #D0D8E2;
                border-radius: 10px;
                padding: 20px;
                margin-top: 10px;
                font-weight: bold;
                font-size: 14px;
                color: #1A4D70;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Grid layout for filters
        from PyQt5.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Ad
        grid.addWidget(QLabel('Ad:'), 0, 0)
        self.member_name_input = QLineEdit()
        self.member_name_input.setPlaceholderText('Üye adı giriniz')
        self.member_name_input.setStyleSheet(self.get_input_style())
        grid.addWidget(self.member_name_input, 0, 1)
        
        # Soyad
        grid.addWidget(QLabel('Soyad:'), 1, 0)
        self.member_surname_input = QLineEdit()
        self.member_surname_input.setPlaceholderText('Üye soyadı giriniz')
        self.member_surname_input.setStyleSheet(self.get_input_style())
        grid.addWidget(self.member_surname_input, 1, 1)
        
        # Email
        grid.addWidget(QLabel('Email:'), 2, 0)
        self.member_email_input = QLineEdit()
        self.member_email_input.setPlaceholderText('Email adresi giriniz')
        self.member_email_input.setStyleSheet(self.get_input_style())
        grid.addWidget(self.member_email_input, 2, 1)
        
        # Telefon
        grid.addWidget(QLabel('Telefon:'), 3, 0)
        self.member_phone_input = QLineEdit()
        self.member_phone_input.setPlaceholderText('Telefon numarası giriniz')
        self.member_phone_input.setStyleSheet(self.get_input_style())
        grid.addWidget(self.member_phone_input, 3, 1)
        
        # Toplam Borç Min
        grid.addWidget(QLabel('Toplam Borç (Min):'), 4, 0)
        self.debt_min_spin = QSpinBox()
        self.debt_min_spin.setRange(0, 100000)
        self.debt_min_spin.setValue(0)
        self.debt_min_spin.setSuffix(' ₺')
        self.debt_min_spin.setStyleSheet(self.get_input_style())
        grid.addWidget(self.debt_min_spin, 4, 1)
        
        # Toplam Borç Max
        grid.addWidget(QLabel('Toplam Borç (Max):'), 5, 0)
        self.debt_max_spin = QSpinBox()
        self.debt_max_spin.setRange(0, 100000)
        self.debt_max_spin.setValue(100000)
        self.debt_max_spin.setSuffix(' ₺')
        self.debt_max_spin.setStyleSheet(self.get_input_style())
        grid.addWidget(self.debt_max_spin, 5, 1)
        
        layout.addLayout(grid)
        
        # Checkbox - Sadece aktif üyeler
        self.active_only_check = QCheckBox('Sadece aktif üyeleri göster')
        self.active_only_check.setChecked(True)
        self.active_only_check.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #333333;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        layout.addWidget(self.active_only_check)
        
        # Checkbox - Borcu olanlar
        self.has_debt_check = QCheckBox('Sadece borcu olan üyeleri göster')
        self.has_debt_check.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #333333;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        layout.addWidget(self.has_debt_check)
        
        # Sıralama seçenekleri
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel('Sıralama:'))
        
        self.member_sort_combo = QComboBox()
        self.member_sort_combo.addItems([
            'Ad (A-Z)',
            'Ad (Z-A)',
            'Soyad (A-Z)',
            'Soyad (Z-A)',
            'Toplam Borç (Artan)',
            'Toplam Borç (Azalan)',
            'Kayıt Tarihi (Eskiden Yeniye)',
            'Kayıt Tarihi (Yeniden Eskiye)'
        ])
        self.member_sort_combo.setStyleSheet(self.get_input_style())
        sort_layout.addWidget(self.member_sort_combo)
        sort_layout.addStretch()
        
        layout.addLayout(sort_layout)
        
        filter_frame.setLayout(layout)
        self.filter_layout.addWidget(filter_frame)
    
    def clear_filter_layout(self):
        """Filtre layout'unu temizle"""
        while self.filter_layout.count():
            child = self.filter_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def get_input_style(self):
        """Input alanları için stil"""
        return """
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #D0D8E2;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #4A90E2;
            }
        """
    
    def load_categories(self):
        """Kategorileri yükle"""
        self.category_combo.clear()
        self.category_combo.addItem('-- Tüm Kategoriler --', None)
        
        try:
            db = DatabaseManager()
            query = "SELECT KategoriID, KategoriAdi FROM KATEGORI ORDER BY KategoriAdi"
            results = db.execute_query(query)
            
            for row in results:
                self.category_combo.addItem(row['KategoriAdi'], row['KategoriID'])
        except Exception as e:
            print(f"Kategori yükleme hatası: {e}")
    
    def execute_query(self):
        """Dinamik sorguyu çalıştır"""
        if self.current_query_type == 'KITAP':
            self.execute_book_query()
        else:
            self.execute_member_query()
    
    def execute_book_query(self):
        """Kitap sorgusu çalıştır"""
        try:
            db = DatabaseManager()
            
            # Temel sorgu
            query = """
                SELECT 
                    k.KitapID,
                    k.KitapAdi,
                    k.Yazar,
                    kat.KategoriAdi,
                    k.Yayinevi,
                    k.BasimYili,
                    k.ISBN,
                    k.ToplamAdet,
                    k.MevcutAdet,
                    k.RafNo
                FROM KITAP k
                LEFT JOIN KATEGORI kat ON k.KategoriID = kat.KategoriID
                WHERE 1=1
            """
            
            params = []
            
            # Dinamik koşullar
            if self.book_name_input.text().strip():
                query += " AND k.KitapAdi LIKE %s"
                params.append(f"%{self.book_name_input.text().strip()}%")
            
            if self.author_input.text().strip():
                query += " AND k.Yazar LIKE %s"
                params.append(f"%{self.author_input.text().strip()}%")
            
            if self.category_combo.currentData() is not None:
                query += " AND k.KategoriID = %s"
                params.append(self.category_combo.currentData())
            
            if self.publisher_input.text().strip():
                query += " AND k.Yayinevi LIKE %s"
                params.append(f"%{self.publisher_input.text().strip()}%")
            
            # Basım yılı aralığı
            if self.year_min_spin.value() != 1800:
                query += " AND k.BasimYili >= %s"
                params.append(self.year_min_spin.value())
            
            if self.year_max_spin.value() != 2100:
                query += " AND k.BasimYili <= %s"
                params.append(self.year_max_spin.value())
            
            # Sadece mevcut kitaplar
            if self.available_only_check.isChecked():
                query += " AND k.MevcutAdet > 0"
            
            # Sıralama
            sort_option = self.book_sort_combo.currentText()
            if 'Kitap Adı (A-Z)' in sort_option:
                query += " ORDER BY k.KitapAdi ASC"
            elif 'Kitap Adı (Z-A)' in sort_option:
                query += " ORDER BY k.KitapAdi DESC"
            elif 'Yazar (A-Z)' in sort_option:
                query += " ORDER BY k.Yazar ASC"
            elif 'Yazar (Z-A)' in sort_option:
                query += " ORDER BY k.Yazar DESC"
            elif 'Basım Yılı (Eskiden Yeniye)' in sort_option:
                query += " ORDER BY k.BasimYili ASC"
            elif 'Basım Yılı (Yeniden Eskiye)' in sort_option:
                query += " ORDER BY k.BasimYili DESC"
            elif 'Mevcut Adet (Artan)' in sort_option:
                query += " ORDER BY k.MevcutAdet ASC"
            elif 'Mevcut Adet (Azalan)' in sort_option:
                query += " ORDER BY k.MevcutAdet DESC"
            
            # Sorguyu çalıştır
            results = db.execute_query(query, tuple(params))
            
            # Sonuçları göster
            self.display_book_results(results)
            
            # Toast bildirimi
            if self.parent:
                self.parent.show_toast(f'{len(results)} sonuç bulundu', 'success')
            
        except Exception as e:
            print(f"Sorgu hatası: {e}")
            QMessageBox.critical(self, 'Hata', f'Sorgu çalıştırılırken hata oluştu:\n{str(e)}')
    
    def execute_member_query(self):
        """Üye sorgusu çalıştır"""
        try:
            db = DatabaseManager()
            
            # Temel sorgu
            query = """
                SELECT 
                    UyeID,
                    Ad,
                    Soyad,
                    Email,
                    Telefon,
                    Adres,
                    KayitTarihi,
                    ToplamBorc,
                    AktifMi
                FROM UYE
                WHERE 1=1
            """
            
            params = []
            
            # Dinamik koşullar
            if self.member_name_input.text().strip():
                query += " AND Ad LIKE %s"
                params.append(f"%{self.member_name_input.text().strip()}%")
            
            if self.member_surname_input.text().strip():
                query += " AND Soyad LIKE %s"
                params.append(f"%{self.member_surname_input.text().strip()}%")
            
            if self.member_email_input.text().strip():
                query += " AND Email LIKE %s"
                params.append(f"%{self.member_email_input.text().strip()}%")
            
            if self.member_phone_input.text().strip():
                query += " AND Telefon LIKE %s"
                params.append(f"%{self.member_phone_input.text().strip()}%")
            
            # Borç aralığı
            if self.debt_min_spin.value() > 0:
                query += " AND ToplamBorc >= %s"
                params.append(self.debt_min_spin.value())
            
            if self.debt_max_spin.value() < 100000:
                query += " AND ToplamBorc <= %s"
                params.append(self.debt_max_spin.value())
            
            # Sadece aktif üyeler
            if self.active_only_check.isChecked():
                query += " AND AktifMi = TRUE"
            
            # Sadece borcu olanlar
            if self.has_debt_check.isChecked():
                query += " AND ToplamBorc > 0"
            
            # Sıralama
            sort_option = self.member_sort_combo.currentText()
            if 'Ad (A-Z)' in sort_option:
                query += " ORDER BY Ad ASC"
            elif 'Ad (Z-A)' in sort_option:
                query += " ORDER BY Ad DESC"
            elif 'Soyad (A-Z)' in sort_option:
                query += " ORDER BY Soyad ASC"
            elif 'Soyad (Z-A)' in sort_option:
                query += " ORDER BY Soyad DESC"
            elif 'Toplam Borç (Artan)' in sort_option:
                query += " ORDER BY ToplamBorc ASC"
            elif 'Toplam Borç (Azalan)' in sort_option:
                query += " ORDER BY ToplamBorc DESC"
            elif 'Kayıt Tarihi (Eskiden Yeniye)' in sort_option:
                query += " ORDER BY KayitTarihi ASC"
            elif 'Kayıt Tarihi (Yeniden Eskiye)' in sort_option:
                query += " ORDER BY KayitTarihi DESC"
            
            # Sorguyu çalıştır
            results = db.execute_query(query, tuple(params))
            
            # Sonuçları göster
            self.display_member_results(results)
            
            # Toast bildirimi
            if self.parent:
                self.parent.show_toast(f'{len(results)} sonuç bulundu', 'success')
            
        except Exception as e:
            print(f"Sorgu hatası: {e}")
            QMessageBox.critical(self, 'Hata', f'Sorgu çalıştırılırken hata oluştu:\n{str(e)}')
    
    def display_book_results(self, results):
        """Kitap sonuçlarını tabloda göster (Modernize Edildi)"""
        headers = ['Kitap ID', 'Kitap Adı', 'Yazar', 'Kategori', 'Yayınevi', 
                   'Basım Yılı', 'ISBN', 'Toplam Adet', 'Mevcut Adet', 'Raf No']
        
        self.results_table.setColumnCount(len(headers))
        # Satır sayısı: Veri + 1 (Header için)
        self.results_table.setRowCount(len(results) + 1)
        
        # --- 1. BAŞLIK SATIRI (Row 0) ---
        for col, text in enumerate(headers):
            item = QTableWidgetItem(text)
            item.setBackground(QColor('#1A4D70')) # Mavi Arka Plan
            item.setForeground(QColor('white'))   # Beyaz Yazı
            item.setFont(QFont('Segoe UI', 10, QFont.Bold))
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled) # Düzenlenemez
            self.results_table.setItem(0, col, item)
        
        # --- 2. VERİ SATIRLARI (Row 1'den başlar) ---
        keys = ['KitapID', 'KitapAdi', 'Yazar', 'KategoriAdi', 'Yayinevi', 
                'BasimYili', 'ISBN', 'ToplamAdet', 'MevcutAdet', 'RafNo']
                
        for row_idx, row_data in enumerate(results, start=1):
            for col_idx, key in enumerate(keys):
                value = row_data.get(key, '')
                if value is None:
                    value = ''
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.results_table.setItem(row_idx, col_idx, item)
        
        # Sütun genişliklerini ayarla
        self.results_table.resizeColumnsToContents()
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # Kitap adı esnek
        
        # Sonuç sayısını güncelle
        self.result_count_label.setText(f'{len(results)} sonuç')
    
    def display_member_results(self, results):
        """Üye sonuçlarını tabloda göster (Modernize Edildi)"""
        headers = ['Üye ID', 'Ad', 'Soyad', 'Email', 'Telefon', 
                   'Adres', 'Kayıt Tarihi', 'Toplam Borç', 'Aktif Mi']
        
        self.results_table.setColumnCount(len(headers))
        # Satır sayısı: Veri + 1 (Header için)
        self.results_table.setRowCount(len(results) + 1)
        
        # --- 1. BAŞLIK SATIRI (Row 0) ---
        for col, text in enumerate(headers):
            item = QTableWidgetItem(text)
            item.setBackground(QColor('#1A4D70'))
            item.setForeground(QColor('white'))
            item.setFont(QFont('Segoe UI', 10, QFont.Bold))
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            self.results_table.setItem(0, col, item)
        
        # --- 2. VERİ SATIRLARI (Row 1'den başlar) ---
        keys = ['UyeID', 'Ad', 'Soyad', 'Email', 'Telefon', 
                'Adres', 'KayitTarihi', 'ToplamBorc', 'AktifMi']
                
        for row_idx, row_data in enumerate(results, start=1):
            for col_idx, key in enumerate(keys):
                value = row_data.get(key, '')
                
                # Özel formatlamalar
                if key == 'KayitTarihi' and value:
                    if isinstance(value, datetime):
                        value = value.strftime('%d.%m.%Y')
                    elif isinstance(value, str):
                        try:
                            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            value = dt.strftime('%d.%m.%Y')
                        except:
                            pass
                elif key == 'ToplamBorc':
                    value = f'{float(value):.2f} ₺' if value else '0.00 ₺'
                elif key == 'AktifMi':
                    value = 'Evet' if value else 'Hayır'
                elif value is None:
                    value = ''
                
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.results_table.setItem(row_idx, col_idx, item)
        
        # Sütun genişliklerini ayarla
        self.results_table.resizeColumnsToContents()
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # Ad esnek
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch) # Soyad esnek
        
        # Sonuç sayısını güncelle
        self.result_count_label.setText(f'{len(results)} sonuç')
    
    def clear_filters(self):
        """Tüm filtreleri temizle"""
        if self.current_query_type == 'KITAP':
            self.book_name_input.clear()
            self.author_input.clear()
            self.category_combo.setCurrentIndex(0)
            self.publisher_input.clear()
            self.year_min_spin.setValue(1900)
            self.year_max_spin.setValue(2100)
            self.available_only_check.setChecked(False)
            self.book_sort_combo.setCurrentIndex(0)
        else:
            self.member_name_input.clear()
            self.member_surname_input.clear()
            self.member_email_input.clear()
            self.member_phone_input.clear()
            self.debt_min_spin.setValue(0)
            self.debt_max_spin.setValue(100000)
            self.active_only_check.setChecked(True)
            self.has_debt_check.setChecked(False)
            self.member_sort_combo.setCurrentIndex(0)
        
        # Sonuçları temizle
        self.results_table.clearContents()
        self.results_table.setRowCount(0)
        self.result_count_label.setText('0 sonuç')
        
        if self.parent:
            self.parent.show_toast('Filtreler temizlendi', 'info')
    
    def refresh_data(self):
        """Sayfa yenilendiğinde kategorileri yeniden yükle"""
        if self.current_query_type == 'KITAP':
            self.load_categories()