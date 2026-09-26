"""
gorsellestirme.py
-------------------
Üç görsel üretir (README.md ile aynı kök dizine kaydedilir):

  1) sunucu_sayisi_analizi.png  — Gişe sayısına göre bekleme süresi ve
                                     toplam maliyet eğrileri; optimum nokta işaretlenir.
  2) havuzlama_karsilastirma.png — M/M/1 (tek hızlı sunucu) ile M/M/c
                                     (aynı toplam kapasiteli çoklu sunucu) karşılaştırması.
  3) sistem_dagilimi.png         — Sistemdeki müşteri sayısının olasılık
                                     dağılımı (farklı gişe sayıları için).
"""

import os
import matplotlib.pyplot as plt
import numpy as np

from kuyruk_modelleri import mm1_metrikleri, mmc_metrikleri, pn_dagilimi, toplam_maliyet_hesapla


# ---------------------------------------------------------------------------
# 1) SUNUCU SAYISI ANALİZİ (maliyet optimizasyonu)
# ---------------------------------------------------------------------------
def sunucu_sayisi_analizi_ciz(lam, mu, sunucu_araligi, sunucu_maliyeti, bekleme_maliyeti,
                                 cikti_yolu="sunucu_sayisi_analizi.png"):
    c_listesi, wq_listesi_dk, maliyet_listesi = [], [], []

    for c in sunucu_araligi:
        metrikler, maliyet = toplam_maliyet_hesapla(lam, mu, c, sunucu_maliyeti, bekleme_maliyeti)
        if metrikler["kararli"]:
            c_listesi.append(c)
            wq_listesi_dk.append(metrikler["Wq"] * 60)
            maliyet_listesi.append(maliyet)

    en_iyi_idx = int(np.argmin(maliyet_listesi))
    en_iyi_c = c_listesi[en_iyi_idx]
    en_iyi_maliyet = maliyet_listesi[en_iyi_idx]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    # --- Sol panel: Bekleme süresi vs gişe sayısı ---
    ax1.plot(c_listesi, wq_listesi_dk, "o-", color="#c0392b", linewidth=2, markersize=7)
    ax1.set_xlabel("Gişe Sayısı (c)")
    ax1.set_ylabel("Ortalama Bekleme Süresi Wq (dakika)")
    ax1.set_title("Gişe Sayısı Arttıkça Bekleme Süresi Değişimi", fontsize=11, fontweight="bold")
    ax1.grid(alpha=0.3)
    ax1.set_xticks(c_listesi)

    # --- Sağ panel: Toplam maliyet vs gişe sayısı ---
    ax2.plot(c_listesi, maliyet_listesi, "o-", color="#2980b9", linewidth=2, markersize=7,
              label="Toplam Maliyet")
    sunucu_maliyet_egrisi = [c * sunucu_maliyeti for c in c_listesi]
    bekleme_maliyet_egrisi = [m - s for m, s in zip(maliyet_listesi, sunucu_maliyet_egrisi)]
    ax2.plot(c_listesi, sunucu_maliyet_egrisi, "--", color="#7f8c8d", linewidth=1.5,
              label="Sunucu (İşletme) Maliyeti")
    ax2.plot(c_listesi, bekleme_maliyet_egrisi, "--", color="#e67e22", linewidth=1.5,
              label="Bekleme Maliyeti")
    ax2.scatter([en_iyi_c], [en_iyi_maliyet], color="#27ae60", s=140, zorder=5,
                 label=f"Optimum: c={en_iyi_c}", edgecolor="black")
    ax2.annotate(f"Optimum\nc={en_iyi_c}\n{en_iyi_maliyet:,.0f} TL/saat",
                  xy=(en_iyi_c, en_iyi_maliyet), xytext=(en_iyi_c + 0.9, en_iyi_maliyet + 90),
                  fontsize=9, fontweight="bold", color="#27ae60",
                  arrowprops=dict(arrowstyle="->", color="#27ae60"))
    ax2.set_xlabel("Gişe Sayısı (c)")
    ax2.set_ylabel("Saatlik Maliyet (TL)")
    ax2.set_title("Toplam Maliyet = Sunucu Maliyeti + Bekleme Maliyeti", fontsize=11, fontweight="bold")
    ax2.legend(fontsize=8.5)
    ax2.grid(alpha=0.3)
    ax2.set_xticks(c_listesi)

    fig.suptitle(f"Optimum Gişe Sayısı Analizi (λ={lam} müşteri/saat, μ={mu} müşteri/saat/gişe)",
                  fontsize=12.5, fontweight="bold")

    if os.path.dirname(cikti_yolu):
        os.makedirs(os.path.dirname(cikti_yolu), exist_ok=True)
    plt.tight_layout()
    plt.savefig(cikti_yolu, dpi=150)
    plt.close()

    return en_iyi_c, en_iyi_maliyet


# ---------------------------------------------------------------------------
# 2) HAVUZLAMA (POOLING) KARŞILAŞTIRMASI
# ---------------------------------------------------------------------------
def havuzlama_karsilastirma_ciz(lam, mu_tek, mu_coklu, c_coklu,
                                   cikti_yolu="havuzlama_karsilastirma.png"):
    mm1 = mm1_metrikleri(lam, mu_tek)
    mmc = mmc_metrikleri(lam, mu_coklu, c_coklu)

    metrik_etiketleri = ["ρ\n(Kullanım)", "Wq (dk)\n(Kuyrukta\nBekleme)",
                          "W (dk)\n(Sistemde\nToplam Süre)", "Lq\n(Kuyruktaki\nMüşteri)"]
    mm1_degerler = [mm1["rho"], mm1["Wq"] * 60, mm1["W"] * 60, mm1["Lq"]]
    mmc_degerler = [mmc["rho"], mmc["Wq"] * 60, mmc["W"] * 60, mmc["Lq"]]

    x = np.arange(len(metrik_etiketleri))
    genislik = 0.32

    fig, ax = plt.subplots(figsize=(11, 6))
    b1 = ax.bar(x - genislik / 2, mm1_degerler, genislik,
                 label=f"Senaryo A: M/M/1 (1 gişe, μ={mu_tek})", color="#2980b9",
                 edgecolor="black", linewidth=0.7)
    b2 = ax.bar(x + genislik / 2, mmc_degerler, genislik,
                 label=f"Senaryo B: M/M/c ({c_coklu} gişe, μ={mu_coklu})", color="#e67e22",
                 edgecolor="black", linewidth=0.7)

    for bars in (b1, b2):
        for bar in bars:
            yukseklik = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yukseklik * 1.02, f"{yukseklik:.2f}",
                     ha="center", fontsize=8.5)

    ax.set_xticks(x)
    ax.set_xticklabels(metrik_etiketleri)
    ax.set_title(f"Havuzlama Karşılaştırması — Aynı Toplam Kapasite (λ={lam} müşteri/saat)\n"
                  "Tek Hızlı Gişe vs Aynı Kapasiteyi Paylaşan Çoklu Normal Gişe",
                  fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    if os.path.dirname(cikti_yolu):
        os.makedirs(os.path.dirname(cikti_yolu), exist_ok=True)
    plt.tight_layout()
    plt.savefig(cikti_yolu, dpi=150)
    plt.close()

    return mm1, mmc


# ---------------------------------------------------------------------------
# 3) SİSTEM DAĞILIMI (P_n)
# ---------------------------------------------------------------------------
def sistem_dagilimi_ciz(lam, mu, c_listesi, n_maks=15, cikti_yolu="sistem_dagilimi.png"):
    fig, ax = plt.subplots(figsize=(12, 6))

    renkler = ["#c0392b", "#27ae60", "#2980b9"]
    genislik = 0.8 / len(c_listesi)
    n_degerleri = np.arange(n_maks + 1)

    for i, c in enumerate(c_listesi):
        olasiliklar = pn_dagilimi(lam, mu, c, n_maks)
        ofset = (i - (len(c_listesi) - 1) / 2) * genislik
        ax.bar(n_degerleri + ofset, olasiliklar, genislik,
                label=f"c={c} gişe", color=renkler[i % len(renkler)],
                edgecolor="black", linewidth=0.4, alpha=0.9)

    ax.set_xlabel("Sistemdeki Müşteri Sayısı (n)")
    ax.set_ylabel("Olasılık P(n)")
    ax.set_title(f"Sistemdeki Müşteri Sayısının Olasılık Dağılımı (λ={lam}, μ={mu})",
                  fontsize=12, fontweight="bold")
    ax.set_xticks(n_degerleri)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    if os.path.dirname(cikti_yolu):
        os.makedirs(os.path.dirname(cikti_yolu), exist_ok=True)
    plt.tight_layout()
    plt.savefig(cikti_yolu, dpi=150)
    plt.close()


def tum_gorselleri_uret(cikti_klasoru="."):
    from veri import (
        LAMBDA_HAVUZLAMA, MU_TEK_GISE, MU_COKLU_GISE, SUNUCU_SAYISI_COKLU,
        LAMBDA_MALIYET, MU_MALIYET, SUNUCU_MALIYETI_SAAT, BEKLEME_MALIYETI_SAAT, SUNUCU_ARALIGI,
    )

    en_iyi_c, en_iyi_maliyet = sunucu_sayisi_analizi_ciz(
        LAMBDA_MALIYET, MU_MALIYET, SUNUCU_ARALIGI, SUNUCU_MALIYETI_SAAT, BEKLEME_MALIYETI_SAAT,
        os.path.join(cikti_klasoru, "sunucu_sayisi_analizi.png")
    )

    mm1, mmc = havuzlama_karsilastirma_ciz(
        LAMBDA_HAVUZLAMA, MU_TEK_GISE, MU_COKLU_GISE, SUNUCU_SAYISI_COKLU,
        os.path.join(cikti_klasoru, "havuzlama_karsilastirma.png")
    )

    sistem_dagilimi_ciz(
        LAMBDA_MALIYET, MU_MALIYET, [3, en_iyi_c, en_iyi_c + 2],
        cikti_yolu=os.path.join(cikti_klasoru, "sistem_dagilimi.png")
    )

    return en_iyi_c, en_iyi_maliyet, mm1, mmc
