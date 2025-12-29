"""
Kategori Yonetim Ekrani
Kategori listeleme, ekleme, silme ve duzenleme
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                             QMessageBox, QDialog, QFormLayout, QTextEdit, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from src.database.db_manager import DatabaseManager
from src.utils.helpers import ask_yes_no_tr

class CategoryWindow(QWidget):
    """Kategori yonetim ekrani"""
    
    def __init__(self, dashboard=None):
        super().__init__()
        self.dashboard = dashboard
        self.init_ui()
        self.load_categories()
    
    def init_ui(self):
        """UI olustur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Baslik
        title = QLabel('KATEGORİ YÖNETİMİ')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #3B4953;')
        layout.addWidget(title)
        
        # --- ARAMA BÖLÜMÜ (EKLENDİ) ---
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Kategori adı ile ara...')
        self.search_input.textChanged.connect(self.search_categories)
        search_layout.addWidget(QLabel('Ara:'))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(3) # ID, Kategori Adı, Açıklama
        
        # --- TABLO AYARLARI (Mavi Çift Başlığı Kaldırır) ---
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(400)
        
        layout.addWidget(self.table)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton('Yeni Kategori Ekle')
        self.add_btn.clicked.connect(self.add_category)
        button_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton('Düzenle')
        self.edit_btn.clicked.connect(self.edit_category)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton('Sil')
        self.delete_btn.clicked.connect(self.delete_category)
        button_layout.addWidget(self.delete_btn)
        
        self.refresh_btn = QPushButton('Yenile')
        self.refresh_btn.clicked.connect(self.load_categories)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def update_table_content(self, categories):
        """Tabloyu doldur ve başlıkları koru"""
        self.table.setRowCount(len(categories) + 1)
        
        # 1. BAŞLIK SATIRI (Row 0)
        headers = ['ID', 'Kategori Adı', 'Açıklama']
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
        for row_idx, cat in enumerate(categories, start=1):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(cat['KategoriID'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(cat['KategoriAdi']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(cat['Aciklama'] or '-'))
            
            # ID Ortala
            if self.table.item(row_idx, 0):
                self.table.item(row_idx, 0).setTextAlignment(Qt.AlignCenter)

        # 3. SÜTUN GENİŞLİKLERİ
        self.table.resizeColumnsToContents()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch) # Kategori Adı Esnek
        header.setSectionResizeMode(2, QHeaderView.Stretch) # Açıklama Esnek

    def load_categories(self):
        try:
            db = DatabaseManager()
            categories = db.execute_query(
                'SELECT KategoriID, KategoriAdi, Aciklama FROM KATEGORI ORDER BY KategoriAdi'
            )
            self.update_table_content(categories)
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Kategoriler yüklenemedi: {str(e)}')

    def search_categories(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_categories()
            return
        
        try:
            db = DatabaseManager()
            query = """
                SELECT KategoriID, KategoriAdi, Aciklama FROM KATEGORI 
                WHERE KategoriAdi LIKE %s OR Aciklama LIKE %s
                ORDER BY KategoriAdi
            """
            search_term = f"%{search_text}%"
            categories = db.execute_query(query, (search_term, search_term))
            self.update_table_content(categories)
        except Exception as e:
             print(f"Arama hatası: {e}")

    def add_category(self):
        dialog = CategoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            if hasattr(dialog, 'success_message') and self.dashboard:
                self.dashboard.show_toast(dialog.success_message[0], dialog.success_message[1])
            self.load_categories()

    def edit_category(self):
        selected = self.table.currentRow()
        
        # --- CRASH DÜZELTME: Başlık (0) veya boş seçim (-1) kontrolü ---
        if selected <= 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen düzenlenecek kategoriyi seçin!')
            return
        
        try:
            # ID 0. sütunda
            cat_id = int(self.table.item(selected, 0).text())
            dialog = CategoryDialog(self, cat_id)
            if dialog.exec_() == QDialog.Accepted:
                if hasattr(dialog, 'success_message') and self.dashboard:
                    self.dashboard.show_toast(dialog.success_message[0], dialog.success_message[1])
                self.load_categories()
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'İşlem hatası: {str(e)}')

    def delete_category(self):
        selected = self.table.currentRow()
        
        # --- CRASH DÜZELTME: Başlık (0) veya boş seçim (-1) kontrolü ---
        if selected <= 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silinecek kategoriyi seçin!')
            return
            
        cat_id = int(self.table.item(selected, 0).text())
        cat_name = self.table.item(selected, 1).text()
        
        if ask_yes_no_tr(self, 'Silme Onayı', f"'{cat_name}' kategorisini silmek istediğinize emin misiniz?"):
            try:
                db = DatabaseManager()
                # Önce kitap var mı kontrol et
                check = db.execute_query("SELECT COUNT(*) as sayi FROM KITAP WHERE KategoriID = %s", (cat_id,), fetch_one=True)
                if check['sayi'] > 0:
                    QMessageBox.warning(self, 'Hata', 'Bu kategoriye ait kitaplar var, silinemez!')
                    return

                db.execute_update('DELETE FROM KATEGORI WHERE KategoriID = %s', (cat_id,))
                if self.dashboard:
                    self.dashboard.show_toast('Kategori başarıyla silindi!', 'success')
                self.load_categories()
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Silme hatası: {str(e)}')


class CategoryDialog(QDialog):
    """Kategori ekleme/düzenleme"""
    
    def __init__(self, parent=None, kategori_id=None):
        super().__init__(parent)
        self.kategori_id = kategori_id
        self.success_message = None
        self.init_ui()
        
        if kategori_id:
            self.load_category_data()
            
    def init_ui(self):
        title = 'Kategori Düzenle' if self.kategori_id else 'Yeni Kategori Ekle'
        self.setWindowTitle(title)
        
        # --- SORU İŞARETİ (?) BUTONUNU KALDIRMA ---
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.setMinimumWidth(350)
        
        layout = QFormLayout()
        
        self.kategori_adi_input = QLineEdit()
        layout.addRow('Kategori Adı:', self.kategori_adi_input)
        
        self.aciklama_input = QTextEdit()
        self.aciklama_input.setMaximumHeight(100)
        layout.addRow('Açıklama:', self.aciklama_input)
        
        # Butonlar
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Kaydet')
        save_btn.clicked.connect(self.save_category)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('İptal')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)

    def load_category_data(self):
        try:
            db = DatabaseManager()
            result = db.execute_query(
                'SELECT KategoriAdi, Aciklama FROM KATEGORI WHERE KategoriID = %s',
                (self.kategori_id,)
            )
            if result:
                cat = result[0]
                self.kategori_adi_input.setText(cat['KategoriAdi'])
                self.aciklama_input.setPlainText(cat['Aciklama'] or '')
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Veri yüklenemedi: {e}')

    def save_category(self):
        ad = self.kategori_adi_input.text().strip()
        aciklama = self.aciklama_input.toPlainText().strip()
        
        if not ad:
            QMessageBox.warning(self, 'Uyarı', 'Kategori adı boş olamaz!')
            return
            
        try:
            db = DatabaseManager()
            
            # İsim kontrolü
            check_sql = "SELECT COUNT(*) as sayi FROM KATEGORI WHERE KategoriAdi = %s"
            params = [ad]
            if self.kategori_id:
                check_sql += " AND KategoriID != %s"
                params.append(self.kategori_id)
            
            check = db.execute_query(check_sql, tuple(params), fetch_one=True)
            if check['sayi'] > 0:
                QMessageBox.warning(self, 'Uyarı', 'Bu kategori adı zaten mevcut!')
                return

            if self.kategori_id:
                db.execute_update(
                    'UPDATE KATEGORI SET KategoriAdi = %s, Aciklama = %s WHERE KategoriID = %s',
                    (ad, aciklama, self.kategori_id)
                )
                self.success_message = ('Kategori güncellendi!', 'success')
            else:
                db.execute_update(
                    'INSERT INTO KATEGORI (KategoriAdi, Aciklama) VALUES (%s, %s)',
                    (ad, aciklama)
                )
                self.success_message = ('Yeni kategori eklendi!', 'success')
                
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Kaydetme hatası: {str(e)}')