# Neon Attendance Pro

A QR-based classroom attendance project built with Django.

## Features

- Teacher dashboard
- Student accounts
- QR attendance sessions
- Duplicate attendance prevention
- SQLite database
- Neon interface

## Installation

Install Python and run:

    pip install -r requirements.txt

Then run:

    python manage.py makemigrations attendance
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Open http://127.0.0.1:8000/
