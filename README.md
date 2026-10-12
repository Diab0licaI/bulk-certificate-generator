# Bulk Certificate Generator

A web-based application for generating personalized PDF certificates in bulk. Built with FastAPI, SQLite, SQLAlchemy, ReportLab, HTML, CSS, and JavaScript.

## Features

- Generate personalized PDF certificates for multiple recipients.
- Validate recipient names and email addresses.
- Track generation jobs and certificate statuses.
- View successful and failed certificate counts.
- Download individual certificates as PDF files.
- Store generation jobs and recipient records in SQLite.
- Use a responsive web dashboard.
- Run automated API tests with Pytest.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API |
| SQLite | Database |
| SQLAlchemy | Database ORM |
| ReportLab | PDF certificate generation |
| Pydantic | Input validation |
| HTML, CSS, JavaScript | Frontend dashboard |
| Pytest | Automated testing |

## Project Structure

```text
bulk-certificate-generator/
├── app/
│   ├── services/
│   │   └── certificate.py
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   └── test_api.py
├── certificates/
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Diab0licaI/bulk-certificate-generator.git
cd bulk-certificate-generator
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Start the application

```powershell
python -m uvicorn app.main:app --reload
```

Open the dashboard:

http://127.0.0.1:8000

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Opens the dashboard |
| POST | `/api/jobs/` | Creates a certificate generation job |
| GET | `/api/jobs/{job_id}` | Retrieves job status and recipient results |
| GET | `/api/certificates/{certificate_id}/download` | Downloads a certificate PDF |

## Example API Request

```json
{
  "event_name": "Python Backend Development Workshop",
  "issuer": "Tech Academy",
  "recipients": [
    {
      "name": "Amit Kumar",
      "email": "amit@example.com"
    },
    {
      "name": "Neha Sharma",
      "email": "neha@example.com"
    }
  ]
}
```

## Run Tests

Run the automated test suite:

```powershell
python -m pytest -v
```

The initial test suite contains tests for the homepage, certificate job creation, and empty recipient validation.

## How It Works

1. Enter event details and recipient information in the dashboard.
2. Submit the form to create a generation job.
3. The backend validates recipients and stores job information in SQLite.
4. FastAPI background tasks generate individual PDF certificates.
5. The dashboard displays job results and download links for successful certificates.

## Future Improvements

- CSV upload for large recipient lists.
- Customizable certificate templates and branding.
- ZIP download for all certificates in a job.
- Durable background processing for production workloads.
- Deployment to a public hosting platform.

## Author

**Dipu Kumar Rajak**

GitHub: [Diab0licaI](https://github.com/Diab0licaI)

---

This project was developed as a practical demonstration of API development, database integration, PDF generation, frontend development, and automated testing.
