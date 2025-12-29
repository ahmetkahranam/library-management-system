USE kutuphane_db;

DELIMITER //

CREATE PROCEDURE sp_YeniOduncVer(
    IN p_UyeID INT,
    IN p_KitapID INT,
    IN p_KullaniciID INT
)
BEGIN
    DECLARE v_AktifOduncSayisi INT;
    DECLARE v_MevcutAdet INT;
    DECLARE v_OduncTarihi DATE;
    DECLARE v_SonTeslimTarihi DATE;
    DECLARE v_HataMesaji VARCHAR(255);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'HATA: Islem sirasinda bir hata olustu!' AS Sonuc, 0 AS Basarili;
    END;
    
    START TRANSACTION;
    
    SELECT COUNT(*) INTO v_AktifOduncSayisi
    FROM ODUNC
    WHERE UyeID = p_UyeID AND TeslimTarihi IS NULL;
    
    IF v_AktifOduncSayisi >= 5 THEN
        SET v_HataMesaji = CONCAT('HATA: Uye maksimum 5 aktif odunc alabilir. Su an aktif odunc: ', v_AktifOduncSayisi);
        SELECT v_HataMesaji AS Sonuc, 0 AS Basarili;
        ROLLBACK;
    ELSE
        SELECT MevcutAdet INTO v_MevcutAdet
        FROM KITAP
        WHERE KitapID = p_KitapID;
        
        IF v_MevcutAdet IS NULL THEN
            SELECT 'HATA: Kitap bulunamadi!' AS Sonuc, 0 AS Basarili;
            ROLLBACK;
        ELSEIF v_MevcutAdet <= 0 THEN
            SELECT 'HATA: Kitap stokta yok!' AS Sonuc, 0 AS Basarili, v_MevcutAdet AS MevcutStok;
            ROLLBACK;
        ELSE
            SET v_OduncTarihi = CURDATE();
            SET v_SonTeslimTarihi = DATE_ADD(v_OduncTarihi, INTERVAL 15 DAY);
            
            INSERT INTO ODUNC (UyeID, KitapID, KullaniciID, OduncTarihi, SonTeslimTarihi)
            VALUES (p_UyeID, p_KitapID, p_KullaniciID, v_OduncTarihi, v_SonTeslimTarihi);
            
            UPDATE KITAP
            SET MevcutAdet = MevcutAdet - 1
            WHERE KitapID = p_KitapID;
            
            INSERT INTO LOG_ISLEM (TabloAdi, IslemTipi, KullaniciID, Aciklama, YeniVeri)
            VALUES (
                'ODUNC',
                'INSERT',
                p_KullaniciID,
                CONCAT('Yeni odunc verildi. Uye: ', p_UyeID, ', Kitap: ', p_KitapID),
                JSON_OBJECT(
                    'OduncID', LAST_INSERT_ID(),
                    'UyeID', p_UyeID,
                    'KitapID', p_KitapID,
                    'OduncTarihi', v_OduncTarihi,
                    'SonTeslimTarihi', v_SonTeslimTarihi
                )
            );
            
            COMMIT;
            
            SELECT 
                'BASARILI: Odunc islemi tamamlandi!' AS Sonuc,
                1 AS Basarili,
                LAST_INSERT_ID() AS OduncID,
                v_OduncTarihi AS OduncTarihi,
                v_SonTeslimTarihi AS SonTeslimTarihi;
        END IF;
    END IF;
    
END //

CREATE PROCEDURE sp_KitapTeslimAl(
    IN p_OduncID INT,
    IN p_TeslimTarihi DATE
)
BEGIN
    DECLARE v_UyeID INT;
    DECLARE v_KitapID INT;
    DECLARE v_SonTeslimTarihi DATE;
    DECLARE v_GecikmeGunu INT;
    DECLARE v_CezaTutari DECIMAL(10, 2);
    DECLARE v_CezaID INT DEFAULT NULL;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'HATA: Islem sirasinda bir hata olustu!' AS Sonuc, 0 AS Basarili;
    END;
    
    START TRANSACTION;
    
    SELECT UyeID, KitapID, SonTeslimTarihi
    INTO v_UyeID, v_KitapID, v_SonTeslimTarihi
    FROM ODUNC
    WHERE OduncID = p_OduncID AND TeslimTarihi IS NULL;
    
    IF v_UyeID IS NULL THEN
        SELECT 'HATA: Odunc kaydi bulunamadi veya zaten teslim edilmis!' AS Sonuc, 0 AS Basarili;
        ROLLBACK;
    ELSE
        UPDATE ODUNC
        SET TeslimTarihi = p_TeslimTarihi
        WHERE OduncID = p_OduncID;
        
        UPDATE KITAP
        SET MevcutAdet = MevcutAdet + 1
        WHERE KitapID = v_KitapID;
        
        SET v_GecikmeGunu = DATEDIFF(p_TeslimTarihi, v_SonTeslimTarihi);
        
        IF v_GecikmeGunu > 0 THEN
            SET v_CezaTutari = v_GecikmeGunu * 5.00;
            
            INSERT INTO CEZA (OduncID, UyeID, Tutar, GecikmeGunu, Aciklama)
            VALUES (
                p_OduncID,
                v_UyeID,
                v_CezaTutari,
                v_GecikmeGunu,
                CONCAT('Gecikme cezasi: ', v_GecikmeGunu, ' gun gecikme')
            );
            
            SET v_CezaID = LAST_INSERT_ID();
            
            UPDATE UYE
            SET ToplamBorc = ToplamBorc + v_CezaTutari
            WHERE UyeID = v_UyeID;
        END IF;
        
        INSERT INTO LOG_ISLEM (TabloAdi, IslemTipi, Aciklama, YeniVeri)
        VALUES (
            'ODUNC',
            'UPDATE',
            CONCAT('Kitap teslim alindi. Odunc ID: ', p_OduncID),
            JSON_OBJECT(
                'OduncID', p_OduncID,
                'TeslimTarihi', p_TeslimTarihi,
                'GecikmeGunu', v_GecikmeGunu,
                'CezaTutari', IFNULL(v_CezaTutari, 0)
            )
        );
        
        COMMIT;
        
        IF v_GecikmeGunu > 0 THEN
            SELECT 
                'BASARILI: Kitap teslim alindi. Gecikme cezasi eklendi!' AS Sonuc,
                1 AS Basarili,
                v_GecikmeGunu AS GecikmeGunu,
                v_CezaTutari AS CezaTutari,
                v_CezaID AS CezaID;
        ELSE
            SELECT 
                'BASARILI: Kitap zamaninda teslim alindi.' AS Sonuc,
                1 AS Basarili,
                0 AS GecikmeGunu,
                0.00 AS CezaTutari,
                NULL AS CezaID;
        END IF;
    END IF;
    
END //

CREATE PROCEDURE sp_UyeOzetRapor(
    IN p_UyeID INT
)
BEGIN
    DECLARE v_ToplamKitapSayisi INT;
    DECLARE v_AktifOduncSayisi INT;
    DECLARE v_ToplamCeza DECIMAL(10, 2);
    DECLARE v_OdenmemisCeza DECIMAL(10, 2);
    
    SELECT COUNT(*) INTO v_ToplamKitapSayisi
    FROM ODUNC
    WHERE UyeID = p_UyeID;
    
    SELECT COUNT(*) INTO v_AktifOduncSayisi
    FROM ODUNC
    WHERE UyeID = p_UyeID AND TeslimTarihi IS NULL;
    
    SELECT IFNULL(SUM(Tutar), 0) INTO v_ToplamCeza
    FROM CEZA
    WHERE UyeID = p_UyeID;
    
    SELECT IFNULL(SUM(Tutar), 0) INTO v_OdenmemisCeza
    FROM CEZA
    WHERE UyeID = p_UyeID AND OdendiMi = FALSE;
    
    SELECT 
        u.UyeID,
        u.Ad,
        u.Soyad,
        u.Email,
        u.Telefon,
        u.ToplamBorc,
        v_ToplamKitapSayisi AS ToplamKitapSayisi,
        v_AktifOduncSayisi AS AktifOduncSayisi,
        v_ToplamCeza AS ToplamCezaTutari,
        v_OdenmemisCeza AS OdenmemisCezaTutari,
        (v_ToplamKitapSayisi - v_AktifOduncSayisi) AS TeslimEdilenKitapSayisi
    FROM UYE u
    WHERE u.UyeID = p_UyeID;
    
END //

CREATE PROCEDURE sp_KitapAra(
    IN p_KitapAdi VARCHAR(200),
    IN p_Yazar VARCHAR(100),
    IN p_KategoriID INT,
    IN p_SadeceMevcut BOOLEAN
)
BEGIN
    SELECT 
        k.KitapID,
        k.KitapAdi,
        k.Yazar,
        kat.KategoriAdi,
        k.Yayinevi,
        k.BasimYili,
        k.ISBN,
        k.ToplamAdet,
        k.MevcutAdet,
        k.RafNo,
        (k.ToplamAdet - k.MevcutAdet) AS OduncteKitapSayisi
    FROM KITAP k
    INNER JOIN KATEGORI kat ON k.KategoriID = kat.KategoriID
    WHERE 
        (p_KitapAdi IS NULL OR k.KitapAdi LIKE CONCAT('%', p_KitapAdi, '%'))
        AND (p_Yazar IS NULL OR k.Yazar LIKE CONCAT('%', p_Yazar, '%'))
        AND (p_KategoriID IS NULL OR k.KategoriID = p_KategoriID)
        AND (p_SadeceMevcut = FALSE OR k.MevcutAdet > 0)
    ORDER BY k.KitapAdi;
    
END //

CREATE PROCEDURE sp_AktifOduncSayisi(
    IN p_UyeID INT
)
BEGIN
    SELECT 
        u.UyeID,
        u.Ad,
        u.Soyad,
        COUNT(o.OduncID) AS AktifOduncSayisi,
        (5 - COUNT(o.OduncID)) AS KalanHak
    FROM UYE u
    LEFT JOIN ODUNC o ON u.UyeID = o.UyeID AND o.TeslimTarihi IS NULL
    WHERE u.UyeID = p_UyeID
    GROUP BY u.UyeID, u.Ad, u.Soyad;
    
END //

DELIMITER ;
