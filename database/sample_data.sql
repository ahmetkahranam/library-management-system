USE kutuphane_db;

-- KULLANICI Tablosu
INSERT INTO KULLANICI (KullaniciAdi, Sifre, Rol, AdSoyad, Email) VALUES
('admin', 'admin123', 'Admin', 'Ahmet Yilmaz', 'admin@kutuphane.com'),
('gorevli1', '123456', 'Gorevli', 'Ayse Demir', 'ayse.demir@kutuphane.com'),
('gorevli2', '123456', 'Gorevli', 'Mehmet Kaya', 'mehmet.kaya@kutuphane.com');

-- KATEGORI Tablosu
INSERT INTO KATEGORI (KategoriAdi, Aciklama) VALUES
('Roman', 'Turk ve dunya edebiyati romanlari'),
('Bilim Kurgu', 'Bilim kurgu ve fantastik romanlar'),
('Tarih', 'Tarih ve arastirma kitaplari'),
('Bilgisayar', 'Programlama ve teknoloji kitaplari'),
('Psikoloji', 'Psikoloji ve kisisel gelisim'),
('Cocuk', 'Cocuk kitaplari'),
('Felsefe', 'Felsefe ve dusunce kitaplari'),
('Biyografi', 'Yasam hikayeleri ve anılar');

-- UYE Tablosu
INSERT INTO UYE (Ad, Soyad, Email, Telefon, Adres) VALUES
('Elif', 'Yilmaz', 'elif.yilmaz@email.com', '5551234567', 'Istanbul, Kadikoy'),
('Can', 'Ozturk', 'can.ozturk@email.com', '5551234568', 'Ankara, Cankaya'),
('Zeynep', 'Arslan', 'zeynep.arslan@email.com', '5551234569', 'Izmir, Bornova'),
('Burak', 'Celik', 'burak.celik@email.com', '5551234570', 'Bursa, Nilufer'),
('Aylin', 'Kara', 'aylin.kara@email.com', '5551234571', 'Antalya, Muratpasa'),
('Emre', 'Sahin', 'emre.sahin@email.com', '5551234572', 'Adana, Seyhan'),
('Selin', 'Yildirim', 'selin.yildirim@email.com', '5551234573', 'Konya, Selcuklu'),
('Baris', 'Aydin', 'baris.aydin@email.com', '5551234574', 'Gaziantep, Sahinbey'),
('Merve', 'Ozkan', 'merve.ozkan@email.com', '5551234575', 'Kayseri, Melikgazi'),
('Murat', 'Turkmen', 'murat.turkmen@email.com', '5551234576', 'Eskisehir, Odunpazari'),
('Deniz', 'Acar', 'deniz.acar@email.com', '5551234577', 'Diyarbakir, Baglar'),
('Gamze', 'Erdogan', 'gamze.erdogan@email.com', '5551234578', 'Samsun, Ilkadim'),
('Onur', 'Polat', 'onur.polat@email.com', '5551234579', 'Trabzon, Ortahisar'),
('Ebru', 'Gunay', 'ebru.gunay@email.com', '5551234580', 'Malatya, Battalgazi'),
('Cem', 'Dogan', 'cem.dogan@email.com', '5551234581', 'Erzurum, Yakutiye');

-- KITAP Tablosu
INSERT INTO KITAP (KitapAdi, Yazar, KategoriID, Yayinevi, BasimYili, ISBN, ToplamAdet, MevcutAdet, RafNo) VALUES
('Tutunamayanlar', 'Oguz Atay', 1, 'Iletisim Yayinlari', 1971, '9789754701159', 5, 5, 'A-101'),
('Suç ve Ceza', 'Fyodor Dostoyevski', 1, 'Is Bankasi Yayinlari', 1866, '9786053322207', 4, 4, 'A-102'),
('1984', 'George Orwell', 2, 'Can Yayinlari', 1949, '9789750718533', 6, 6, 'B-201'),
('Dune', 'Frank Herbert', 2, 'Ithaki Yayinlari', 1965, '9786257285679', 3, 3, 'B-202'),
('Nutuk', 'Mustafa Kemal Ataturk', 3, 'Is Bankasi Yayinlari', 1927, '9786053600916', 8, 8, 'C-301'),
('Sapiens', 'Yuval Noah Harari', 3, 'Kolektif Kitap', 2011, '9786053607960', 7, 7, 'C-302'),
('Python Programlama', 'Mustafa Emre Civelek', 4, 'Dikeyeksen Yayinlari', 2020, '9786257285123', 10, 10, 'D-401'),
('Clean Code', 'Robert C. Martin', 4, 'Pearson', 2008, '9780132350884', 5, 5, 'D-402'),
('Algoritma ve Veri Yapilari', 'Kadir Kircaali', 4, 'Seckin Yayinlari', 2019, '9786050650321', 6, 6, 'D-403'),
('Akil Oyunlari', 'Sinan Canan', 5, 'Say Yayinlari', 2016, '9786050918762', 4, 4, 'E-501'),
('Ikigai', 'Hector Garcia', 5, 'Indigo Kitap', 2016, '9786257285742', 5, 5, 'E-502'),
('Kucuk Prens', 'Antoine de Saint-Exupery', 6, 'Can Cocuk Yayinlari', 1943, '9789750738128', 12, 12, 'F-601'),
('Harry Potter ve Felsefe Tasi', 'J.K. Rowling', 6, 'YKY', 1997, '9789750718267', 8, 8, 'F-602'),
('Simyaci', 'Paulo Coelho', 7, 'Can Yayinlari', 1988, '9789750718342', 6, 6, 'G-701'),
('Meditations', 'Marcus Aurelius', 7, 'Is Bankasi Yayinlari', 180, '9786257285456', 3, 3, 'G-702'),
('Steve Jobs', 'Walter Isaacson', 8, 'Boyner Yayinlari', 2011, '9786053607854', 4, 4, 'H-801'),
('Einstein', 'Walter Isaacson', 8, 'Alfa Yayinlari', 2007, '9789750513237', 3, 3, 'H-802'),
('Sefiller', 'Victor Hugo', 1, 'Turkiye Is Bankasi', 1862, '9789944888530', 5, 5, 'A-103'),
('Beyaz Dis', 'Jack London', 1, 'Iletisim Yayinlari', 1906, '9789754701203', 4, 4, 'A-104'),
('Foundation', 'Isaac Asimov', 2, 'Ithaki Yayinlari', 1951, '9786257285987', 5, 5, 'B-203'),
('Neuromancer', 'William Gibson', 2, 'Ithaki Yayinlari', 1984, '9786257285321', 3, 3, 'B-204'),
('Osmanli Tarihi', 'Ilber Ortayli', 3, 'Timas Yayinlari', 2018, '9786050650789', 6, 6, 'C-303'),
('Java Programlama', 'Huseyin Eroglu', 4, 'Kodlab Yayinlari', 2021, '9786257285654', 8, 8, 'D-404'),
('JavaScript', 'Atil Samancioglu', 4, 'Seckin Yayinlari', 2020, '9786050650987', 7, 7, 'D-405'),
('Mindset', 'Carol Dweck', 5, 'Pegasus Yayinlari', 2006, '9786257285147', 4, 4, 'E-503'),
('Cesur Yeni Dunya', 'Aldous Huxley', 2, 'Ithaki Yayinlari', 1932, '9786257285369', 4, 4, 'B-205'),
('Otomatik Portakal', 'Anthony Burgess', 2, 'Ithaki Yayinlari', 1962, '9786257285743', 3, 3, 'B-206'),
('Bir Idam Mahkumunun Son Gunu', 'Victor Hugo', 1, 'Can Yayinlari', 1829, '9789750718456', 4, 4, 'A-105'),
('Agir Roman', 'Metin Kacan', 1, 'Everest Yayinlari', 1990, '9789754421231', 3, 3, 'A-106'),
('Machine Learning', 'Andrew Ng', 4, 'OReilly Media', 2019, '9781492032649', 5, 5, 'D-406');

-- ODUNC Tablosu (Aktif ve tamamlanmis oduncler)
INSERT INTO ODUNC (UyeID, KitapID, KullaniciID, OduncTarihi, SonTeslimTarihi, TeslimTarihi) VALUES
(1, 7, 2, '2025-12-01', '2025-12-16', '2025-12-15'),
(2, 10, 1, '2025-12-05', '2025-12-20', '2025-12-19'),
(3, 15, 2, '2025-12-10', '2025-12-25', NULL),
(4, 3, 1, '2025-12-12', '2025-12-27', NULL),
(5, 20, 2, '2025-12-08', '2025-12-23', NULL),
(1, 12, 1, '2025-12-15', '2025-12-30', NULL),
(6, 8, 2, '2025-12-11', '2025-12-26', NULL),
(7, 25, 1, '2025-11-20', '2025-12-05', '2025-12-10'),
(8, 18, 2, '2025-12-14', '2025-12-29', NULL),
(9, 5, 1, '2025-12-16', '2025-12-31', NULL);
