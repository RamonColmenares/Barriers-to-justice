# 🚀 Immigration Research Platform - Makefile
# Comandos útiles para desarrollo y despliegue

.PHONY: help build up down logs clean dev prod status health

# Colores para output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

help: ## Mostrar esta ayuda
	@echo "$(GREEN)Immigration Research Platform - Comandos Disponibles$(NC)"
	@echo "======================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

build: ## Construir todas las imágenes Docker
	@echo "$(GREEN)🏗️ Construyendo imágenes Docker...$(NC)"
	docker-compose build --no-cache

up: ## Iniciar todos los servicios
	@echo "$(GREEN)🚀 Iniciando servicios...$(NC)"
	docker-compose up -d

down: ## Detener todos los servicios
	@echo "$(YELLOW)🛑 Deteniendo servicios...$(NC)"
	docker-compose down

logs: ## Ver logs de todos los servicios
	@echo "$(GREEN)📋 Mostrando logs...$(NC)"
	docker-compose logs -f

logs-backend: ## Ver logs del backend
	docker-compose logs -f backend

logs-frontend: ## Ver logs del frontend
	docker-compose logs -f frontend

status: ## Mostrar estado de los servicios
	@echo "$(GREEN)📊 Estado de los servicios:$(NC)"
	docker-compose ps

health: ## Verificar salud de los servicios
	@echo "$(GREEN)🔍 Verificando salud de servicios...$(NC)"
	@curl -f http://localhost:5000/api/health 2>/dev/null && echo "✅ Backend: Healthy" || echo "❌ Backend: Unhealthy"
	@curl -f http://localhost:3000 2>/dev/null && echo "✅ Frontend: Healthy" || echo "❌ Frontend: Unhealthy"

dev: ## Modo desarrollo con hot reload
	@echo "$(GREEN)🔧 Iniciando en modo desarrollo...$(NC)"
	docker-compose -f docker-compose.dev.yml up --build

prod: ## Modo producción con Nginx
	@echo "$(GREEN)🌐 Iniciando en modo producción...$(NC)"
	docker-compose --profile production up -d

restart: ## Reiniciar todos los servicios
	@echo "$(YELLOW)🔄 Reiniciando servicios...$(NC)"
	docker-compose restart

clean: ## Limpiar contenedores, imágenes y volúmenes
	@echo "$(RED)🧹 Limpiando sistema Docker...$(NC)"
	docker-compose down -v
	docker system prune -af

deploy: ## Despliegue completo (build + up)
	@echo "$(GREEN)🚀 Despliegue completo...$(NC)"
	make build
	make up
	@echo "$(GREEN)✅ Despliegue completado!$(NC)"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔌 Backend: http://localhost:5000"

backup: ## Crear backup de volúmenes
	@echo "$(GREEN)💾 Creando backup...$(NC)"
	docker run --rm -v immigration-data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/backup-$(shell date +%Y%m%d-%H%M%S).tar.gz /data

shell-backend: ## Acceder al shell del backend
	docker exec -it immigration-backend bash

shell-frontend: ## Acceder al shell del frontend
	docker exec -it immigration-frontend sh

test: ## Ejecutar tests (cuando estén implementados)
	@echo "$(GREEN)🧪 Ejecutando tests...$(NC)"
	# docker-compose exec backend python -m pytest
	# docker-compose exec frontend npm test

update: ## Actualizar imágenes base
	@echo "$(GREEN)⬆️ Actualizando imágenes base...$(NC)"
	docker-compose pull
	make build

monitor: ## Monitorear recursos de contenedores
	@echo "$(GREEN)📊 Monitoreando recursos...$(NC)"
	docker stats

# Comandos de desarrollo
install-backend: ## Instalar dependencias del backend
	docker-compose exec backend pip install -r requirements.txt

install-frontend: ## Instalar dependencias del frontend
	docker-compose exec frontend npm install

# Comandos de utilidad
port-check: ## Verificar puertos en uso
	@echo "$(GREEN)🔍 Verificando puertos...$(NC)"
	@lsof -i :3000 || echo "Puerto 3000: libre"
	@lsof -i :5000 || echo "Puerto 5000: libre"
	@lsof -i :80 || echo "Puerto 80: libre"

docker-info: ## Información del sistema Docker
	@echo "$(GREEN)🐳 Información de Docker:$(NC)"
	docker version
	docker-compose version
	docker system df

# Default target
.DEFAULT_GOAL := help
