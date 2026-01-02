"""
Kutuphane Yonetim Sistemi - Dashboard (Ana Menu)
Ana menu ve istatistikler
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QGridLayout, QFrame, QMessageBox,
                             QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from src.models.loan import Loan
from src.models.penalty import Penalty
from src.models.member import Member
from src.models.book import Book
from src.utils.toast_notification import ToastNotification


class DashboardWindow(QMainWindow):
    """Dashboard ana pencere"""
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.current_screen_name = 'Ana Sayfa'
        self.init_ui()
        self.load_statistics()
    
    def show_toast(self, message, toast_type='success'):
        """Toast bildirim göster"""
        # CentralWidget'ı parent olarak kullan (daha güvenilir)
        parent = self.centralWidget() if hasattr(self, 'centralWidget') and self.centralWidget() else self
        toast = ToastNotification(message, parent, duration=3000, toast_type=toast_type)
        toast.show()
        toast.raise_()
        toast.activateWindow()
    
    def init_ui(self):
        """UI baslangic"""
        self.setWindowTitle(f'Kütüphane Yönetim Sistemi - {self.user.get_full_name()}')
        # Fullscreen olarak başlat
        self.showMaximized()
        
        # Pencere ikonu
        import os
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app_icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Merkezi widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked Widget (sayfa geçişleri için)
        self.stacked_widget = QStackedWidget()
        
        # Ana sayfa (dashboard home) - önce oluştur
        self.home_page = self.create_home_page()
        self.stacked_widget.addWidget(self.home_page)
        
        # Header (her zaman üstte) - home_page'den sonra oluştur
        self.header = self.create_header()
        main_layout.addWidget(self.header)
        
        main_layout.addWidget(self.stacked_widget)
        
        central_widget.setLayout(main_layout)
    
    def create_home_page(self):
        """Ana dashboard sayfası"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Istatistikler
        stats_frame = self.create_statistics_section()
        layout.addWidget(stats_frame)
        
        # Menu butonlari
        menu_frame = self.create_menu_section()
        layout.addWidget(menu_frame)
        
        # Dinamik sorgu butonu (tam genişlik, yeşil)
        dynamic_query_btn = QPushButton('📊 Dinamik Sorgu ve Raporlama')
        dynamic_query_btn.setMinimumHeight(80)
        dynamic_query_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 20px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        dynamic_query_btn.clicked.connect(self.open_dynamic_query)
        layout.addWidget(dynamic_query_btn)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_header(self):
        """Header olustur"""
        frame = QFrame()
        frame.setObjectName("header")
        frame.setStyleSheet("""
            QFrame#header {
                background-color: #1A4D70;
                border-radius: 0px;
                padding: 20px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Geri butonu (başlangıçta gizli)
        self.back_btn = QPushButton('← Ana Sayfa')
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
        """)
        self.back_btn.clicked.connect(self.go_home)
        self.back_btn.hide()  # Başlangıçta gizli
        layout.addWidget(self.back_btn)
        
        # Sayfa başlığı
        self.page_title = QLabel('Ana Sayfa')
        self.page_title.setStyleSheet('color: #FFFFFF; font-size: 20px; font-weight: bold; background: transparent;')
        layout.addWidget(self.page_title)
        
        layout.addStretch()
        
        # Hosgeldin mesaji (ad soyad + rol)
        welcome_label = QLabel(f'{self.user.get_full_name()}\n({self.user.rol})')
        welcome_label.setStyleSheet('color: #FFFFFF; font-size: 14px; background: transparent; line-height: 1.4;')
        welcome_label.setAlignment(Qt.AlignRight)
        layout.addWidget(welcome_label)
        
        # Cikis butonu
        logout_btn = QPushButton('Çıkış')
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #1A4D70;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A90E2;
                color: white;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        frame.setLayout(layout)
        return frame
    
    def create_statistics_section(self):
        """Istatistikler bolumu - Clean Code ile StatisticCard kullanarak"""
        frame = QFrame()
        frame.setStyleSheet('background-color: transparent; border: none;')
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        title = QLabel('Sistem İstatistikleri')
        title.setStyleSheet('font-size: 20px; font-weight: bold; color: #333333; background: transparent; margin-bottom: 10px;')
        layout.addWidget(title)
        
        # Grid Layout - 2 satır x 2 sütun
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        stats_grid.setContentsMargins(0, 0, 0, 0)
        
        # Statistic Cards - her biri için referans sakla
        self.stat_cards = {}
        
        # Toplam Üye - Mavi
        member_card = StatisticCard('Toplam Üye', '0', '#4A90E2')
        self.stat_cards['Toplam Üye'] = member_card
        stats_grid.addWidget(member_card, 0, 0)
        
        # Toplam Kitap - Mavi
        book_card = StatisticCard('Toplam Kitap', '0', '#4A90E2')
        self.stat_cards['Toplam Kitap'] = book_card
        stats_grid.addWidget(book_card, 0, 1)
        
        # Aktif Ödünç - Turuncu
        loan_card = StatisticCard('Aktif Ödünç', '0', '#F5A623')
        self.stat_cards['Aktif Ödünç'] = loan_card
        stats_grid.addWidget(loan_card, 1, 0)
        
        # Geciken Ödünç - Kırmızı
        overdue_card = StatisticCard('Geciken Ödünç', '0', '#E74C3C')
        self.stat_cards['Geciken Ödünç'] = overdue_card
        stats_grid.addWidget(overdue_card, 1, 1)
        
        layout.addLayout(stats_grid)
        frame.setLayout(layout)
        return frame
    
    def create_menu_section(self):
        """Menu bolumu"""
        frame = QFrame()
        frame.setStyleSheet('background-color: transparent; border: none;')
        
        layout = QVBoxLayout()
        
        title = QLabel('Menü')
        title.setStyleSheet('font-size: 16px; font-weight: bold; color: #333333; background: transparent;')
        layout.addWidget(title)
        
        # Menu butonlari grid
        menu_grid = QGridLayout()
        menu_grid.setSpacing(15)
        
        # Butonlar
        # (Başlık, Fonksiyon, Renk, Colspan)
        buttons = [
            ('Üye Yönetimi', self.open_member_management, '#1A4D70', 1),
            ('Kitap Yönetimi', self.open_book_management, '#1A4D70', 1),
            ('Kategori Yönetimi', self.open_category_management, '#1A4D70', 1),
            ('Ödünç & Teslim', self.open_loan_management, '#1A4D70', 1), # İsim güncellendi
            # 'Kitap Teslim Al' butonu kaldırıldı
            ('Ceza Görüntüleme', self.open_penalty_management, '#E74C3C', 1),
            ('Raporlar', self.open_reports, '#1A4D70', 1),
        ]
        
        row, col = 0, 0
        for text, handler, color, colspan in buttons:
            btn = self.create_menu_button(text, color)
            btn.clicked.connect(handler)
            menu_grid.addWidget(btn, row, col, 1, colspan)  # row, col, rowspan, colspan
            col += colspan
            if col >= 3:  # 3 sütunluk grid
                col = 0
                row += 1
        
        layout.addLayout(menu_grid)
        frame.setLayout(layout)
        return frame
    
    def create_menu_button(self, text, color):
        """Menu butonu olustur"""
        btn = QPushButton(text)
        btn.setMinimumHeight(100)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                padding: 20px;
            }}
            QPushButton:hover {{
                background-color: #3a7bc8;
            }}
            QPushButton:pressed {{
                background-color: #2c5d8f;
            }}
        """)
        return btn
    
    def load_statistics(self):
        """Istatistikleri yukle"""
        try:
            # Uye sayisi
            members = Member.get_all()
            self.stat_cards['Toplam Üye'].update_value(len(members))
            
            # Kitap sayisi
            books = Book.get_all()
            self.stat_cards['Toplam Kitap'].update_value(len(books))
            
            # Odunc istatistikleri
            loan_stats = Loan.get_statistics()
            self.stat_cards['Aktif Ödünç'].update_value(loan_stats.get('AktifOdunc', 0))
            self.stat_cards['Geciken Ödünç'].update_value(loan_stats.get('Geciken', 0))
            
        except Exception as e:
            print(f"[DASHBOARD ERROR] Istatistik yukleme hatasi: {e}")
            # Hata durumunda varsayilan degerler
            if hasattr(self, 'stat_cards'):
                for card in self.stat_cards.values():
                    if card.value_label.text() == '0':
                        card.update_value('0')
    
    def refresh_statistics(self):
        """Istatistikleri yeniden yukle - diğer ekranlar tarafından çağrılabilir"""
        self.load_statistics()
    
    def open_category_management(self):
        """Kategori yonetimi ekranini ac"""
        from src.ui.category_window import CategoryWindow
        if not hasattr(self, 'category_window') or self.category_window is None:
            self.category_window = CategoryWindow(self)
            self.stacked_widget.addWidget(self.category_window)
        self.show_page(self.category_window, 'Kategori Yönetimi')
    
    def open_member_management(self):
        """Uye yonetimi ekranini ac"""
        from src.ui.member_management_window import MemberManagementWindow
        if not hasattr(self, 'member_window') or self.member_window is None:
            self.member_window = MemberManagementWindow(self)
            self.stacked_widget.addWidget(self.member_window)
        self.show_page(self.member_window, 'Üye Yönetimi')
    
    def open_book_management(self):
        """Kitap yonetimi ekranini ac"""
        from src.ui.book_management_window import BookManagementWindow
        if not hasattr(self, 'book_window') or self.book_window is None:
            self.book_window = BookManagementWindow(self)
            self.stacked_widget.addWidget(self.book_window)
        self.show_page(self.book_window, 'Kitap Yönetimi')
    
    def open_loan_management(self):
        """Odunc verme ekranini ac"""
        from src.ui.loan_window import LoanWindow
        if not hasattr(self, 'loan_window') or self.loan_window is None:
            self.loan_window = LoanWindow(self.user, self)
            self.stacked_widget.addWidget(self.loan_window)
        self.show_page(self.loan_window, 'Ödünç & Teslim İşlemleri')

    # open_return_management FONKSİYONU SİLİNDİ (Artık LoanWindow içinde)
    
    def open_penalty_management(self):
        """Ceza yonetimi ekranini ac"""
        from src.ui.penalty_window import PenaltyWindow
        if not hasattr(self, 'penalty_window') or self.penalty_window is None:
            self.penalty_window = PenaltyWindow(self)
            self.stacked_widget.addWidget(self.penalty_window)
        self.show_page(self.penalty_window, 'Ceza Görüntüleme')
    
    def open_reports(self):
        """Raporlar ekranini ac"""
        from src.ui.reports_window import ReportsWindow
        if not hasattr(self, 'reports_window') or self.reports_window is None:
            self.reports_window = ReportsWindow(self)
            self.stacked_widget.addWidget(self.reports_window)
        self.show_page(self.reports_window, 'Raporlar')
    
    def open_dynamic_query(self):
        """Dinamik sorgu ekranini ac"""
        from src.ui.dynamic_query_window import DynamicQueryWindow
        if not hasattr(self, 'dynamic_query_window') or self.dynamic_query_window is None:
            self.dynamic_query_window = DynamicQueryWindow(self)
            self.stacked_widget.addWidget(self.dynamic_query_window)
        self.show_page(self.dynamic_query_window, 'Dinamik Sorgu ')
    
    def show_page(self, widget, title):
        """Belirtilen sayfayı göster"""
        self.stacked_widget.setCurrentWidget(widget)
        self.page_title.setText(title)
        self.current_screen_name = title
        self.back_btn.show()
        # Sayfa yenileniyorsa load metodunu çağır
        if hasattr(widget, 'refresh_data'):
            widget.refresh_data()
    
    def go_home(self):
        """Ana sayfaya dön"""
        self.stacked_widget.setCurrentWidget(self.home_page)
        self.page_title.setText('Ana Sayfa')
        self.current_screen_name = 'Ana Sayfa'
        self.back_btn.hide()
        self.load_statistics()
    
    def logout(self):
        """Cikis yap"""
        reply = QMessageBox.question(
            self,
            'Çıkış',
            'Çıkmak istediğinize emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()
            from src.ui.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()


class StatisticCard(QFrame):
    """
    Özel İstatistik Kartı Widget
    """
    
    def __init__(self, title, value, accent_color):
        super().__init__()
        self.title_text = title
        self.value_text = str(value)
        self.accent_color = accent_color
        self.setObjectName("statCard") 
        self.init_ui()
    
    def init_ui(self):
        """UI bileşenlerini oluştur"""
        
        # 1. KART ÇERÇEVESİ
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: #FFFFFF;
                border: 1px solid #D0D8E2;
                border-radius: 12px;
                padding: 0px; 
            }}
            QFrame#statCard:hover {{
                border: 2px solid {self.accent_color};
                background-color: #F8FBFF;
                cursor: pointer;
            }}
        """)
        
        self.setMinimumHeight(140)
        self.setMaximumHeight(200)
        
        # Ana layout (Yatay)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 2. SOL RENKLİ ŞERİT
        accent_bar = QFrame()
        accent_bar.setFixedWidth(8)
        accent_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {self.accent_color};
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
                border: none;
            }}
        """)
        main_layout.addWidget(accent_bar)
        
        # 3. İÇERİK YERLEŞİMİ (Dikey)
        content_widget = QWidget()
        content_widget.setStyleSheet("border: none; background: transparent;")
        
        text_layout = QVBoxLayout(content_widget)
        text_layout.setContentsMargins(20, 15, 20, 15) 
        text_layout.setSpacing(10)
        
        # --- BAŞLIK ---
        self.title_label = QLabel(self.title_text)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-family: 'Segoe UI';
                font-size: 16px; 
                font-weight: 500;
            }
        """)
        text_layout.addWidget(self.title_label)
        
        # --- SAYI ---
        self.value_label = QLabel(self.value_text)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {self.accent_color};
                font-family: 'Segoe UI';
                font-size: 42px; 
                font-weight: bold;
                padding-bottom: 5px; 
            }}
        """)
        text_layout.addWidget(self.value_label)
        
        text_layout.addStretch()
        
        main_layout.addWidget(content_widget)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def update_value(self, new_value):
        """Kart değerini güncelle"""
        self.value_label.setText(str(new_value))