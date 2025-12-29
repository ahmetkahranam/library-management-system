
CREATE DATABASE IF NOT EXISTS kutuphane_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_turkish_ci;

USE kutuphane_db;


CREATE TABLE KULLANICI (
    KullaniciID INT AUTO_INCREMENT PRIMARY KEY,
    KullaniciAdi VARCHAR(50) NOT NULL UNIQUE,
    Sifre VARCHAR(255) NOT NULL,
    Rol ENUM('Admin', 'Gorevli') NOT NULL DEFAULT 'Gorevli',
    AdSoyad VARCHAR(100) NOT NULL,
    Email VARCHAR(100),
    OlusturmaTarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    AktifMi BOOLEAN DEFAULT TRUE,
    INDEX idx_kullanici_adi (KullaniciAdi),
    INDEX idx_rol (Rol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;


CREATE TABLE UYE (
    UyeID INT AUTO_INCREMENT PRIMARY KEY,
    Ad VARCHAR(50) NOT NULL,
    Soyad VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Telefon VARCHAR(15) NOT NULL,
    Adres TEXT,
    KayitTarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    ToplamBorc DECIMAL(10, 2) DEFAULT 0.00 CHECK (ToplamBorc >= 0),
    AktifMi BOOLEAN DEFAULT TRUE,
    INDEX idx_uye_ad (Ad, Soyad),
    INDEX idx_uye_email (Email),
    INDEX idx_uye_borc (ToplamBorc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;


CREATE TABLE KATEGORI (
    KategoriID INT AUTO_INCREMENT PRIMARY KEY,
    KategoriAdi VARCHAR(100) NOT NULL UNIQUE,
    Aciklama TEXT,
    INDEX idx_kategori_adi (KategoriAdi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;


CREATE TABLE KITAP (
    KitapID INT AUTO_INCREMENT PRIMARY KEY,
    KitapAdi VARCHAR(200) NOT NULL,
    Yazar VARCHAR(100) NOT NULL,
    KategoriID INT NOT NULL,
    Yayinevi VARCHAR(100),
    BasimYili YEAR,
    ISBN VARCHAR(20) UNIQUE,
    ToplamAdet INT NOT NULL DEFAULT 1 CHECK (ToplamAdet >= 0),
    MevcutAdet INT NOT NULL DEFAULT 1 CHECK (MevcutAdet >= 0),
    RafNo VARCHAR(20),
    EklenmeTarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (KategoriID) REFERENCES KATEGORI(KategoriID) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CHECK (MevcutAdet <= ToplamAdet),
    INDEX idx_kitap_adi (KitapAdi),
    INDEX idx_yazar (Yazar),
    INDEX idx_kategori (KategoriID),
    INDEX idx_mevcut_adet (MevcutAdet)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;


CREATE TABLE ODUNC (
    OduncID INT AUTO_INCREMENT PRIMARY KEY,
    UyeID INT NOT NULL,
    KitapID INT NOT NULL,
    KullaniciID INT NOT NULL,
    OduncTarihi DATE NOT NULL,
    SonTeslimTarihi DATE NOT NULL,
    TeslimTarihi DATE DEFAULT NULL,
    Notlar TEXT,
    FOREIGN KEY (UyeID) REFERENCES UYE(UyeID) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (KitapID) REFERENCES KITAP(KitapID) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (KullaniciID) REFERENCES KULLANICI(KullaniciID) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_uye (UyeID),
    INDEX idx_kitap (KitapID),
    INDEX idx_teslim_tarihi (TeslimTarihi),
    INDEX idx_son_teslim (SonTeslimTarihi),
    INDEX idx_odunc_tarihi (OduncTarihi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;


CREATE TABLE CEZA (
    CezaID INT AUTO_INCREMENT PRIMARY KEY,
    OduncID INT NULL,
    UyeID INT NOT NULL,
    Tutar DECIMAL(10, 2) NOT NULL CHECK (Tutar >= 0),
    GecikmeGunu INT NOT NULL DEFAULT 0 CHECK (GecikmeGunu >= 0),
    OlusturmaTarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    OdendiMi BOOLEAN DEFAULT FALSE,
    Aciklama TEXT,
    FOREIGN KEY (OduncID) REFERENCES ODUNC(OduncID) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (UyeID) REFERENCES UYE(UyeID) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_uye_ceza (UyeID),
    INDEX idx_odunc_ceza (OduncID),
    INDEX idx_odendi (OdendiMi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;


CREATE TABLE LOG_ISLEM (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    TabloAdi VARCHAR(50) NOT NULL,
    IslemTipi ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    IslemTarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    KullaniciID INT DEFAULT NULL,
    Aciklama TEXT,
    EskiVeri JSON,
    YeniVeri JSON,
    FOREIGN KEY (KullaniciID) REFERENCES KULLANICI(KullaniciID) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_tablo_adi (TabloAdi),
    INDEX idx_islem_tipi (IslemTipi),
    INDEX idx_islem_tarihi (IslemTarihi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

