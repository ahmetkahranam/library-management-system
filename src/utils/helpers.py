"""
Kutuphane Yonetim Sistemi - Yardimci Fonksiyonlar
Genel amacli utility fonksiyonlari ve Global Yamalar
"""

from datetime import datetime, date
from PyQt5.QtWidgets import QMessageBox

from .constants import (
    DATE_FORMAT,
    DISPLAY_DATE_FORMAT,
    DATETIME_FORMAT,
    GUNLUK_CEZA_TUTARI
)


def format_date_for_db(date_obj):
    if date_obj is None: return None
    if isinstance(date_obj, datetime): return date_obj.strftime(DATE_FORMAT)
    elif isinstance(date_obj, date): return date_obj.strftime(DATE_FORMAT)
    return None

def format_date_for_display(date_str):
    if not date_str: return ""
    try:
        date_obj = datetime.strptime(str(date_str), DATE_FORMAT)
        return date_obj.strftime(DISPLAY_DATE_FORMAT)
    except (ValueError, TypeError): return str(date_str)

def format_datetime_for_db(datetime_obj):
    if datetime_obj is None: return None
    if isinstance(datetime_obj, datetime): return datetime_obj.strftime(DATETIME_FORMAT)
    return None

def parse_date_from_string(date_str, format_str=DATE_FORMAT):
    if not date_str: return None
    try:
        return datetime.strptime(date_str, format_str).date()
    except (ValueError, TypeError): return None

def calculate_penalty(days_late):
    if not days_late or days_late <= 0: return 0.0
    return float(days_late) * GUNLUK_CEZA_TUTARI

def calculate_days_between(start_date, end_date):
    if start_date is None or end_date is None: return 0
    if isinstance(start_date, str): start_date = parse_date_from_string(start_date)
    if isinstance(end_date, str): end_date = parse_date_from_string(end_date)
    if isinstance(start_date, datetime): start_date = start_date.date()
    if isinstance(end_date, datetime): end_date = end_date.date()
    if start_date is None or end_date is None: return 0
    delta = end_date - start_date
    return delta.days

def normalize_turkish_chars(text):
    if not text: return text
    replacements = {'ç': 'c', 'Ç': 'C', 'ğ': 'g', 'Ğ': 'G', 'ı': 'i', 'İ': 'I', 'ö': 'o', 'Ö': 'O', 'ş': 's', 'Ş': 'S', 'ü': 'u', 'Ü': 'U'}
    for turkish, ascii_char in replacements.items():
        text = text.replace(turkish, ascii_char)
    return text

def format_currency(amount):
    if amount is None: return "0.00 TL"
    try: return f"{float(amount):.2f} TL"
    except (ValueError, TypeError): return "0.00 TL"

def truncate_text(text, max_length=50):
    if not text: return ""
    text = str(text)
    if len(text) <= max_length: return text
    return text[:max_length-3] + "..."

def safe_int(value, default=0):
    try: return int(value)
    except (ValueError, TypeError): return default

def safe_float(value, default=0.0):
    try: return float(value)
    except (ValueError, TypeError): return default

# --- ÖZEL FONKSİYONLAR (BURASI EKLENDİ) ---

def ask_yes_no_tr(parent, title, message):
    """
    Manuel olarak çağrılan Türkçe Evet/Hayır kutusu.
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Question)
    
    yes_btn = msg_box.addButton("Evet", QMessageBox.YesRole)
    no_btn = msg_box.addButton("Hayır", QMessageBox.NoRole)
    
    msg_box.exec_()
    
    return msg_box.clickedButton() == yes_btn


def install_turkish_message_box_patch():
    """
    Sistem genelindeki standart QMessageBox.question fonksiyonunu
    Türkçe butonlu haliyle değiştirir.
    """
    original_question = QMessageBox.question

    def custom_question(parent, title, text, buttons=None, defaultButton=None):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Question)
        
        yes_btn = msg_box.addButton("Evet", QMessageBox.YesRole)
        no_btn = msg_box.addButton("Hayır", QMessageBox.NoRole)
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == yes_btn:
            return QMessageBox.Yes
        else:
            return QMessageBox.No

    QMessageBox.question = custom_question