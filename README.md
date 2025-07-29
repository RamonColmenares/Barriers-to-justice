# Barriers to Justice - Immigration Research Web Application

MIT Emerging Talent research project analyzing barriers to justice in the U.S. immigration system for juveniles.

## 🚀 Quick Start

### Local Development

1. **Setup (first time only):**
   ```bash
   ./setup-local.sh
   ```

2. **Run both servers:**
   ```bash
   ./run-local.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

### Manual Development

**Backend:**
```bash
cd api
pip3 install -r requirements.txt
python3 index.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Deployment

### Vercel (Production)

1. Push to GitHub
2. Import repository in Vercel
3. Deploy automatically

The `vercel.json` configuration handles both frontend and backend deployment.

## 📁 Project Structure

```
├── api/                    # Backend (Flask API)
│   ├── index.py           # Main API endpoints
│   └── requirements.txt   # Python dependencies
├── frontend/              # Frontend (SvelteKit)
│   ├── src/              # Source code
│   └── package.json      # Node dependencies
├── vercel.json           # Vercel deployment config
├── setup-local.sh        # Setup script
└── run-local.sh          # Development server script
```

## 🔍 API Endpoints

- `GET /api/health` - Health check
- `GET /api/overview` - Immigration data overview

## 👥 Team

MIT Emerging Talent students researching barriers to justice in immigration.

## 📊 Data

This application analyzes juvenile immigration case data to identify patterns and barriers in legal representation and case outcomes.

## 🔧 Technology Stack

- **Frontend:** SvelteKit, TailwindCSS
- **Backend:** Flask, Python
- **Data:** Pandas, NumPy, Plotly
- **Deployment:** Vercel
