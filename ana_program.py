"""
ana_program.py
----------------
Kuyruk teorisi analizlerini uçtan uca çalıştırır:
  1) Havuzlama (pooling) karşılaştırması: M/M/1 vs M/M/c
  2) Optimum gişe sayısı (maliyet minimizasyonu)
  3) Üç görselin üretilmesi

Kullanım:
    python ana_program.py
"""

from veri import (
    LAMBDA_HAVUZLAMA, MU_TEK_GISE, MU_COKLU_GISE, SUNUCU_SAYISI_COKLU,
    LAMBDA_MALIYET, MU_MALIYET, SUNUCU_MALIYETI_SAAT, BEKLEME_MALIYETI_SAAT, SUNUCU_ARALIGI,
)
from kuyruk_modelleri import mm1_metrikleri, mmc_metrikleri, toplam_maliyet_hesapla
from gorsellestirme import tum_gorselleri_uret


def metrik_tablosu_yazdir(baslik, metrikler):
    print(f"\n--- {baslik} ---")
    print(f"  Kullanım oranı (ρ)          : {metrikler['rho']:.3f}")
    print(f"  Boş olma olasılığı (P0)     : {metrikler['P0']:.3f}")
    print(f"  Bekleme olasılığı (Erlang-C): {metrikler['Pbekle']:.3f}")
    print(f"  Kuyruktaki ort. müşteri (Lq): {metrikler['Lq']:.3f}")
    print(f"  Sistemdeki ort. müşteri (L) : {metrikler['L']:.3f}")
    print(f"  Kuyrukta bekleme (Wq)       : {metrikler['Wq']*60:.2f} dakika")
    print(f"  Sistemde toplam süre (W)    : {metrikler['W']*60:.2f} dakika")


def maliyet_tablosu_yazdir():
    print("\n" + "=" * 70)
    print("OPTİMUM GİŞE SAYISI ANALİZİ")
    print("=" * 70)
    print(f"{'Gişe':>5}{'ρ':>8}{'Lq':>9}{'Wq(dk)':>9}{'Sun.Mly.':>11}{'Bek.Mly.':>11}{'Toplam':>11}")
    en_iyi = (None, float("inf"))
    for c in SUNUCU_ARALIGI:
        metrikler, maliyet = toplam_maliyet_hesapla(
            LAMBDA_MALIYET, MU_MALIYET, c, SUNUCU_MALIYETI_SAAT, BEKLEME_MALIYETI_SAAT
        )
        if not metrikler["kararli"]:
            print(f"{c:>5}   KARARSIZ (ρ ≥ 1) — kuyruk sınırsız büyür")
            continue
        sunucu_mly = c * SUNUCU_MALIYETI_SAAT
        bekleme_mly = maliyet - sunucu_mly
        print(f"{c:>5}{metrikler['rho']:>8.3f}{metrikler['Lq']:>9.3f}"
              f"{metrikler['Wq']*60:>9.2f}{sunucu_mly:>11,.0f}{bekleme_mly:>11,.0f}{maliyet:>11,.0f}")
        if maliyet < en_iyi[1]:
            en_iyi = (c, maliyet)
    print("-" * 70)
    print(f"OPTİMUM: {en_iyi[0]} gişe, toplam maliyet = {en_iyi[1]:,.0f} TL/saat")


if __name__ == "__main__":
    print("=" * 70)
    print("HAVUZLAMA (POOLING) KARŞILAŞTIRMASI")
    print("=" * 70)
    print(f"Talep: λ = {LAMBDA_HAVUZLAMA} müşteri/saat")

    mm1 = mm1_metrikleri(LAMBDA_HAVUZLAMA, MU_TEK_GISE)
    metrik_tablosu_yazdir(f"Senaryo A: M/M/1 — 1 hızlı gişe (μ={MU_TEK_GISE})", mm1)

    mmc = mmc_metrikleri(LAMBDA_HAVUZLAMA, MU_COKLU_GISE, SUNUCU_SAYISI_COKLU)
    metrik_tablosu_yazdir(
        f"Senaryo B: M/M/c — {SUNUCU_SAYISI_COKLU} normal gişe (μ={MU_COKLU_GISE}, "
        f"toplam kapasite={SUNUCU_SAYISI_COKLU*MU_COKLU_GISE})", mmc
    )

    maliyet_tablosu_yazdir()

    print("\nGörseller üretiliyor...")
    en_iyi_c, en_iyi_maliyet, _, _ = tum_gorselleri_uret(cikti_klasoru=".")
    print("Tamamlandı. Proje kök dizinine kaydedildi (README.md ile aynı yer):")
    print("  - sunucu_sayisi_analizi.png")
    print("  - havuzlama_karsilastirma.png")
    print("  - sistem_dagilimi.png")
