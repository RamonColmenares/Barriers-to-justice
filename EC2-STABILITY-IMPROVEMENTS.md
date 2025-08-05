# 🚨 EC2 Stability Improvements

Este documento describe las mejoras implementadas para solucionar el problema de la EC2 que deja de responder cuando hay fallos en las APIs.

## 🔧 Problemas Identificados y Soluciones

### 1. **Uso Excesivo de Recursos**
**Problema:** El contenedor Docker usaba 1.7GB+ de RAM de los 2GB disponibles
**Solución:** 
- Reducido a 1.2GB de RAM (60% del total)
- Limitado a 1.5 CPUs en lugar de 2.0
- Swap reducido de 4GB a 2GB más conservador

### 2. **Timeouts Excesivos en Nginx**
**Problema:** Timeouts de 300 segundos saturaban la instancia
**Solución:**
- Reducidos a 120 segundos
- Buffers optimizados (64k en lugar de 128k)
- Menos buffers concurrentes (8 en lugar de 100)

### 3. **Falta de Monitoreo**
**Problema:** No había visibilidad cuando el sistema se degradaba
**Solución:**
- Script de monitoreo automático cada 2 minutos
- Health checks del contenedor Docker
- Alertas de uso de memoria/CPU
- Auto-reinicio en caso de fallo

### 4. **Configuración del Sistema**
**Problema:** Configuración agresiva de memoria virtual
**Solución:**
- `vm.swappiness=5` (más conservador)
- `vm.dirty_ratio=10` (previene bloqueos de I/O)
- Instalación de herramientas de monitoreo (htop, iotop, sysstat)

## 🛠️ Nuevas Herramientas

### 1. **diagnose-ec2.sh**
Script de diagnóstico completo para cuando la EC2 no responde:
```bash
./diagnose-ec2.sh --ip YOUR_EC2_IP
```

**Funciones:**
- Test de conectividad (ping, puertos)
- Verificación de servicios via SSH
- Análisis de logs y recursos
- Sugerencias de recuperación

### 2. **recover-ec2.sh**
Script de recuperación rápida con múltiples opciones:
```bash
./recover-ec2.sh --ip YOUR_EC2_IP --action cleanup
```

**Acciones disponibles:**
- `restart-api`: Solo reinicia el contenedor
- `restart-services`: Reinicia Nginx + contenedor
- `cleanup`: Limpia recursos y reinicia todo
- `monitor`: Monitoreo en tiempo real

### 3. **Monitor Automático**
Se instala automáticamente en la EC2:
- **Ubicación:** `/usr/local/bin/monitor-api.sh`
- **Frecuencia:** Cada 2 minutos
- **Logs:** `/var/log/api-monitor.log`

**Funciones:**
- Verifica estado del contenedor
- Monitorea uso de CPU/memoria
- Auto-reinicia en caso de fallo
- Limpia caches si memoria >95%

## 📊 Configuración Optimizada

### Recursos del Contenedor
```bash
--memory="1200m"         # 60% de RAM total (era 85%)
--memory-swap="2400m"    # 2x memoria (era 2x)
--cpus="1.5"            # 75% de CPUs (era 100%)
--shm-size=128m         # Reducido de 256m/512m
```

### Timeouts de Nginx
```nginx
proxy_connect_timeout 120s;  # Reducido de 300s
proxy_send_timeout 120s;     # Reducido de 300s
proxy_read_timeout 120s;     # Reducido de 300s
```

### Sistema de Swap
```bash
# Swap más conservador
fallocate -l 2G /swapfile    # Reducido de 4G
vm.swappiness=5              # Muy conservador (era 10)
vm.dirty_ratio=10            # Previene bloqueos I/O
```

## 🚨 Procedimiento de Emergencia

### Si la EC2 deja de responder:

1. **Diagnóstico inicial:**
   ```bash
   ./diagnose-ec2.sh --ip YOUR_EC2_IP
   ```

2. **Recuperación rápida:**
   ```bash
   ./recover-ec2.sh --ip YOUR_EC2_IP --action cleanup
   ```

3. **Si SSH no funciona:**
   - Reiniciar instancia desde AWS Console
   - Verificar Security Groups
   - Comprobar estado de la instancia

4. **Monitoreo continuo:**
   ```bash
   ./recover-ec2.sh --ip YOUR_EC2_IP --action monitor
   ```

## 📈 Comandos de Monitoreo Manual

### Recursos del sistema:
```bash
ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'free -h && df -h'
```

### Estado del contenedor:
```bash
ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo docker stats --no-stream'
```

### Logs de la API:
```bash
ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo docker logs --tail 50 juvenile-api'
```

### Logs de monitoreo:
```bash
ssh -i ~/.ssh/juvenile-immigration-key.pem ubuntu@$EC2_IP 'sudo tail -20 /var/log/api-monitor.log'
```

## ✅ Beneficios de las Mejoras

1. **Estabilidad:** Sistema más robusto con límites conservadores
2. **Observabilidad:** Monitoreo automático y herramientas de diagnóstico
3. **Recuperación:** Scripts automatizados para resolver problemas
4. **Prevención:** Configuración que previene saturación de recursos
5. **Mantenimiento:** Limpieza automática de caches y logs

Con estos cambios, la EC2 debería mantenerse estable incluso cuando hay errores en las APIs, y tendrás herramientas para diagnosticar y resolver problemas rápidamente.
