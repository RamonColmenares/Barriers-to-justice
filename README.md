# 🌐 Immigration Research Platform - Web Application

This directory contains the complete web application for the Immigration Research Platform, including both frontend and backend components, along with Docker configuration for easy deployment.

## 📁 Structure

```
web/
├── backend/           # Flask API server with real data integration
│   ├── app.py         # Main Flask application
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/          # SvelteKit web application
│   ├── src/           # Source code
│   ├── package.json
│   ├── Dockerfile
│   └── .dockerignore
└── README.md          # This file
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

From the project root directory, run:

```bash
# Make sure you're in the project root
cd /path/to/ET6-CDSP-group-19-repo

# Deploy everything with one command
./deploy.sh
```

This will:
- Build both frontend and backend Docker images
- Start services with docker-compose
- Make the application available at:
  - 🌐 **Frontend**: http://localhost:3000
  - 🔌 **Backend API**: http://localhost:5000

### Option 2: Manual Development

If you want to run components separately for development:

#### Backend
```bash
cd web/backend
pip install -r requirements.txt
python app.py
```

#### Frontend
```bash
cd web/frontend
npm install
npm run dev
```

## 🔧 Configuration

### Environment Variables

The application supports the following environment variables:

#### Backend
- `FLASK_ENV`: Set to `production` or `development`
- `FLASK_DEBUG`: Set to `false` for production

#### Frontend
- `NODE_ENV`: Set to `production` or `development`
- `VITE_API_URL`: Backend API URL (default: `http://localhost:5000`)

### Data Sources

The backend automatically attempts to load real immigration data from:
- `4_data_analysis/juvenile_cases_cleaned.csv.gz`
- `4_data_analysis/juvenile_reps_assigned.csv.gz`
- `4_data_analysis/juvenile_proceedings_cleaned.csv.gz`

If real data files are not found, the application falls back to simulated data for demonstration purposes.

## 📊 Features

### Frontend Features
- **Interactive Dashboards**: Dynamic charts using Plotly.js
- **Real-time Data**: Connects to backend API for live data
- **Responsive Design**: Works on desktop and mobile
- **Professional UI**: Clean, modern interface with Tailwind CSS

### Backend Features
- **Real Data Integration**: Uses actual EOIR juvenile immigration datasets
- **RESTful API**: Clean API endpoints for data access
- **Chart Generation**: Plotly-powered chart generation
- **Data Analysis**: Replicates analysis from research notebooks
- **Health Monitoring**: Built-in health checks

### Available Charts
1. **Legal Representation Analysis**: Success rates by representation status
2. **Time Series Analysis**: Representation rates over time (2018-2024)
3. **Odds Ratio Analysis**: Logistic regression results
4. **Outcome Percentages**: Stacked bar charts of case outcomes
5. **Demographics**: Age group breakdowns
6. **Geographic Analysis**: Case volumes by country of origin
7. **Court Performance**: Comparative court statistics

## 🔌 API Endpoints

### Health & Status
- `GET /api/health` - Service health check
- `GET /api/cases/summary` - Case summary statistics

### Chart Data
- `GET /api/charts/representation` - Legal representation analysis
- `GET /api/charts/time-series` - Time series analysis
- `GET /api/charts/odds-ratio` - Logistic regression odds ratios
- `GET /api/charts/outcome-percentages` - Outcome percentage breakdown
- `GET /api/charts/trends` - General trends over time
- `GET /api/charts/demographics` - Demographic breakdowns
- `GET /api/charts/countries` - Country-specific data
- `GET /api/charts/courts` - Court performance metrics

### Filtering
All chart endpoints support query parameters for filtering:
- `start_date` / `end_date`: Date range filtering
- `court`: Filter by specific court
- `representation`: Filter by representation status
- `age_group`: Filter by age group
- `country`: Filter by country of origin

## 🛠️ Development

### Adding New Charts

1. **Backend**: Add new endpoint in `app.py`:
```python
@app.route('/api/charts/new-chart', methods=['GET'])
def get_new_chart():
    # Your chart logic here
    return jsonify({'chart': chart_data})
```

2. **Frontend**: Add chart loading function in `findings/+page.svelte`:
```javascript
async function loadNewChart() {
    const response = await fetch(`${API_BASE_URL}/charts/new-chart`);
    const data = await response.json();
    // Render with Plotly
}
```

### Debugging

- **View logs**: `docker-compose logs -f`
- **Restart services**: `docker-compose restart`
- **Rebuild**: `docker-compose up --build`

## 🔒 Production Deployment

For production deployment:

1. **Environment**: Set production environment variables
2. **Security**: Configure proper CORS settings
3. **SSL**: Add HTTPS certificates
4. **Scaling**: Use Docker Swarm or Kubernetes for scaling
5. **Monitoring**: Add application monitoring (Prometheus, etc.)

## 📝 Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 3000 and 5000 are available
2. **Data files missing**: Ensure data files are in `4_data_analysis/` directory
3. **Docker issues**: Restart Docker service and try again
4. **Build failures**: Clear Docker cache with `docker system prune`

### Getting Help

- Check logs: `docker-compose logs -f [service-name]`
- Verify health: Visit http://localhost:5000/api/health
- Check network: `docker-compose ps`

## 📈 Performance

The application is optimized for:
- **Fast loading**: Efficient data processing and caching
- **Responsive UI**: Optimized frontend bundle size
- **Scalability**: Stateless API design for horizontal scaling
- **Real-time updates**: WebSocket support for live data updates

---

**🎯 Ready to explore juvenile immigration data with powerful visualizations and real-time analytics!**
# ET6-CDSP-group-19-repo-web
