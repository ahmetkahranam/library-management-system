USE kutuphane_db;

DELIMITER //

CREATE TRIGGER TR_ODUNC_INSERT
AFTER INSERT ON ODUNC
FOR EACH ROW
BEGIN
    UPDATE KITAP
    SET MevcutAdet = MevcutAdet - 1
    WHERE KitapID = NEW.KitapID;
    
    INSERT INTO LOG_ISLEM (TabloAdi, IslemTipi, KullaniciID, Aciklama, YeniVeri)
    VALUES (
        'ODUNC',
        'INSERT',
        NEW.KullaniciID,
        CONCAT('Trigger: Yeni odunc eklendi. OduncID: ', NEW.OduncID),
        JSON_OBJECT(
            'OduncID', NEW.OduncID,
            'UyeID', NEW.UyeID,
            'KitapID', NEW.KitapID,
            'OduncTarihi', NEW.OduncTarihi
        )
    );
END //

CREATE TRIGGER TR_ODUNC_UPDATE_TESLIM
AFTER UPDATE ON ODUNC
FOR EACH ROW
BEGIN
    IF OLD.TeslimTarihi IS NULL AND NEW.TeslimTarihi IS NOT NULL THEN
        UPDATE KITAP
        SET MevcutAdet = MevcutAdet + 1
        WHERE KitapID = NEW.KitapID;
        
        INSERT INTO LOG_ISLEM (TabloAdi, IslemTipi, KullaniciID, Aciklama, YeniVeri)
        VALUES (
            'ODUNC',
            'UPDATE',
            NEW.KullaniciID,
            CONCAT('Trigger: Kitap teslim alindi. OduncID: ', NEW.OduncID),
            JSON_OBJECT(
                'OduncID', NEW.OduncID,
                'TeslimTarihi', NEW.TeslimTarihi
            )
        );
    END IF;
END //

CREATE TRIGGER TR_CEZA_INSERT
AFTER INSERT ON CEZA
FOR EACH ROW
BEGIN
    UPDATE UYE
    SET ToplamBorc = ToplamBorc + NEW.Tutar
    WHERE UyeID = NEW.UyeID;
    
    INSERT INTO LOG_ISLEM (TabloAdi, IslemTipi, Aciklama, YeniVeri)
    VALUES (
        'CEZA',
        'INSERT',
        CONCAT('Trigger: Yeni ceza eklendi. UyeID: ', NEW.UyeID, ', Tutar: ', NEW.Tutar),
        JSON_OBJECT(
            'CezaID', NEW.CezaID,
            'UyeID', NEW.UyeID,
            'Tutar', NEW.Tutar,
            'GecikmeGunu', NEW.GecikmeGunu
        )
    );
END //

CREATE TRIGGER TR_UYE_DELETE_BLOCK
BEFORE DELETE ON UYE
FOR EACH ROW
BEGIN
    DECLARE v_AktifOdunc INT;
    DECLARE v_ToplamBorc DECIMAL(10, 2);
    
    SELECT COUNT(*) INTO v_AktifOdunc
    FROM ODUNC
    WHERE UyeID = OLD.UyeID AND TeslimTarihi IS NULL;
    
    SET v_ToplamBorc = OLD.ToplamBorc;
    
    IF v_AktifOdunc > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'HATA: Aktif oduncu olan uye silinemez!';
    END IF;
    
    IF v_ToplamBorc > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'HATA: Borcu olan uye silinemez!';
    END IF;
END //

DELIMITER ;
