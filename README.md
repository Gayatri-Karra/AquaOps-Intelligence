# AquaOps Intelligence
### Smart Water Treatment Monitoring & Predictive Maintenance

AquaOps Intelligence is a Python and PostgreSQL-based monitoring dashboard for water treatment plants. It organizes sensor readings, equipment information, and maintenance records into a centralized dashboard.

## Features
- **Plant Overview:** View plant, equipment, and sensor summaries.
- **Sensor Monitoring:** View recent sensor readings.
- **Trend Analysis:** Explore sensor parameter trends over a selected time window.
- **Equipment Monitoring:** Review equipment status across plants.
- **Maintenance Tracking:** View maintenance work orders and priorities.

## Tech Stack
- **Language:** Python
- **Database:** PostgreSQL
- **Database Toolkit:** SQLAlchemy
- **Dashboard:** Streamlit
- **Data Processing:** Pandas
- **Visualization:** Plotly
- **Testing:** Pytest

## Project Structure
```text
aquaops-intelligence/
├── sql/
│   ├── migrations/
│   └── seeds/
├── src/
│   └── aquaops/
│       ├── config.py
│       ├── queries.py
│       └── dashboard.py
├── tests/
├── data/
├── logs/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/Gayatri-Karra/aquaops-intelligence.git
cd aquaops-intelligence
```

### 2. Create and activate a virtual environment
Windows PowerShell:
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

### 4. Configure environment variables
Create a `.env` file in the project root.

```env
APP_ENV=development
LOG_LEVEL=INFO
POSTGRES_DB=aquaops_db
POSTGRES_USER=aquaops_user
POSTGRES_PASSWORD=aquaops_password
DB_HOST=localhost
DB_PORT=5432
```

Use your actual local PostgreSQL credentials. Do not commit `.env`.

### 5. Start PostgreSQL
Start the project's configured PostgreSQL service using Docker Compose:

```powershell
docker compose up -d
```

### 6. Initialize the database
Apply the schema migration and load the sample dataset using the SQL files in `sql/migrations/` and `sql/seeds/`.

Run the migration and seed scripts only as intended for your database setup.

### 7. Launch the dashboard
```powershell
python -m streamlit run src/aquaops/dashboard.py --server.port 8502
```

Open http://localhost:8502.

## Testing
```powershell
python -m pytest -v
ruff check src tests
```

## Data
The project uses sample/demo data for development. Sensor readings should not be interpreted as live measurements from real water treatment plants.

## Current Scope
The project focuses on database-backed monitoring, trend visualization, equipment summaries, and maintenance tracking.

Predictive maintenance is a project direction, not a validated prediction capability in the current dashboard.

## Future Improvements
- Maintenance risk scoring
- Sensor anomaly detection
- Improved data validation
- Additional reporting features
