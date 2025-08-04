"""
Exportador de resultados a formato CSV compatible con Centro Regional Base.
Genera archivos CSV con la estructura exacta requerida para análisis.
"""
import csv
import os
from datetime import datetime
from typing import List, Dict
from urllib.parse import urlparse
from .intelligent_search_agent import ProcessedNews, SearchResults


class CentroRegionalCSVExporter:
    """Exportador a formato CSV compatible con Centro Regional Base"""
    
    def __init__(self):
        # Mapeo de clasificaciones de drogas
        self.drug_classification_map = {
            'Estimulante y empatogeno': 'Estimulante y empatogeno',
            'Opioide sintetico': 'Opioide sintetico', 
            'Anestesico disociativo': 'Anestesico disociativo',
            'Alucinogeno': 'Alucinogeno',
            'Depresor': 'Depresor',
            'Estimulante sintetico': 'Estimulante sintetico',
            'NSP (Nuevas Drogas Sinteticas)': 'NPS'
        }
        
        # Mapeo de tipos específicos de sustancias
        self.substance_type_map = {
            'cocaina': 'Cocaína',
            'cocaína': 'Cocaína',
            'marihuana': 'Marihuana',
            'heroina': 'Heroína',
            'heroína': 'Heroína',
            'fentanilo': 'Fentanilo',
            'metanfetamina': 'Metanfetaminas',
            'lsd': 'LSD',
            'mdma': 'MDMA',
            'extasis': 'MDMA',
            'tusi': 'TUSI',
            'ketamina': 'Ketamina',
            'cristal': 'Cristal'
        }
        
    def export_to_csv(self, results: SearchResults, output_path: str) -> str:
        """
        Exporta los resultados a CSV en formato Centro Regional Base
        
        Args:
            results: Resultados de la búsqueda
            output_path: Ruta donde guardar el archivo CSV
            
        Returns:
            Ruta del archivo generado
        """
        
        # Preparar datos para el CSV
        csv_rows = []
        
        for processed_news in results.processed_news:
            # Crear fila base
            base_row = self._create_base_row(processed_news)
            
            # Si hay múltiples drogas mencionadas, crear filas adicionales
            drug_mentions = processed_news.relevance.drug_mentions
            
            if drug_mentions:
                for i, drug in enumerate(drug_mentions):
                    row = base_row.copy()
                    
                    # Solo la primera fila tiene todos los datos, las demás solo datos de droga
                    if i > 0:
                        row = self._create_additional_drug_row(base_row, drug)
                    else:
                        # Actualizar datos de droga para la primera fila
                        self._update_drug_data(row, drug)
                        
                    csv_rows.append(row)
            else:
                # Si no hay drogas específicas, agregar fila sin clasificación
                csv_rows.append(base_row)
                
        # Escribir CSV
        filename = self._generate_filename(output_path)
        self._write_csv_file(csv_rows, filename)
        
        return filename
        
    def _create_base_row(self, processed_news: ProcessedNews) -> Dict:
        """Crea la fila base con todos los campos"""
        
        article = processed_news.article
        relevance = processed_news.relevance
        location = processed_news.location_info
        geocoding = processed_news.geocoding_result
        
        # Extraer coordenadas
        coordinates = ""
        geo_pais = ""
        geo_prov = ""
        geo_distrito = ""
        
        if geocoding.success and geocoding.coordinates:
            coordinates = f"\"{geocoding.coordinates.latitude}, {geocoding.coordinates.longitude}\""
            geo_pais = coordinates  # Para simplicidad, usar mismas coordenadas
            geo_prov = coordinates
            geo_distrito = coordinates
            
        # Determinar país y códigos
        country_code = location.country_code or "XX"
        iso_code = f"ISO 3166-2:{country_code}"
        
        # Fecha actual
        current_date = datetime.now()
        fecha_str = current_date.strftime("%d/%m/%Y")
        
        # Crear fila
        row = {
            'Articulo_ID': processed_news.article_id,
            'CUI': processed_news.cui,
            'Fecha_Publicacion_Articulo': fecha_str,
            'Titulo_Articulo': article.title,
            'Descripcion_Articulo': article.description,
            'Medio': article.source,
            'URL_Acortada': self._shorten_url(article.url),
            'Pais_Origen_Articulo': location.country or "Sin especificar",
            'Cod_Continente': "SA",  # Sudamérica por defecto
            'Idioma': "ES",
            'Categoria_tematica': "Incidente",
            'Relevancia_Mencion': relevance.level,
            'Frecuencia_Mencion': self._map_frequency(relevance.score),
            'Impacto_Articulo': self._map_impact(relevance.score),
            'Keywords': ", ".join(relevance.drug_mentions + relevance.reasons),
            'Clasificacion_Sust_Estup_Decomisada': "",  # Se llena por droga específica
            'Tipo_Sus_Estup_Decomisada': "",  # Se llena por droga específica
            'Cant_Sust_Estup_Sintetica_incautada': "0,00",
            'Unidad': "Sin datos",
            'Fueza_interviniente': self._extract_force(article.title + " " + article.description),
            'Ubicacion_Secuestro': location.full_address or "Sin especificar",
            'Region': "America",
            'Sub region': self._determine_subregion(location.country),
            'Pais': location.country or "Sin especificar",
            'Provincia': location.state_province or "",
            'Distrito': location.city or "",
            'Alfa_2': country_code,
            'ISO_3166_2': iso_code,
            'Geo_Pais': geo_pais,
            'Geo_Prov': geo_prov,
            'Geo_Distrito': geo_distrito,
            'Fecha': fecha_str,
            'Dia': str(current_date.day),
            'Semana': str(current_date.isocalendar()[1]),
            'Quincena': "1" if current_date.day <= 15 else "2",
            'Mes_Largo': current_date.strftime("%B").title(),
            'Trimestre': f"T{(current_date.month - 1) // 3 + 1}",
            'Año': str(current_date.year)
        }
        
        return row
        
    def _create_additional_drug_row(self, base_row: Dict, drug: str) -> Dict:
        """Crea fila adicional para droga secundaria (sin datos generales)"""
        
        row = {key: "" for key in base_row.keys()}
        
        # Mantener solo datos esenciales
        row['CUI'] = base_row['CUI']
        row['Fecha_Publicacion_Articulo'] = base_row['Fecha_Publicacion_Articulo']
        row['Cant_Sust_Estup_Sintetica_incautada'] = "0,00"
        row['Unidad'] = "Sin datos"
        row['Geo_Pais'] = base_row['Geo_Pais']
        row['Geo_Prov'] = base_row['Geo_Prov']
        row['Geo_Distrito'] = base_row['Geo_Distrito']
        row['Fecha'] = base_row['Fecha']
        row['Dia'] = base_row['Dia']
        row['Semana'] = base_row['Semana']
        row['Quincena'] = base_row['Quincena']
        row['Mes_Largo'] = base_row['Mes_Largo']
        row['Trimestre'] = base_row['Trimestre']
        row['Año'] = base_row['Año']
        
        # Actualizar datos de droga
        self._update_drug_data(row, drug)
        
        return row
        
    def _update_drug_data(self, row: Dict, drug: str) -> None:
        """Actualiza los datos específicos de la droga en la fila"""
        
        drug_lower = drug.lower()
        
        # Determinar clasificación
        classification = "Sin clasificar"
        drug_type = "Sin especificar"
        
        # Mapear droga específica
        if drug_lower in self.substance_type_map:
            drug_type = self.substance_type_map[drug_lower]
            
            # Determinar clasificación basada en el tipo
            if drug_lower in ['mdma', 'extasis']:
                classification = "Estimulante y empatogeno"
            elif drug_lower in ['fentanilo']:
                classification = "Opioide sintetico"
            elif drug_lower in ['ketamina']:
                classification = "Anestesico disociativo"
            elif drug_lower in ['lsd', 'tusi']:
                classification = "Alucinogeno"
            elif drug_lower in ['metanfetamina', 'cristal']:
                classification = "Estimulante sintetico"
                
        row['Clasificacion_Sust_Estup_Decomisada'] = classification
        row['Tipo_Sus_Estup_Decomisada'] = drug_type
        
    def _shorten_url(self, url: str) -> str:
        """Simula el acortamiento de URL (en producción usar servicio real)"""
        try:
            domain = urlparse(url).netloc
            return f"https://tinyurl.com/{hash(url) % 100000}"
        except:
            return url
            
    def _map_frequency(self, score: float) -> str:
        """Mapea score a frecuencia de mención"""
        if score >= 70:
            return "Alta"
        elif score >= 40:
            return "Media"
        else:
            return "Baja"
            
    def _map_impact(self, score: float) -> str:
        """Mapea score a impacto del artículo"""
        if score >= 70:
            return "Alto"
        elif score >= 40:
            return "Medio"
        else:
            return "Bajo"
            
    def _extract_force(self, text: str) -> str:
        """Extrae la fuerza interviniente del texto"""
        
        forces = [
            "Policía Nacional", "Policía", "Carabineros", "SENAD", "DEA",
            "Antinarcóticos", "Fuerza Pública", "Guardia Civil",
            "Brigada Antidrogas", "FELCN", "PNP"
        ]
        
        text_lower = text.lower()
        for force in forces:
            if force.lower() in text_lower:
                return force
                
        return "Sin especificar"
        
    def _determine_subregion(self, country: str) -> str:
        """Determina la subregión basada en el país"""
        
        if not country:
            return "Sin especificar"
            
        caribe_countries = [
            "Cuba", "República Dominicana", "Jamaica", "Trinidad y Tobago",
            "Barbados", "Granada", "Santa Lucía", "Dominica"
        ]
        
        central_america = [
            "Guatemala", "Belice", "El Salvador", "Honduras", 
            "Nicaragua", "Costa Rica", "Panamá"
        ]
        
        if country in caribe_countries:
            return "Caribe"
        elif country in central_america:
            return "America Central"
        else:
            return "America del Sur"
            
    def _generate_filename(self, output_path: str) -> str:
        """Genera nombre de archivo único"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Centro_Regional_DrugNews_{timestamp}.csv"
        
        if os.path.isdir(output_path):
            return os.path.join(output_path, filename)
        else:
            return filename
            
    def _write_csv_file(self, rows: List[Dict], filename: str) -> None:
        """Escribe el archivo CSV"""
        
        if not rows:
            return
            
        # Definir orden de columnas (basado en Centro Regional Base)
        fieldnames = [
            'Articulo_ID', 'CUI', 'Fecha_Publicacion_Articulo', 'Titulo_Articulo',
            'Descripcion_Articulo', 'Medio', 'URL_Acortada', 'Pais_Origen_Articulo',
            'Cod_Continente', 'Idioma', 'Categoria_tematica', 'Relevancia_Mencion',
            'Frecuencia_Mencion', 'Impacto_Articulo', 'Keywords',
            'Clasificacion_Sust_Estup_Decomisada', 'Tipo_Sus_Estup_Decomisada',
            'Cant_Sust_Estup_Sintetica_incautada', 'Unidad', 'Fueza_interviniente',
            'Ubicacion_Secuestro', 'Region', 'Sub region', 'Pais', 'Provincia',
            'Distrito', 'Alfa_2', 'ISO_3166_2', 'Geo_Pais', 'Geo_Prov',
            'Geo_Distrito', 'Fecha', 'Dia', 'Semana', 'Quincena', 'Mes_Largo',
            'Trimestre', 'Año'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
        print(f"✅ CSV exportado: {filename}")
        print(f"📊 Total filas: {len(rows)}")
        
    def export_summary_report(self, results: SearchResults, output_path: str) -> str:
        """Exporta un reporte resumen de la búsqueda"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"Drug_News_Search_Report_{timestamp}.txt"
        
        if os.path.isdir(output_path):
            report_path = os.path.join(output_path, report_filename)
        else:
            report_path = report_filename
            
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("🔍 REPORTE DE BÚSQUEDA DE NOTICIAS SOBRE DROGAS\\n")
            f.write("=" * 50 + "\\n\\n")
            
            f.write(f"📅 Fecha de búsqueda: {datetime.now().strftime('%d/%m/%Y %H:%M')}\\n")
            f.write(f"⏱️  Tiempo de procesamiento: {results.processing_time:.1f} segundos\\n\\n")
            
            f.write("📊 MÉTRICAS GENERALES:\\n")
            f.write("-" * 25 + "\\n")
            for key, value in results.search_metrics.items():
                f.write(f"• {key.replace('_', ' ').title()}: {value}\\n")
                
            f.write("\\n🎯 RESULTADOS POR RELEVANCIA:\\n")
            f.write("-" * 30 + "\\n")
            
            relevance_counts = {'Alta': 0, 'Media': 0, 'Baja': 0}
            for news in results.processed_news:
                relevance_counts[news.relevance.level] += 1
                
            for level, count in relevance_counts.items():
                f.write(f"• {level}: {count} artículos\\n")
                
            f.write("\\n🌎 PAÍSES CON MÁS NOTICIAS:\\n")
            f.write("-" * 25 + "\\n")
            
            country_counts = {}
            for news in results.processed_news:
                country = news.location_info.country or "Sin especificar"
                country_counts[country] = country_counts.get(country, 0) + 1
                
            sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
            for country, count in sorted_countries[:10]:
                f.write(f"• {country}: {count} artículos\\n")
                
            if results.duplicate_groups:
                f.write("\\n🔄 GRUPOS DE NOTICIAS DUPLICADAS:\\n")
                f.write("-" * 30 + "\\n")
                
                for i, group in enumerate(results.duplicate_groups[:5]):
                    f.write(f"• Grupo {i+1}: {len(group.duplicates)} duplicados\\n")
                    f.write(f"  Artículo principal: {group.primary_article.title[:60]}...\\n")
                    f.write(f"  Similitud: {group.similarity_score:.2f}\\n\\n")
                    
        print(f"📋 Reporte generado: {report_path}")
        return report_path


if __name__ == "__main__":
    # Test del exportador
    print("🧪 Test del exportador CSV...")
    
    # Este sería llamado normalmente con resultados reales
    # exporter = CentroRegionalCSVExporter()
    # csv_file = exporter.export_to_csv(results, "./output")
    # report_file = exporter.export_summary_report(results, "./output")
    
    print("✅ Exportador listo para usar")