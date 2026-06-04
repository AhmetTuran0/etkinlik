import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QHeaderView, QFrame, QFormLayout, QDialog, QDateEdit)
from PyQt5.QtCore import Qt, QDate

# ==========================================
# VERİTABANI YÖNETİMİ
# ==========================================
class Veritabani:
    def __init__(self):
        self.baglanti = sqlite3.connect("etkinlik_pro_final.db")
        self.imlec = self.baglanti.cursor()
        self.tablolari_olustur()

    def tablolari_olustur(self):
        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS etkinlikler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT, bas_tarih TEXT, bit_tarih TEXT, 
                f_vip REAL, f_std REAL, f_ayk REAL
            )
        """)
        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS biletler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etkinlik_id INTEGER, etkinlik_ad TEXT, 
                katilimci_ad TEXT, kategori TEXT, fiyat REAL, tel TEXT
            )
        """)
        self.baglanti.commit()

# ==========================================
# BİLET DÜZENLEME PENCERESİ
# ==========================================
class BiletDuzenle(QDialog):
    def __init__(self, veri, fiyatlar):
        super().__init__()
        self.setWindowTitle("Bilet Düzenle")
        self.setFixedSize(350, 250)
        self.fiyatlar = fiyatlar
        
        layout = QFormLayout(self)
        self.ad = QLineEdit(str(veri[3]))
        self.tel = QLineEdit(str(veri[6]))
        self.kat = QComboBox(); self.kat.addItems(["VIP", "Standart", "Ayakta"])
        self.kat.setCurrentText(veri[4])
        
        self.lbl_bilgi = QLabel(f"Tutar: {veri[5]} TL")
        self.kat.currentIndexChanged.connect(lambda: self.lbl_bilgi.setText(f"Yeni Tutar: {self.fiyatlar[self.kat.currentText()]} TL"))
        
        btn = QPushButton("Güncelle")
        btn.clicked.connect(self.accept)
        btn.setStyleSheet("background: #2980b9; color: white; padding: 8px; font-weight: bold;")
        
        layout.addRow("Müşteri:", self.ad)
        layout.addRow("Telefon:", self.tel)
        layout.addRow("Kategori:", self.kat)
        layout.addRow(self.lbl_bilgi)
        layout.addRow(btn)

# ==========================================
# ANA UYGULAMA MOTORU (GİRİŞSİZ VERSİYON)
# ==========================================
class BiletSistemi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Veritabani()
        self.setWindowTitle("Global Ticket Terminal v2.0 (Açık Erişim)")
        self.resize(1100, 750)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.init_satis_tab()
        self.init_admin_tab()
        
        # Sekme değiştiğinde sadece raporu yenile, şifre sorma
        self.tabs.currentChanged.connect(self.sekme_degisti)
        self.etkinlik_yenile()

    def sekme_degisti(self, index):
        if index == 1: # Yönetici paneli seçildiyse
            self.rapor_yenile()

    def init_satis_tab(self):
        tab = QWidget(); layout = QHBoxLayout(tab)
        form_frame = QFrame(); form_frame.setObjectName("MainCard")
        form_frame.setStyleSheet("QFrame#MainCard { background: #f9f9f9; border-radius: 15px; border: 1px solid #ddd; }")
        f_layout = QVBoxLayout(form_frame)
        
        self.cb_etk = QComboBox()
        self.cb_kat = QComboBox(); self.cb_kat.addItems(["VIP", "Standart", "Ayakta"])
        self.in_ad = QLineEdit(); self.in_ad.setPlaceholderText("Müşteri Ad Soyad")
        self.in_tel = QLineEdit(); self.in_tel.setPlaceholderText("Telefon No")
        
        self.lbl_fiyat = QLabel("Ödenecek: 0 TL")
        self.lbl_fiyat.setStyleSheet("font-size: 24px; color: #27ae60; font-weight: bold; margin: 15px 0;")
        
        btn_sat = QPushButton("SATIŞI TAMAMLA")
        btn_sat.setStyleSheet("background: #27ae60; color: white; height: 50px; font-weight: bold; border-radius: 8px;")
        
        self.cb_etk.currentIndexChanged.connect(self.fiyat_guncelle)
        self.cb_kat.currentIndexChanged.connect(self.fiyat_guncelle)
        btn_sat.clicked.connect(self.bilet_sat)
        
        f_layout.addWidget(QLabel("<h1 style='color: #2c3e50;'>🎫 Bilet Satış</h1>"))
        f_layout.addWidget(QLabel("Aktif Etkinlik:")); f_layout.addWidget(self.cb_etk)
        f_layout.addWidget(QLabel("Kategori:")); f_layout.addWidget(self.cb_kat)
        f_layout.addWidget(QLabel("Müşteri Bilgileri:")); f_layout.addWidget(self.in_ad); f_layout.addWidget(self.in_tel)
        f_layout.addWidget(self.lbl_fiyat); f_layout.addWidget(btn_sat); f_layout.addStretch()
        
        layout.addWidget(form_frame, 2); layout.addStretch(1)
        self.tabs.addTab(tab, "Bilet Satış")

    def init_admin_tab(self):
        self.admin_tab = QWidget(); layout = QVBoxLayout(self.admin_tab)
        sub_tabs = QTabWidget()
        
        # Yeni Etkinlik
        t1 = QWidget(); fl = QFormLayout(t1); fl.setContentsMargins(20,20,20,20)
        self.a_ad = QLineEdit(); self.a_bas = QDateEdit(); self.a_bit = QDateEdit()
        self.a_bas.setCalendarPopup(True); self.a_bit.setCalendarPopup(True)
        self.a_bas.setDate(QDate.currentDate())
        self.a_bit.setDate(QDate.currentDate().addDays(7))
        self.a_v = QLineEdit(); self.a_s = QLineEdit(); self.a_a = QLineEdit()
        btn_e = QPushButton("Etkinliği Kaydet")
        btn_e.setStyleSheet("background: #34495e; color: white; height: 35px; font-weight: bold;")
        btn_e.clicked.connect(self.etkinlik_kaydet)
        fl.addRow("Etkinlik Adı:", self.a_ad); fl.addRow("Başlangıç:", self.a_bas); fl.addRow("Bitiş:", self.a_bit)
        fl.addRow("VIP Fiyat:", self.a_v); fl.addRow("Std Fiyat:", self.a_s); fl.addRow("Ayk Fiyat:", self.a_a); fl.addRow(btn_e)
        
        # Satış Kayıtları
        t2 = QWidget(); vl = QVBoxLayout(t2)
        self.tablo = QTableWidget(0, 6)
        self.tablo.setHorizontalHeaderLabels(["ID", "Etkinlik", "Müşteri", "Kategori", "Tutar", "Telefon"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows)
        
        h_btn = QHBoxLayout()
        b_edit = QPushButton("🔧 Düzenle"); b_edit.clicked.connect(self.bilet_duzenle_logic)
        b_del = QPushButton("❌ Sil"); b_del.clicked.connect(self.bilet_sil_logic)
        b_del.setStyleSheet("background: #c0392b; color: white;")
        h_btn.addWidget(b_edit); h_btn.addWidget(b_del)
        vl.addWidget(self.tablo); vl.addLayout(h_btn)
        
        sub_tabs.addTab(t1, "📅 Yeni Etkinlik")
        sub_tabs.addTab(t2, "📋 Satış Kayıtları")
        layout.addWidget(sub_tabs)
        
        self.tabs.addTab(self.admin_tab, "Yönetici Paneli")

    def etkinlik_kaydet(self):
        try:
            self.db.imlec.execute("INSERT INTO etkinlikler (ad, bas_tarih, bit_tarih, f_vip, f_std, f_ayk) VALUES (?,?,?,?,?,?)",
                (self.a_ad.text(), self.a_bas.date().toString("dd.MM.yyyy"), self.a_bit.date().toString("dd.MM.yyyy"),
                 float(self.a_v.text()), float(self.a_s.text()), float(self.a_a.text())))
            self.db.baglanti.commit()
            QMessageBox.information(self, "Başarılı", "Etkinlik eklendi.")
            self.etkinlik_yenile()
        except:
            QMessageBox.warning(self, "Hata", "Lütfen bilgileri doğru girin.")

    def bilet_sat(self):
        e = self.cb_etk.currentData()
        if not e or not self.in_ad.text(): return
        self.db.imlec.execute("INSERT INTO biletler (etkinlik_id, etkinlik_ad, katilimci_ad, kategori, fiyat, tel) VALUES (?,?,?,?,?,?)",
            (e[0], e[1], self.in_ad.text(), self.cb_kat.currentText(), self.guncel_f, self.in_tel.text()))
        self.db.baglanti.commit()
        QMessageBox.information(self, "Bilgi", "Bilet satışı başarılı.")
        self.in_ad.clear(); self.in_tel.clear()

    def etkinlik_yenile(self):
        self.cb_etk.clear()
        self.db.imlec.execute("SELECT * FROM etkinlikler")
        for e in self.db.imlec.fetchall():
            self.cb_etk.addItem(e[1], e)
        self.fiyat_guncelle()

    def fiyat_guncelle(self):
        e = self.cb_etk.currentData()
        if not e: return
        k = self.cb_kat.currentText()
        f = e[4] if k=="VIP" else e[5] if k=="Standart" else e[6]
        self.lbl_fiyat.setText(f"Ödenecek: {f} TL"); self.guncel_f = f

    def rapor_yenile(self):
        self.db.imlec.execute("SELECT id, etkinlik_ad, katilimci_ad, kategori, fiyat, tel FROM biletler")
        self.tablo.setRowCount(0)
        for row_data in self.db.imlec.fetchall():
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            for i, data in enumerate(row_data):
                self.tablo.setItem(r, i, QTableWidgetItem(str(data)))

    def bilet_sil_logic(self):
        row = self.tablo.currentRow()
        if row < 0: return
        bid = self.tablo.item(row, 0).text()
        self.db.imlec.execute("DELETE FROM biletler WHERE id=?", (bid,))
        self.db.baglanti.commit(); self.rapor_yenile()

    def bilet_duzenle_logic(self):
        row = self.tablo.currentRow()
        if row < 0: return
        bid = int(self.tablo.item(row, 0).text())
        self.db.imlec.execute("SELECT * FROM biletler WHERE id=?", (bid,))
        b_veri = self.db.imlec.fetchone()
        self.db.imlec.execute("SELECT * FROM etkinlikler WHERE id=?", (b_veri[1],))
        e_veri = self.db.imlec.fetchone()
        f_map = {"VIP": e_veri[4], "Standart": e_veri[5], "Ayakta": e_veri[6]}
        
        d = BiletDuzenle(b_veri, f_map)
        if d.exec_() == QDialog.Accepted:
            self.db.imlec.execute("UPDATE biletler SET katilimci_ad=?, kategori=?, fiyat=?, tel=? WHERE id=?",
                (d.ad.text(), d.kat.currentText(), f_map[d.kat.currentText()], d.tel.text(), bid))
            self.db.baglanti.commit(); self.rapor_yenile()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = BiletSistemi()
    win.show()
    sys.exit(app.exec_())