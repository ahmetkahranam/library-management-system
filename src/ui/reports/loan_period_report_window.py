"""
Tarih Aralığına Göre Ödünç ve İade Raporu
Belirli bir tarih aralığında ödünç alınan veya teslim edilen kitapları gösterir
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QHeaderView, QDateEdit, QGroupBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from src.database.db_manager import DatabaseManager
from datetime import datetime, timedelta


class LoanPeriodReportWindow(QWidget):
    """Tarih aralığına göre ödünç ve iade raporu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.init_ui()
        # Varsayılan olarak son 30 günü göster
        self.load_report()
    
    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Başlık
        title = QLabel('TARİH ARALIĞINA GÖRE ÖDÜNÇ VE İADE RAPORU')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #3B4953;')
        layout.addWidget(title)
        
        # Filtre Grubu
        filter_group = QGroupBox('Tarih Aralığı Seçin')
        filter_group.setStyleSheet("""
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
        filter_layout = QHBoxLayout()
        
        # Başlangıç Tarihi
        filter_layout.addWidget(QLabel('Başlangıç:'))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat('dd.MM.yyyy')
        # Son 30 gün başlangıç
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setStyleSheet("""
            QDateEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 120px;
            }
        """)
        filter_layout.addWidget(self.start_date)
        
        # Bitiş Tarihi
        filter_layout.addWidget(QLabel('Bitiş:'))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat('dd.MM.yyyy')
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setStyleSheet("""
            QDateEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 120px;
            }
        """)
        filter_layout.addWidget(self.end_date)
        
        # Sorgula Butonu
        self.query_btn = QPushButton('Sorgula')
        self.query_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
        """)
        self.query_btn.clicked.connect(self.load_report)
        filter_layout.addWidget(self.query_btn)
        
        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Özet Bilgi
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("""
            font-size: 14px; 
            padding: 10px; 
            background-color: #f8f9fa; 
            border: 1px solid #ddd; 
            border-radius: 5px;
        """)
        layout.addWidget(self.summary_label)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        
        # Tablo başlıkları gizli, manuel header ekleyeceğiz
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMinimumHeight(400)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # Alt Butonlar
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton('Yenile')
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A4D70;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #153d5a;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_report)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_report(self):
        """Raporu yükle"""
        try:
            # Tarihleri al
            start_date = self.start_date.date().toString('yyyy-MM-dd')
            end_date = self.end_date.date().toString('yyyy-MM-dd')
            
            # Tarih kontrolü
            if self.start_date.date() > self.end_date.date():
                QMessageBox.warning(self, 'Uyarı', 'Başlangıç tarihi, bitiş tarihinden sonra olamaz!')
                return
            
            # SQL sorgusu: Tarih aralığında ödünç alınan VEYA teslim edilen kitaplar
            # MySQL syntax kullanımı
            query = """
                SELECT 
                    o.OduncID,
                    CONCAT(u.Ad, ' ', u.Soyad) AS UyeAdi,
                    u.Email AS UyeEmail,
                    k.KitapAdi,
                    k.Yazar,
                    o.OduncTarihi,
                    o.SonTeslimTarihi,
                    o.TeslimTarihi,
                    CASE 
                        WHEN o.TeslimTarihi IS NOT NULL AND o.TeslimTarihi > o.SonTeslimTarihi 
                        THEN DATEDIFF(o.TeslimTarihi, o.SonTeslimTarihi)
                        WHEN o.TeslimTarihi IS NULL AND CURDATE() > o.SonTeslimTarihi
                        THEN DATEDIFF(CURDATE(), o.SonTeslimTarihi)
                        ELSE 0
                    END AS GecikmeGunu,
                    IFNULL(c.Tutar, 0) AS CezaTutari
                FROM ODUNC o
                INNER JOIN UYE u ON o.UyeID = u.UyeID
                INNER JOIN KITAP k ON o.KitapID = k.KitapID
                LEFT JOIN CEZA c ON o.OduncID = c.OduncID
                WHERE 
                    (DATE(o.OduncTarihi) BETWEEN %s AND %s) 
                    OR 
                    (DATE(o.TeslimTarihi) BETWEEN %s AND %s)
                ORDER BY 
                    CASE 
                        WHEN o.TeslimTarihi IS NOT NULL THEN o.TeslimTarihi 
                        ELSE o.OduncTarihi 
                    END DESC
            """
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, (start_date, end_date, start_date, end_date))
                loans = cursor.fetchall()
                cursor.close()
            
            # Tabloyu güncelle
            self.populate_table(loans)
            
            # Özet bilgiyi güncelle
            self.update_summary(loans, start_date, end_date)
            
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Rapor yüklenirken hata oluştu:\n{str(e)}')
    
    def populate_table(self, loans):
        """Tabloyu doldur"""
        # Tablo boyutunu ayarla (başlık + veri)
        self.table.setRowCount(len(loans) + 1)
        
        # Başlık satırı ekle
        headers = ['Ödünç ID', 'Üye Adı', 'İletişim', 'Kitap Adı', 'Yazar', 
                   'Ödünç Tarihi', 'Son Teslim', 'Teslim Tarihi', 'Gecikme/Ceza']
        
        for col, header in enumerate(headers):
            header_item = QTableWidgetItem(header)
            header_item.setFont(QFont('Arial', 10, QFont.Bold))
            header_item.setForeground(QColor('white'))
            header_item.setBackground(QColor('#1A4D70'))
            header_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, col, header_item)
        
        # Veri satırları
        for row_idx, loan in enumerate(loans, start=1):
            # Dictionary'den değerleri al
            odunc_id = loan['OduncID']
            uye_adi = loan['UyeAdi']
            uye_email = loan['UyeEmail']
            kitap_adi = loan['KitapAdi']
            yazar = loan['Yazar']
            odunc_tarihi = loan['OduncTarihi']
            son_teslim = loan['SonTeslimTarihi']
            teslim_tarihi = loan['TeslimTarihi']
            gecikme_gunu = loan['GecikmeGunu']
            ceza_tutari = loan['CezaTutari']
            
            # Satır verileri
            row_data = [
                str(odunc_id),
                uye_adi,
                uye_email,
                kitap_adi,
                yazar,
                odunc_tarihi.strftime('%d.%m.%Y') if odunc_tarihi else '-',
                son_teslim.strftime('%d.%m.%Y') if son_teslim else '-',
                teslim_tarihi.strftime('%d.%m.%Y') if teslim_tarihi else 'Henüz İade Edilmedi',
            ]
            
            # Gecikme/Ceza bilgisi
            if gecikme_gunu > 0:
                gecikme_info = f'{gecikme_gunu} gün | {ceza_tutari:.2f} TL'
            else:
                gecikme_info = 'Gecikme Yok'
            row_data.append(gecikme_info)
            
            # Satırı doldur
            for col_idx, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter if col_idx in [0, 5, 6, 7, 8] else Qt.AlignLeft | Qt.AlignVCenter)
                
                # Ödünç durumuna göre renklendirme
                if teslim_tarihi is None and gecikme_gunu > 0:
                    # Henüz iade edilmemiş ve gecikmiş
                    item.setBackground(QColor('#ffebee'))
                elif gecikme_gunu > 0:
                    # İade edilmiş ama gecikmeli
                    item.setBackground(QColor('#fff3e0'))
                elif teslim_tarihi:
                    # Zamanında iade edilmiş
                    item.setBackground(QColor('#e8f5e9'))
                
                self.table.setItem(row_idx, col_idx, item)
        
        # Sütun genişliklerini ayarla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Üye
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Email
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Kitap
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Yazar
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Ödünç T.
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Son Teslim
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Teslim T.
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Gecikme
    
    def update_summary(self, loans, start_date, end_date):
        """Özet bilgiyi güncelle"""
        total = len(loans)
        returned = sum(1 for loan in loans if loan['TeslimTarihi'] is not None)  # TeslimTarihi dolu olanlar
        not_returned = total - returned
        
        # Gecikme olan kayıtlar
        delayed = sum(1 for loan in loans if loan['GecikmeGunu'] > 0)  # GecikmeGunu > 0
        
        # Toplam ceza
        total_penalty = sum(loan['CezaTutari'] for loan in loans if loan['CezaTutari'])  # CezaTutari
        
        # Tarih formatı
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        summary_text = (
            f"<b>Tarih Aralığı:</b> {start_dt.strftime('%d.%m.%Y')} - {end_dt.strftime('%d.%m.%Y')} | "
            f"<b>Toplam İşlem:</b> {total} | "
            f"<b>İade Edildi:</b> {returned} | "
            f"<b>İade Bekliyor:</b> {not_returned} | "
            f"<b>Gecikmeli:</b> {delayed} | "
            f"<b>Toplam Ceza:</b> {total_penalty:.2f} TL"
        )
        
        self.summary_label.setText(summary_text)
    
    def refresh_data(self):
        """Veriyi yenile (üst menüden çağrılabilir)"""
        self.load_report()
