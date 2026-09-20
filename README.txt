
FRIENDS SCHOOL MBALE WEBSITE
=============================

Project:
Friends School – Mbale

Location:
Sabatia Sub-County, Vihiga County

Principal:
Manasseh Kagasi

Telephone:
0728 382395

Email:
mbalehighoffice@gmail.com

KNEC:
38622202

UIC:
QGV4


HOW TO RUN
----------

1. Open PowerShell.

2. Go to the project folder:

   cd "$env:USERPROFILE\Desktop\MbaleHighWebsite"

3. Start the Flask server:

   python app.py

4. Open your browser and visit:

   http://127.0.0.1:5000


FOLDER STRUCTURE
----------------

MbaleHighWebsite/
│
├── app.py
├── README.txt
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── about.html
│   ├── academics.html
│   ├── news.html
│   ├── gallery.html
│   └── contact.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    ├── js/
    │   └── script.js
    │
    └── images/


ADDING SCHOOL PHOTOS
--------------------

Put permitted school photographs inside:

static/images/

The homepage currently looks for:

school.jpg

So if you have a permitted school photograph, rename it:

school.jpg

and place it inside:

static/images/


IMPORTANT
---------

This is a Flask development website project.
Before publishing it as an official school website,
verify contact details, school leadership, photographs,
official branding and other current information with
the school.
