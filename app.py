import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from flask import Flask, Response, render_template, request, redirect, url_for, session, flash, jsonify
from xml.sax.saxutils import escape
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Keep sessions working locally even when SECRET_KEY has not been configured.
# Set SECRET_KEY in Render for a stable production session key across restarts/workers.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("COOKIE_SECURE", "false").lower() == "true"
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
app.config["DATABASE_PATH"] = os.environ.get("DATABASE_PATH") or os.path.join(app.instance_path, "school_admin.db")
app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER") or os.path.join(app.static_folder, "uploads")
ALLOWED_UPLOADS = {"pdf", "epub", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "txt", "jpg", "jpeg", "png", "webp", "gif"}


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;")
    if request.path.startswith("/admin"):
        response.headers.setdefault("Cache-Control", "no-store")
        response.headers.setdefault("Pragma", "no-cache")
    return response



@contextmanager
def db_connect():
    database_directory = os.path.dirname(app.config["DATABASE_PATH"])
    if database_directory:
        os.makedirs(database_directory, exist_ok=True)
    connection = sqlite3.connect(app.config["DATABASE_PATH"])
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_admin_storage():
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    with db_connect() as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS content_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            url TEXT NOT NULL DEFAULT '',
            file_path TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )""")
        connection.execute("""CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            created_at TEXT NOT NULL
        )""")
        connection.execute("""CREATE TABLE IF NOT EXISTS site_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT NOT NULL DEFAULT ''
        )""")


init_admin_storage()


def allowed_upload(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_UPLOADS


def save_upload(upload):
    if not upload or not upload.filename:
        return ""
    if not allowed_upload(upload.filename):
        raise ValueError("That file type is not allowed. Use PDF, EPUB, Office documents, text files or common image formats.")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    safe_name = secure_filename(upload.filename)
    stem, extension = os.path.splitext(safe_name)
    filename = f"{stem[:70]}-{secrets.token_hex(6)}{extension.lower()}"
    upload.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return "uploads/" + filename


def remove_upload(relative_path):
    if not relative_path or not relative_path.startswith("uploads/"):
        return
    destination = os.path.abspath(os.path.join(app.static_folder, relative_path))
    upload_root = os.path.abspath(app.config["UPLOAD_FOLDER"])
    if destination.startswith(upload_root + os.sep) and os.path.isfile(destination):
        os.remove(destination)


def get_saved_setting(key, fallback=""):
    with db_connect() as connection:
        row = connection.execute("SELECT setting_value FROM site_settings WHERE setting_key = ?", (key,)).fetchone()
    return row["setting_value"] if row else fallback


def save_settings(values):
    with db_connect() as connection:
        for key, value in values.items():
            connection.execute(
                "INSERT INTO site_settings (setting_key, setting_value) VALUES (?, ?) "
                "ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value",
                (key, value.strip())
            )


def current_school():
    school = dict(SCHOOL)
    for key in school:
        school[key] = get_saved_setting("school." + key, school[key])
    return school


def current_payment_info():
    import copy
    info = copy.deepcopy(PAYMENT_INFO)
    for method, fields in info.items():
        for key, value in fields.items():
            if isinstance(value, str):
                fields[key] = get_saved_setting("payment." + method + "." + key, value)
    return info


# ============================================================
# SCHOOL INFORMATION
# ============================================================

SCHOOL = {
    "name": "Friends School Mbale",
    "full_name": "Friends School – Mbale",
    "county": "Vihiga County",
    "sub_county": "Sabatia Sub-County",
    "region": "Western Kenya",
    "type": "Public Boys' Boarding School",
    "cluster": "C2",
    "knec": "38622202",
    "uic": "QGV4",
    "phone": "0728 382395",
    "email": "mbalehighoffice@gmail.com",
    "principal": "Manasseh Kagasi"
}


# ============================================================
# SCHOOL PAYMENT INFORMATION
# ============================================================

PAYMENT_INFO = {

    "mpesa": {
        "name": "M-PESA",
        "available": True,
        "paybill": "",
        "account_format": "Student Admission Number",

        "instructions": [
            "Open the M-PESA menu on your phone.",
            "Select Lipa na M-PESA.",
            "Select Pay Bill.",
            "Enter the official school PayBill number.",
            "Enter the student's admission number as the account/reference.",
            "Enter the amount to pay.",
            "Enter your M-PESA PIN and confirm.",
            "Keep the M-PESA confirmation message."
        ]
    },

    "kcb": {
        "name": "KCB Bank",
        "available": True,
        "account_number": "",
        "reference": "Student Admission Number",

        "instructions": [
            "Open the KCB Mobile App.",
            "Select Pay or Lipa Karo.",
            "Search for the school if it is registered.",
            "Enter the student's admission number.",
            "Enter the amount to pay.",
            "Confirm the payment details.",
            "Authorise the payment using your PIN.",
            "Keep the confirmation message."
        ]
    },

    "bank": {
        "name": "Bank Payment",
        "available": True,
        "bank_name": "",
        "account_name": "Friends School Mbale",
        "account_number": "",
        "branch": "",

        "instructions": [
            "Visit your bank or use your bank's mobile/internet banking.",
            "Enter the school's official bank account details.",
            "Use the student's admission number as the payment reference.",
            "Enter the amount.",
            "Confirm the transaction.",
            "Keep the bank transaction receipt."
        ]
    }
}


# ============================================================
# SENIOR SCHOOL PATHWAYS
# ============================================================

PATHWAYS = {

    # ========================================================
    # STEM
    # ========================================================

    "stem": {

        "title": "STEM",

        "subtitle": (
            "Science, Technology, Engineering and Mathematics"
        ),

        "description": (
            "Explore science, mathematics, technology and "
            "related learning areas."
        ),

        "subjects": {

            "mathematics": {
                "name": "Mathematics",
                "description": (
                    "Explore mathematical concepts, "
                    "problem-solving and applications."
                )
            },

            "computer-science": {
                "name": "Computer Science",
                "description": (
                    "Explore computing, programming and "
                    "digital technologies."
                )
            },

            "physics": {
                "name": "Physics",
                "description": (
                    "Study matter, energy, forces and "
                    "the physical world."
                )
            },

            "chemistry": {
                "name": "Chemistry",
                "description": (
                    "Explore substances, reactions and "
                    "chemical principles."
                )
            },

            "biology": {
                "name": "Biology",
                "description": (
                    "Study living organisms and "
                    "biological systems."
                )
            }
        }
    },


    # ========================================================
    # SOCIAL SCIENCES
    # ========================================================

    "social-sciences": {

        "title": "Social Sciences",

        "subtitle": (
            "People, Society, Culture and Business"
        ),

        "description": (
            "Explore learning areas related to people, "
            "communities, society, history and business."
        ),

        "subjects": {

            "history": {
                "name": "History",
                "description": (
                    "Explore past events, societies and "
                    "historical developments."
                )
            },

            "geography": {
                "name": "Geography",
                "description": (
                    "Study places, environments, people "
                    "and the world around us."
                )
            },

            "business-studies": {
                "name": "Business Studies",
                "description": (
                    "Explore business, entrepreneurship "
                    "and economic activities."
                )
            },

            "religious-education": {
                "name": "Religious Education",
                "description": (
                    "Explore religious teachings, values "
                    "and their role in society."
                )
            }
        }
    },


    # ========================================================
    # ARTS & SPORTS
    # ========================================================

    "arts-sports": {

        "title": "Arts & Sports",

        "subtitle": (
            "Creativity, Performance and Physical Development"
        ),

        "description": (
            "Discover creative expression, performance, "
            "talent development and sporting activities."
        ),

        "subjects": {

            "art-design": {
                "name": "Art & Design",
                "description": (
                    "Explore visual creativity, design "
                    "principles and artistic expression."
                )
            },

            "music": {
                "name": "Music",
                "description": (
                    "Explore musical skills, performance "
                    "and appreciation."
                )
            },

            "theatre": {
                "name": "Theatre and Film",
                "description": (
                    "Explore acting, storytelling, "
                    "performance and film."
                )
            },

            "sports": {
                "name": "Sports",
                "description": (
                    "Explore sporting skills, physical "
                    "development and teamwork."
                )
            }
        }
    }
}


# ============================================================
# LEARNING RESOURCE CATEGORIES
# ============================================================

RESOURCE_TYPES = {

    "materials": {
        "title": "Learning Materials",
        "description": (
            "Study resources and learning materials."
        )
    },

    "notes": {
        "title": "Notes",
        "description": (
            "Subject notes for learning and revision."
        )
    },

    "revision": {
        "title": "Revision Questions",
        "description": (
            "Questions to help learners practise and revise."
        )
    },

    "assignments": {
        "title": "Assignments",
        "description": (
            "Assignments and practice activities."
        )
    }
}


# ============================================================
# ACTUAL ONLINE LEARNING RESOURCES
# ============================================================

RESOURCE_LINKS = {

    "materials": [

        {
            "title": "KICD CBC Materials",
            "description": (
                "Official CBC curriculum materials and "
                "learning resources from KICD."
            ),
            "url": "https://kicd.ac.ke/cbc-materials/",
            "icon": "🇰🇪"
        },

        {
            "title": "KICD Curriculum Designs",
            "description": (
                "Official curriculum designs and "
                "learning area information."
            ),
            "url": "https://kicd.ac.ke/cbc-materials/",
            "icon": "📘"
        },

        {
            "title": "Khan Academy",
            "description": (
                "Free lessons, exercises and learning "
                "resources."
            ),
            "url": "https://www.khanacademy.org/",
            "icon": "🎓"
        },

        {
            "title": "CK-12",
            "description": (
                "Free digital textbooks and interactive "
                "learning resources."
            ),
            "url": "https://www.ck12.org/",
            "icon": "📚"
        }
    ],


    "notes": [

        {
            "title": "KICD Curriculum Resources",
            "description": (
                "Use official curriculum resources to "
                "guide your studies."
            ),
            "url": "https://kicd.ac.ke/cbc-materials/",
            "icon": "📖"
        },

        {
            "title": "Khan Academy",
            "description": (
                "Interactive lessons and explanations "
                "for mathematics and science."
            ),
            "url": "https://www.khanacademy.org/",
            "icon": "🎓"
        },

        {
            "title": "CK-12",
            "description": (
                "Explore free digital textbooks and "
                "subject learning materials."
            ),
            "url": "https://www.ck12.org/",
            "icon": "📚"
        }
    ],


    "revision": [

        {
            "title": "Khan Academy Practice",
            "description": (
                "Practise mathematics, science and "
                "other academic skills."
            ),
            "url": "https://www.khanacademy.org/",
            "icon": "🧠"
        },

        {
            "title": "KICD CBC Materials",
            "description": (
                "Use official curriculum resources "
                "to support revision."
            ),
            "url": "https://kicd.ac.ke/cbc-materials/",
            "icon": "📖"
        },

        {
            "title": "CK-12 Practice Resources",
            "description": (
                "Explore interactive learning and "
                "practice resources."
            ),
            "url": "https://www.ck12.org/",
            "icon": "✏️"
        }
    ],


    "assignments": [

        {
            "title": "Khan Academy Exercises",
            "description": (
                "Practise through interactive exercises "
                "and activities."
            ),
            "url": "https://www.khanacademy.org/",
            "icon": "📝"
        },

        {
            "title": "KICD Learning Resources",
            "description": (
                "Explore official curriculum support "
                "materials."
            ),
            "url": "https://kicd.ac.ke/cbc-materials/",
            "icon": "📚"
        }
    ]
}


# ============================================================
# MAIN WEBSITE ROUTES
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        school=current_school(),
        pathways=PATHWAYS
    )


@app.route("/about")
def about():
    with db_connect() as connection:
        school_updates = connection.execute(
            "SELECT * FROM content_items WHERE section = ? ORDER BY id DESC", ("school",)
        ).fetchall()
    return render_template("about.html", school=current_school(), school_updates=school_updates)


@app.route("/academics")
def academics():
    with db_connect() as connection:
        learning_items = connection.execute(
            "SELECT * FROM content_items WHERE section = ? ORDER BY id DESC", ("resources",)
        ).fetchall()
        pathway_updates = connection.execute(
            "SELECT * FROM content_items WHERE section = ? ORDER BY id DESC", ("pathways",)
        ).fetchall()
    return render_template("academics.html", school=current_school(), pathways=PATHWAYS, learning_items=learning_items, pathway_updates=pathway_updates)


@app.route("/news")
def news():
    with db_connect() as connection:
        news_items = connection.execute(
            "SELECT * FROM content_items WHERE section IN (?, ?) ORDER BY id DESC",
            ("news", "announcements")
        ).fetchall()
    return render_template("news.html", school=current_school(), news_items=news_items)


@app.route("/gallery")
def gallery():
    with db_connect() as connection:
        gallery_items = connection.execute(
            "SELECT * FROM content_items WHERE section = ? ORDER BY id DESC",
            ("gallery",)
        ).fetchall()
    return render_template("gallery.html", school=current_school(), gallery_items=gallery_items)


@app.route("/contact")
def contact():

    return render_template(
        "contact.html",
        school=current_school()
    )


# ============================================================
# SCHOOL FEES / PAYMENTS
# ============================================================

@app.route("/fees")
def fees():
    with db_connect() as connection:
        payment_updates = connection.execute(
            "SELECT * FROM content_items WHERE section = ? ORDER BY id DESC", ("payments",)
        ).fetchall()
    return render_template("fees.html", school=current_school(), payment_info=current_payment_info(), payment_updates=payment_updates)


# ============================================================
# PATHWAY PAGE
# ============================================================

@app.route("/pathways/<pathway_key>")
def pathway_page(pathway_key):

    pathway = PATHWAYS.get(pathway_key)

    if pathway is None:

        return render_template(
            "404.html",
            school=current_school(),
            message="The requested pathway was not found."
        ), 404

    return render_template(
        "pathway.html",
        pathway=pathway,
        pathway_key=pathway_key,
        school=current_school()
    )


# ============================================================
# SUBJECT PAGE
# ============================================================

@app.route("/pathways/<pathway_key>/<subject_key>")
def subject_page(pathway_key, subject_key):

    pathway = PATHWAYS.get(pathway_key)

    if pathway is None:

        return render_template(
            "404.html",
            school=current_school(),
            message="The requested pathway was not found."
        ), 404

    subject = pathway["subjects"].get(subject_key)

    if subject is None:

        return render_template(
            "404.html",
            school=current_school(),
            message="The requested subject was not found."
        ), 404

    return render_template(
        "subject.html",
        pathway=pathway,
        pathway_key=pathway_key,
        subject=subject,
        subject_key=subject_key,
        resource_types=RESOURCE_TYPES,
        school=current_school()
    )


# ============================================================
# LEARNING RESOURCE PAGE
# ============================================================

@app.route(
    "/pathways/<pathway_key>/<subject_key>/<resource_key>"
)
def learning_resource_page(
    pathway_key,
    subject_key,
    resource_key
):

    pathway = PATHWAYS.get(pathway_key)

    if pathway is None:

        return render_template(
            "404.html",
            school=current_school(),
            message="The requested pathway was not found."
        ), 404

    subject = pathway["subjects"].get(subject_key)

    if subject is None:

        return render_template(
            "404.html",
            school=current_school(),
            message="The requested subject was not found."
        ), 404

    resource = RESOURCE_TYPES.get(resource_key)

    if resource is None:

        return render_template(
            "404.html",
            school=current_school(),
            message=(
                "The requested learning resource "
                "was not found."
            )
        ), 404

    links = RESOURCE_LINKS.get(
        resource_key,
        []
    )

    return render_template(
        "resource.html",
        pathway=pathway,
        pathway_key=pathway_key,
        subject=subject,
        subject_key=subject_key,
        resource=resource,
        resource_key=resource_key,
        links=links,
        school=current_school()
    )



# ============================================================
# SEARCH ENGINE DISCOVERY: SITEMAP AND ROBOTS.TXT
# ============================================================


# Public-information assistant. Answers are grounded in this site's published pages only.
SCHOOL_ASSISTANT_KB = [
    (("fee", "fees", "pay", "payment", "mpesa", "bank", "account"), "Please visit the Fees & Payments page for the school's currently published payment guidance. Confirm payment details directly with the school before sending money.", "/fees"),
    (("academic", "academics", "subject", "subjects", "pathway", "pathways", "cbc", "curriculum"), "Explore the Academics page for senior-school pathways, subjects and learning resources.", "/academics"),
    (("news", "announcement", "announcements", "event", "events"), "The News page contains published school updates and announcements.", "/news"),
    (("gallery", "photo", "photos", "pictures"), "Visit the Gallery to view published school photographs.", "/gallery"),
    (("contact", "phone", "email", "reach", "address", "location"), "Please use the Contact page for the school's published contact information.", "/contact"),
    (("school", "about", "principal", "mission", "history"), "The About page contains the school's published profile and information.", "/about"),
    (("resource", "resources", "revision", "notes", "textbook", "textbooks", "learning"), "Visit Academics to browse available learning resources. Ask a teacher or the school if a resource is missing.", "/academics"),
]

@app.post("/api/assistant")
def school_assistant():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("message", "")).strip()
    if not question or len(question) > 500:
        return jsonify({"answer": "Please ask a short question of up to 500 characters.", "link": None}), 400
    lowered = question.casefold()
    for keywords, answer, path in SCHOOL_ASSISTANT_KB:
        if any(keyword in lowered for keyword in keywords):
            return jsonify({"answer": answer, "link": url_for("home")[:-1] + path if url_for("home").endswith("/") else path})
    return jsonify({"answer": "I can help with published information about academics, learning resources, fees, news, the gallery and school contacts. For anything not listed on this website, please contact the school directly.", "link": url_for("contact")})



@app.route("/sitemap.xml")
def sitemap():
    """Generate an XML sitemap using the canonical HTTPS site URL."""
    site_base = "https://mbale-high-website-1.onrender.com"
    pages = [
        site_base + url_for("home"),
        site_base + url_for("about"),
        site_base + url_for("academics"),
        site_base + url_for("news"),
        site_base + url_for("gallery"),
        site_base + url_for("contact"),
        site_base + url_for("fees"),
    ]

    # Include the public senior-school pathway, subject and resource pages.
    for pathway_key, pathway in PATHWAYS.items():
        pages.append(site_base + url_for("pathway_page", pathway_key=pathway_key))
        for subject_key in pathway["subjects"]:
            pages.append(site_base + url_for(
                "subject_page",
                pathway_key=pathway_key,
                subject_key=subject_key,
            ))
            for resource_key in RESOURCE_TYPES:
                pages.append(site_base + url_for(
                    "learning_resource_page",
                    pathway_key=pathway_key,
                    subject_key=subject_key,
                    resource_key=resource_key,
                ))

    # Remove duplicates while preserving order.
    pages = list(dict.fromkeys(pages))
    url_entries = "\n".join(
        f"  <url><loc>{escape(page)}</loc></url>" for page in pages
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{url_entries}\n'
        '</urlset>\n'
    )
    return Response(xml, mimetype="application/xml")


@app.route("/robots.txt")
def robots_txt():
    """Tell search crawlers where the sitemap is located."""
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Sitemap: https://mbale-high-website-1.onrender.com/sitemap.xml\n"
    )
    return Response(body, mimetype="text/plain")


# ============================================================
# 404 ERROR HANDLER
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html",
        school=SCHOOL,
        message=(
            "The page you are looking for "
            "could not be found."
        )
    ), 404


# ============================================================
# 500 ERROR HANDLER
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    return render_template(
        "500.html",
        school=SCHOOL
    ), 500


# =========================
# ADMIN PORTAL
# =========================

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        with db_connect() as connection:
            database_user = connection.execute(
                "SELECT * FROM admin_users WHERE username = ?", (username,)
            ).fetchone()
        valid_database_login = bool(database_user and check_password_hash(database_user["password_hash"], password))
        valid_environment_login = bool(ADMIN_USERNAME and ADMIN_PASSWORD and username == ADMIN_USERNAME and password == ADMIN_PASSWORD)
        if valid_database_login or valid_environment_login:
            session["admin_logged_in"] = True
            session["admin_username"] = username
            session["admin_role"] = database_user["role"] if valid_database_login else "admin"
            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin_login.html",
            error="Invalid username or password."
        )

    return render_template("admin_login.html")


@app.route("/admin")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    with db_connect() as connection:
        item_count = connection.execute("SELECT COUNT(*) FROM content_items").fetchone()[0]
        user_count = connection.execute("SELECT COUNT(*) FROM admin_users").fetchone()[0]
    return render_template("admin_dashboard.html", item_count=item_count, user_count=user_count)


@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    session.pop("admin_role", None)
    return redirect(url_for("admin_login"))


# ============================================================
# ADMIN DASHBOARD SECTIONS
# ============================================================

ADMIN_SECTIONS = {
    "news": {"title": "Manage News", "description": "Publish school news stories and updates.", "public_endpoint": "news", "public_label": "news"},
    "announcements": {"title": "Manage Announcements", "description": "Publish notices for students, parents and staff.", "public_endpoint": "news", "public_label": "announcements"},
    "gallery": {"title": "Manage Gallery", "description": "Upload school photographs and event images.", "public_endpoint": "gallery", "public_label": "gallery"},
    "resources": {"title": "Manage Learning Resources", "description": "Upload e-textbooks, books, notes, revision papers, assignments and other learning files.", "public_endpoint": "academics", "public_label": "academics"},
    "payments": {"title": "Manage Payments", "description": "Store payment notices and verified payment information. Only publish official account details after confirming them with the school.", "public_endpoint": "fees", "public_label": "payments"},
    "school": {"title": "School Information Settings", "description": "Add and maintain school profile updates, contacts and information notices.", "public_endpoint": "about", "public_label": "school profile"},
    "pathways": {"title": "Manage Senior School Pathways", "description": "Add pathway information, subjects and curriculum updates.", "public_endpoint": "academics", "public_label": "academics"},
    "users": {"title": "Manage Users & Accounts", "description": "Create administrator accounts with securely hashed passwords, assign roles and remove accounts.", "public_endpoint": None, "public_label": None},
    "settings": {"title": "Website Settings", "description": "Maintain website notices and operational notes. Hosting secrets such as SECRET_KEY remain in Render environment settings.", "public_endpoint": None, "public_label": None},
}


def require_admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    return None


@app.route("/admin/sections/<section_key>", methods=["GET", "POST"])
def admin_section(section_key):
    denied = require_admin()
    if denied:
        return denied
    section = ADMIN_SECTIONS.get(section_key)
    if section is None:
        return render_template("404.html", school=SCHOOL, message="The requested admin section was not found."), 404
    if session.get("admin_role") == "editor" and section_key in ("users", "settings", "payments", "school"):
        return render_template("404.html", school=SCHOOL, message="Your account does not have permission to manage this section."), 403

    if section_key == "users":
        if request.method == "POST":
            action = request.form.get("action", "create")
            if action == "update-role":
                user_id = request.form.get("user_id", type=int)
                role = request.form.get("role") or "editor"
                if role not in ("admin", "editor"):
                    role = "editor"
                with db_connect() as connection:
                    target = connection.execute("SELECT username FROM admin_users WHERE id = ?", (user_id,)).fetchone()
                    if target and target["username"] == session.get("admin_username"):
                        flash("You cannot change the role of the account currently in use.", "error")
                    elif target:
                        connection.execute("UPDATE admin_users SET role = ? WHERE id = ?", (role, user_id))
                        flash("Account role updated.", "success")
                return redirect(url_for("admin_section", section_key="users"))
            if action == "delete":
                user_id = request.form.get("user_id", type=int)
                with db_connect() as connection:
                    target = connection.execute("SELECT username FROM admin_users WHERE id = ?", (user_id,)).fetchone()
                    if target and target["username"] == session.get("admin_username"):
                        flash("You cannot delete the account currently in use.", "error")
                    elif target:
                        connection.execute("DELETE FROM admin_users WHERE id = ?", (user_id,))
                        flash("Admin account deleted.", "success")
                return redirect(url_for("admin_section", section_key="users"))
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            role = request.form.get("role") or "editor"
            if not username or len(password) < 10:
                flash("Enter a username and a password of at least 10 characters.", "error")
            else:
                try:
                    with db_connect() as connection:
                        connection.execute(
                            "INSERT INTO admin_users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                            (username, generate_password_hash(password), role if role in ("admin", "editor") else "editor", datetime.utcnow().isoformat(timespec="seconds"))
                        )
                    flash("Admin account created. Save the credentials securely.", "success")
                except sqlite3.IntegrityError:
                    flash("That username already exists.", "error")
                return redirect(url_for("admin_section", section_key="users"))
        with db_connect() as connection:
            users = connection.execute("SELECT id, username, role, created_at FROM admin_users ORDER BY id DESC").fetchall()
        return render_template("admin_section.html", section=section, section_key=section_key, items=[], edit_item=None, users=users)

    if request.method == "POST":
        action = request.form.get("action", "create")
        if action == "save-config" and section_key == "school":
            allowed_fields = ("name", "full_name", "county", "sub_county", "region", "type", "cluster", "knec", "uic", "phone", "email", "principal")
            save_settings({"school." + key: request.form.get(key, "") for key in allowed_fields})
            flash("School profile settings saved and applied to the public About page.", "success")
            return redirect(url_for("admin_section", section_key="school"))
        if action == "save-config" and section_key == "payments":
            fields = {
                "mpesa.paybill": request.form.get("mpesa_paybill", ""),
                "kcb.account_number": request.form.get("kcb_account_number", ""),
                "bank.bank_name": request.form.get("bank_name", ""),
                "bank.account_name": request.form.get("bank_account_name", ""),
                "bank.account_number": request.form.get("bank_account_number", ""),
                "bank.branch": request.form.get("bank_branch", ""),
            }
            save_settings({"payment." + key: value for key, value in fields.items()})
            flash("Payment settings saved. Verify every account detail before publishing it.", "success")
            return redirect(url_for("admin_section", section_key="payments"))
        if action == "delete":
            item_id = request.form.get("item_id", type=int)
            with db_connect() as connection:
                item = connection.execute("SELECT file_path FROM content_items WHERE id = ? AND section = ?", (item_id, section_key)).fetchone()
                if item:
                    connection.execute("DELETE FROM content_items WHERE id = ? AND section = ?", (item_id, section_key))
                    remove_upload(item["file_path"])
                    flash("Item deleted.", "success")
            return redirect(url_for("admin_section", section_key=section_key))
        item_id = request.form.get("item_id", type=int) if action == "update" else None
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        url = (request.form.get("url") or "").strip()
        upload = request.files.get("file")
        if not title:
            flash("A title is required.", "error")
        else:
            try:
                uploaded_path = save_upload(upload)
                with db_connect() as connection:
                    if action == "update" and item_id:
                        existing = connection.execute("SELECT file_path FROM content_items WHERE id = ? AND section = ?", (item_id, section_key)).fetchone()
                        if not existing:
                            flash("That item was not found.", "error")
                            if uploaded_path:
                                remove_upload(uploaded_path)
                            return redirect(url_for("admin_section", section_key=section_key))
                        file_path = uploaded_path or existing["file_path"]
                        connection.execute(
                            "UPDATE content_items SET title = ?, description = ?, url = ?, file_path = ? WHERE id = ? AND section = ?",
                            (title, description, url, file_path, item_id, section_key)
                        )
                        if uploaded_path and existing["file_path"]:
                            remove_upload(existing["file_path"])
                        flash("Changes saved.", "success")
                    else:
                        connection.execute(
                            "INSERT INTO content_items (section, title, description, url, file_path, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                            (section_key, title, description, url, uploaded_path, datetime.utcnow().isoformat(timespec="seconds"))
                        )
                        flash("Item added.", "success")
            except ValueError as error:
                flash(str(error), "error")
            return redirect(url_for("admin_section", section_key=section_key))

    edit_id = request.args.get("edit", type=int)
    with db_connect() as connection:
        items = connection.execute("SELECT * FROM content_items WHERE section = ? ORDER BY id DESC", (section_key,)).fetchall()
        edit_item = connection.execute("SELECT * FROM content_items WHERE id = ? AND section = ?", (edit_id, section_key)).fetchone() if edit_id else None
    school_config = current_school() if section_key == "school" else {}
    payment_config = current_payment_info() if section_key == "payments" else {}
    return render_template("admin_section.html", section=section, section_key=section_key, items=items, edit_item=edit_item, users=[], school_config=school_config, payment_config=payment_config)



# ============================================================
# RUN WEBSITE
# ============================================================


if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )