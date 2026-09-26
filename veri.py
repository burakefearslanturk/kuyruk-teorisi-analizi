"""
veri.py
--------
Kuyruk teorisi analizinde kullanılacak sistem parametreleri.

İki bağımsız analiz için veri içerir:

1) HAVUZLAMA KARŞILAŞTIRMASI (Pooling)
   Aynı TOPLAM hizmet kapasitesine sahip iki farklı tasarımın karşılaştırılması:
     Senaryo A (M/M/1) : Tek, hızlı bir gişe/temsilci
     Senaryo B (M/M/c) : Aynı toplam kapasiteyi sağlayan, birden fazla
                          normal hızlı gişe/temsilci
   Bu, "tek hızlı sunucu mu, yoksa aynı kapasiteyi paylaşan çoklu sunucu mu
   daha iyi?" sorusuna sayısal bir cevap verir.

2) OPTİMUM SUNUCU SAYISI (Maliyet Optimizasyonu)
   Bir çağrı merkezi / banka gişesi örneğinde, sunucu (gişe) sayısı arttıkça
   bekleme maliyeti azalır ama işletme maliyeti artar. İkisinin toplamını
   minimize eden optimum gişe sayısı bulunur.
"""

# ---------------------------------------------------------------------------
# 1) HAVUZLAMA (POOLING) KARŞILAŞTIRMASI
# ---------------------------------------------------------------------------
LAMBDA_HAVUZLAMA = 40     # müşteri/saat (her iki senaryoda da aynı talep)

# Senaryo A: M/M/1 — tek, hızlı gişe
MU_TEK_GISE = 45          # müşteri/saat (tek gişenin hizmet hızı)

# Senaryo B: M/M/c — aynı TOPLAM kapasiteyi (45 müşteri/saat) sağlayan
# 3 normal hızlı gişe (3 x 15 = 45)
MU_COKLU_GISE = 15        # müşteri/saat (her bir gişenin hizmet hızı)
SUNUCU_SAYISI_COKLU = 3

# ---------------------------------------------------------------------------
# 2) OPTİMUM SUNUCU SAYISI (MALİYET OPTİMİZASYONU)
# ---------------------------------------------------------------------------
LAMBDA_MALIYET = 40       # müşteri/saat
MU_MALIYET = 15           # müşteri/saat/gişe

SUNUCU_MALIYETI_SAAT = 120     # TL/saat — bir gişeyi (personel+altyapı) açık tutmanın maliyeti
BEKLEME_MALIYETI_SAAT = 60     # TL/saat/müşteri — kuyrukta bekleyen bir müşterinin maliyeti
                                # (memnuniyetsizlik, kaybedilen satış, itibar kaybı vb.)

# Kararlılık koşulu (ρ = λ/(c·μ) < 1) gereği minimum gişe sayısı:
#   c_min = ceil(λ/μ) + 1 = ceil(40/15) + 1 = 3 + 1 = 4  (güvenli tarafta başlamak için)
SUNUCU_ARALIGI = range(3, 10)   # denenecek gişe sayıları (3 kararsız çıkacak, bilerek dahil edildi)
