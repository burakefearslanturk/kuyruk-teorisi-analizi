"""
kuyruk_modelleri.py
---------------------
M/M/1 ve M/M/c kuyruk modellerinin kapalı-form (analitik) formüllerini
uygular. Her iki model de "doğuş-ölüm" (birth-death) sürecinin özel
durumlarıdır; M/M/c formülleri c=1 için M/M/1 formüllerine indirgenir,
bu yüzden tek bir genel fonksiyon seti ile ikisi de hesaplanabilir.

Notasyon
--------
λ (lam)  : ortalama varış oranı (müşteri/saat)
μ (mu)   : bir sunucunun ortalama hizmet oranı (müşteri/saat)
c        : sunucu (gişe/temsilci) sayısı
a = λ/μ  : sunulan yük (offered load), Erlang cinsinden
ρ = a/c  : sunucu başına kullanım oranı (utilization) — kararlılık için ρ<1 şart
"""

import math


def kararlilik_kontrolu(lam, mu, c):
    """ρ = λ/(cμ) < 1 kararlılık koşulunu kontrol eder."""
    return lam / (c * mu) < 1


def _p0_hesapla(a, c, rho):
    """
    Sistemde hiç müşteri olmama olasılığı (P0):
        P0 = [ Σ_{n=0}^{c-1} (a^n/n!) + (a^c/c!)·(1/(1-ρ)) ]^(-1)
    """
    toplam = sum((a ** n) / math.factorial(n) for n in range(c))
    son_terim = (a ** c) / math.factorial(c) * (1 / (1 - rho))
    return 1 / (toplam + son_terim)


def mmc_metrikleri(lam, mu, c):
    """
    M/M/c kuyruk sisteminin tüm performans ölçütlerini hesaplar.
    c=1 verildiğinde otomatik olarak M/M/1 sonuçlarına indirgenir.

    Dönüş: dict —
      rho   : sunucu kullanım oranı
      P0    : sistemde 0 müşteri olma olasılığı
      Pbekle: Erlang-C — bir müşterinin beklemek zorunda kalma olasılığı
      Lq    : kuyrukta ortalama bekleyen müşteri sayısı
      L     : sistemdeki (kuyruk + hizmet) ortalama müşteri sayısı
      Wq    : kuyrukta ortalama bekleme süresi (saat)
      W     : sistemde ortalama geçirilen süre (saat, bekleme + hizmet)
      kararli: ρ<1 sağlanıyor mu
    """
    a = lam / mu
    rho = a / c

    if rho >= 1:
        return {"rho": rho, "P0": None, "Pbekle": None, "Lq": float("inf"),
                "L": float("inf"), "Wq": float("inf"), "W": float("inf"), "kararli": False}

    P0 = _p0_hesapla(a, c, rho)
    Pbekle = (a ** c) / (math.factorial(c) * (1 - rho)) * P0  # Erlang-C formülü
    Lq = Pbekle * rho / (1 - rho)
    Wq = Lq / lam
    L = Lq + a
    W = Wq + 1 / mu

    return {"rho": rho, "P0": P0, "Pbekle": Pbekle, "Lq": Lq, "L": L,
            "Wq": Wq, "W": W, "kararli": True}


def mm1_metrikleri(lam, mu):
    """M/M/1 özel durumu (c=1 ile mmc_metrikleri'nin sadeleştirilmiş hali)."""
    return mmc_metrikleri(lam, mu, c=1)


def pn_dagilimi(lam, mu, c, n_maks):
    """
    Sistemde tam olarak n müşteri bulunma olasılığını n=0..n_maks için hesaplar.
        n < c  :  P_n = (a^n / n!) · P0
        n >= c :  P_n = (a^n / (c! · c^(n-c))) · P0
    """
    a = lam / mu
    rho = a / c
    P0 = _p0_hesapla(a, c, rho)

    olasiliklar = []
    for n in range(n_maks + 1):
        if n < c:
            p_n = (a ** n) / math.factorial(n) * P0
        else:
            p_n = (a ** n) / (math.factorial(c) * (c ** (n - c))) * P0
        olasiliklar.append(p_n)
    return olasiliklar


def toplam_maliyet_hesapla(lam, mu, c, sunucu_maliyeti, bekleme_maliyeti):
    """
    Saatlik toplam sistem maliyeti = sunucu (işletme) maliyeti + bekleme maliyeti
        Toplam Maliyet = c · Cs + Cw · Lq
    Kararsız (ρ≥1) durumda maliyet sonsuz kabul edilir (kuyruk sınırsız büyür).
    """
    metrikler = mmc_metrikleri(lam, mu, c)
    if not metrikler["kararli"]:
        return metrikler, float("inf")
    maliyet = c * sunucu_maliyeti + bekleme_maliyeti * metrikler["Lq"]
    return metrikler, maliyet


if __name__ == "__main__":
    from veri import LAMBDA_HAVUZLAMA, MU_TEK_GISE, MU_COKLU_GISE, SUNUCU_SAYISI_COKLU

    print("--- Senaryo A: M/M/1 (tek hızlı gişe) ---")
    a_sonuc = mm1_metrikleri(LAMBDA_HAVUZLAMA, MU_TEK_GISE)
    for k, v in a_sonuc.items():
        print(f"  {k}: {v}")

    print("\n--- Senaryo B: M/M/c (3 normal hızlı gişe, aynı toplam kapasite) ---")
    b_sonuc = mmc_metrikleri(LAMBDA_HAVUZLAMA, MU_COKLU_GISE, SUNUCU_SAYISI_COKLU)
    for k, v in b_sonuc.items():
        print(f"  {k}: {v}")
