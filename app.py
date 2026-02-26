# API_KEY = "91e936bb9d1ae2b2671d1399359afbd6"  # <-- CHECK THIS
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os
import requests
import razorpay

from werkzeug.utils import secure_filename

from db import get_db_connection
from pest_ai import predict_pest
from soil_ai import predict_soil
from disease_solutions import DISEASE_SOLUTIONS

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

    
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})


# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

UPLOAD_FOLDER = "uploads/equipment"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



client = razorpay.Client(auth=(
    "rzp_test_R9qLSasaJ4bKfi",      # KEY_ID
    "VlAZ41FvXVi2Gvioq71gLqVy"           # KEY_SECRET
))


# ---------------- HOME ----------------
@app.route("/")
def home():
    return "ShetiMitraAI Backend Running"

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    if not request.is_json:
        return jsonify({"error":"JSON required"}),400

    data = request.get_json()
    name = data.get("name")
    mobile = data.get("mobile")
    password = data.get("password")

    if not name or not mobile or not password:
        return jsonify({"error":"All fields required"}),400

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name,mobile,password) VALUES (%s,%s,%s)",
            (name,mobile,password)
        )
        db.commit()
        return jsonify({"message":"Signup successful"})
    except:
        return jsonify({"error":"Mobile already exists"}),400

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    data = request.get_json()
    mobile = data.get("mobile")
    password = data.get("password")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, name, mobile FROM users WHERE mobile=%s AND password=%s",
        (mobile, password)
    )
    user = cursor.fetchone()

    cursor.close()
    db.close()

    if user:
        return jsonify({"message": "Login successful", "user": user})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# ---------------- ADD CROP ----------------
@app.route("/add-crop", methods=["POST"])
def add_crop():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    data = request.get_json()
    user_id = data.get("user_id")
    crop_name = data.get("crop_name")
    sowing_date = data.get("sowing_date")

    if not user_id or not crop_name or not sowing_date:
        return jsonify({"error": "All fields required"}), 400

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO crops (user_id, crop_name, sowing_date) VALUES (%s,%s,%s)",
        (user_id, crop_name, sowing_date)
    )
    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Crop saved successfully"})

# ---------------- GET USER CROPS ----------------
@app.route("/my-crops/<int:user_id>", methods=["GET"])
def my_crops(user_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, crop_name, sowing_date, created_at FROM crops WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    crops = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(crops)

# ---------------- UPDATE CROP ----------------
@app.route("/update-crop", methods=["POST"])
def update_crop():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    data = request.get_json()
    crop_id = data.get("crop_id")
    crop_name = data.get("crop_name")
    sowing_date = data.get("sowing_date")
    user_id = data.get("user_id")

    if not crop_id or not crop_name or not sowing_date or not user_id:
        return jsonify({"error": "All fields required"}), 400

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE crops SET crop_name=%s, sowing_date=%s WHERE id=%s AND user_id=%s",
        (crop_name, sowing_date, crop_id, user_id)
    )
    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Crop updated successfully"})

# ---------------- DELETE CROP ----------------
@app.route("/delete-crop/<int:crop_id>/<int:user_id>", methods=["DELETE"])
def delete_crop(crop_id, user_id):
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM crops WHERE id=%s AND user_id=%s",
        (crop_id, user_id)
    )
    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Crop deleted successfully"})

# ---------------- WALLET ----------------
@app.route("/add-wallet", methods=["POST"])
def add_wallet():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    data = request.get_json()
    user_id = data.get("user_id")
    wtype = data.get("type")
    amount = data.get("amount")
    description = data.get("description")

    if not user_id or not wtype or not amount:
        return jsonify({"error": "Required fields missing"}), 400

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO wallet (user_id, type, amount, description) VALUES (%s,%s,%s,%s)",
        (user_id, wtype, amount, description)
    )
    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Wallet entry added"})

@app.route("/wallet/<int:user_id>", methods=["GET"])
def wallet(user_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, type, amount, description, created_at FROM wallet WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()

    cursor.close()
    db.close()

    income = sum(r["amount"] for r in rows if r["type"] == "income")
    expense = sum(r["amount"] for r in rows if r["type"] == "expense")

    return jsonify({
        "income": income,
        "expense": expense,
        "balance": income - expense,
        "history": rows
    })

@app.route("/delete-wallet/<int:wallet_id>/<int:user_id>", methods=["DELETE"])
def delete_wallet(wallet_id, user_id):
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM wallet WHERE id=%s AND user_id=%s",
        (wallet_id, user_id)
    )
    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Wallet entry deleted"})

# ---------------- WEATHER ----------------
@app.route("/weather", methods=["POST"])
def weather():
    data = request.get_json()
    city = data.get("city")

    API_KEY = "91e936bb9d1ae2b2671d1399359afbd6"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()

    return jsonify({
        "city": city,
        "temperature": res["main"]["temp"],
        "humidity": res["main"]["humidity"],
        "condition": res["weather"][0]["description"]
    })

# ---------------- SOIL AI (TRI-LANGUAGE) ----------------

# ── Move these maps outside the function (module-level constants) ──
# So they are not rebuilt on every single request

SOIL_MAP = {
    "black": {"en": "Black Soil",  "mr": "काळी माती",    "hi": "काली मिट्टी"},
    "red":   {"en": "Red Soil",    "mr": "लाल माती",     "hi": "लाल मिट्टी"},
    "sandy": {"en": "Sandy Soil",  "mr": "वाळूची माती",  "hi": "रेतीली मिट्टी"},
    "clay":  {"en": "Clay Soil",   "mr": "चिकण माती",    "hi": "चिकनी मिट्टी"},
    "loam":  {"en": "Loam Soil",   "mr": "सुपीक माती",   "hi": "दोमट मिट्टी"},
}

CROP_MAP = {
    "black": [
        {"en": "Cotton",    "mr": "कापूस",       "hi": "कपास"},
        {"en": "Soybean",   "mr": "सोयाबीन",     "hi": "सोयाबीन"},
        {"en": "Wheat",     "mr": "गहू",          "hi": "गेहूँ"},       # ← added
        {"en": "Sunflower", "mr": "सूर्यफूल",    "hi": "सूरजमुखी"},    # ← added
    ],
    "red": [
        {"en": "Groundnut", "mr": "भुईमूग",      "hi": "मूंगफली"},
        {"en": "Millets",   "mr": "ज्वारी/बाजरी","hi": "बाजरा/ज्वार"},
        {"en": "Pulses",    "mr": "डाळी",         "hi": "दालें"},       # ← added
    ],
    "sandy": [
        {"en": "Watermelon","mr": "टरबूज",        "hi": "तरबूज"},
        {"en": "Peanuts",   "mr": "शेंगदाणे",    "hi": "मूंगफली"},     # ← added
        {"en": "Carrots",   "mr": "गाजर",         "hi": "गाजर"},        # ← added
    ],
    "clay": [
        {"en": "Paddy",     "mr": "भात",          "hi": "धान"},
        {"en": "Sugarcane", "mr": "ऊस",           "hi": "गन्ना"},       # ← added
    ],
    "loam": [
        {"en": "Most crops","mr": "बहुतेक पिके",  "hi": "अधिकांश फसलें"},
        {"en": "Vegetables","mr": "भाजीपाला",     "hi": "सब्जियाँ"},    # ← added
        {"en": "Fruits",    "mr": "फळे",          "hi": "फल"},          # ← added
    ],
}

# Agronomic tips per soil type (NEW — real-world value for farmers)
TIPS_MAP = {
    "black": {"en": "High water-retention. Avoid waterlogging; deep ploughing recommended.",
              "mr": "पाणी जास्त टिकते. पाणी साचणे टाळा; खोल नांगरणी करा.",
              "hi": "पानी धारण क्षमता अधिक। जलभराव से बचें; गहरी जुताई करें।"},
    "red":   {"en": "Low nutrients. Add compost; prefer drought-tolerant crops.",
              "mr": "पोषणे कमी. कंपोस्ट घाला; दुष्काळ-सहनशील पिके निवडा.",
              "hi": "पोषण कम। जैविक खाद डालें; सूखा-प्रतिरोधी फसलें चुनें।"},
    "sandy": {"en": "Poor water retention. Use drip irrigation and organic mulch.",
              "mr": "पाणी कमी टिकते. ठिबक सिंचन व सेंद्रिय आच्छादन वापरा.",
              "hi": "पानी कम रुकता है। ड्रिप सिंचाई और जैविक मल्च का उपयोग करें।"},
    "clay":  {"en": "Slow drainage. Add gypsum to improve structure.",
              "mr": "निचरा मंद. रचना सुधारण्यासाठी जिप्सम घाला.",
              "hi": "जल निकासी धीमी। संरचना सुधारने के लिए जिप्सम मिलाएं।"},
    "loam":  {"en": "Ideal soil. Maintain fertility with crop rotation.",
              "mr": "आदर्श माती. पीक फेरपालटीने सुपीकता टिकवा.",
              "hi": "आदर्श मिट्टी। फसल चक्र से उर्वरता बनाए रखें।"},
}

CONFIDENCE_THRESHOLD = 0.60   # single place to tune


@app.route("/soil-ai", methods=["POST"])
def soil_ai():
    import os, uuid                          # already imported in your app; kept for clarity

    # ── 1. Validate input ─────────────────────────────────────────
    if "photo" not in request.files:
        return jsonify({"error": "Photo required"}), 400

    photo = request.files["photo"]
    if photo.filename == "":
        return jsonify({"error": "No photo selected"}), 400

    # Block non-image file types
    allowed = {"jpg", "jpeg", "png", "webp"}
    ext = photo.filename.rsplit(".", 1)[-1].lower() if "." in photo.filename else ""
    if ext not in allowed:
        return jsonify({"error": f"Invalid file type. Allowed: {', '.join(allowed)}"}), 415

    # ── 2. Save with a unique name (avoids filename collisions) ───
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    photo.save(path)

    try:
        # ── 3. Run model inference ────────────────────────────────
        soil, conf = predict_soil(path)   # your existing predict_soil() unchanged

        # ── 4. Low-confidence → ask for a better photo ────────────
        if conf < CONFIDENCE_THRESHOLD:
            return jsonify({
                "soil": {
                    "en": "Unclear",
                    "mr": "माती ओळखता आली नाही",
                    "hi": "मिट्टी स्पष्ट नहीं है",
                },
                "confidence": round(conf * 100, 2),
                "crops": [],
                "tips": None,
                "note": {
                    "en": "Confidence too low. Upload a clear, close-up soil photo in good lighting.",
                    "mr": "आत्मविश्वास कमी. चांगल्या प्रकाशात मातीचा स्पष्ट, जवळचा फोटो टाका.",
                    "hi": "विश्वास कम है। अच्छी रोशनी में मिट्टी की साफ और नज़दीकी तस्वीर अपलोड करें।",
                },
            }), 200

        # ── 5. Successful prediction ──────────────────────────────
        return jsonify({
            "soil":       SOIL_MAP.get(soil, {"en": soil, "mr": soil, "hi": soil}),
            "confidence": round(conf * 100, 2),
            "crops":      CROP_MAP.get(soil, []),
            "tips":       TIPS_MAP.get(soil),                    # ← NEW: farming tips
            "note": {
                "en": "AI predicts soil type only. Consult a local agronomist for best results.",
                "mr": "AI फक्त मातीचा प्रकार सांगते. उत्तम परिणामांसाठी कृषी तज्ञाशी संपर्क करा.",
                "hi": "AI केवल मिट्टी का प्रकार बताता है। सर्वोत्तम परिणामों के लिए कृषि विशेषज्ञ से मिलें।",
            },
        }), 200

    except Exception as e:
        app.logger.error("soil_ai inference error: %s", e, exc_info=True)
        return jsonify({"error": "Prediction failed. Please try again."}), 500

    finally:
        # ── Always delete the temp file, even on errors ───────────
        if os.path.exists(path):
            os.remove(path)
    
# ---------- DISEASE AI ----------
@app.route("/disease-ai", methods=["POST"])
def disease_ai():

    if "photo" not in request.files:
        return jsonify({"error": "Photo required"}), 400

    crop = request.form.get("crop")
    SUPPORTED = ["maize", "cotton"]

    if crop not in SUPPORTED:
        return jsonify({"error": "Unsupported crop"}), 400

    photo = request.files["photo"]
    filename = secure_filename(photo.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    photo.save(path)

    status, confidence = predict_pest(path, crop)

    # ❌ uncertain
    if status == "uncertain":
        return jsonify({
            "status": "uncertain",
            "message": "Image not clear. Please upload close leaf photo.",
            "confidence": round(confidence * 100, 2)
        })

    # ✅ diseased
    if status == "diseased":
        sol = DISEASE_SOLUTIONS[crop]
        return jsonify({
            "crop": crop,
            "status": "diseased",
            "confidence": round(confidence * 100, 2),
            "mr": sol["mr"],
            "hi": sol["hi"],
            "en": sol["en"]
        })

    # ✅ healthy
    return jsonify({
        "crop": crop,
        "status": "healthy",
        "confidence": round(confidence * 100, 2),
        "mr": {"text": "पिक निरोगी आहे", "spray": "फवारणीची गरज नाही"},
        "hi": {"text": "फसल स्वस्थ है", "spray": "छिड़काव की आवश्यकता नहीं"},
        "en": {"text": "Crop is healthy", "spray": "No spray required"}
    })
    
# ---------------- ADD EQUIPMENT ----------------
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = "uploads/equipment"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/add-equipment", methods=["POST"])
def add_equipment():

    owner_id = request.form.get("owner_id")
    title = request.form.get("title")
    etype = request.form.get("type")
    price_per_day = request.form.get("price_per_day")
    sell_price = request.form.get("sell_price")
    village = request.form.get("village")
    contact = request.form.get("contact")

    if not owner_id or not title or not village:
        return jsonify({"error": "Required fields missing"}), 400

    # ---------- IMAGE UPLOAD ----------
    photos = request.files.getlist("photos")
    image_paths = []

    upload_dir = "uploads/equipment"
    os.makedirs(upload_dir, exist_ok=True)

    for photo in photos:
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            save_path = os.path.join(upload_dir, filename)
            photo.save(save_path)
            image_paths.append(save_path)

    # ---------- DB INSERT ----------
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO equipment
        (title, type, price_per_day, sell_price, village, contact, owner_id, photos)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        title,
        etype,
        price_per_day if etype=="rent" else None,
        sell_price if etype=="sell" else None,
        village,
        contact,
        owner_id,
        json.dumps(image_paths)   # 🔥 MOST IMPORTANT LINE
    ))

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Equipment added successfully"})

# =================================================
# GET ALL EQUIPMENT
@app.route("/equipment", methods=["GET"])
def get_equipment():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT title, description, price_per_day, sell_price, type, location, contact
        FROM equipment
        ORDER BY created_at DESC
    """)
    items = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(items)

# =================================================
# SEARCH EQUIPMENT BY VILLAGE
# =================================================
import json

@app.route("/equipment/nearby/<village>")
def nearby_equipment(village):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM equipment WHERE village=%s",
        (village,)
    )
    rows = cursor.fetchall()

    for r in rows:
        r["photos"] = json.loads(r["photos"]) if r["photos"] else []

    cursor.close()
    db.close()

    return jsonify(rows)

# =================================================
@app.route("/equipment/add-availability", methods=["POST"])
def add_availability():
    data = request.get_json()

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO equipment_availability (equipment_id, available_date)
        VALUES (%s,%s)
    """, (data["equipment_id"], data["date"]))

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Availability added"})

@app.route("/equipment/availability/<int:equipment_id>", methods=["GET"])
def check_availability(equipment_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT available_date FROM equipment_availability
        WHERE equipment_id=%s
    """, (equipment_id,))

    dates = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify(dates)


# =================================================
# BOOK EQUIPMENT (RENT ONLY)
# =================================================
# =================================================
# BOOK EQUIPMENT (FIXED WITH OWNER_ID)
# =================================================
@app.route("/equipment/book", methods=["POST"])
def book_equipment():
    try:
        data = request.get_json()

        equipment_id = data.get("equipment_id")
        user_id = data.get("user_id")
        customer_name = data.get("customer_name")
        customer_mobile = data.get("customer_mobile")
        customer_village = data.get("customer_village")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        payment_mode = data.get("payment_mode")

        if not equipment_id or not user_id:
            return jsonify({"error": "Invalid booking data"}), 400

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Get equipment owner & price
        cursor.execute(
            "SELECT owner_id, price_per_day FROM equipment WHERE id=%s",
            (equipment_id,)
        )
        eq = cursor.fetchone()

        if not eq:
            cursor.close()
            db.close()
            return jsonify({"error": "Equipment not found"}), 404

        owner_id = eq["owner_id"]
        price_per_day = eq["price_per_day"]

        from datetime import datetime
        d1 = datetime.strptime(start_date, "%Y-%m-%d")
        d2 = datetime.strptime(end_date, "%Y-%m-%d")
        days = (d2 - d1).days + 1
        total_price = days * price_per_day

        cursor.execute("""
            INSERT INTO equipment_booking
            (equipment_id, user_id, owner_id,
             customer_name, customer_mobile, customer_village,
             start_date, end_date, total_price, payment_mode, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending')
        """, (
            equipment_id,
            user_id,
            owner_id,
            customer_name,
            customer_mobile,
            customer_village,
            start_date,
            end_date,
            total_price,
            payment_mode
        ))

        db.commit()
        booking_id = cursor.lastrowid
        cursor.close()
        db.close()

        return jsonify({
            "booking_id": booking_id,
            "total_price": total_price
        })
    except Exception as e:
        print(f"Error in book_equipment: {str(e)}")
        return jsonify({"error": f"Booking failed: {str(e)}"}), 500

# =================================================
# SERVE EQUIPMENT IMAGES
# =================================================
@app.route("/uploads/equipment/<filename>")
def equipment_image(filename):
    return send_from_directory("uploads/equipment", filename)

@app.route("/equipment/rate", methods=["POST"])
def rate_equipment():
    data = request.get_json()

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO equipment_rating (equipment_id,user_id,rating,review)
        VALUES (%s,%s,%s,%s)
    """, (
        data["equipment_id"],
        data["user_id"],
        data["rating"],
        data.get("review")
    ))

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Rating added"})

@app.route("/equipment/rating/<int:equipment_id>", methods=["GET"])
def get_rating(equipment_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT AVG(rating) as avg_rating
        FROM equipment_rating
        WHERE equipment_id=%s
    """, (equipment_id,))

    rating = cursor.fetchone()
    cursor.close()
    db.close()

    return jsonify(rating)

# =========================================
# OWNER DASHBOARD - MY EQUIPMENT
# =========================================
@app.route("/owner/equipment/<int:owner_id>", methods=["GET"])
def owner_equipment(owner_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT e.id, e.title, e.type, e.price_per_day, e.sell_price,
               COUNT(b.id) AS total_bookings
        FROM equipment e
        LEFT JOIN equipment_booking b ON e.id = b.equipment_id
        WHERE e.owner_id=%s
        GROUP BY e.id
    """, (owner_id,))

    rows = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify(rows), 200

@app.route("/owner/booking/approve/<int:booking_id>/<int:owner_id>", methods=["POST"])
def approve_booking(booking_id, owner_id):
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE equipment_booking SET status='approved' WHERE id=%s AND owner_id=%s",
        (booking_id, owner_id)
    )
    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Booking approved successfully"})

# =================================================
# OWNER - VIEW ONLY HIS BOOKINGS
# =================================================
@app.route("/owner/bookings/<int:owner_id>", methods=["GET"])
def owner_bookings(owner_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.id, b.customer_name, b.customer_mobile,
               b.customer_village, b.start_date, b.end_date,
               b.total_price, b.status,
               e.title
        FROM equipment_booking b
        JOIN equipment e ON b.equipment_id = e.id
        WHERE b.owner_id=%s
        ORDER BY b.id DESC
    """, (owner_id,))

    rows = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify(rows), 200


@app.route("/owner/booking/cancel/<int:booking_id>/<int:owner_id>", methods=["DELETE"])
def cancel_booking(booking_id, owner_id):
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE equipment_booking SET status='cancelled' WHERE id=%s AND owner_id=%s",
        (booking_id, owner_id)
    )
    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Booking cancelled"})

@app.route("/owner/booking/update/<int:booking_id>", methods=["POST"])
def owner_update_booking(booking_id):
    data = request.get_json()
    start = data.get("start_date")
    end = data.get("end_date")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT status FROM equipment_booking WHERE id=%s",
        (booking_id,)
    )
    b = cursor.fetchone()

    if not b or b["status"] != "pending":
        return jsonify({"error":"Booking cannot be edited"}),400

    cursor.execute("""
        UPDATE equipment_booking 
        SET start_date=%s, end_date=%s
        WHERE id=%s
    """,(start,end,booking_id))

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message":"Booking updated"}),200

@app.route("/user/bookings/<int:user_id>", methods=["GET"])
def user_bookings(user_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            eb.id,
            e.title,
            eb.start_date,
            eb.end_date,
            eb.total_price,
            eb.status
        FROM equipment_booking eb
        JOIN equipment e ON eb.equipment_id = e.id
        WHERE eb.user_id = %s
        ORDER BY eb.id DESC
    """, (user_id,))

    rows = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify(rows)

# =========================================
# OWNER INCOME ANALYTICS
# =========================================
@app.route("/owner/income/<int:owner_id>", methods=["GET"])
def owner_income(owner_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            COALESCE(SUM(total_price), 0) AS total_income
        FROM equipment_booking
        WHERE owner_id = %s
          AND status = 'approved'
    """, (owner_id,))

    result = cursor.fetchone()

    cursor.close()
    db.close()

    return jsonify({
        "owner_id": owner_id,
        "total_income": result["total_income"]
    })

# ---------- PAY INIT ----------
@app.route("/equipment/pay/upi", methods=["POST"])
def pay_upi():
    try:
        d = request.get_json()
        booking_id = d.get("booking_id")
        amount = d.get("amount")

        if not booking_id or not amount:
            return jsonify({"error": "booking_id and amount required"}), 400

        try:
            amount_int = int(amount)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid amount"}), 400

        order = client.order.create({
            "amount": amount_int * 100,
            "currency": "INR",
            "payment_capture": 1
        })

        return jsonify({"order_id": order["id"], "amount": order["amount"]})
    except Exception as e:
        print(f"Error in pay_upi: {str(e)}")
        return jsonify({"error": f"Payment initiation failed: {str(e)}"}), 500

# ---------- PAY VERIFY ----------
@app.route("/equipment/pay/verify", methods=["POST"])
def verify_pay():
    try:
        d = request.get_json()
        
        if not all(k in d for k in ["razorpay_payment_id", "razorpay_order_id", "razorpay_signature", "booking_id"]):
            return jsonify({"error": "Missing required fields"}), 400
        
        client.utility.verify_payment_signature({
            "razorpay_payment_id": d["razorpay_payment_id"],
            "razorpay_order_id": d["razorpay_order_id"],
            "razorpay_signature": d["razorpay_signature"]
        })

        db = get_db_connection()
        c = db.cursor()
        c.execute("UPDATE equipment_booking SET status='paid' WHERE id=%s", (d["booking_id"],))
        db.commit()
        c.close()
        db.close()

        return jsonify({"message": "Payment verified"})
    except Exception as e:
        print(f"Error in verify_pay: {str(e)}")
        return jsonify({"error": f"Payment verification failed: {str(e)}"}), 500

# ---------- INVOICE ----------
@app.route("/equipment/invoice/<int:booking_id>")
def invoice(booking_id):
    db = get_db_connection()
    c = db.cursor(dictionary=True)

    c.execute("""
        SELECT b.id, b.start_date, b.end_date, b.total_price, b.status,
               b.customer_name, b.customer_mobile,
               e.title, e.price_per_day
        FROM equipment_booking b
        JOIN equipment e ON b.equipment_id = e.id
        WHERE b.id=%s
    """, (booking_id,))
    data = c.fetchone()
    c.close(); db.close()

    if not data:
        return jsonify({"error": "Invoice not found"}), 404

    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(BASE, "invoices"), exist_ok=True)
    path = os.path.join(BASE, "invoices", f"invoice_{booking_id}.pdf")

    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="center", alignment=TA_CENTER, fontSize=18))

    elems = []

    logo = os.path.join(BASE, "static", "logo.png")
    if os.path.exists(logo):
        elems.append(Image(logo, 120, 50))

    elems.append(Spacer(1, 10))
    elems.append(Paragraph("<b>Agriset.ai</b>", styles["center"]))
    elems.append(Spacer(1, 20))

    table = Table([
        ["Invoice", f"INV-{data['id']}"],
        ["Customer", data["customer_name"]],
        ["Mobile", data["customer_mobile"]],
        ["Equipment", data["title"]],
        ["Price / Day", f"₹{data['price_per_day']}"],
        ["Start", str(data["start_date"])],
        ["End", str(data["end_date"])],
        ["Status", data["status"]],
        ["Total", f"₹{data['total_price']}"]
    ])
    table.setStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.grey),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold")
    ])

    elems.append(table)
    doc.build(elems)

    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)