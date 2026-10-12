# 🏎️ DriverBot: Otonom Yarış Arabası Yapay Zekası

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Pygame-CE](https://img.shields.io/badge/Engine-Pygame--CE-green.svg?logo=python&logoColor=white)](https://pyga.me/)
[![Stable-Baselines3](https://img.shields.io/badge/RL-Stable--Baselines3-orange.svg)](https://stable-baselines3.readthedocs.io/)
[![Algorithm](https://img.shields.io/badge/Algorithm-PPO-red.svg)](https://arxiv.org/abs/1707.06347)
[![Gymnasium](https://img.shields.io/badge/Env-Gymnasium-brightgreen.svg)](https://gymnasium.farama.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

> **Pekiştirmeli Öğrenme (Reinforcement Learning - PPO)** ile sıfırdan eğitilmiş, sanal 7 ışınlı LiDAR sensörleriyle pisti algılayan ve insan sürücülerden daha agresif yarış çizgileri (*racing line*) keşfedebilen otonom yarış simülasyonu.

---

## 📌 Proje Hakkında

**DriverBot**, 2D bir yarış pistinde bir araca kendi kendine en hızlı ve en güvenli şekilde tur atmayı öğreten uçtan uca bir Reinforcement Learning projesidir. Hazır simülasyon ortamları yerine; fizik motoru, raycasting sensörleri, spline tabanlı yarış pisti ve Gymnasium ortamı **tamamen sıfırdan** geliştirilmiştir.

Eğitim sürecinde standart RL modellerinin karşılaştığı en kritik teorik ve pratik problemler (Ödül İstismarı, İntihar Eden Ajan, Seyrek Ödül ve Görüş Mesafesi Kısıtlamaları) analiz edilerek çözülmüştür.

---

## ✨ Temel Özellikler

- **🎯 Sıfırdan 2D Fizik & Raycasting Motoru:** Arabanın hızlanma, frenleme, açısal dönüş dinamikleri ve 500 piksel menzilli 7 yönlü lazer (LiDAR) sensör sistemi.
- **🛣️ Pürüzsüz Eğrisel Pist (Catmull-Rom Splines):** Keskin virajlar, dar geçişler ve geniş apekslerden oluşan dinamik pist haritası.
- **🧠 PPO (Proximal Policy Optimization):** Sürekli eylem uzayında (Continuous Action Space) çalışan kararlı ve modern derin pekiştirmeli öğrenme politikası.
- **🏁 Geniş Dilimli (Wide-Gate) Kontrol Noktaları:** Arabayı yolun merkezine sabitlemek yerine, virajları içten/dıştan keserek kendi ideal yarış çizgisini (*racing line*) bulmasına izin veren 150px yarıçaplı görünmez kılavuzlar.
- **🏎️ İnsan vs Yapay Zeka (VS Modu):** Eğitilmiş bota karşı klavye ile birebir yarışabileceğiniz gerçek zamanlı rekabet modu.
- **👻 100 Hayalet Araba ile Evrim İzleme (Playback Modu):** Eğitimin başlangıcından (acemi/kırmızı), ortasına (orta/sarı) ve ustalık seviyesine (yeşil) kadar 100 farklı jenerasyonu aynı anda pistte izleme imkânı.

---

## 📐 Pekiştirmeli Öğrenme Mimarisi

### 1. Gözlem Uzayı (Observation Space) — `Box(8,)`
Model her karede 8 boyutlu normalize edilmiş bir vektör alır:
| İndeks | Açıklama | Değer Aralığı |
|---|---|---|
| `0 - 6` | 7 Sensör Mesafesi (`-90°` sol ile `+90°` sağ arası, 500px normalize) | `[0.0, 1.0]` |
| `7` | Arabanın Mevcut Hızı (Maksimum hıza göre normalize) | `[0.0, 1.0]` |

### 2. Eylem Uzayı (Action Space) — `Box(2,)`
| Eylem | Aralık | Anlamı |
|---|---|---|
| `action[0]` | `[-1.0, 1.0]` | Direksiyon Açısı (Sol / Sağ) |
| `action[1]` | `[-1.0, 1.0]` | Gaz / Fren (İleri / Geri) |

---

## 🔬 Karşılaşılan ve Çözülen RL Problemleri

Bu proje geliştirilirken karşılaşılan teorik engeller ve çözümleri:

```
[Problem: Reward Hacking] ──► Gaza basma ödülü verildiğinde bot pisti en dıştan dönerek
                               yolu uzattı ve daha çok puan topladı.
                               Çözüm: Hız ödülü kaldırıldı, katı zaman cezası konuldu.

[Problem: Suicidal AI]     ──► Zaman cezası kaza cezasından büyük olunca bot puan kaybetmemek
                               için 1. adımda duvara çarpıp intihar etti.
                               Çözüm: Kaza cezası zaman cezasından çok daha ağır yapıldı.

[Problem: Sparse Reward]   ──► Sadece bitiş çizgisi ödüllendirilince bot ilerlemeyi keşfedemedi
                               ve kaza yapmamak için durdu.
                               Çözüm: Yola geniş, pisti ortalamaya zorlamayan ekmek kırıntısı
                               kontrol noktaları bırakıldı.

[Problem: Miyop Sensörler] ──► 200px sensörler yüksek hızda virajları çok geç fark ettirdi.
                               Çözüm: Sensörler 7 açıya ve 500px uzunluğa çıkarıldı.
```

### Ödül Fonksiyonu Formülasyonu:
$$\text{Reward}_t = -0.005 \text{ (Zaman Cezası)} + \mathbb{I}_{\text{checkpoint}} \cdot 0.2 + \mathbb{I}_{\text{finish}} \cdot 10.0 - \mathbb{I}_{\text{crash}} \cdot 5.0$$

---

## 📁 Proje Dosya Yapısı

```plaintext
DriverBot/
├── src/
│   ├── car.py              # Araç fiziği, dönüş dinamikleri ve çizim
│   ├── env.py              # Gymnasium ortamı ve ödül mekanizması
│   ├── manual_drive.py     # İnsan kontrolü için test sürüş scripti
│   ├── sensor.py           # 7 yönlü 500px Raycasting lazer sensörü
│   └── track.py            # Spline tabanlı yarış pisti geometrisi
├── driverbot_model.zip     # Eğitilmiş hazır PPO yapay zeka modeli
├── ghost_trajectories.json # 100 jenerasyonluk evrim yörünge verisi
├── playback.py             # 100 hayalet arabayı aynı anda oynatıcı
├── race.py                 # İnsan vs Yapay Zeka yarış modu
├── requirements.txt        # Gerekli Python bağımlılıkları
├── test_model.py           # Eğitilmiş modeli pistte tek başına izleme
└── train.py                # PPO eğitim döngüsü ve yörünge kayıt sistemi
```

---

## 🚀 Hızlı Başlangıç

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/metinalperen/DriverBot.git
cd DriverBot
```

### 2. Gerekli Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

---

## 🎮 Çalıştırma Modları

### 🏆 1. Yapay Zekaya Karşı Yarış (VS Modu)
Eğitilmiş yapay zekaya meydan okuyun! Kırmızı araba sizsiniz (`WASD` veya Yön Tuşları), mavi araba ise yapay zeka.
```bash
python race.py
```

### 👁️ 2. Şampiyon Modeli İzleme
Yapay zekanın pistte tek başına attığı kusursuz turları izleyin:
```bash
python test_model.py
```

### 👻 3. 100 Hayalet Araba ile Evrimi İzleme
Yapay zekanın ilk adımlardaki rastgele bocalamalarından (Kırmızı), ortalama sürüşe (Sarı) ve kusursuz yarış çizgisine (Yeşil) uzanan evrimini aynı pistte 100 araba ile izleyin:
```bash
python playback.py
```

### 🕹️ 4. Manuel Sürüş Testi
Pisti ve araç dinamiklerini tek başınıza klavye ile test etmek için:
```bash
python src/manual_drive.py
```

### 🏋️ 5. Modeli Yeniden Eğitme
Modeli sıfırdan veya mevcut ağırlıkların üzerine daha fazla adım eğitmek için:
```bash
python train.py
```

---

## 🛠️ Kullanılan Teknolojiler

- **Dil:** Python 3.10+
- **Görselleştirme & Simülasyon:** [Pygame-CE](https://pyga.me/)
- **RL Altyapısı:** [Gymnasium](https://gymnasium.farama.org/) & [Stable-Baselines3](https://stable-baselines3.readthedocs.io/)
- **Matematik & Vektör Hesaplamaları:** [NumPy](https://numpy.org/)

---

## 👤 Geliştirici

**Metin Alperen Uçan**  
GitHub: [@metinalperen](https://github.com/metinalperen)

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır. Dilediğiniz gibi geliştirebilir, fork'layabilir ve kullanabilirsiniz.
