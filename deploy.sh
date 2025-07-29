#!/bin/bash

# 🚀 Script de despliegue para Immigration Research Platform
# Autor: Ramon Colmenares
# Fecha: $(date +"%Y-%m-%d")

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado. Por favor instala Docker Desktop."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado. Por favor instala Docker Compose."
        exit 1
    fi
    
    print_success "Docker y Docker Compose están instalados ✅"
}

# Check if required files exist
check_files() {
    print_status "Verificando archivos necesarios..."
    
    required_files=(
        "docker-compose.yml"
        "backend/Dockerfile"
        "backend/app.py"
        "backend/requirements.txt"
        "frontend/Dockerfile"
        "frontend/package.json"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Archivo requerido no encontrado: $file"
            exit 1
        fi
    done
    
    print_success "Todos los archivos necesarios están presentes ✅"
}

# Build and start services
deploy() {
    print_status "🏗️ Construyendo imágenes Docker..."
    
    # Stop any running containers
    docker-compose down 2>/dev/null || true
    
    # Build images
    docker-compose build --no-cache
    
    print_status "🚀 Iniciando servicios..."
    
    # Start services
    docker-compose up -d
    
    print_status "⏳ Esperando que los servicios estén listos..."
    
    # Wait for services to be healthy
    timeout=120
    counter=0
    
    while [ $counter -lt $timeout ]; do
        backend_status=$(docker inspect immigration-backend --format='{{.State.Health.Status}}' 2>/dev/null || echo "starting")
        frontend_status=$(docker inspect immigration-frontend --format='{{.State.Health.Status}}' 2>/dev/null || echo "starting")
        
        if [[ "$backend_status" == "healthy" && "$frontend_status" == "healthy" ]]; then
            break
        fi
        
        echo -n "."
        sleep 2
        counter=$((counter + 2))
    done
    
    echo ""
    
    if [ $counter -ge $timeout ]; then
        print_warning "Los servicios están tardando más de lo esperado en estar listos"
        print_status "Puedes verificar los logs con: docker-compose logs"
    else
        print_success "¡Servicios desplegados exitosamente! 🎉"
    fi
}

# Show service status
show_status() {
    echo ""
    print_status "📊 Estado de los servicios:"
    docker-compose ps
    
    echo ""
    print_status "🌐 Aplicación disponible en:"
    echo "  • Frontend: http://localhost:3000"
    echo "  • Backend API: http://localhost:5000"
    echo "  • API Health: http://localhost:5000/api/health"
    
    echo ""
    print_status "📝 Comandos útiles:"
    echo "  • Ver logs: docker-compose logs -f"
    echo "  • Detener: docker-compose down"
    echo "  • Reiniciar: docker-compose restart"
    echo "  • Logs específicos: docker-compose logs <service_name>"
}

# Main execution
main() {
    echo "🌐 Immigration Research Platform - Deployment Script"
    echo "=================================================="
    
    check_docker
    check_files
    deploy
    show_status
    
    print_success "🚀 ¡Despliegue completado!"
}

# Handle script arguments
case "${1:-}" in
    "stop")
        print_status "🛑 Deteniendo servicios..."
        docker-compose down
        print_success "Servicios detenidos"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        show_status
        ;;
    "clean")
        print_status "🧹 Limpiando contenedores e imágenes..."
        docker-compose down -v --rmi all
        print_success "Limpieza completada"
        ;;
    *)
        main
        ;;
esac
