"""
Agente de búsqueda inteligente principal.
Orquesta todo el sistema de búsqueda, análisis y geocodificación de noticias sobre drogas.
"""
import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Agregar el path del proyecto para importar las herramientas
sys.path.append('/Users/macbook/Documents/AgenteWeb/WebAgent/WebDancer')

from demos.tools.private.search import Search
from demos.tools.private.visit import Visit
from .data_loader import DataLoader
from .relevance_classifier import NewsArticle, RelevanceClassifier, RelevanceScore
from .deduplication import NewsDeduplicator, DuplicateGroup
from .location_extractor import LocationExtractor, LocationInfo
from .geocoder import GoogleMapsGeocoder, CachedGeocoder, GeocodingResult


@dataclass
class ProcessedNews:
    """Noticia procesada con toda la información analizada"""
    article_id: str
    cui: str
    article: NewsArticle
    relevance: RelevanceScore
    location_info: LocationInfo
    geocoding_result: GeocodingResult
    is_duplicate: bool = False
    duplicate_group_id: str = ""
    

@dataclass
class SearchResults:
    """Resultados completos de la búsqueda"""
    processed_news: List[ProcessedNews]
    duplicate_groups: List[DuplicateGroup]
    search_metrics: Dict
    processing_time: float


class IntelligentDrugNewsAgent:
    """Agente inteligente de búsqueda de noticias sobre drogas"""
    
    def __init__(self, google_maps_api_key: str = None):
        print("🚀 Inicializando Agente de Noticias sobre Drogas...")
        
        # Cargar datos de referencia
        self.data_loader = DataLoader()
        self.data_loader.load_all_data()
        
        # Inicializar componentes
        self.search_tool = Search()
        self.visit_tool = Visit()
        self.relevance_classifier = RelevanceClassifier(self.data_loader)
        self.deduplicator = NewsDeduplicator()
        self.location_extractor = LocationExtractor(self.data_loader)
        
        # Inicializar geocodificador con caché
        base_geocoder = GoogleMapsGeocoder(google_maps_api_key)
        self.geocoder = CachedGeocoder(base_geocoder)
        
        print("✅ Agente inicializado correctamente")
        
    def search_drug_news(self, 
                        days_back: int = 7,
                        max_articles_per_query: int = 20,
                        min_relevance: str = "Media") -> SearchResults:
        """
        Realiza búsqueda inteligente de noticias sobre drogas
        
        Args:
            days_back: Días hacia atrás para buscar noticias
            max_articles_per_query: Máximo artículos por consulta de búsqueda  
            min_relevance: Relevancia mínima (Alta, Media, Baja)
        """
        start_time = datetime.now()
        print(f"\n🔍 Iniciando búsqueda de noticias de los últimos {days_back} días...")
        
        # 1. Generar consultas de búsqueda inteligentes
        search_queries = self._generate_search_queries(days_back)
        print(f"📝 Generadas {len(search_queries)} consultas de búsqueda")
        
        # 2. Realizar búsquedas
        raw_articles = self._perform_searches(search_queries, max_articles_per_query)
        print(f"📰 Encontrados {len(raw_articles)} artículos en total")
        
        # 3. Filtrar por países objetivo
        filtered_articles = self._filter_by_target_countries(raw_articles)
        print(f"🌎 Filtrados {len(filtered_articles)} artículos de países objetivo\")
        
        # 4. Clasificar relevancia
        classified_articles = self._classify_relevance(filtered_articles, min_relevance)
        print(f"⭐ {len(classified_articles)} artículos cumplen criterios de relevancia\")
        
        # 5. Deduplicar noticias
        unique_articles, duplicate_groups = self._deduplicate_news(classified_articles)
        print(f"🔄 Identificados {len(unique_articles)} eventos únicos, {len(duplicate_groups)} grupos duplicados\")
        
        # 6. Extraer ubicaciones
        articles_with_locations = self._extract_locations(unique_articles)
        print(f"📍 Extraídas ubicaciones de {len(articles_with_locations)} artículos\")
        
        # 7. Geocodificar ubicaciones
        final_results = self._geocode_locations(articles_with_locations)
        print(f"🗺️  Geocodificados {len(final_results)} artículos\")
        
        # 8. Preparar resultados finales
        processing_time = (datetime.now() - start_time).total_seconds()
        
        search_metrics = {
            'total_queries': len(search_queries),
            'raw_articles_found': len(raw_articles),
            'target_country_articles': len(filtered_articles),
            'relevant_articles': len(classified_articles),
            'unique_events': len(unique_articles),
            'duplicate_groups': len(duplicate_groups),
            'geocoded_articles': len(final_results),
            'processing_time_seconds': processing_time
        }
        
        results = SearchResults(
            processed_news=final_results,
            duplicate_groups=duplicate_groups,
            search_metrics=search_metrics,
            processing_time=processing_time
        )
        
        print(f"\\n✅ Búsqueda completada en {processing_time:.1f} segundos\")
        return results
        
    def _generate_search_queries(self, days_back: int) -> List[str]:
        \"\"\"Genera consultas de búsqueda inteligentes\"\"\"
        
        # Obtener palabras clave principales de drogas
        drug_categories = list(self.data_loader.drug_keywords.keys())
        
        # Países objetivo principales
        main_countries = [
            \"Colombia\", \"México\", \"Argentina\", \"Brasil\", \"Perú\", 
            \"Venezuela\", \"Chile\", \"Ecuador\", \"Bolivia\", \"Uruguay\"
        ]
        
        # Términos operativos
        operational_terms = [
            \"incautación\", \"decomiso\", \"operativo\", \"captura\", 
            \"narcotráfico\", \"drogas\", \"antinarcóticos\"
        ]
        
        queries = []
        
        # Consultas por categoría de droga + país
        for category in drug_categories[:3]:  # Primeras 3 categorías más importantes
            main_drug = self.data_loader.drug_keywords[category][0] if self.data_loader.drug_keywords[category] else category
            for country in main_countries[:5]:  # Top 5 países
                query = f"{main_drug} {country} últimos días\"
                queries.append(query)
                
        # Consultas operativas generales
        for term in operational_terms[:4]:
            for country in main_countries[:3]:
                query = f"{term} drogas {country} {days_back} días\"
                queries.append(query)
                
        # Consultas regionales amplias
        regional_queries = [
            f"incautación drogas América Latina últimos {days_back} días\",
            f"operativo antinarcóticos Sudamérica {days_back} días\",
            f"decomiso cocaína Caribe {days_back} días\",
            \"narcotráfico operaciones recientes América\"
        ]
        
        queries.extend(regional_queries)
        
        return queries[:25]  # Límite de consultas para optimizar tokens
        
    def _perform_searches(self, queries: List[str], max_per_query: int) -> List[NewsArticle]:
        \"\"\"Realiza las búsquedas web\"\"\"
        
        all_articles = []
        
        # Procesar consultas en lotes para optimizar
        batch_size = 3
        for i in range(0, len(queries), batch_size):
            batch_queries = queries[i:i+batch_size]
            
            print(f"  🔍 Procesando lote {(i//batch_size)+1}/{(len(queries)-1)//batch_size+1}\")
            
            # Realizar búsqueda con múltiples consultas
            search_params = {\"query\": batch_queries}
            search_results = self.search_tool.call(str(search_params).replace(\"'\", '\"'))
            
            # Parsear resultados y convertir a NewsArticle objects
            articles = self._parse_search_results(search_results, batch_queries)
            all_articles.extend(articles)
            
            if len(all_articles) >= max_per_query * len(queries):
                break
                
        return all_articles
        
    def _parse_search_results(self, search_results: str, queries: List[str]) -> List[NewsArticle]:
        \"\"\"Convierte resultados de búsqueda en objetos NewsArticle\"\"\"
        
        articles = []
        
        # Dividir resultados por separador
        if \"=======\" in search_results:
            result_sections = search_results.split(\"=======\")
        else:
            result_sections = [search_results]
            
        for section in result_sections:
            if not section.strip():
                continue
                
            # Extraer artículos individuales del texto
            lines = section.strip().split('\\n')
            current_article = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Detectar inicio de nuevo artículo (formato: \"1. [Título](URL)\")
                if line.startswith((\"1.\", \"2.\", \"3.\", \"4.\", \"5.\", \"6.\", \"7.\", \"8.\", \"9.\", \"10.\")):
                    if current_article:
                        articles.append(current_article)
                        
                    # Extraer título y URL usando regex
                    import re
                    match = re.match(r'\\d+\\. \\[(.+?)\\]\\((.+?)\\)', line)
                    if match:
                        title = match.group(1)
                        url = match.group(2)
                        
                        current_article = NewsArticle(
                            title=title,
                            description=\"\",
                            content=\"\",
                            url=url,
                            date=datetime.now().strftime(\"%d/%m/%Y\"),
                            source=self._extract_domain(url)
                        )
                        
                elif current_article and line:
                    # Agregar línea como descripción/contenido
                    if \"Date published:\" in line:
                        # Extraer fecha si está disponible
                        current_article.date = line.split(\":\", 1)[1].strip()
                    elif \"Source:\" in line:
                        # Extraer fuente
                        current_article.source = line.split(\":\", 1)[1].strip()
                    else:
                        # Agregar como descripción
                        if current_article.description:
                            current_article.description += \" \" + line
                        else:
                            current_article.description = line
                            
            # Agregar último artículo si existe
            if current_article:
                articles.append(current_article)
                
        return articles
        
    def _extract_domain(self, url: str) -> str:
        \"\"\"Extrae el dominio de una URL\"\"\"
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return \"unknown\"
            
    def _filter_by_target_countries(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        \"\"\"Filtra artículos por países objetivo\"\"\"
        
        filtered = []
        
        for article in articles:
            full_text = f"{article.title} {article.description}\".lower()
            
            # Verificar si menciona algún país objetivo
            for country_code, country in self.data_loader.countries.items():
                if country.name.lower() in full_text:
                    article.country = country.name
                    filtered.append(article)
                    break
                    
        return filtered
        
    def _classify_relevance(self, articles: List[NewsArticle], min_relevance: str) -> List[Tuple[NewsArticle, RelevanceScore]]:
        \"\"\"Clasifica relevancia de los artículos\"\"\"
        
        classified = self.relevance_classifier.batch_classify(articles)
        
        # Filtrar por relevancia mínima
        relevance_order = {\"Baja\": 1, \"Media\": 2, \"Alta\": 3}
        min_level = relevance_order.get(min_relevance, 2)
        
        filtered = []
        for article, relevance in classified:
            article_level = relevance_order.get(relevance.level, 1)
            if article_level >= min_level:
                filtered.append((article, relevance))
                
        return filtered
        
    def _deduplicate_news(self, classified_articles: List[Tuple[NewsArticle, RelevanceScore]]) -> Tuple[List[Tuple[NewsArticle, RelevanceScore]], List[DuplicateGroup]]:
        \"\"\"Deduplica noticias similares\"\"\"
        
        articles = [item[0] for item in classified_articles]
        unique_articles, duplicate_groups, metrics = self.deduplicator.deduplicate(articles)
        
        # Reconstruir con scores de relevancia
        unique_with_scores = []
        for unique_article in unique_articles:
            # Encontrar el score correspondiente
            for article, score in classified_articles:
                if article.url == unique_article.url:
                    unique_with_scores.append((article, score))
                    break
                    
        return unique_with_scores, duplicate_groups
        
    def _extract_locations(self, articles_with_scores: List[Tuple[NewsArticle, RelevanceScore]]) -> List[Tuple[NewsArticle, RelevanceScore, LocationInfo]]:
        \"\"\"Extrae información de ubicación\"\"\"
        
        results = []
        articles = [item[0] for item in articles_with_scores]
        
        locations = self.location_extractor.batch_extract_locations(articles)
        
        for i, (article, location) in enumerate(locations):
            # Encontrar el score de relevancia correspondiente
            score = articles_with_scores[i][1]
            results.append((article, score, location))
            
        return results
        
    def _geocode_locations(self, articles_with_locations: List[Tuple[NewsArticle, RelevanceScore, LocationInfo]]) -> List[ProcessedNews]:
        \"\"\"Geocodifica las ubicaciones extraídas\"\"\"
        
        processed_news = []
        
        for article, relevance, location in articles_with_locations:
            # Geocodificar
            geocoding_result = self.geocoder.geocode_location(location)
            
            # Crear objeto ProcessedNews
            processed = ProcessedNews(
                article_id=f'A{str(uuid.uuid4())[:7]}',
                cui=f'CUI{str(uuid.uuid4())[:6]}',
                article=article,
                relevance=relevance,
                location_info=location,
                geocoding_result=geocoding_result
            )
            
            processed_news.append(processed)
            
        return processed_news


if __name__ == \"__main__\":
    # Test del agente completo
    agent = IntelligentDrugNewsAgent()
    
    print(\"\\n🧪 Realizando búsqueda de prueba...\")
    results = agent.search_drug_news(days_back=7, max_articles_per_query=5, min_relevance=\"Media\")
    
    print(f"\\n📊 Resultados:\")\n    print(f"- Artículos procesados: {len(results.processed_news)}\")\n    print(f"- Grupos duplicados: {len(results.duplicate_groups)}\")\n    print(f"- Tiempo de procesamiento: {results.processing_time:.1f} segundos\")\n    \n    if results.processed_news:\n        print(f"\\n📰 Primer artículo:\")\n        first = results.processed_news[0]\n        print(f"- Título: {first.article.title}\")\n        print(f"- Relevancia: {first.relevance.level} ({first.relevance.score:.1f})\")\n        print(f"- Ubicación: {first.location_info.full_address}\")\n        if first.geocoding_result.success:\n            coords = first.geocoding_result.coordinates\n            print(f"- Coordenadas: {coords.latitude}, {coords.longitude}\")"