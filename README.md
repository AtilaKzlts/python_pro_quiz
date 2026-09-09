# Python Pro Sınav Sitesi (Basit Versiyon)

Flask + SQLAlchemy ile yapılmış, çocuklara / gençlere yönelik basit sınav + görsel algılama sitesi.

## Özellikler
- 6 soruluk sınav (Discord.py, Flask, AI, Computer Vision, NLP konuları)
- İlişkisel veritabanı (SQLite + Flask-SQLAlchemy)
- Kullanıcı ismi ile giriş, son skor + en yüksek skor takibi
- Sağ üstte: Genel en yüksek + kullanıcının en yüksek puanı
- Görsel yükleme + basit sınıflandırma (sonuç + güven skoru) → veritabanına kayıt
- Her sayfada footer (yazar bilgisi)

## Yerelde çalıştırma
```bash
pip install -r requirements.txt
python app.py
```
Tarayıcıda: http://127.0.0.1:5000

## PythonAnywhere'e yükleme (senin yapman gerekenler)

1. **GitHub'a yükle**
   - Yeni bir public repo oluştur (örnek isim: `python-pro-quiz`)
   - Bu klasörün içindeki tüm dosyaları yükle (app.py, templates/, static/, requirements.txt, README.md)
   - Repo public olsun.

2. **PythonAnywhere hesabı**
   - https://www.pythonanywhere.com → ücretsiz hesap aç
   - Dashboard → **Web** sekmesi → **Add a new web app**
   - Manual configuration → Python 3.10 (veya mevcut en yüksek)
   - Source code path: `/home/SENIN_KULLANICI_ADIN/python-pro-quiz` (veya yüklediğin klasör)
   - Working directory: aynı path
   - WSGI file'ı düzenle (aşağıdaki gibi):

```python
import sys
path = '/home/SENIN_KULLANICI_ADIN/python-pro-quiz'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

3. **Konsolda paketleri yükle**
   - Consoles → Bash
   ```bash
   cd ~/python-pro-quiz
   pip3.10 install --user -r requirements.txt
   ```

4. **Reload** butonuna bas. Site çalışır.

5. **Yetenek Testi** formuna proje linkini yaz:
   - GitHub repo linki
   - PythonAnywhere site linki (örnek: https://SENIN_KULLANICI_ADIN.pythonanywhere.com)

## Not
Görsel algılama kısmı ağır model (YOLO / Teachable Machine) yerine basit renk analizi kullanıyor.  
PythonAnywhere free tier'da ağır modeller genelde çalışmaz veya çok yavaştır.  
İstersen daha sonra Teachable Machine'den indirdiğin `.h5` modeli `models/` klasörüne koyup `simple_image_classify` fonksiyonunu değiştirebilirsin.
