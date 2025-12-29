"""
Toast Notification Widget
Modern, Bootstrap tarzi bildirim balonlari (Garantili Arka Plan Fix + Zarif Tasarım)
"""

from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QFrame, QWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont

class ToastNotification(QWidget):
    """
    Modern Toast bildirim widget'ı.
    Daha zarif, küçük ve yumuşak kenarlı versiyon.
    """
    
    def __init__(self, message, parent=None, duration=3000, toast_type='info'):
        super().__init__(parent)
        self.duration = duration
        self.toast_type = toast_type
        
        # 1. PENCERE AYARLARI (Dış Kabuk - Şeffaf)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # 2. ANA LAYOUT
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 3. İÇERİK KUTUSU
        self.content_frame = QFrame()
        self.content_frame.setObjectName("ToastContentFrame")
        self.main_layout.addWidget(self.content_frame)
        
        self.setup_ui(message)
        self.setup_animation()
        
    def setup_ui(self, message):
        """UI ve Renkleri Oluştur"""
        
        # --- RENK PALETİ ---
        themes = {
            'success': ('#C3E6CB', '#155724', '#155724', '✓'),
            'error':   ('#F5C6CB', '#721C24', '#721C24', '✕'),
            'warning': ('#FFEeba', '#856404', '#856404', '⚠'),
            'info':    ('#B8DAFF', '#004085', '#004085', 'i')
        }
        
        bg_color, border_color, text_color, icon_char = themes.get(self.toast_type, themes['info'])
        
        # --- STİL DOSYASI (Zarifleştirilmiş) ---
        self.content_frame.setStyleSheet(f"""
            QFrame#ToastContentFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color}; /* Çerçeveyi incelttik (2px -> 1px) */
                border-radius: 12px; /* Köşeleri daha çok yumuşattık (8px -> 12px) */
            }}
            QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        # İçerik Layout
        inner_layout = QHBoxLayout(self.content_frame)
        # Paddingleri azalttık (Daha küçük kutu)
        # (Sol, Üst, Sağ, Alt) -> (15, 12, 20, 12) yerine:
        inner_layout.setContentsMargins(12, 8, 15, 8)
        # İkon ve yazı arası boşluğu azalttık
        inner_layout.setSpacing(10) 
        
        # 1. İKON
        icon_label = QLabel(icon_char)
        # İkon boyutunu biraz küçülttük (24px -> 20px)
        icon_label.setStyleSheet(f"color: {text_color}; font-size: 20px; font-weight: bold;")
        icon_label.setAlignment(Qt.AlignCenter)
        inner_layout.addWidget(icon_label)
        
        # 2. MESAJ
        self.label = QLabel(message)
        self.label.setWordWrap(True)
        font = QFont("Segoe UI", 10) # Fontu bir tık küçülttük (11 -> 10)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setStyleSheet(f"color: {text_color};")
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        inner_layout.addWidget(self.label)
        
        # Widget Boyutlandırma
        self.adjustSize()
        current_width = self.width()
        # Zorunlu minimum genişliği azalttık
        self.setMinimumWidth(max(250, current_width)) 
        self.setMaximumWidth(400)
        
    def setup_animation(self):
        """Animasyonlar (Değişmedi)"""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out.finished.connect(self.close)
        
        if self.duration > 0:
            QTimer.singleShot(self.duration, self.close_notification)
    
    def showEvent(self, event):
        """Konumlandırma (Sağ alt köşe)"""
        super().showEvent(event)
        if self.parent():
            parent_rect = self.parent().rect()
            # Köşeden boşluğu biraz azalttık
            target_x = parent_rect.width() - self.width() - 20
            target_y = parent_rect.height() - self.height() - 20
            self.move(target_x, target_y)
        self.fade_in.start()
    
    def close_notification(self):
        self.fade_out.start()

def show_toast(parent, message, toast_type='info', duration=3000):
    toast = ToastNotification(message, parent, duration, toast_type)
    toast.show()
    return toast