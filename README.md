# Evidentia

A desktop-based digital evidence timeline system that extracts and organizes metadata from digital files to support structured investigation analysis.

## Description

Evidentia is a digital forensics tool designed to help investigators manage cases, upload evidence files, extract metadata, and visualize timelines. The application provides an intuitive interface for organizing digital evidence and generating comprehensive reports.

## Team Members

- Gul-e-Zara (24L-2592)
- Rumesha Naveed (24L-2603)

## Tech Stack

- Backend: Python
- Frontend: PySide6 (Qt for Python)
- Database: SQLite

## Project Structure

```
evidentia/
├── backend/          # Backend logic and data processing
│   └── app/          # Application logic, routes, models
├── frontend/         # UI components and screens
│   └── src/          # Component files, pages, assets
├── database/         # Database files and schemas
│   ├── schema.sql    # Database schema
│   └── evidentia.db  # SQLite database
├── docs/             # Project documentation and iteration documents
├── requirements.txt  # Python dependencies
├── .gitignore        # Files to exclude from version control
└── README.md         # This file
```

## How to Run

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Backend

1. Navigate to the project root directory:
   ```bash
   cd evidentia
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database (if needed):
   ```bash
   python -c "from backend.app.database import init_database; init_database()"
   ```

### Frontend

Run the application:
```bash
python main.py
```

## Features

- Case management and organization
- Evidence file upload and tracking
- Metadata extraction from digital files
- Timeline visualization
- Report generation
- User authentication and profiles


