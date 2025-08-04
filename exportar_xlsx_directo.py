#!/usr/bin/env python3
"""
Exportador directo de XLSX para análisis de noticias sobre drogas
"""
import os
import pandas as pd
from datetime import datetime

print("📊 GENERANDO ARCHIVO XLSX")
print("=" * 35)

# Crear directorio de salida
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Generar timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Datos de ejemplo realistas
noticias_data = [
    {
        'Articulo_ID': 'A0000001',
        'CUI': 'A1',
        'Fecha_Publicacion_Articulo': '04/08/2025',
        'Titulo_Articulo': 'Incautan 8.2 toneladas de cocaína en operativo conjunto en Colombia',
        'Descripcion_Articulo': 'La Policía Nacional de Colombia, en coordinación con autoridades internacionales, incautó una gran cantidad de cocaína en puerto de Cartagena',
        'Medio': 'www.reuters.com',
        'URL_Acortada': 'https://tinyurl.com/colombia-cocaine-2025',
        'Pais_Origen_Articulo': 'Colombia',
        'Cod_Continente': 'SA',
        'Idioma': 'ES',
        'Categoria_tematica': 'Incidente',
        'Relevancia_Mencion': 'Alta',
        'Frecuencia_Mencion': 'Alta',
        'Impacto_Articulo': 'Alto',
        'Keywords': 'Cocaína, Operativo, Policía Nacional, Cartagena, Narcotráfico',
        'Clasificacion_Sust_Estup_Decomisada': 'Estimulante',
        'Tipo_Sus_Estup_Decomisada': 'Cocaína',
        'Cant_Sust_Estup_Sintetica_incautada': '8200',
        'Unidad': 'KG',
        'Fueza_interviniente': 'Policía Nacional de Colombia',
        'Ubicacion_Secuestro': 'Cartagena, Bolívar, Colombia',
        'Region': 'America',
        'Sub_region': 'America del Sur',
        'Pais': 'Colombia',
        'Provincia': 'Bolívar',
        'Distrito': 'Cartagena',
        'Alfa_2': 'CO',
        'ISO_3166_2': 'ISO 3166-2:CO',
        'Geo_Pais': '10.391049, -75.479426',
        'Geo_Prov': '10.391049, -75.479426',
        'Geo_Distrito': '10.391049, -75.479426',
        'Fecha': '04/08/2025',
        'Dia': '4',
        'Semana': '31',
        'Quincena': '1',
        'Mes_Largo': 'Agosto',
        'Trimestre': 'T3',
        'Año': '2025'
    },
    {
        'Articulo_ID': 'A0000002',
        'CUI': 'A2',
        'Fecha_Publicacion_Articulo': '04/08/2025',
        'Titulo_Articulo': 'Decomisan 25 kilos de cocaína en Aeropuerto El Dorado, Bogotá',
        'Descripcion_Articulo': 'Autoridades aeroportuarias incautaron droga oculta en equipajes de pasajeros con destino a Europa',
        'Medio': 'www.infobae.com',
        'URL_Acortada': 'https://tinyurl.com/eldorado-cocaine-bust',
        'Pais_Origen_Articulo': 'Colombia',
        'Cod_Continente': 'SA',
        'Idioma': 'ES',
        'Categoria_tematica': 'Incidente',
        'Relevancia_Mencion': 'Media',
        'Frecuencia_Mencion': 'Media',
        'Impacto_Articulo': 'Medio',
        'Keywords': 'Cocaína, Aeropuerto, El Dorado, Contrabando, Europa',
        'Clasificacion_Sust_Estup_Decomisada': 'Estimulante',
        'Tipo_Sus_Estup_Decomisada': 'Cocaína',
        'Cant_Sust_Estup_Sintetica_incautada': '25',
        'Unidad': 'KG',
        'Fueza_interviniente': 'Policía Antinarcóticos',
        'Ubicacion_Secuestro': 'Aeropuerto El Dorado, Bogotá, Colombia',
        'Region': 'America',
        'Sub_region': 'America del Sur',
        'Pais': 'Colombia',
        'Provincia': 'Cundinamarca',
        'Distrito': 'Bogotá',
        'Alfa_2': 'CO',
        'ISO_3166_2': 'ISO 3166-2:CO',
        'Geo_Pais': '4.681854, -74.063644',
        'Geo_Prov': '4.681854, -74.063644',
        'Geo_Distrito': '4.681854, -74.063644',
        'Fecha': '04/08/2025',
        'Dia': '4',
        'Semana': '31',
        'Quincena': '1',
        'Mes_Largo': 'Agosto',
        'Trimestre': 'T3',
        'Año': '2025'
    },
    {
        'Articulo_ID': 'A0000003',
        'CUI': 'A3',
        'Fecha_Publicacion_Articulo': '03/08/2025',
        'Titulo_Articulo': 'Operativo en México deja 2 toneladas de metanfetaminas incautadas',
        'Descripcion_Articulo': 'Fuerzas federales mexicanas desmantelan laboratorio clandestino en Sinaloa',
        'Medio': 'www.milenio.com',
        'URL_Acortada': 'https://tinyurl.com/mexico-meth-lab-2025',
        'Pais_Origen_Articulo': 'México',
        'Cod_Continente': 'NA',
        'Idioma': 'ES',
        'Categoria_tematica': 'Incidente',
        'Relevancia_Mencion': 'Alta',
        'Frecuencia_Mencion': 'Alta',
        'Impacto_Articulo': 'Alto',
        'Keywords': 'Metanfetaminas, Laboratorio, Sinaloa, Cártel, Operativo Federal',
        'Clasificacion_Sust_Estup_Decomisada': 'Estimulante sintético',
        'Tipo_Sus_Estup_Decomisada': 'Metanfetaminas',
        'Cant_Sust_Estup_Sintetica_incautada': '2000',
        'Unidad': 'KG',
        'Fueza_interviniente': 'Fuerzas Federales Mexicanas',
        'Ubicacion_Secuestro': 'Culiacán, Sinaloa, México',
        'Region': 'America',
        'Sub_region': 'America del Norte',
        'Pais': 'México',
        'Provincia': 'Sinaloa',
        'Distrito': 'Culiacán',
        'Alfa_2': 'MX',
        'ISO_3166_2': 'ISO 3166-2:MX',
        'Geo_Pais': '24.794500, -107.394012',
        'Geo_Prov': '24.794500, -107.394012',
        'Geo_Distrito': '24.794500, -107.394012',
        'Fecha': '03/08/2025',
        'Dia': '3',
        'Semana': '31',
        'Quincena': '1',
        'Mes_Largo': 'Agosto',
        'Trimestre': 'T3',
        'Año': '2025'
    }
]

# Crear DataFrame
df = pd.DataFrame(noticias_data)

# Nombre del archivo XLSX
xlsx_filename = f"output/Centro_Regional_DrugNews_{timestamp}.xlsx"

print("1️⃣ Creando archivo XLSX...")

# Crear el archivo Excel con formato
with pd.ExcelWriter(xlsx_filename, engine='openpyxl') as writer:
    # Hoja principal con datos
    df.to_excel(writer, sheet_name='Noticias_Drogas', index=False)
    
    # Hoja de resumen
    resumen_data = {
        'Métrica': [
            'Total de noticias',
            'Países monitoreados',
            'Incautaciones reportadas',
            'Total cocaína (kg)',
            'Total metanfetaminas (kg)',
            'Relevancia alta',
            'Relevancia media',
            'Fecha de análisis'
        ],
        'Valor': [
            len(noticias_data),
            2,
            3,
            8225,
            2000,
            2,
            1,
            datetime.now().strftime('%d/%m/%Y %H:%M')
        ]
    }
    
    resumen_df = pd.DataFrame(resumen_data)
    resumen_df.to_excel(writer, sheet_name='Resumen', index=False)
    
    # Hoja de ubicaciones
    ubicaciones_data = []
    for noticia in noticias_data:
        ubicaciones_data.append({
            'País': noticia['Pais'],
            'Provincia': noticia['Provincia'],
            'Ciudad': noticia['Distrito'],
            'Coordenadas': noticia['Geo_Distrito'],
            'Sustancia': noticia['Tipo_Sus_Estup_Decomisada'],
            'Cantidad_kg': noticia['Cant_Sust_Estup_Sintetica_incautada']
        })
    
    ubicaciones_df = pd.DataFrame(ubicaciones_data)
    ubicaciones_df.to_excel(writer, sheet_name='Ubicaciones', index=False)

print(f"✅ Archivo XLSX creado: {xlsx_filename}")
print(f"   📊 {len(noticias_data)} filas de datos")
print(f"   📋 3 hojas: Noticias, Resumen, Ubicaciones")

# Obtener ruta absoluta
xlsx_path = os.path.abspath(xlsx_filename)
print(f"\n📁 ARCHIVO EXPORTADO:")
print(f"   {xlsx_path}")

# Verificar archivo
if os.path.exists(xlsx_filename):
    file_size = os.path.getsize(xlsx_filename)
    print(f"\n🔍 VERIFICACIÓN:")
    print(f"   ✅ Archivo existe: {file_size:,} bytes")
    print(f"   📊 Formato: Excel (.xlsx)")
    print(f"   🗂️  3 hojas de cálculo incluidas")

print(f"\n🎉 EXPORTACIÓN XLSX COMPLETADA")
print("✅ Listo para descarga y análisis")

# Retornar ruta para uso en interfaz
if __name__ == "__main__":
    print(f"\n📤 Archivo disponible para descarga:")
    print(f"   {xlsx_path}")