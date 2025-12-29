"""
Kutuphane Yonetim Sistemi - Validasyon Fonksiyonlari
Input dogrulama ve validasyon islemleri
"""

import re
from datetime import datetime


def validate_email(email):
    """
    Email adresini dogrular
    
    Args:
        email (str): Dogrulanacak email adresi
        
    Returns:
        bool: Gecerli ise True, degilse False
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """
    Telefon numarasini dogrular (Turk telefon numarasi formati)
    Format: 10 haneli, 5 ile baslar
    
    Args:
        phone (str): Dogrulanacak telefon numarasi
        
    Returns:
        bool: Gecerli ise True, degilse False
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Sadece rakamlari al
    digits = re.sub(r'\D', '', phone)
    
    # 10 haneli ve 5 ile baslamali
    if len(digits) == 10 and digits.startswith('5'):
        return True
    
    return False


def validate_required(value):
    """
    Zorunlu alan kontrolu
    
    Args:
        value: Kontrol edilecek deger
        
    Returns:
        bool: Dolu ise True, bos ise False
    """
    if value is None:
        return False
    
    if isinstance(value, str):
        return bool(value.strip())
    
    return True


def validate_positive_number(value):
    """
    Pozitif sayi kontrolu
    
    Args:
        value: Kontrol edilecek deger
        
    Returns:
        bool: Pozitif sayi ise True, degilse False
    """
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False


def validate_year(year):
    """
    Gecerli bir yil kontrolu
    
    Args:
        year: Kontrol edilecek yil
        
    Returns:
        bool: Gecerli yil ise True, degilse False
    """
    try:
        year_int = int(year)
        current_year = datetime.now().year
        return 1000 <= year_int <= current_year + 1
    except (ValueError, TypeError):
        return False


def validate_isbn(isbn):
    """
    ISBN numarasi kontrolu (basit format kontrolu)
    
    Args:
        isbn (str): Kontrol edilecek ISBN
        
    Returns:
        bool: Gecerli format ise True, degilse False
    """
    if not isbn or not isinstance(isbn, str):
        return False
    
    # Sadece rakam ve tire
    cleaned = re.sub(r'[-\s]', '', isbn)
    
    # 10 veya 13 haneli olmali
    return len(cleaned) in [10, 13] and cleaned.isdigit()
