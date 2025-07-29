#!/bin/bash

# 🆓 Script de Despliegue Gratuito
# Frontend: Vercel | Backend: Railway

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "🆓 Immigration Research Platform - Free Deployment"
echo "================================================="

print_status "Opciones de despliegue gratuito disponibles:"
echo ""
echo "1. 🚄 Railway (Backend) + Vercel (Frontend) - RECOMENDADO"
echo "2. 🎨 Render (Full Stack)"
echo "3. 🪰 Fly.io (Full Stack)"
echo "4. 📦 GitHub Pages + Netlify Functions"
echo ""

read -p "Selecciona una opción (1-4): " choice

case $choice in
    1)
        print_status "🚀 Configurando para Railway + Vercel..."
        
        # Verificar si existe .git
        if [ ! -d ".git" ]; then
            print_warning "Necesitas inicializar Git primero:"
            echo "git init"
            echo "git add ."
            echo "git commit -m 'Initial commit'"
            echo "git remote add origin https://github.com/tu-usuario/tu-repo.git"
            echo "git push -u origin main"
            exit 1
        fi
        
        print_status "✅ Setup completo para Railway + Vercel"
        echo ""
        echo "📋 Pasos siguientes:"
        echo ""
        echo "BACKEND (Railway):"
        echo "1. Ve a https://railway.app"
        echo "2. Conecta tu GitHub"
        echo "3. Deploy from repo → selecciona /backend"
        echo "4. Copia la URL que te da Railway"
        echo ""
        echo "FRONTEND (Vercel):"
        echo "1. Ve a https://vercel.com"
        echo "2. Import Git Repository"
        echo "3. Root Directory: frontend"
        echo "4. Environment Variables:"
        echo "   PUBLIC_API_URL=https://tu-backend.up.railway.app"
        echo ""
        print_success "🎉 Tu app será 100% gratis!"
        ;;
        
    2)
        print_status "🎨 Configurando para Render..."
        
        # Crear render.yaml
        cat > render.yaml << 'EOF'
services:
  - type: web
    name: immigration-backend
    env: python
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && python app.py
    envVars:
      - key: PORT
        value: 10000
      - key: FLASK_ENV
        value: production
        
  - type: web
    name: immigration-frontend
    env: node
    plan: free
    buildCommand: cd frontend && npm install && npm run build
    startCommand: cd frontend && npm start
    envVars:
      - key: PUBLIC_API_URL
        value: https://immigration-backend.onrender.com
EOF
        
        print_success "✅ render.yaml creado"
        echo ""
        echo "📋 Pasos siguientes:"
        echo "1. Sube tu código a GitHub"
        echo "2. Ve a https://render.com"
        echo "3. New → Blueprint"
        echo "4. Conecta tu repo"
        echo "5. Render detectará el render.yaml automáticamente"
        ;;
        
    3)
        print_status "🪰 Configurando para Fly.io..."
        
        if ! command -v flyctl &> /dev/null; then
            print_warning "Instala flyctl primero:"
            echo "curl -L https://fly.io/install.sh | sh"
            exit 1
        fi
        
        # Crear fly.toml para backend
        mkdir -p fly-configs
        cat > fly-configs/backend-fly.toml << 'EOF'
app = "immigration-backend"
primary_region = "sjc"

[build]
  dockerfile = "backend/Dockerfile"

[env]
  FLASK_ENV = "production"
  PORT = "8080"

[[services]]
  http_checks = []
  internal_port = 8080
  processes = ["app"]
  protocol = "tcp"
  script_checks = []

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[machine]
  memory = 256
EOF

        # Crear fly.toml para frontend
        cat > fly-configs/frontend-fly.toml << 'EOF'
app = "immigration-frontend"
primary_region = "sjc"

[build]
  dockerfile = "frontend/Dockerfile"

[env]
  NODE_ENV = "production"
  PUBLIC_API_URL = "https://immigration-backend.fly.dev"

[[services]]
  http_checks = []
  internal_port = 3000
  processes = ["app"]
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[machine]
  memory = 256
EOF

        print_success "✅ Configuración de Fly.io creada"
        echo ""
        echo "📋 Pasos siguientes:"
        echo "1. flyctl auth login"
        echo "2. cd backend && flyctl launch --config ../fly-configs/backend-fly.toml"
        echo "3. cd ../frontend && flyctl launch --config ../fly-configs/frontend-fly.toml"
        ;;
        
    4)
        print_status "📦 Configurando para GitHub Pages + Netlify..."
        
        # Configurar para static deployment
        cat > frontend/.env.production << 'EOF'
PUBLIC_API_URL=https://immigration-api.netlify.app/.netlify/functions
EOF

        print_success "✅ Configuración estática creada"
        echo ""
        echo "📋 Pasos siguientes:"
        echo "1. Convierte tu backend a Netlify Functions"
        echo "2. Deploy frontend a GitHub Pages"
        echo "3. Configura dominio personalizado"
        ;;
        
    *)
        print_warning "Opción no válida"
        exit 1
        ;;
esac

print_success "🎉 Configuración completada!"
echo ""
print_status "💡 Tips para mantenerlo gratis:"
echo "• Railway: 500 horas/mes (suficiente para demos)"
echo "• Vercel: Ilimitado para frontend"
echo "• Render: Se duerme tras 15min inactivo"
echo "• Fly.io: 3 apps pequeñas gratis"
