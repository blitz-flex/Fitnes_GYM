# 🏋️ GYM - Fitness Management System

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/yourusername/Fitnes_GYM_tt)

> A Hyper-Premium, SaaS-grade administrative dashboard and public portal for modern fitness centers. Featuring glassmorphism design, real-time analytics, and full Georgian/English localization.

---

## ✨ Key Features

### 🏢 Public Portal

- **Immersive UX**: Modern glassmorphism UI with smooth animations and responsive layouts.
- **Program Enrollment**: Seamless registration for Yoga, Crossfit, Boxing, and more.
- **Dynamic Blog**: Multi-category fitness articles with reading time estimation and AI-assisted content.
- **Bilingual Support**: Full English and Georgian localization with persistent preference.

### 🛡️ Administrative Suite

- **Advanced Analytics**: Real-time KPI tracking, demographic insights, and interactive charts (Chart.js).
- **User Management**: Complete control over accounts, roles, and profile settings.
- **Content Engine**: Full CRUD for blog posts with advanced image processing (Pillow).
- **Security**: Role-based access control (RBAC), password hashing, and secure session management.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12, Flask, SQLAlchemy, Flask-Migrate, Flask-Mail |
| **Frontend** | HTML5, CSS3 (Vanilla + Glassmorphism), JavaScript (ES6+), Bootstrap 5 |
| **Database** | SQLite (Development), PostgreSQL (Production ready) |
| **Security** | Flask-Login, Authlib (Google OAuth 2.0), Werkzeug |

---

## 📁 Project Structure

```text
├── src/
│   ├── models/       # Database Schemas (SQLAlchemy)
│   ├── views/        # Blueprints & Route Handlers
│   ├── templates/    # Jinja2 Templates (Modularized)
│   ├── static/       # CSS, JS, and Media Assets
│   ├── extensions.py # Flask Extension Initializations
│   └── utils.py      # Helper Functions (Images, Slugs)
├── instance/         # Local Database & Instance Files
├── migrations/       # Database Migration Scripts
├── app.py            # Application Entry Point
└── requirements.txt  # Project Dependencies
```

---

## 🌐 Deployment

The project is configured for deployment on platforms like **Render**

📌 **Live Demo:** [Fitnes GYM Live](https://fitnes-gym.onrender.com/)
