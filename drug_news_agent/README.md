# 🔍 Agente de Búsqueda Inteligente de Noticias sobre Drogas

Sistema de inteligencia artificial para la búsqueda, análisis y geocodificación automática de noticias relacionadas con drogas en América Latina y el Caribe.

## 🎯 Características Principales

- **Búsqueda Inteligente**: Utiliza múltiples consultas optimizadas con palabras clave específicas
- **Filtrado Geográfico**: Se enfoca en 57 países de América Latina y Caribe (México hacia abajo)  
- **Clasificación de Relevancia**: Sistema de scoring automático (Alta/Media/Baja)
- **Deduplicación Avanzada**: Detecta y agrupa noticias que reportan el mismo evento
- **Extracción de Ubicación**: Identifica ubicaciones granulares (país, provincia, ciudad, barrio)
- **Geocodificación**: Obtiene coordenadas precisas usando Google Maps API
- **Exportación CSV**: Compatible con formato Centro Regional Base (37 campos)

## 📋 Estructura del Sistema

```
drug_news_agent/
├── __init__.py                     # Módulo principal
├── main.py                        # Script de ejecución
├── data_loader.py                 # Carga datos de referencia
├── relevance_classifier.py        # Clasificador de relevancia
├── deduplication.py              # Sistema de deduplicación
├── location_extractor.py         # Extractor de ubicación
├── geocoder.py                   # Geocodificación con Google Maps
├── intelligent_search_agent.py   # Agente principal
├── csv_exporter.py              # Exportador a CSV
└── README.md                    # Documentación
```

## 🔧 Requisitos

### APIs Necesarias
- **GOOGLE_SEARCH_KEY**: Para búsquedas web (Serper API)
- **JINA_API_KEY**: Para lectura de páginas web
- **DASHSCOPE_API_KEY**: Para procesamiento con modelo Qwen
- **GOOGLE_MAPS_API_KEY**: Para geocodificación (opcional)

### Archivos de Referencia
- `paises.csv`: Lista de países objetivo
- `drogas palabras clave.csv`: Palabras clave de drogas por categoría
- `relevancia.csv`: Criterios de relevancia
- `Centro_Regional_2025 - Base.csv`: Estructura de datos objetivo

## 🚀 Instalación y Uso

### 1. Configurar Variables de Entorno

```bash
export GOOGLE_SEARCH_KEY="tu_clave_serper"
export JINA_API_KEY="tu_clave_jina" 
export DASHSCOPE_API_KEY="tu_clave_dashscope"
export GOOGLE_MAPS_API_KEY="tu_clave_google_maps"  # Opcional
```

O crear archivo `.env`:
```
GOOGLE_SEARCH_KEY=tu_clave_serper
JINA_API_KEY=tu_clave_jina
DASHSCOPE_API_KEY=tu_clave_dashscope
GOOGLE_MAPS_API_KEY=tu_clave_google_maps
```

### 2. Ejecutar el Sistema

#### Búsqueda Completa (Modo Producción)
```bash
python main.py --days 7 --min-relevance Alta --output-dir ./resultados
```

#### Prueba Rápida
```bash
python main.py --quick-test --verbose
```

#### Opciones Avanzadas
```bash
python main.py \
  --days 14 \
  --max-articles 30 \
  --min-relevance Media \
  --output-dir /ruta/salida \
  --google-maps-key tu_clave \
  --verbose
```

### 3. Parámetros Disponibles

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `--days` | Días hacia atrás para buscar | 7 |
| `--max-articles` | Máx. artículos por consulta | 20 |
| `--min-relevance` | Relevancia mínima (Alta/Media/Baja) | Media |
| `--output-dir` | Directorio de salida | ./output |
| `--google-maps-key` | API key Google Maps | None |
| `--quick-test` | Prueba rápida | False |
| `--verbose` | Información detallada | False |

## 📊 Formato de Salida

### Archivo CSV Principal
Compatible con Centro Regional Base, incluye 37 campos:

- **Identificación**: Articulo_ID, CUI, Fecha_Publicacion
- **Contenido**: Titulo_Articulo, Descripcion_Articulo, Medio, URL
- **Clasificación**: Relevancia, Categoria_tematica, Keywords
- **Sustancias**: Clasificacion_Sust_Estup, Tipo_Sus_Estup, Cantidad
- **Ubicación**: Pais, Provincia, Distrito, Ubicacion_Secuestro
- **Coordenadas**: Geo_Pais, Geo_Prov, Geo_Distrito
- **Temporal**: Fecha, Dia, Semana, Mes, Trimestre, Año

### Reporte de Resumen
- Métricas de búsqueda y procesamiento
- Estadísticas por relevancia y país
- Información sobre duplicados detectados
- Análisis de efectividad del sistema

## 🧠 Algoritmos Implementados

### Clasificador de Relevancia
Utiliza sistema de scoring basado en:
- **Menciones de drogas** (15 pts c/u, máx 30)
- **Palabras clave en título** (20 pts c/u, máx 40) 
- **País objetivo** (20 pts)
- **Contexto operativo** (5 pts c/u, máx 25)
- **Alta prioridad** (15 pts c/u, máx 30)
- **Indicadores de impacto** (10 pts c/u, máx 20)

**Umbrales**: Alta ≥70, Media ≥40, Baja <40

### Sistema de Deduplicación
Calcula similitud combinando:
- **Similitud de títulos** (40% peso)
- **Proximidad temporal** (20% peso)
- **Similitud de ubicación** (30% peso)
- **Drogas en común** (10% peso)

**Umbral de duplicado**: 75% similitud

### Extractor de Ubicación
Patrones de extracción jerárquicos:
1. **Estructurados**: "Ciudad, Provincia, País"
2. **Contextuales**: "en el barrio X de Y"
3. **Indicadores**: "municipio", "departamento", etc.
4. **Fallback**: Solo país

## 🗺️ Geocodificación

### Con Google Maps API
- Coordenadas precisas usando Google Geocoding
- Sesgo regional para mejorar resultados
- Caché para evitar consultas repetidas
- Rate limiting integrado

### Sin API (Fallback)
- Coordenadas aproximadas por país
- Basado en datos de referencia
- Funcionalidad básica garantizada

## 📈 Métricas y Análisis

El sistema proporciona métricas detalladas:

- **Eficiencia de búsqueda**: Artículos útiles vs encontrados
- **Cobertura geográfica**: Distribución por países
- **Calidad de clasificación**: Distribución por relevancia
- **Efectividad de deduplicación**: Reducción de duplicados
- **Precisión de geocodificación**: Tasa de éxito

## 🔍 Países Objetivo

El sistema se enfoca en 57 países de América Latina y Caribe:

**América del Sur**: Argentina, Bolivia, Brasil, Chile, Colombia, Ecuador, Guyana, Paraguay, Perú, Suriname, Uruguay, Venezuela

**América Central**: Belice, Costa Rica, El Salvador, Guatemala, Honduras, Nicaragua, Panamá

**Caribe**: Antigua y Barbuda, Bahamas, Barbados, Cuba, Dominica, Granada, Haití, Jamaica, República Dominicana, San Cristóbal y Nieves, Santa Lucía, San Vicente y las Granadinas, Trinidad y Tobago

**América del Norte**: México

## 💊 Categorías de Drogas Monitoreadas

1. **Estimulante y empático**: MDMA, Éxtasis, Molly
2. **Opioide sintético**: Fentanilo, Actiq, Duragesic
3. **Anestésico disociativo**: Ketamina, K Special, Special K
4. **Alucinógeno**: TUSI, LSD, DMT, 2C-B
5. **Depresor**: GHB, Liquid X, Fantasy
6. **Estimulante sintético**: Metanfetaminas, Crystal, Ice
7. **NSP**: Spice, K2, Flakka, Sales de baño

## 🚨 Criterios de Relevancia

### Alta Relevancia
- Palabras clave en título
- Incautaciones masivas
- Operaciones internacionales
- Carteles y organizaciones criminales

### Media Relevancia
- Menciones en cuerpo del texto
- Incautaciones menores
- Operativos locales

### Baja Relevancia
- Referencias tangenciales
- Menciones únicas
- Impacto limitado

## 🛠️ Mantenimiento y Extensión

### Agregar Nuevas Drogas
Editar `drogas palabras clave.csv` con nuevas categorías y términos.

### Modificar Países Objetivo
Actualizar `paises.csv` con países adicionales.

### Ajustar Criterios de Relevancia
Modificar `relevancia.csv` y algoritmo en `relevance_classifier.py`.

### Personalizar Exportación
Extender `csv_exporter.py` para nuevos formatos de salida.

## 📞 Soporte y Troubleshooting

### Problemas Comunes

**Error: API keys no encontradas**
- Verificar variables de entorno
- Comprobar archivo `.env`

**Pocas noticias encontradas**
- Ajustar `--min-relevance` a "Baja"
- Aumentar `--days` para período más amplio
- Verificar conectividad de APIs

**Geocodificación fallida**
- Configurar `GOOGLE_MAPS_API_KEY`
- Sistema funciona con coordenadas aproximadas

**Archivos de referencia faltantes**
- Verificar ruta: `/Users/macbook/Documents/WebSearchAgent/AnalisisArchivo/`
- Asegurar presencia de todos los CSV

### Logs y Debugging
```bash
python main.py --verbose --quick-test
```

## 📄 Licencia

Sistema desarrollado para Centro Regional de Inteligencia.
Uso interno y con fines de investigación en seguridad.

## 🔄 Actualizaciones

**v1.0** - Sistema base completo
- Búsqueda inteligente multi-API
- Clasificación automática de relevancia  
- Deduplicación avanzada
- Geocodificación con Google Maps
- Exportación compatible Centro Regional

---

*Sistema optimizado para análisis de noticias sobre drogas en América Latina y Caribe* 🌎