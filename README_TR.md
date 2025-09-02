# Tehloger

`tehloger` Windows Güvenlik günlüğünden **4625 – Logon Failure** olaylarını toplayıp bunları kullanıcı dostu bir şekilde raporlamayı amaçlayan basit bir Python aracıdır. Bu olay türü hem yerel oturum açma ekranından hem de ağ üzerinden (RDP, SMB paylaşımı, WinRM vb.) gelen başarısız oturum açma denemeleri için oluşturulur. Araç, olaylardaki tarih ve kullanıcı bilgilerini normalleştirir, en çok deneme yapan IP adreslerini ve kullanıcıları listeleyebilir ve istenirse JSON çıktısı üretebilir.

## Özellikler

- Windows Güvenlik günlüğünden 4625 kodlu hatalı oturum açma olaylarını okur.
- Hem yerel hem de uzak oturum açma denemelerini toplar; uzak denemelerde IP adresi ve bilgisayar adı gibi alanları gösterir.
- `pywin32` kütüphanesinin iki farklı API’sini kullanarak hem yeni (`EvtQuery`) hem de eski (`ReadEventLog`) yöntemlerle kayıt çekmeye çalışır ve gerekiyorsa otomatik olarak geri düşer.
- Çıktı üç bölümden oluşur:
  - **İnsan okunabilir liste (HUMAN READABLE)** – her bir girişin zamanını, kullanıcı adını, kaynak IP/host bilgisini, logon türünü ve durum kodunu gösterir.
  - **En çok kaynak IP ve kullanıcı** – hangi IP adreslerinden ve hangi kullanıcı adlarıyla en çok deneme yapıldığını özetler.
  - **JSON** – normalleştirilmiş olay nesnelerini JSON olarak çıktılar; `--json` parametresi ile bir dosyaya kaydedilebilir.
- Parametreler ile esnek kullanım: `--since`, `--max` ve `--json`.

## Gereksinimler

- Windows 10/11 veya sunucu sürümleri (Linux/macOS desteklenmez)
- Python 3.7+ (Python 3.9 önerilir)
- **Yönetici yetkileri (Administrator)** – Güvenlik günlüğüne erişim için gereklidir.
- Python paketleri:
  - `pywin32` – Windows olay günlüklerine erişim için
  - `PyYAML` – yapılandırma dosyasını okumak için

## Kurulum

Depoyu klonlayın veya indirin:

```bash
git clone https://github.com/talhaozbay/tehloger.git
cd tehloger
```

Bir sanal ortam oluşturup etkinleştirin (önerilir):

```bash
python -m venv venv
venv\Scripts\activate  # Windows PowerShell / Cmd
```

Gereksinimleri yükleyin:

```bash
pip install pywin32 pyyaml
```

Yapılandırma dosyasını düzeltin (`tehloger/default.yaml`):

```yaml
threshold:
  window_sec: 300   # 5 dakika penceresi
  max_fails: 3      # uyarı eşiği
max_events: 500
```

Python dosyalarını doğrudan çalıştırıyorsanız, `tehloger/main.py` içindeki göreceli içe aktarmaları mutlak hâle getirin veya aşağıdaki kullanım bölümündeki modül çağrısını tercih edin.

## Kullanım

Paket olarak çalıştırmanız önerilir:

```bash
python -m tehloger.main
```

### Parametreler

- `--max <sayı>` – Kaç adet kayıt alınacağını sınırlar.
- `--since <tarih>` – ISO 8601 biçiminde tarih (örn. `2025-09-01T00:00:00Z`).
- `--json <dosya>` – JSON çıktısını dosyaya kaydeder.

### Örnekler

```bash
# Son 200 başarısız giriş denemesini oku ve ekrana yazdır
python -m tehloger.main --max 200

# Son 24 saat içindeki olayları JSON dosyasına kaydet
python -m tehloger.main --since 2025-09-01T00:00:00Z --json C:\temp\failures.json
```

**Not:** Komutu yönetici haklarıyla çalıştırmanız gerekir.

## Zaman Damgaları ve Saat Dilimi

Olaylar varsayılan olarak **UTC** cinsinden kaydedilir (`ts_utc` alanı ISO‑8601). Türkiye saati UTC+3 olduğundan `formatters.py` içinde dönüşüm yaparak yerel saate çevirebilirsiniz.

## Yapılandırma

`configs/default.yaml` içeriği:

- `threshold.window_sec` – pencere süresi (varsayılan: 300 sn)
- `threshold.max_fails` – eşik (varsayılan: 3)
- `max_events` – alınacak olay sayısı (varsayılan: 500)

Dosya yoksa veya okunamazsa, `tehloger/config.py` içindeki varsayılan değerler kullanılır.

## Neden bazı alanlar boş?

Yerel oturum açma denemelerinde IP adresi, etki alanı adı veya uzak bilgisayar adı bulunmayabilir. Bu nedenle JSON çıktısında bu alanlar `null` görünebilir.

## Testler

Birim testi çalıştırmak için:

```bash
pip install pytest
pytest -q
```

## Lisans ve Katkılar

Bu proje kişisel bir çalışmadır ve henüz açık kaynak lisansı ile lisanslanmamıştır. Hataları bildirmek veya katkıda bulunmak için pull request veya issue açabilirsiniz. Kullanım sırasında **şirket politikalarına ve mevzuata uygun hareket etmek sizin sorumluluğunuzdadır**.
