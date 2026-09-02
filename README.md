# LinkedIn Profile Search Application

A full-stack web application designed to parse, ingest, search, and filter candidate profiles from a dataset. Built with Django REST Framework on the backend and React with Tailwind CSS on the frontend.

---

## 🌟 Key Features

- **Data Ingestion & Parsing:** Custom Django management command (`import_csv`) that safely handles complex string formatting, single/multi-line fields, and both CSV and JSON formats without breaking line counts.
- **Full-Text & Multi-Field Search:** Instant search functionality filtering candidates across `full_name`, `job_title`, `summary`, and `skills`.
- **Dynamic Filtering:** Live dropdown filters for specific Job Roles (`job_title_role`) and Candidate Locations (`location_country`).
- **Debounced Input:** Frontend search input uses debouncing (300ms) to prevent unnecessary network requests while typing.
- **Clean UI & Responsive Design:** Built using React, Tailwind CSS, and Lucide icons for an intuitive user experience.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Django 5+, Django REST Framework, SQLite
- **Frontend:** React 18+, Vite, Tailwind CSS, Axios, Lucide React
- **Tooling & Environment:** `venv`, `npm`

---

## 🏗️ System Architecture & Design Decisions

### 1. Robust Data Parsing (`import_csv.py`)
To handle unescaped commas, newlines, and quotes within LinkedIn summaries, the import command uses standard Python `csv` and `json` readers instead of strict rigid line-by-line parsers. This ensures all candidate profiles are ingested into SQLite without field mismatch errors (`ParserError`).

### 2. Search & Query Optimization
The Django REST Framework backend utilizes Django `Q` objects for efficient ORM queries:
- Partial case-insensitive matches (`icontains`) for text search.
- Exact match filtering for dropdowns (`role` and `country`).
- Dynamic aggregation for filter dropdown values sent directly in the initial API metadata.

### 3. Modern React Frontend
- Powered by **Vite** for high-performance developer build times.
- Styled using **Tailwind CSS** for clean responsive utility classes.
- Direct link integration to candidate LinkedIn profiles (`linkedin_url`).

---

## 🚀 Getting Started

Follow these steps to set up and run the application locally.

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher & npm

---

### 📦 Installation & Setup

#### 1. Repository Setup
```bash
git clone [https://github.com/pedimmdi/linkedin-search-app.git](https://github.com/pedimmdi/linkedin-search-app.git)
cd linkedin-search-app

#### 2. Backend Setup (Django)
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install django djangorestframework django-cors-headers pandas

# Run migrations
python manage.py migrate

# Import dataset into database (Make sure 300 user linkedin.txt is in the backend directory)
python manage.py import_csv "300 user linkedin.txt"

# Start the Django development server
python manage.py runserver
The backend server will run at http://127.0.0.1:8000/.

#### Frontend Setup (React + Vite)
Open a new terminal window:
# Navigate to frontend directory from project root
cd frontend

# Install node dependencies
npm install

# Start the Vite development server
npm run dev

The frontend application will be live at http://localhost:5173/.

#### API Endpoints Summary
Method,Endpoint,Description
GET,/api/profiles/search/,"Search profiles with query parameters (q, role, country)"

#### Example Query
GET /api/profiles/search/?q=developer&role=Software%20Engineer&country=United%20States

📄 License
This project is open-source and available under the MIT License.