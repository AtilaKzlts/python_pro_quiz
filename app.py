from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import random

app = Flask(__name__)
app.secret_key = "python_pro_secret_key_2026"  # Değiştirebilirsin
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)

# ==================== MODELLER ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    highest_score = db.Column(db.Integer, default=0)
    last_score = db.Column(db.Integer, default=0)
    scores = db.relationship("Score", backref="user", lazy=True)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Detection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    result = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== SINAV SORULARI ====================
# Konular: Discord.py, Flask, AI, Computer Vision, NLP
QUESTIONS = [
    {
        "id": 1,
        "topic": "Discord.py - Sohbet Botu",
        "question": "Discord.py ile bot oluştururken botun token'ını saklamak için en güvenli yöntem hangisidir?",
        "options": [
            "Kodun içine yazmak",
            "Ortam değişkeni (environment variable) kullanmak",
            "Herkese açık GitHub'da paylaşmak",
            "Ekran görüntüsü almak"
        ],
        "answer": 1
    },
    {
        "id": 2,
        "topic": "Flask - Web Geliştirme",
        "question": "Flask'ta bir route tanımlamak için hangi dekoratör kullanılır?",
        "options": [
            "@app.route()",
            "@flask.path()",
            "@web.page()",
            "@server.get()"
        ],
        "answer": 0
    },
    {
        "id": 3,
        "topic": "Yapay Zeka (AI)",
        "question": "Python'da yapay zeka modelleri eğitmek için en çok kullanılan kütüphanelerden biri hangisidir?",
        "options": [
            "Requests",
            "TensorFlow veya PyTorch",
            "BeautifulSoup",
            "Flask"
        ],
        "answer": 1
    },
    {
        "id": 4,
        "topic": "Computer Vision",
        "question": "Görüntüdeki nesneleri tespit etmek (object detection) için hangi teknik kullanılır?",
        "options": [
            "Sadece metin okuma",
            "YOLO veya benzeri modeller",
            "Sadece ses tanıma",
            "Dosya silme"
        ],
        "answer": 1
    },
    {
        "id": 5,
        "topic": "Doğal Dil İşleme (NLP)",
        "question": "Web sayfalarından metin çekmek için hangi kütüphane sık kullanılır?",
        "options": [
            "NLTK veya BeautifulSoup",
            "OpenCV",
            "Discord.py",
            "Pillow"
        ],
        "answer": 0
    },
    {
        "id": 6,
        "topic": "Flask + Veritabanı",
        "question": "Flask-SQLAlchemy ile veritabanı tablosu oluşturmak için hangi sınıf kullanılır?",
        "options": [
            "db.Model",
            "db.TableOnly",
            "sql.Create",
            "flask.DB"
        ],
        "answer": 0
    }
]

# ==================== YARDIMCI FONKSİYONLAR ====================
def get_or_create_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
    return user

def get_global_highest():
    result = db.session.query(db.func.max(User.highest_score)).scalar()
    return result if result is not None else 0

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"png", "jpg", "jpeg", "gif", "webp"}

# ==================== ROUTE'LAR ====================
@app.route("/")
def index():
    username = session.get("username")
    user_highest = 0
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user_highest = user.highest_score
    global_highest = get_global_highest()
    return render_template(
        "index.html",
        username=username,
        user_highest=user_highest,
        global_highest=global_highest
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username or len(username) < 2:
            flash("Lütfen en az 2 karakterlik bir isim gir.", "error")
            return redirect(url_for("login"))
        user = get_or_create_user(username)
        session["username"] = username
        flash(f"Merhaba {username}! Sınava başlayabilirsin.", "success")
        return redirect(url_for("quiz"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Çıkış yaptın.", "info")
    return redirect(url_for("index"))

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "username" not in session:
        flash("Önce ismini girmen gerekiyor.", "error")
        return redirect(url_for("login"))

    username = session["username"]
    user = get_or_create_user(username)
    global_highest = get_global_highest()

    if request.method == "POST":
        score = 0
        total = len(QUESTIONS)
        for q in QUESTIONS:
            selected = request.form.get(f"q{q['id']}")
            if selected is not None and int(selected) == q["answer"]:
                score += 1

        # Skor kaydet
        new_score = Score(user_id=user.id, score=score, total=total)
        db.session.add(new_score)

        user.last_score = score
        if score > user.highest_score:
            user.highest_score = score
        db.session.commit()

        return render_template(
            "result.html",
            score=score,
            total=total,
            username=username,
            user_highest=user.highest_score,
            global_highest=get_global_highest(),
            last_score=user.last_score
        )

    # Soruları karıştır (isteğe bağlı)
    questions = QUESTIONS.copy()
    # random.shuffle(questions)  # istersen aç

    return render_template(
        "quiz.html",
        questions=questions,
        username=username,
        user_highest=user.highest_score,
        global_highest=global_highest
    )

@app.route("/detect", methods=["GET", "POST"])
def detect():
    username = session.get("username")
    user_highest = 0
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user_highest = user.highest_score
    global_highest = get_global_highest()

    result_text = None
    confidence = None
    filename = None

    if request.method == "POST":
        if "image" not in request.files:
            flash("Dosya seçilmedi.", "error")
            return redirect(url_for("detect"))

        file = request.files["image"]
        if file.filename == "":
            flash("Dosya seçilmedi.", "error")
            return redirect(url_for("detect"))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Benzersiz isim
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # --- Basit görsel sınıflandırma (gerçek model yerine) ---
            # PythonAnywhere free tier'da ağır modeller zor çalışır.
            # Burada renk/özellik bazlı basit bir örnek + rastgele güven skoru kullanıyoruz.
            # Gerçek model istersen Teachable Machine .h5 dosyasını models/ klasörüne koyup
            # aşağıdaki kısmı değiştirebilirsin.

            result_text, confidence = simple_image_classify(filepath)

            # Veritabanına kaydet
            det = Detection(filename=filename, result=result_text, confidence=confidence)
            db.session.add(det)
            db.session.commit()

            flash("Görsel analiz edildi!", "success")
        else:
            flash("Sadece png, jpg, jpeg, gif, webp kabul edilir.", "error")

    # Son 5 tespiti göster
    recent = Detection.query.order_by(Detection.created_at.desc()).limit(5).all()

    return render_template(
        "detect.html",
        username=username,
        user_highest=user_highest,
        global_highest=global_highest,
        result=result_text,
        confidence=confidence,
        filename=filename,
        recent=recent
    )

def simple_image_classify(filepath):
    """
    Gerçek bir ML modeli yerine basit ve çalışan bir örnek.
    Renk yoğunluğuna göre kaba sınıflandırma yapar.
    Teachable Machine modeli eklemek istersen bu fonksiyonu değiştir.
    """
    try:
        from PIL import Image
        import numpy as np

        img = Image.open(filepath).convert("RGB")
        img = img.resize((64, 64))
        arr = np.array(img)

        avg_r = arr[:, :, 0].mean()
        avg_g = arr[:, :, 1].mean()
        avg_b = arr[:, :, 2].mean()

        # Çok basit kural tabanlı sınıflandırma (demo amaçlı)
        if avg_r > avg_g and avg_r > avg_b:
            label = "Kırmızımsı / Sıcak renkli nesne"
            conf = min(0.95, 0.55 + (avg_r - avg_g) / 255)
        elif avg_g > avg_r and avg_g > avg_b:
            label = "Yeşilimsi / Doğal renkli nesne"
            conf = min(0.95, 0.55 + (avg_g - avg_r) / 255)
        elif avg_b > avg_r and avg_b > avg_g:
            label = "Mavimsi / Soğuk renkli nesne"
            conf = min(0.95, 0.55 + (avg_b - avg_r) / 255)
        else:
            label = "Nötr / Dengeli renkli nesne"
            conf = 0.60

        # Biraz rastgelelik ekle (daha gerçekçi görünsün)
        conf = round(float(conf) * random.uniform(0.85, 1.0), 2)
        return label, conf
    except Exception as e:
        return f"Analiz hatası: {str(e)[:50]}", 0.0

@app.route("/about")
def about():
    username = session.get("username")
    user_highest = 0
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user_highest = user.highest_score
    return render_template(
        "about.html",
        username=username,
        user_highest=user_highest,
        global_highest=get_global_highest()
    )

# ==================== BAŞLAT ====================
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
