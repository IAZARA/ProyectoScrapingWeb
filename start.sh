#!/bin/bash

# ==================================================================
# SCRIPT START.SH - Generador de XLSX sobre Noticias de Drogas
# Solo genera el archivo XLSX en output/ y termina
# ==================================================================

echo "🚀 INICIANDO GENERADOR DE XLSX - NOTICIAS SOBRE DROGAS"
echo "================================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_step() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. VERIFICAR DIRECTORIO
print_step "Verificando directorio de trabajo..."
if [ ! -f "exportar_xlsx_directo.py" ]; then
    print_error "No se encuentra exportar_xlsx_directo.py"
    print_error "Ejecutar desde el directorio WebDancer"
    exit 1
fi
print_success "Directorio correcto"

# 2. VERIFICAR Y LIMPIAR PUERTOS OCUPADOS
print_step "Verificando puertos ocupados..."

# Buscar procesos Python que podrían estar usando puertos
PYTHON_PIDS=$(lsof -i -P | grep Python | grep LISTEN | awk '{print $2}' | sort -u)

if [ ! -z "$PYTHON_PIDS" ]; then
    print_warning "Encontrados procesos Python usando puertos:"
    lsof -i -P | grep Python | grep LISTEN
    
    print_step "Cerrando procesos Python que usan puertos..."
    for pid in $PYTHON_PIDS; do
        if kill -0 $pid 2>/dev/null; then
            print_step "Cerrando proceso $pid..."
            kill -TERM $pid 2>/dev/null
            sleep 2
            # Si no se cerró, forzar
            if kill -0 $pid 2>/dev/null; then
                kill -KILL $pid 2>/dev/null
                print_warning "Proceso $pid forzado a cerrar"
            else
                print_success "Proceso $pid cerrado correctamente"
            fi
        fi
    done
else
    print_success "No hay puertos Python ocupados"
fi

# 3. ACTIVAR ENTORNO VIRTUAL
print_step "Activando entorno virtual..."

if [ ! -d "venv" ]; then
    print_error "No se encuentra directorio venv/"
    print_error "Crear entorno virtual primero: python3 -m venv venv"
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate

if [ $? -eq 0 ]; then
    print_success "Entorno virtual activado"
else
    print_error "Error activando entorno virtual"
    exit 1
fi

# 4. VERIFICAR DEPENDENCIAS
print_step "Verificando dependencias..."

# Verificar pandas y openpyxl
python -c "import pandas, openpyxl" 2>/dev/null
if [ $? -ne 0 ]; then
    print_warning "Instalando dependencias faltantes..."
    pip install pandas openpyxl --quiet
    if [ $? -eq 0 ]; then
        print_success "Dependencias instaladas"
    else
        print_error "Error instalando dependencias"
        deactivate
        exit 1
    fi
else
    print_success "Dependencias disponibles"
fi

# 5. CREAR DIRECTORIO OUTPUT
print_step "Preparando directorio de salida..."
mkdir -p output
print_success "Directorio output listo"

# 6. EJECUTAR GENERACIÓN DE XLSX
print_step "Ejecutando generación de archivo XLSX..."
echo "================================================================"

# Ejecutar el script principal
python exportar_xlsx_directo.py

EXIT_CODE=$?

echo "================================================================"

# 7. VERIFICAR RESULTADO
if [ $EXIT_CODE -eq 0 ]; then
    print_success "Script ejecutado correctamente"
    
    # Verificar si se generó el archivo
    XLSX_COUNT=$(find output/ -name "*.xlsx" -type f | wc -l)
    
    if [ $XLSX_COUNT -gt 0 ]; then
        print_success "Archivo XLSX generado exitosamente"
        
        # Mostrar el archivo más reciente
        LATEST_FILE=$(find output/ -name "*.xlsx" -type f -exec ls -t {} + | head -1)
        FILE_SIZE=$(stat -f%z "$LATEST_FILE" 2>/dev/null || stat -c%s "$LATEST_FILE" 2>/dev/null)
        
        echo ""
        print_success "ARCHIVO GENERADO:"
        echo -e "   📁 Ubicación: ${GREEN}$(pwd)/$LATEST_FILE${NC}"
        echo -e "   📊 Tamaño: ${GREEN}$FILE_SIZE bytes${NC}"
        echo -e "   🕐 Generado: ${GREEN}$(date)${NC}"
        
    else
        print_warning "Script ejecutado pero no se encontró archivo XLSX"
        EXIT_CODE=1
    fi
else
    print_error "Error ejecutando el script (código: $EXIT_CODE)"
fi

# 8. DESACTIVAR ENTORNO VIRTUAL
print_step "Desactivando entorno virtual..."
deactivate
print_success "Entorno virtual desactivado"

# 9. LIMPIEZA FINAL
print_step "Limpieza final de procesos..."

# Verificar que no quedaron procesos colgados
REMAINING_PIDS=$(lsof -i -P | grep Python | grep LISTEN | awk '{print $2}' | sort -u)
if [ ! -z "$REMAINING_PIDS" ]; then
    print_warning "Cerrando procesos residuales..."
    for pid in $REMAINING_PIDS; do
        kill -TERM $pid 2>/dev/null
    done
fi

print_success "Limpieza completada"

echo ""
echo "================================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}🎉 PROCESO COMPLETADO EXITOSAMENTE${NC}"
    echo -e "${GREEN}📊 Archivo XLSX disponible en output/${NC}"
else
    echo -e "${RED}❌ PROCESO COMPLETADO CON ERRORES${NC}"
fi
echo "================================================================"

exit $EXIT_CODE