from flask import Flask, render_template

app = Flask(__name__)


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
        school=SCHOOL,
        pathways=PATHWAYS
    )


@app.route("/about")
def about():

    return render_template(
        "about.html",
        school=SCHOOL
    )


@app.route("/academics")
def academics():

    return render_template(
        "academics.html",
        school=SCHOOL,
        pathways=PATHWAYS
    )


@app.route("/news")
def news():

    return render_template(
        "news.html",
        school=SCHOOL
    )


@app.route("/gallery")
def gallery():

    return render_template(
        "gallery.html",
        school=SCHOOL
    )


@app.route("/contact")
def contact():

    return render_template(
        "contact.html",
        school=SCHOOL
    )


# ============================================================
# SCHOOL FEES / PAYMENTS
# ============================================================

@app.route("/fees")
def fees():

    return render_template(
        "fees.html",
        school=SCHOOL,
        payment_info=PAYMENT_INFO
    )


# ============================================================
# PATHWAY PAGE
# ============================================================

@app.route("/pathways/<pathway_key>")
def pathway_page(pathway_key):

    pathway = PATHWAYS.get(pathway_key)

    if pathway is None:

        return render_template(
            "404.html",
            school=SCHOOL,
            message="The requested pathway was not found."
        ), 404

    return render_template(
        "pathway.html",
        pathway=pathway,
        pathway_key=pathway_key,
        school=SCHOOL
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
            school=SCHOOL,
            message="The requested pathway was not found."
        ), 404

    subject = pathway["subjects"].get(subject_key)

    if subject is None:

        return render_template(
            "404.html",
            school=SCHOOL,
            message="The requested subject was not found."
        ), 404

    return render_template(
        "subject.html",
        pathway=pathway,
        pathway_key=pathway_key,
        subject=subject,
        subject_key=subject_key,
        resource_types=RESOURCE_TYPES,
        school=SCHOOL
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
            school=SCHOOL,
            message="The requested pathway was not found."
        ), 404

    subject = pathway["subjects"].get(subject_key)

    if subject is None:

        return render_template(
            "404.html",
            school=SCHOOL,
            message="The requested subject was not found."
        ), 404

    resource = RESOURCE_TYPES.get(resource_key)

    if resource is None:

        return render_template(
            "404.html",
            school=SCHOOL,
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
        school=SCHOOL
    )


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


# ============================================================
# RUN WEBSITE
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )