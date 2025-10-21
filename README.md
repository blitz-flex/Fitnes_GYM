# Fitnes_GYM 💪

A comprehensive fitness gym management web application built with Flask.

## 📋 Project Description

Fitnes_GYM is a web-based application designed for efficient management of fitness gyms. The project is built on the Python Flask framework and provides a user-friendly interface for managing gym operations, memberships, and member activities.


## 🚀 Setup and Running

### Prerequisites

- Python 3.x or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Git

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/blitz-flex/Fitnes_GYM.git
cd Fitnes_GYM
```

2. **Create a virtual environment:**
```bash
python -m venv venv
```

3. **Activate the virtual environment:**
   - On Linux/macOS:
   ```bash
   source venv/bin/activate
   ```
   - On Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Install required packages:**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables:**
   - Create a `.env` file in the root directory
   - Add necessary configuration variables

6. **Run database migrations:**
```bash
flask db upgrade
```

7. **Run the application:**
```bash
python app.py
```

8. **Access the application:**
   - Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## 📦 Features

- **👥 Members Management** - Add, update, and manage gym members
- **📅 Subscription Administration** - Handle membership plans and subscriptions
- **💳 Payment Tracking** - Monitor and record member payments
- **📊 Statistics and Reports** - View gym analytics and generate reports
- **🔐 User Authentication** - Secure login system for staff
- **📱 Responsive Design** - Works on desktop and mobile devices
- **🔔 Notifications** - Send alerts and reminders to members
