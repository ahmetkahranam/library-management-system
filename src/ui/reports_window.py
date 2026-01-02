"""
Rapor Ekranlari - Ana Menu ve Alt Raporlar
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGridLayout, QStackedWidget, QFrame)
from PyQt5.QtCore import Qt


class ReportsWindow(QWidget):
    """Raporlar ana menu - Stacked widget ile alt sayfalar"""
    
    def __init__(self, dashboard=None):
        super().__init__()
        self.dashboard = dashboard
        self.init_ui()
    
    def init_ui(self):
        """UI olustur"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header: Geri butonu ve baslik
        header = QFrame()
        header.setStyleSheet('background: transparent; border: none;')
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Geri butonu (başlangıçta gizli)
        self.back_btn = QPushButton('← Geri')
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
        """)
        self.back_btn.clicked.connect(self.go_home)
        self.back_btn.hide()
        header_layout.addWidget(self.back_btn)
        
        # Baslik
        self.page_title = QLabel('RAPORLAR')
        self.page_title.setStyleSheet('font-size: 18px; font-weight: bold; color: #333333; background: transparent;')
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()
        
        header.setLayout(header_layout)
        main_layout.addWidget(header)
        
        # Stacked widget (sayfa geçişleri için)
        self.stacked_widget = QStackedWidget()
        
        # Ana sayfa (rapor menüsü)
        self.home_page = self.create_home_page()
        self.stacked_widget.addWidget(self.home_page)
        
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
    
    def create_home_page(self):
        """Ana rapor menusunu olustur"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Rapor butonlari
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Uye Raporu
        member_btn = QPushButton('Üye Raporları')
        member_btn.setMinimumHeight(80)
        member_btn.clicked.connect(self.open_member_report)
        grid.addWidget(member_btn, 0, 0)
        
        # Kitap Raporu
        book_btn = QPushButton('Kitap Raporları')
        book_btn.setMinimumHeight(80)
        book_btn.clicked.connect(self.open_book_report)
        grid.addWidget(book_btn, 0, 1)
        
        # Geciken Oduncler
        overdue_btn = QPushButton('Geciken Ödünçler')
        overdue_btn.setMinimumHeight(80)
        overdue_btn.clicked.connect(self.open_overdue_report)
        grid.addWidget(overdue_btn, 1, 0)
        
        # Tarih Aralığı Raporu
        loan_period_btn = QPushButton('Tarih Aralığı Raporu')
        loan_period_btn.setMinimumHeight(80)
        loan_period_btn.clicked.connect(self.open_loan_period_report)
        grid.addWidget(loan_period_btn, 1, 1)
        
        layout.addLayout(grid)
        
        # Istatistikler - Tam genişlikte en altta
        stats_btn = QPushButton('İstatistikler')
        stats_btn.setMinimumHeight(80)
        stats_btn.clicked.connect(self.open_statistics)
        layout.addWidget(stats_btn)
        layout.addStretch()
        
        page.setLayout(layout)
        return page
    
    def show_report_page(self, widget, title):
        """Alt rapor sayfasini goster"""
        self.stacked_widget.setCurrentWidget(widget)
        self.page_title.setText(title)
        self.back_btn.show()
        if hasattr(widget, 'refresh_data'):
            widget.refresh_data()
    
    def go_home(self):
        """Ana rapor menusune don"""
        self.stacked_widget.setCurrentWidget(self.home_page)
        self.page_title.setText('RAPORLAR')
        self.back_btn.hide()
    
    def refresh_data(self):
        """Sayfa yenilendiğinde çağrılır"""
        self.go_home()  # Ana menüye dön
    
    def open_member_report(self):
        """Uye raporu ac"""
        from src.ui.reports.member_report_window import MemberReportWindow
        if not hasattr(self, 'member_report'):
            self.member_report = MemberReportWindow(parent=self)
            self.stacked_widget.addWidget(self.member_report)
        self.show_report_page(self.member_report, 'Üye Raporları')
    
    def open_book_report(self):
        """Kitap raporu ac"""
        from src.ui.reports.book_report_window import BookReportWindow
        if not hasattr(self, 'book_report'):
            self.book_report = BookReportWindow(parent=self)
            self.stacked_widget.addWidget(self.book_report)
        self.show_report_page(self.book_report, 'Kitap Raporları')
    
    def open_overdue_report(self):
        """Geciken oduncler raporu ac"""
        from src.ui.reports.overdue_report_window import OverdueReportWindow
        if not hasattr(self, 'overdue_report'):
            self.overdue_report = OverdueReportWindow(parent=self)
            self.stacked_widget.addWidget(self.overdue_report)
        self.show_report_page(self.overdue_report, 'Geciken Ödünçler')
    
    def open_statistics(self):
        """Istatistikler ac"""
        from src.ui.reports.statistics_window import StatisticsWindow
        if not hasattr(self, 'statistics'):
            self.statistics = StatisticsWindow(parent=self)
            self.stacked_widget.addWidget(self.statistics)
        self.show_report_page(self.statistics, 'İstatistikler')
    
    def open_loan_period_report(self):
        """Tarih aralığı raporu ac"""
        from src.ui.reports.loan_period_report_window import LoanPeriodReportWindow
        if not hasattr(self, 'loan_period_report'):
            self.loan_period_report = LoanPeriodReportWindow(parent=self)
            self.stacked_widget.addWidget(self.loan_period_report)
        self.show_report_page(self.loan_period_report, 'Tarih Aralığı Raporu')
