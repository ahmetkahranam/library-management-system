"""
Uye Yonetim Ekrani
Basit CRUD islemleri
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                             QMessageBox, QDialog, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont
from src.models.member import Member
# YENİ IMPORT EKLENDİ
from src.utils.helpers import ask_yes_no_tr


class MemberManagementWindow(QWidget):
    """Uye yonetim ekrani"""
    
    def __init__(self, dashboard=None):
        super().__init__()
        self.dashboard = dashboard
        self.init_ui()
        self.load_members()
    
    def init_ui(self):
        """UI olustur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Baslik
        title = QLabel('ÜYE YÖNETİMİ')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #3B4953;')
        layout.addWidget(title)
        
        # Arama bolumu
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Üye adı veya Email ile ara...')
        self.search_input.textChanged.connect(self.search_members)
        search_layout.addWidget(QLabel('Ara:'))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        
        # Header bar'ı gizle - ilk satır başlık olacak
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton('Yeni Üye Ekle')
        self.add_btn.clicked.connect(self.add_member)
        button_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton('Düzenle')
        self.edit_btn.clicked.connect(self.edit_member)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton('Sil')
        self.delete_btn.clicked.connect(self.delete_member)
        button_layout.addWidget(self.delete_btn)
        
        self.refresh_btn = QPushButton('Yenile')
        self.refresh_btn.clicked.connect(self.load_members)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_members(self):
        """Uyeleri yukle"""
        try:
            members = Member.get_all()
            # +1 for header row
            self.table.setRowCount(len(members) + 1)
            
            # İlk satır başlık
            headers = ['ID', 'Ad Soyad', 'Telefon', 'Email', 'Toplam Borç', 'Kayıt Tarihi', 'Durum']
            for col, header_text in enumerate(headers):
                header_item = QTableWidgetItem(header_text)
                header_item.setBackground(QColor('#1A4D70'))
                header_item.setForeground(QColor('#FFFFFF'))
                font = QFont('Segoe UI', 12, QFont.Bold)
                header_item.setFont(font)
                header_item.setTextAlignment(Qt.AlignCenter)
                header_item.setFlags(Qt.ItemIsEnabled)  # Read-only
                self.table.setItem(0, col, header_item)
            
            # Data satırları 1'den başlar
            for row, member in enumerate(members, start=1):
                self.table.setItem(row, 0, QTableWidgetItem(str(member['UyeID'])))
                ad_soyad = f"{member['Ad']} {member['Soyad']}"
                self.table.setItem(row, 1, QTableWidgetItem(ad_soyad))
                self.table.setItem(row, 2, QTableWidgetItem(member['Telefon'] or ''))
                self.table.setItem(row, 3, QTableWidgetItem(member['Email'] or ''))
                self.table.setItem(row, 4, QTableWidgetItem(f"{member['ToplamBorc']:.2f} TL"))
                self.table.setItem(row, 5, QTableWidgetItem(str(member['KayitTarihi'])))
                
                durum = 'Aktif' if member.get('AktifMi', True) else 'Pasif'
                self.table.setItem(row, 6, QTableWidgetItem(durum))
            
            self.table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Üyeler yüklenemedi: {str(e)}')
    
    def refresh_data(self):
        """Sayfa yenilendiğinde çağrılır"""
        self.load_members()
        if self.dashboard:
            self.dashboard.load_statistics()
    
    def search_members(self):
        """Uye ara"""
        search_text = self.search_input.text().strip()
        
        if not search_text:
            self.load_members()
            return
        
        try:
            members = Member.search(search_text)
            self.table.setRowCount(len(members))
            
            for row, member in enumerate(members):
                self.table.setItem(row, 0, QTableWidgetItem(str(member['UyeID'])))
                ad_soyad = f"{member['Ad']} {member['Soyad']}"
                self.table.setItem(row, 1, QTableWidgetItem(ad_soyad))
                self.table.setItem(row, 2, QTableWidgetItem(member['Telefon'] or ''))
                self.table.setItem(row, 3, QTableWidgetItem(member['Email'] or ''))
                self.table.setItem(row, 4, QTableWidgetItem(f"{member['ToplamBorc']:.2f} TL"))
                self.table.setItem(row, 5, QTableWidgetItem(str(member['KayitTarihi'])))
                
                durum = 'Aktif' if member.get('AktifMi', True) else 'Pasif'
                self.table.setItem(row, 6, QTableWidgetItem(durum))
            
            self.table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Arama hatası: {str(e)}')
    
    def add_member(self):
        """Yeni uye ekle"""
        dialog = MemberDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            if self.dashboard and hasattr(dialog, 'success_message'):
                self.dashboard.show_toast(dialog.success_message, 'success')
            self.load_members()
            # Dashboard'u guncelle
            if self.dashboard:
                self.dashboard.refresh_statistics()
    
    def edit_member(self):
        """Uye duzenle"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen düzenlenecek üyeyi seçin!')
            return
        
        member_id = int(self.table.item(selected, 0).text())
        dialog = MemberDialog(self, member_id)
        if dialog.exec_() == QDialog.Accepted:
            if self.dashboard and hasattr(dialog, 'success_message'):
                self.dashboard.show_toast(dialog.success_message, 'success')
            self.load_members()
            # Dashboard'u guncelle
            if self.dashboard:
                self.dashboard.refresh_statistics()
    
    def delete_member(self):
        """Uye sil"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen silinecek üyeyi seçin!')
            return
        
        member_id = int(self.table.item(selected, 0).text())
        member_name = self.table.item(selected, 1).text()
        
        # --- TÜRKÇE SORU PENCERESİ KULLANIMI ---
        if ask_yes_no_tr(self, 'Silme Onayı', f'{member_name} adlı üyeyi silmek istediğinize emin misiniz?'):
            try:
                Member.delete(member_id)
                if self.dashboard:
                    self.dashboard.show_toast('Üye başarıyla silindi!', 'success')
                self.load_members()
                # Dashboard'u guncelle
                if self.dashboard:
                    self.dashboard.refresh_statistics()
            except Exception as e:
                QMessageBox.critical(self, 'Hata', f'Üye silinemedi: {str(e)}')


class MemberDialog(QDialog):
    """Uye ekleme/duzenleme dialog"""
    
    def __init__(self, parent=None, member_id=None):
        super().__init__(parent)
        self.member_id = member_id
        self.success_message = ''
        self.init_ui()
        
        if member_id:
            self.load_member_data()
    
    def init_ui(self):
        """UI olustur"""
        title = 'Üye Düzenle' if self.member_id else 'Yeni Üye Ekle'
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        self.ad_soyad_input = QLineEdit()
        layout.addRow('Ad Soyad:', self.ad_soyad_input)
        
        self.email_input = QLineEdit()
        layout.addRow('Email:', self.email_input)
        
        self.telefon_input = QLineEdit()
        self.telefon_input.setMaxLength(10)
        layout.addRow('Telefon:', self.telefon_input)
        
        self.adres_input = QLineEdit()
        layout.addRow('Adres:', self.adres_input)
        
        self.aktif_combo = QComboBox()
        self.aktif_combo.addItems(['Aktif', 'Pasif'])
        layout.addRow('Durum:', self.aktif_combo)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton('Kaydet')
        save_btn.clicked.connect(self.save_member)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('İptal')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def load_member_data(self):
        """Uye verilerini yukle"""
        try:
            member = Member.get_by_id(self.member_id)
            if member:
                ad_soyad = f"{member['Ad']} {member['Soyad']}"
                self.ad_soyad_input.setText(ad_soyad)
                self.email_input.setText(member['Email'] or '')
                self.telefon_input.setText(member['Telefon'] or '')
                self.adres_input.setText(member['Adres'] or '')
                self.aktif_combo.setCurrentIndex(0 if member.get('AktifMi', True) else 1)
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Üye bilgileri yüklenemedi: {str(e)}')
    
    def save_member(self):
        """Uye kaydet"""
        ad_soyad = self.ad_soyad_input.text().strip()
        email = self.email_input.text().strip()
        telefon = self.telefon_input.text().strip()
        adres = self.adres_input.text().strip()
        aktif = self.aktif_combo.currentIndex() == 0
        
        # Validasyon
        if not ad_soyad:
            QMessageBox.warning(self, 'Uyarı', 'Ad Soyad boş olamaz!')
            return
        
        if not email:
            QMessageBox.warning(self, 'Uyarı', 'Email boş olamaz!')
            return
        
        # Ad ve Soyad'ı ayır
        parts = ad_soyad.split(' ', 1)
        ad = parts[0]
        soyad = parts[1] if len(parts) > 1 else ''
        
        try:
            if self.member_id:
                # Guncelleme
                success, message = Member.update(
                    self.member_id, 
                    ad=ad, 
                    soyad=soyad, 
                    email=email, 
                    telefon=telefon, 
                    adres=adres, 
                    aktif_mi=aktif
                )
                if success:
                    self.success_message = 'Üye başarıyla güncellendi!'
                    self.accept()
                else:
                    QMessageBox.warning(self, 'Hata', message)
            else:
                # Yeni ekleme
                success, result = Member.create(ad, soyad, email, telefon, adres)
                if success:
                    self.success_message = f'Yeni üye eklendi! (ID: {result})'
                    self.accept()
                else:
                    QMessageBox.warning(self, 'Hata', result)
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Kayıt hatası: {str(e)}')