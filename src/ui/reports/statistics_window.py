"""
Istatistikler Ekrani
Modern Kart Tasarımı ve Tablo Yapısı (Okunabilirlik Düzeltildi)
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QGridLayout, QFrame, QScrollArea, QHeaderView,
                             QAbstractScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from src.models.loan import Loan
from src.models.penalty import Penalty
from src.models.member import Member
from src.models.book import Book

class StatCard(QFrame):
    """Küçük İstatistik Kartı"""
    def __init__(self, title, value="0", icon_char="📊"):
        super().__init__()
        self.title_text = title
        self.value_text = str(value)
        # Varsayılan renk, sonradan set ediliyor
        self.accent_color = "#1A4D70" 
        
        self.setObjectName("statCard")
        self.init_ui()
        
    def init_ui(self):
        # 1. Stil
        # Yükseklik sınırlarını kaldırdık/esnetik ki yazılar sığsın
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: #FFFFFF;
                border: 1px solid #D0D8E2;
                border-radius: 12px;
            }}
            QFrame#statCard:hover {{
                border: 1px solid #1A4D70;
                background-color: #F8FBFF;
            }}
        """)
        self.setMinimumHeight(120)  # Biraz daha yüksek
        
        # 2. Layout
        layout = QVBoxLayout()
        # İç boşlukları artırdık (Top, Right, Bottom, Left)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 3. Başlık
        self.lbl_title = QLabel(self.title_text)
        self.lbl_title.setStyleSheet("""
            color: #666666;
            font-family: 'Segoe UI';
            font-size: 15px; 
            font-weight: 500;
            border: none; 
            background: transparent;
        """)
        # Word wrap (uzun başlıklar alt satıra geçsin, kesilmesin)
        self.lbl_title.setWordWrap(True)
        layout.addWidget(self.lbl_title)
        
        # 4. Değer (Sayı)
        self.lbl_value = QLabel(self.value_text)
        # Padding ekleyerek alt kısmın kesilmesini önlüyoruz
        self.lbl_value.setStyleSheet(f"""
            color: {self.accent_color};
            font-family: 'Segoe UI';
            font-size: 32px; 
            font-weight: bold;
            border: none; 
            background: transparent;
            padding-bottom: 5px; 
        """)
        layout.addWidget(self.lbl_value)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def set_value(self, value):
        self.lbl_value.setText(str(value))
        
    def set_color(self, color):
        self.accent_color = color
        # Rengi güncelle
        current_style = self.lbl_value.styleSheet()
        # Basitçe yeniden set ediyoruz, string replace yerine
        self.lbl_value.setStyleSheet(f"""
            color: {self.accent_color};
            font-family: 'Segoe UI';
            font-size: 32px; 
            font-weight: bold;
            border: none; 
            background: transparent;
            padding-bottom: 5px;
        """)


class StatisticsWindow(QWidget):
    """Istatistikler ekrani"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stat_cards = {} # Kartları tutmak için
        self.init_ui()
        self.load_statistics()
    
    def init_ui(self):
        """UI olustur"""
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Sayfa Başlığı
        title = QLabel('SİSTEM İSTATİSTİKLERİ')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #3B4953;')
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background-color: transparent; }')
        
        # İçerik widget
        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(0, 20, 0, 20)
        
        # --- 1. BÖLÜM: GENEL İSTATİSTİK KARTLARI ---
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # Kart Tanımları (Başlık, Key, Satır, Sütun)
        card_defs = [
            ('Toplam Üye', 'total_members', 0, 0),
            ('Aktif Üye', 'active_members', 0, 1),
            ('Toplam Kitap', 'total_books', 0, 2),
            ('Mevcut Kitap', 'avail_books', 1, 0),
            ('Aktif Ödünç', 'active_loans', 1, 1),
            ('Geciken Ödünç', 'overdue_loans', 1, 2),
            ('Toplam Ceza Sayısı', 'total_penalties', 2, 0),
            ('Ödenmemiş Ceza', 'unpaid_penalties', 2, 1),
            ('Toplam Borç Tutarı', 'total_debt', 2, 2)
        ]
        
        for title_text, key, r, c in card_defs:
            card = StatCard(title_text)
            # Kart renklerini hafif özelleştir (Satıra göre)
            if r == 0: card.set_color("#1A4D70") # Mavi ton
            elif r == 1: card.set_color("#E67E22") # Turuncu ton (İşlemler)
            else: card.set_color("#C0392B") # Kırmızı ton (Finans/Ceza)
                
            self.stat_cards[key] = card
            grid_layout.addWidget(card, r, c)
            
        layout.addLayout(grid_layout)
        
        # --- 2. BÖLÜM: ÖDÜNÇ İSTATİSTİKLERİ TABLOSU ---
        loan_title = QLabel('Ödünç Dağılımı')
        loan_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A4D70; margin-top: 10px;")
        layout.addWidget(loan_title)
        
        self.loan_table = QTableWidget()
        self.setup_table(self.loan_table)
        layout.addWidget(self.loan_table)
        
        # --- 3. BÖLÜM: CEZA İSTATİSTİKLERİ TABLOSU ---
        penalty_title = QLabel('Ceza Durumu')
        penalty_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A4D70; margin-top: 10px;")
        layout.addWidget(penalty_title)
        
        self.penalty_table = QTableWidget()
        self.setup_table(self.penalty_table)
        layout.addWidget(self.penalty_table)
        
        # Yenile Butonu
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        self.refresh_btn = QPushButton('Verileri Yenile')
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A4D70;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #153d5a; }
        """)
        self.refresh_btn.clicked.connect(self.load_statistics)
        refresh_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(refresh_layout)
        layout.addStretch()
        
        content_widget.setLayout(layout)
        scroll.setWidget(content_widget)
        
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def setup_table(self, table_widget):
        """Tablo ayarlarını standartlaştırır"""
        table_widget.setColumnCount(2)
        table_widget.horizontalHeader().setVisible(False) # Header gizle
        table_widget.verticalHeader().setVisible(False)
        table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Scrollbar'ı kaldır - Yükseklik otomatik ayarlanacak
        table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Sütunları yay
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Stil
        table_widget.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D0D8E2;
                border-radius: 8px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #EEEEEE;
            }
        """)

    def update_table_data(self, table_widget, headers, data_rows):
        """Tabloyu verilerle doldurur ve YÜKSEKLİĞİ AYARLAR"""
        table_widget.setRowCount(len(data_rows) + 1)
        
        # 1. BAŞLIK SATIRI (Row 0)
        for col, text in enumerate(headers):
            item = QTableWidgetItem(text)
            item.setBackground(QColor('#1A4D70'))
            item.setForeground(QColor('white'))
            item.setFont(QFont('Segoe UI', 10, QFont.Bold))
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            table_widget.setItem(0, col, item)
            
        # 2. VERİ SATIRLARI
        for row_idx, row_data in enumerate(data_rows, start=1):
            # Kategori
            item_cat = QTableWidgetItem(str(row_data[0]))
            item_cat.setTextAlignment(Qt.AlignCenter)
            table_widget.setItem(row_idx, 0, item_cat)
            
            # Değer
            item_val = QTableWidgetItem(str(row_data[1]))
            item_val.setTextAlignment(Qt.AlignCenter)
            item_val.setFont(QFont('Segoe UI', 10, QFont.Bold))
            table_widget.setItem(row_idx, 1, item_val)
            
        # --- SCROLL GİZLEMEK İÇİN YÜKSEKLİK AYARI ---
        # Tablonun içeriğine göre yüksekliğini hesapla
        table_widget.resizeRowsToContents()
        
        total_height = 0
        # Tüm satırların yüksekliğini topla
        for i in range(table_widget.rowCount()):
            total_height += table_widget.rowHeight(i)
            
        # Header yüksekliği (gerçi gizli ama row 0 var) + çerçeve payı
        # Biraz pay ekleyelim (border vb için)
        table_widget.setFixedHeight(total_height + 5)

    def load_statistics(self):
        """Istatistikleri veritabanından çek ve UI güncelle"""
        try:
            # --- 1. ÜYE İSTATİSTİKLERİ ---
            members = Member.get_all()
            active_members = [m for m in members if m['AktifMi']]
            
            self.stat_cards['total_members'].set_value(len(members))
            self.stat_cards['active_members'].set_value(len(active_members))
            
            # --- 2. KİTAP İSTATİSTİKLERİ ---
            books = Book.get_all()
            total_books = sum(b['ToplamAdet'] for b in books)
            avail_books = sum(b['MevcutAdet'] for b in books)
            
            self.stat_cards['total_books'].set_value(total_books)
            self.stat_cards['avail_books'].set_value(avail_books)
            
            # --- 3. ÖDÜNÇ İSTATİSTİKLERİ ---
            loan_stats = Loan.get_statistics()
            self.stat_cards['active_loans'].set_value(loan_stats.get('AktifOdunc', 0))
            self.stat_cards['overdue_loans'].set_value(loan_stats.get('Geciken', 0))
            
            # Tablo Verisi Hazırla
            loan_data = [
                ('Toplam İşlem Hacmi', loan_stats.get('ToplamOdunc', 0)),
                ('Aktif Ödünç Verilen', loan_stats.get('AktifOdunc', 0)),
                ('Başarıyla Teslim Edilen', loan_stats.get('TeslimEdilmis', 0)),
                ('Gecikmeye Düşen', loan_stats.get('Geciken', 0))
            ]
            self.update_table_data(self.loan_table, ['İstatistik Türü', 'Adet'], loan_data)
            
            # --- 4. CEZA İSTATİSTİKLERİ ---
            penalty_stats = Penalty.get_statistics()
            self.stat_cards['total_penalties'].set_value(penalty_stats.get('ToplamCeza', 0))
            self.stat_cards['unpaid_penalties'].set_value(penalty_stats.get('OdenmemisCeza', 0))
            self.stat_cards['total_debt'].set_value(f"{penalty_stats.get('ToplamTutar', 0):.2f} TL")
            
            # Tablo Verisi Hazırla
            penalty_data = [
                ('Toplam Kesilen Ceza', f"{penalty_stats.get('ToplamTutar', 0):.2f} TL"),
                ('Tahsil Edilen Tutar', f"{penalty_stats.get('OdenenTutar', 0):.2f} TL"),
                ('Bekleyen (Ödenmemiş) Tutar', f"{penalty_stats.get('OdenmemisTutar', 0):.2f} TL")
            ]
            self.update_table_data(self.penalty_table, ['Finansal Durum', 'Tutar'], penalty_data)
            
        except Exception as e:
            print(f"Istatistik hatasi: {e}")
            QMessageBox.critical(self, 'Hata', f'İstatistikler yüklenemedi: {str(e)}')
    
    def refresh_data(self):
        """Sayfa yenilendiginde cagirilir"""
        self.load_statistics()