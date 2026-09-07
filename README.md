# LinkedIn Profile Search

A production-minded full-stack search application for exploring a supplied LinkedIn profile dataset.

The project implements the core requirements of the take-home assignment: reliable dataset ingestion, keyword search, multiple filters, a clean REST API, a responsive React interface, pagination, Elasticsearch-backed search, PostgreSQL persistence, Docker-based local setup, and automated CI checks.

## ✨ Features

- **Keyword search** across profile name, job title, skills, summary, and city.
- **Fuzzy search** powered by Elasticsearch to tolerate small spelling differences.
- **Two independent filters**: job role and country.
- **Combined search + filters** with pagination.
- **Search highlighting** for matched profile fields.
- **Responsive profile cards** with skills, location, summary, and LinkedIn links.
- **Debounced search input** to avoid a request on every keystroke.
- **Loading, empty, validation, and service-error states** in the UI.
- **Robust dataset importer** designed to handle irregular/malformed rows in the supplied source file.
- **PostgreSQL persistence** for canonical profile records.
- **Elasticsearch index** optimized for full-text search and filtering.
- **Docker Compose** setup for the complete local stack.
- **Health endpoint** covering database and Elasticsearch availability.
- **Automated CI** for backend tests and frontend lint/build checks.

## 📸 Screenshots

### Home / Search

![LinkedIn Profile Search - Home](docs/screenshots/LinkedIn%20Profile%20Search%28Home%29.png)

### Search + Filters

![LinkedIn Profile Search - Search and Filter](docs/screenshots/LinkedIn%20Profile%20Search%28Search%2BFilter%29.png)

### Pagination

![LinkedIn Profile Search - Pagination](docs/screenshots/LinkedIn%20Profile%20Search%28Pagination%29.png)

## 🏗️ Architecture

The application is intentionally split into clear responsibilities:

```text
┌──────────────────────────────┐
│        React + Vite UI       │
│ Tailwind CSS + Axios + Icons │
└──────────────┬───────────────┘
               │ HTTP / JSON
               ▼
┌──────────────────────────────┐
│     Django REST Framework    │
│      API + Search Service    │
└──────────┬───────────┬───────┘
           │           │
           │           └──────────────────┐
           ▼                              ▼
┌────────────────────┐        ┌────────────────────┐
│    PostgreSQL      │        │   Elasticsearch    │
│ canonical profiles │        │ search index       │
└────────────────────┘        └────────────────────┘
```

### Responsibilities

| Layer | Responsibility |
| --- | --- |
| **React / Vite** | Search UI, filters, pagination, loading/error states, and result presentation. |
| **Django REST Framework** | HTTP API, request validation, pagination, health checks, and application orchestration. |
| **Search service** | Builds Elasticsearch queries, applies filters, ranking, highlighting, and maps search hits back to Django profiles. |
| **PostgreSQL** | Stores the canonical `Profile` records. |
| **Elasticsearch** | Provides full-text search, fuzzy matching, filtering, ranking, and highlights. |
| **Docker Compose** | Runs PostgreSQL, Elasticsearch, Django, and the production-style frontend container together. |

## 🔎 Search & Filtering

Keyword search is implemented in Elasticsearch rather than with database `icontains` queries. This keeps the search concern isolated in a dedicated service and makes ranking/highlighting available without coupling the API to database-specific full-text behavior.

The keyword query searches these fields with different weights:

```text
full_name^4
job_title^3
skills^2
summary
location_city
```

This means a name match is considered more relevant than a match in a less important text field. Elasticsearch `fuzziness: AUTO` is enabled, while the query uses `operator: and` so all query terms must participate in the match.

When no keyword is supplied, the service uses `match_all` and the filters can still be applied independently.

The available filters are:

- **Role** → exact match against `job_title_role`.
- **Country** → exact match against `location_country`.

Results are ordered primarily by Elasticsearch relevance score and secondarily by profile name for deterministic ordering.

### Why PostgreSQL + Elasticsearch?

PostgreSQL is the source of truth for application records, while Elasticsearch is a purpose-built read/search index. Search results contain the indexed Django profile ID; the API then loads the canonical records from PostgreSQL. This separation keeps persistence and search responsibilities explicit and makes the search implementation easy to evolve.

## 📥 Dataset Ingestion

The supplied dataset is not treated as a perfectly clean CSV. The importer contains defensive parsing and semantic field detection so that irregular quoting, inconsistent row widths, embedded structures, and malformed records do not prevent the usable profiles from being imported.

The main command is:

```bash
python manage.py import_csv "300 user linkedin.txt"
```

After importing, the Elasticsearch index is rebuilt with:

```bash
python manage.py reindex_profiles
```

The Docker setup copies the dataset into the backend image, so the same commands can be executed directly inside the running backend container.

## 🚀 Quick Start with Docker

### Prerequisites

- [Docker](https://www.docker.com/) with Docker Compose support.
- Git.

### 1. Clone the repository

```bash
git clone https://github.com/pedimmdi/linkedin-search-app.git
cd linkedin-search-app
```

### 2. Build and start the stack

```bash
docker compose build
docker compose up -d
```

The backend container runs Django migrations automatically on startup. PostgreSQL and Elasticsearch have health checks, and the backend waits for both services to become healthy.

### 3. Import the supplied dataset

```bash
docker compose exec backend python manage.py import_csv "/app/300 user linkedin.txt"
```

### 4. Build the Elasticsearch index

```bash
docker compose exec backend python manage.py reindex_profiles
```

### 5. Open the application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/
- **Health check:** http://localhost:8000/api/health/
- **Elasticsearch:** http://localhost:9200
- **PostgreSQL:** localhost:55432

### Useful Docker commands

```bash
# View service status
docker compose ps

# Follow backend logs
docker compose logs -f backend

# Follow all logs
docker compose logs -f

# Stop services
docker compose down

# Stop services and remove persisted database/index volumes
docker compose down -v
```

> The Compose configuration uses development credentials and settings for local evaluation. It is not intended as a production deployment configuration.

## 🧪 Testing & Quality Checks

### Backend

Run the Django test suite inside the backend container:

```bash
docker compose exec backend python manage.py test
```

Run Django's system checks:

```bash
docker compose exec backend python manage.py check
```

### Frontend

For local frontend development:

```bash
cd frontend
npm install
npm run lint
npm run build
```

### Continuous Integration

GitHub Actions runs the same core quality gates on pushes to `main` and pull requests:

- Backend: dependency installation, PostgreSQL-backed migrations, and Django tests.
- Frontend: `npm ci`, ESLint, and production build.

Workflow definition: `.github/workflows/ci.yml`.

## 💻 Local Development Without Docker

Docker Compose is the recommended path because the application depends on both PostgreSQL and Elasticsearch. If running services manually, start PostgreSQL and Elasticsearch first and configure the backend environment accordingly.

### Backend

```bash
cd backend
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies and configure environment variables:

```bash
pip install -r requirements.txt
copy .env.example .env
```

On Linux/macOS, use `cp .env.example .env` instead of `copy`.

Then run:

```bash
python manage.py migrate
python manage.py import_csv "300 user linkedin.txt"
python manage.py reindex_profiles
python manage.py runserver
```

The backend uses `http://127.0.0.1:8000` by default.

### Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server runs at `http://localhost:5173`.

The frontend API base URL can be configured through `VITE_API_BASE_URL`.

## 🔌 API Reference

### Health

```http
GET /api/health/
```

Returns the application health status, including database and Elasticsearch checks.

### Search profiles

```http
GET /api/profiles/search/
```

Query parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| `q` | string | Keyword search. Optional. |
| `role` | string | Exact job-role filter. Optional. |
| `country` | string | Exact country filter. Optional. |
| `page` | integer | 1-based result page. Optional; defaults to `1`. |

Example:

```text
/api/profiles/search/?q=engineer&country=united%20states&page=1
```

The response contains the total count, pagination links, profile results, and search highlights.

### Filter options

```http
GET /api/profiles/filters/
```

Returns the available job-role and country values used by the frontend filter controls.

## 📁 Project Structure

```text
linkedin-search-app/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── config/                  # Django project configuration
│   ├── profiles/                # Profile model, API, search service, commands, tests
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── import_csv.py
│   │   │       └── reindex_profiles.py
│   │   ├── services/
│   │   │   └── search.py
│   │   └── search_index.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── 300 user linkedin.txt   # supplied dataset
├── frontend/
│   ├── src/
│   │   ├── api/                 # API client
│   │   ├── components/           # reusable UI components
│   │   └── ...
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docs/
│   └── screenshots/             # application screenshots
├── docker-compose.yml
└── README.md
```

## 🧩 Design Notes

### Separation of concerns

Search construction lives in a dedicated backend service instead of being embedded directly in the API view. The frontend communicates with the API through a small Axios client, keeping transport details separate from UI components.

### Pagination

The API uses Elasticsearch pagination with a fixed page size of 20. The backend validates page bounds and protects the Elasticsearch result window. The frontend exposes previous/next navigation and compact page controls.

### Resilience

The UI explicitly handles loading, empty results, invalid requests, and backend service failures. Backend search errors are surfaced as service-unavailable responses instead of returning misleading empty search results.

### Data consistency

Elasticsearch stores the fields required for searching and the Django profile ID. The API resolves returned IDs against PostgreSQL before serializing results, keeping PostgreSQL as the canonical profile store.

## 📝 Notes

- The application is designed for local evaluation and demonstration of the requested search/filter workflow rather than production deployment.
- LinkedIn profile links are opened directly in the user's browser. Their availability and access behavior are controlled by LinkedIn and may vary by network/session.
- The supplied dataset is included in the repository because it is part of the take-home assignment and is required for a straightforward clone-and-run evaluation workflow.

## 👤 Author

Built as a full-stack take-home assignment demonstrating backend architecture, search implementation, frontend integration, containerization, testing, and documentation.
