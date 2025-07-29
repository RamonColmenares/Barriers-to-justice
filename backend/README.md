# Immigration Data API Backend

A simple Python backend API to serve processed immigration data for dynamic dashboards.

## Features

- RESTful API for immigration case data
- Data aggregation and filtering endpoints
- CORS support for frontend integration
- Efficient data processing with pandas

## API Endpoints

### Data Endpoints
- `GET /api/cases/summary` - Get case statistics summary
- `GET /api/cases/trends` - Get time-based trends
- `GET /api/cases/demographics` - Get demographic breakdowns
- `GET /api/cases/outcomes` - Get case outcome statistics
- `GET /api/cases/courts` - Get court-specific data

### Filter Parameters
- `start_date` - Filter by start date (YYYY-MM-DD)
- `end_date` - Filter by end date (YYYY-MM-DD)
- `court` - Filter by court name/code
- `outcome` - Filter by case outcome
- `age_group` - Filter by age group (juvenile, adult)

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Data Sources

This API serves processed data from EOIR (Executive Office for Immigration Review) datasets, specifically focusing on juvenile immigration cases from 2018-2025.
