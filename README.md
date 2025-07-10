![Built with Flask](https://img.shields.io/badge/Built%20with-Flask-000?logo=flask)
![Deployed on Railway](https://img.shields.io/badge/Deployed%20on-Railway-5528FF?logo=railway)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
![Last Commit](https://img.shields.io/github/last-commit/Hcha-byte/WaypointsAndWonders)
![Issues](https://img.shields.io/github/issues/Hcha-byte/WaypointsAndWonders)

**Waypoints and Wonders** is a Flask-based blog platform designed for travelers, storytellers, and wanderers to share
their journeys through Markdown-powered posts, beautiful images, and a clean, user-friendly interface.

## ✨ Features

* 📝 Markdown-based blog post creation
* 📸 Cloudinary-powered image upload
* 🔍 Typesense-integrated search
* 🔐 Google login authentication
* 🧠 Admin content management
* 🌐 Fully responsive layout

## 🚀 Quick Start

1. **Clone the repo**

   ```bash
   git clone https://github.com/Hcha-byte/WaypointsAndWonders.git
   cd WaypointsAndWonders
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Copy `.env.example` to `.env` and fill in your values:

   ```bash
   cp .env.example .env
   ```

5. **Run the app**

   ```bash
   hypercorn run:app --bind 0.0.0.0:5000 --certfile cert.pem --keyfile key.pem --reload --access-logfile - --access-logformat ' -- %(r)s %(s)s' --log-level info | python3 log_colorizer.py
   ```

## 🛠 Tech Stack

* Python + Flask
* Jinja2 templates
* PostgreSQL
* Cloudinary (media hosting)
* Typesense (search engine)
* Railway (hosting)

## 📂 Project Structure

```
WaypointsAndWonders/
├── .venv/                       # Local virtual environment (not committed to git)
├── app/                         # Main Flask application package
│   ├── admin/                   # Admin-related views and logic
│   ├── auth/                    # Authentication (login, signup, Google OAuth)
│   ├── main/                    # Home and general routes
│   ├── posts/                   # Blog post viewing
│   ├── search/                  # Search routes and logic (uses Typesense)
│   ├── static/                  # Static files (CSS, images)
│   │   ├── css/                 # Stylesheets
│   │   └── images/              # Static image assets
│   ├── templates/               # Jinja2 templates
│   │   ├── admin/               # Admin dashboard templates
│   │   ├── email/               # Email-related templates (e.g. confirmation)
│   │   ├── password/            # Password reset/change templates
│   │   └── terms_and_privacy/   # Legal info templates
│   │   # etc.
│   ├── __init__.py        # App factory function
│   ├── cli.py             # Custom CLI commands (e.g. database seed)
│   ├── database.py        # Database connection and helpers
│   ├── decoraters.py      # Custom decorators (e.g. admin_required)
│   ├── extensions.py      # Initialize extensions like login, db, etc.
│   └── models.py          # SQLAlchemy database models
├── migrations/            # Database migration files (e.g. Alembic)
├── .gitignore             # Files/folders to exclude from git
├── cert.pem               # SSL certificate (dev only)
├── config.py              # Flask config settings
├── key.pem                # SSL key (dev only)
├── LICENSE                # MIT License file
├── log_colorizer.py       # Optional logging formatter (colors)
├── Procfile               # For deployment on platforms like Railway
├── README.md              # Project overview and instructions
├── requirements.txt       # Python package dependencies
└──  run.py                # Entrypoint for running the app

```

## 🧑‍💻 Contributing

Please follow best practices for contributing to this project.

## 📝 License

This project is licensed under the [MIT License](LICENSE).
