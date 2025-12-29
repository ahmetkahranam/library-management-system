"""
Kutuphane Yonetim Sistemi - Login Ekrani
Kullanici girisi
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from src.models.user import User


class LoginWindow(QWidget):
    """Login ekrani"""
    
    # Signal: Giris basarili (user objesi doner)
    login_successful = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.init_ui()
    
    def init_ui(self):
        """UI baslangic"""
        self.setWindowTitle('Kütüphane Yönetim Sistemi - Giriş')
        self.setFixedSize(450, 550)
        self.center_window()
        
        # Pencere ikonu
        import os
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app_icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Ana widget ile arka plan
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F7FA;
            }
        """)
        
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Login kutusu (beyaz modal)
        login_box = QFrame()
        login_box.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #D0D8E2;
            }
        """)
        login_box.setMaximumWidth(400)
        
        box_layout = QVBoxLayout()
        box_layout.setSpacing(20)
        box_layout.setContentsMargins(40, 50, 40, 50)
        
        # Logo placeholder (ikon varsa eklenebilir)
        # Icon/Logo alanı
        
        # Baslik - Sadece "Kütüphane Yönetim Sistemi"
        title = QLabel('Kütüphane Yönetim Sistemi')
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet('color: #333333; background: transparent; padding: 10px;')
        box_layout.addWidget(title)
        
        box_layout.addSpacing(30)
        
        # Kullanici adi input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Kullanıcı Adı')
        self.username_input.setMinimumHeight(50)
        input_font = QFont()
        input_font.setPointSize(11)
        self.username_input.setFont(input_font)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #D0D8E2;
                border-radius: 8px;
                padding: 12px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
            QLineEdit::placeholder {
                color: #999999;
            }
        """)
        self.username_input.returnPressed.connect(self.login)
        box_layout.addWidget(self.username_input)
        
        # Sifre input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Şifre')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(50)
        self.password_input.setFont(input_font)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #D0D8E2;
                border-radius: 8px;
                padding: 12px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
            QLineEdit::placeholder {
                color: #999999;
            }
        """)
        self.password_input.returnPressed.connect(self.login)
        box_layout.addWidget(self.password_input)
        
        box_layout.addSpacing(10)
        
        # Giris butonu
        self.login_btn = QPushButton('Giriş Yap')
        self.login_btn.setMinimumHeight(50)
        btn_font = QFont()
        btn_font.setPointSize(13)
        btn_font.setBold(True)
        self.login_btn.setFont(btn_font)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A4D70;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #153d5a;
            }
            QPushButton:pressed {
                background-color: #0f2d44;
            }
        """)
        self.login_btn.clicked.connect(self.login)
        box_layout.addWidget(self.login_btn)
        
        box_layout.addSpacing(10)
        
        # Test kullanıcı bilgisi (küçük ve gri)
        info_label = QLabel('Test: admin/admin123 veya gorevli1/123456')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet('color: #999999; font-size: 9px; background: transparent;')
        box_layout.addWidget(info_label)
        
        login_box.setLayout(box_layout)
        main_layout.addWidget(login_box)
        
        self.setLayout(main_layout)
        
        # Focus
        self.username_input.setFocus()
    
    def center_window(self):
        """Pencereyi ekranin ortasina getir"""
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def login(self):
        """Giris islemi"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validasyon
        if not username:
            QMessageBox.warning(self, 'Uyarı', 'Kullanıcı adı boş olamaz!')
            self.username_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, 'Uyarı', 'Şifre boş olamaz!')
            self.password_input.setFocus()
            return
        
        # Login denemesi
        self.login_btn.setEnabled(False)
        self.login_btn.setText('Giriş yapılıyor...')
        
        user = User.login(username, password)
        
        if user:
            self.current_user = user
            self.login_successful.emit(user)
            
            # Dashboard'a gecis
            from src.ui.dashboard_window import DashboardWindow
            self.dashboard = DashboardWindow(user)
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.critical(
                self, 
                'Hata', 
                'Kullanıcı adı veya şifre hatalı!\n\nLütfen tekrar deneyin.'
            )
            self.login_btn.setEnabled(True)
            self.login_btn.setText('Giriş Yap')
            self.password_input.clear()
            self.password_input.setFocus()
    
    def keyPressEvent(self, event):
        """Klavye olaylari"""
        if event.key() == Qt.Key_Escape:
            self.close()
