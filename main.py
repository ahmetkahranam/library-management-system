"""
Kutuphane Yonetim Sistemi - Ana Uygulama
PyQt5 GUI Uygulamasi
"""

import sys
import os
# ctypes importunu buraya taşıdım (standart olması için)
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from src.ui.login_window import LoginWindow
# --- EKLENEN KISIM 1: Patch fonksiyonunu import et ---
from src.utils.helpers import install_turkish_message_box_patch


def load_stylesheet(app):
    """QSS stil dosyasını yükle"""
    try:
        qss_path = os.path.join(os.path.dirname(__file__), 'src', 'resources', 'styles', 'main_style.qss')
        if os.path.exists(qss_path):
            with open(qss_path, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
        else:
            print(f"[WARNING] QSS dosyası bulunamadı: {qss_path}")
    except Exception as e:
        print(f"[ERROR] QSS yükleme hatası: {e}")


def main():
    """Ana uygulama fonksiyonu"""
    
    # --- EKLENEN KISIM 2: Türkçe Buton Yamasını Aktif Et ---
    # Uygulama daha başlamadan mesaj kutularını Türkçe'ye çeviriyoruz.
    install_turkish_message_box_patch()
    
    # Windows için AppUserModelID ayarla (taskbar ikonu için)
    try:
        myappid = 'com.universite.kutuphane.dbms.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        print(f"[INFO] AppUserModelID ayarlandı: {myappid}")
    except Exception as e:
        print(f"[WARNING] AppUserModelID ayarlanamadı: {e}")
    
    # High DPI desteği
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    # Uygulama olustur
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Uygulama bilgileri
    app.setApplicationName('Kutuphane Yonetim Sistemi')
    app.setOrganizationName('Universite Kutuphanesi')
    
    # Uygulama ikonu (.ico formatı - Windows taskbar için)
    icon_path = os.path.join(os.path.dirname(__file__), 'src', 'resources', 'icons', 'app_icon.ico')
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
        app.setWindowIcon(icon)
        print(f"[INFO] İkon yüklendi: {icon_path}")
    else:
        print(f"[ERROR] İkon bulunamadı: {icon_path}")
        # Fallback: PNG kullan
        icon_path = os.path.join(os.path.dirname(__file__), 'src', 'resources', 'icons', 'kutuphane.png')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            print(f"[INFO] PNG ikon yüklendi: {icon_path}")
    
    # Stil dosyasını yükle
    load_stylesheet(app)
    
    # Login ekranini goster
    login = LoginWindow()
    login.show()
    
    # Uygulamayi calistir
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()