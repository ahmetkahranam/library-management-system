"""
Kitap Yonetim Ekrani
Kitap listeleme, ekleme, silme ve duzenleme (Yıl Limiti ve UI Düzeltmeleri)
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                             QMessageBox, QDialog, QFormLayout, QComboBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from src.models.book import Book
from src.utils.helpers import ask_yes_no_tr
from src.database.db_manager import db_manager

class BookManagementWindow(QWidget):
    """Kitap yonetim ekrani"""
    
    def __init__(self, dashboard=None):
        super().__init__()
        self.dashboard = dashboard
        self.init_ui()
        self.load_books()
    
    def init_ui(self):
        """UI olustur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Baslik
        title = QLabel('KİTAP YÖNETİMİ')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #3B4953;')
        layout.addWidget(title)
        
        # Arama bolumu
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Kitap adı, yazar veya ISBN ile ara...')
        self.search_input.textChanged.connect(self.search_books)
        search_layout.addWidget(QLabel('Ara:'))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(8) # ID, ISBN, Kitap Adı, Yazar, Kategori, Basım Yılı, Toplam, Mevcut
        
        # Header gizle
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(400)
        
        layout.addWidget(self.table)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton('Yeni Kitap Ekle')
        self.add_btn.clicked.connect(self.add_book)
        button_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton('Düzenle')
        self.edit_btn.clicked.connect(self.edit_book)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton('Sil')
        self.delete_btn.clicked.connect(self.delete_book)
        button_layout.addWidget(self.delete_btn)
        
        self.refresh_btn = QPushButton('Yenile')
        self.refresh_btn.clicked.connect(self.load_books)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def update_table_content(self, books):
        """Tabloyu verilerle doldurur."""
        self.table.setRowCount(len(books) + 1)
        
        # 1. BAŞLIK SATIRI
        headers = ['ID', 'ISBN', 'Kitap Adı', 'Yazar', 'Kategori', 'Basım Yılı', 'Toplam', 'Mevcut']
        
        for col, header_text in enumerate(headers):
            item = QTableWidgetItem(header_text)
            item.setBackground(QColor('#1A4D70'))
            item.setForeground(QColor('#FFFFFF'))
            font = QFont('Segoe UI', 11, QFont.Bold)
            item.setFont(font)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(0, col, item)
            
        # 2. VERİ SATIRLARI
        for row_idx, book in enumerate(books, start=1):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(book.get('KitapID', ''))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(book.get('ISBN') or '')))
            
            # Kitap Adı
            kitap_adi = book.get('KitapAdi') or book.get('Baslik') or "-"
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(kitap_adi)))
            
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(book.get('Yazar', ''))))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(book.get('KategoriAdi') or '-')))
            
            # Basım Yılı
            yil = book.get('BasimYili') or book.get('YayinYili') or ''
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(yil)))
            
            # Toplam
            toplam = book.get('ToplamAdet')
            if toplam is None: toplam = book.get('StokSayisi', 0)
            self.table.setItem(row_idx, 6, QTableWidgetItem(str(toplam)))
            
            # Mevcut
            mevcut = book.get('MevcutAdet')
            if mevcut is None: mevcut = 0
            self.table.setItem(row_idx, 7, QTableWidgetItem(str(mevcut)))
            
            # Hizalama
            for col in [0, 5, 6, 7]:
                if self.table.item(row_idx, col):
                    self.table.item(row_idx, col).setTextAlignment(Qt.AlignCenter)

        self.table.resizeColumnsToContents()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        for col in [0, 1, 3, 4, 5, 6, 7]:
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
            
        if self.table.columnWidth(7) < 60:
            self.table.setColumnWidth(7, 60)

    def load_books(self):
        try:
            books = Book.get_all()
            self.update_table_content(books)
        except Exception as e:
            print(f"Hata detayı: {e}")
            QMessageBox.critical(self, 'Hata', f'Kitaplar yüklenemedi: {str(e)}')
    
    def refresh_data(self):
        self.load_books()
        if self.dashboard:
            self.dashboard.load_statistics()
    
    def search_books(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_books()
            return
        try:
            books = Book.search(search_text)
            self.update_table_content(books)
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Arama hatası: {str(e)}')
    
    def add_book(self):
        dialog = BookDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            if self.dashboard and hasattr(dialog, 'success_message'):
                self.dashboard.show_toast(dialog.success_message, 'success')
            self.load_books()
            if self.dashboard:
                self.dashboard.refresh_statistics()
    
    def edit_book(self):
        selected = self.table.currentRow()
        if selected <= 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen düzenlenecek kitabı seçin!')
            return
        
        book_id_item = self.table.item(selected, 0)
        if not book_id_item: return
        
        book_id = int(book_id_item.text())
        dialog = BookDialog(self, book_id)
        if dialog.exec_() == QDialog.Accepted:
            if self.dashboard and hasattr(dialog, 'success_message'):
                self.dashboard.show_toast(dialog.success_message, 'success')
            self.load_books()
            if self.dashboard:
                self.dashboard.refresh_statistics()
    
    def delete_book(self):
        selected = self.table.currentRow()
        if selected <= 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silinecek kitabı seçin!')
            return
        
        book_id = int(self.table.item(selected, 0).text())
        book_title = self.table.item(selected, 2).text()
        
        if ask_yes_no_tr(self, 'Silme Onayı', f'{book_title} adlı kitabı silmek istediğinize emin misiniz?'):
            try:
                Book.delete(book_id)
                if self.dashboard:
                    self.dashboard.show_toast('Kitap başarıyla silindi!', 'success')
                self.load_books()
                if self.dashboard:
                    self.dashboard.refresh_statistics()
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Kitap silinemedi: {str(e)}')


class BookDialog(QDialog):
    """Kitap ekleme/duzenleme penceresi"""
    
    def __init__(self, parent=None, book_id=None):
        super().__init__(parent)
        self.book_id = book_id
        self.success_message = ''
        self.init_ui()
        self.load_categories()
        
        if book_id:
            self.load_book_data()
            
    def init_ui(self):
        title = 'Kitap Düzenle' if self.book_id else 'Yeni Kitap Ekle'
        self.setWindowTitle(title)
        
        # --- SORU İŞARETİNİ (?) KALDIRAN KOD ---
        # Bu satır, pencere başlığındaki yardım butonunu devre dışı bırakır.
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        self.isbn_input = QLineEdit()
        layout.addRow('ISBN:', self.isbn_input)
        
        self.baslik_input = QLineEdit()
        layout.addRow('Kitap Adı:', self.baslik_input)
        
        self.yazar_input = QLineEdit()
        layout.addRow('Yazar:', self.yazar_input)
        
        self.yayinevi_input = QLineEdit()
        layout.addRow('Yayınevi:', self.yayinevi_input)
        
        self.kategori_combo = QComboBox()
        self.kategori_combo.setMinimumWidth(200)
        layout.addRow('Kategori:', self.kategori_combo)
        
        self.yil_input = QLineEdit()
        self.yil_input.setPlaceholderText('YYYY')
        layout.addRow('Basım Yılı:', self.yil_input)
        
        self.stok_input = QLineEdit()
        self.stok_input.setPlaceholderText('1')
        layout.addRow('Toplam Adet:', self.stok_input)
        
        # Butonlar
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Kaydet')
        save_btn.clicked.connect(self.save_book)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('İptal')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
        
    def load_categories(self):
        """Kategorileri veritabanından yükle"""
        try:
            # schema.sql'e göre tablo adı: KATEGORI
            query = "SELECT KategoriID, KategoriAdi FROM KATEGORI ORDER BY KategoriAdi"
            categories = db_manager.execute_query(query)
            
            self.kategori_combo.clear()
            self.kategori_combo.addItem('Seçiniz...', None)
            
            if not categories:
                print("[UYARI] Veritabanında hiç kategori bulunamadı.")
            
            for cat in categories:
                self.kategori_combo.addItem(cat['KategoriAdi'], cat['KategoriID'])
                
        except Exception as e:
            print(f"Kategori yükleme hatası: {e}")
            self.kategori_combo.clear()
            self.kategori_combo.addItem(f'Hata: {str(e)}', None)

    def load_book_data(self):
        try:
            book = Book.get_by_id(self.book_id)
            if book:
                self.isbn_input.setText(book.get('ISBN') or '')
                self.baslik_input.setText(book.get('KitapAdi') or book.get('Baslik') or '')
                self.yazar_input.setText(book.get('Yazar', ''))
                self.yayinevi_input.setText(book.get('Yayinevi', ''))
                self.yil_input.setText(str(book.get('BasimYili') or book.get('YayinYili') or ''))
                self.stok_input.setText(str(book.get('ToplamAdet') or book.get('StokSayisi', 1)))
                
                if book.get('KategoriID'):
                    index = self.kategori_combo.findData(book['KategoriID'])
                    if index >= 0:
                        self.kategori_combo.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Kitap verisi yüklenemedi: {str(e)}')

    def save_book(self):
        isbn = self.isbn_input.text().strip()
        baslik = self.baslik_input.text().strip()
        yazar = self.yazar_input.text().strip()
        yayinevi = self.yayinevi_input.text().strip()
        kategori_id = self.kategori_combo.currentData()
        
        # Validasyon
        if not baslik or not yazar or not isbn:
            QMessageBox.warning(self, 'Uyarı', 'Kitap adı, yazar ve ISBN zorunludur!')
            return
            
        if not kategori_id:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen bir kategori seçiniz!')
            return
            
        try:
            yil_text = self.yil_input.text().strip()
            yil = int(yil_text) if yil_text else 2024
            
            # --- YIL KONTROLÜ (BU KISIM EKLENDİ) ---
            # Veritabanı YEAR tipi sadece 1901-2155 arasını destekler
            if not (1901 <= yil <= 2155):
                QMessageBox.warning(self, 'Uyarı', 'Basım yılı 1901 ile 2155 arasında olmalıdır! (Veritabanı kısıtlaması)')
                return
            
            stok_text = self.stok_input.text().strip()
            stok = int(stok_text) if stok_text else 1
            
            if self.book_id:
                success, msg = Book.update(
                    kitap_id=self.book_id, 
                    isbn=isbn, 
                    kitap_adi=baslik, 
                    yazar=yazar, 
                    yayinevi=yayinevi,
                    basim_yili=yil, 
                    toplam_adet=stok, 
                    kategori_id=kategori_id
                )
                if success:
                    self.success_message = 'Kitap başarıyla güncellendi!'
                    self.accept()
                else:
                    QMessageBox.warning(self, 'Hata', msg)
            else:
                success, result = Book.create(
                    kitap_adi=baslik, 
                    yazar=yazar, 
                    isbn=isbn, 
                    yayinevi=yayinevi,
                    basim_yili=yil, 
                    toplam_adet=stok, 
                    kategori_id=kategori_id
                )
                if success:
                    self.success_message = f'Yeni kitap eklendi! ID: {result}'
                    self.accept()
                else:
                    QMessageBox.warning(self, 'Hata', result)
                    
        except ValueError:
            QMessageBox.warning(self, 'Uyarı', 'Yıl ve Adet alanlarına sayısal değer giriniz!')
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Kaydetme hatası: {str(e)}')