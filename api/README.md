# Juvenile Immigration API - Refactored Structure

This API has been refactored into modular components for better maintainability and organization.

## Project Structure

```
api/
├── __init__.py              # Package initialization
├── index.py                 # Main Flask application and routes
├── config.py                # Configuration and constants
├── models.py                # Data models and cache management
├── data_loader.py           # Data loading functionality
├── data_processor.py        # Data processing and analysis
├── chart_generator.py       # Chart generation functionality
├── api_routes.py            # API route handlers
├── requirements.txt         # Python dependencies
└── cache/                   # Cache directory for processed data
```

## Module Overview

### 1. `config.py`
- Application configuration
- Google Drive file IDs
- Decision code classifications
- Directory path helpers

### 2. `models.py`
- `DataCache` singleton class for managing cached data
- Thread-safe data access patterns
- Cache statistics and status management

### 3. `data_loader.py`
- Google Drive download functionality
- Local file loading
- Cache management (save/load)
- Fallback sample data generation

### 4. `data_processor.py`
- Data merging and processing logic (exactly like notebook)
- Policy era determination
- Legal representation analysis
- Statistical calculations

### 5. `chart_generator.py`
- Plotly chart generation
- Representation vs outcomes charts
- Time series analysis charts
- Chi-square analysis results

### 6. `api_routes.py`
- All API endpoint handler functions
- Business logic for each route
- Error handling and response formatting

### 7. `index.py`
- Flask application setup
- Route registration
- CORS configuration
- Vercel handler function

## Benefits of Refactoring

1. **Modularity**: Each file has a single responsibility
2. **Maintainability**: Easier to find and modify specific functionality
3. **Testability**: Individual modules can be tested independently
4. **Readability**: Code is organized logically
5. **Reusability**: Functions can be imported and reused
6. **Scalability**: Easy to add new features without bloating files

## Running the Application

### Development
```bash
cd api
python3 index.py
```

### Production (Vercel)
The `handler` function in `index.py` serves as the entry point for Vercel deployment.

## Import Strategy

The modules use a flexible import strategy that works both:
- As part of a package (with relative imports)
- As standalone modules (with absolute imports)

This allows for easier testing and development while maintaining package structure for production.

## API Endpoints

All original endpoints are preserved:
- `/api/health` - Health check
- `/api/overview` - Data overview and statistics
- `/api/load-data` - Trigger data loading
- `/api/force-reload-data` - Force reload from Google Drive
- `/api/data-status` - Check data loading status
- `/api/findings/representation-outcomes` - Representation vs outcomes chart
- `/api/findings/time-series` - Time series analysis
- `/api/findings/chi-square` - Statistical analysis
- `/api/findings/outcome-percentages` - Outcome percentage breakdown
