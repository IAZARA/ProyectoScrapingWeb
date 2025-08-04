"""
Extractor de ubicación geográfica de noticias.
Identifica y extrae información de ubicación de manera granular (país, provincia, ciudad, barrio).
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .data_loader import DataLoader
from .relevance_classifier import NewsArticle


@dataclass
class LocationInfo:
    """Información de ubicación extraída"""
    country: str = ""
    country_code: str = ""
    state_province: str = ""
    city: str = ""
    district_neighborhood: str = ""
    full_address: str = ""
    confidence_score: float = 0.0
    extraction_method: str = ""


class LocationExtractor:
    """Extractor inteligente de ubicación geográfica"""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        
        # Patrones de ubicación en español
        self.location_patterns = {
            'city_country': [
                r'en\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+),\s*([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)',
                r'de\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+),\s*([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)',
                r'([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+),\s*([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)'
            ],
            'city_state_country': [
                r'en\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+),\s*([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+),\s*([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)',
                r'de\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+),\s*([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+),\s*([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)'
            ],
            'specific_location': [
                r'en\s+el\s+([a-záéíóúñü\s]+)\s+de\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)',
                r'en\s+la\s+([a-záéíóúñü\s]+)\s+de\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)',
                r'en\s+([a-záéíóúñü\s]+)\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)',
                r'barrio\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)',
                r'comuna\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)',
                r'sector\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)',
                r'zona\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)'
            ]
        }
        
        # Palabras clave que indican ubicación específica
        self.location_indicators = [
            'municipio', 'departamento', 'provincia', 'estado', 'región',
            'ciudad', 'pueblo', 'villa', 'barrio', 'comuna', 'sector',
            'zona', 'distrito', 'localidad', 'corregimiento'
        ]
        
        # Países y sus variaciones de nombre
        self.country_variations = self._build_country_variations()
        
        # Estados/provincias conocidas por país
        self.known_states = self._load_known_states()
        
    def extract_location(self, article: NewsArticle) -> LocationInfo:
        """Extrae información de ubicación de un artículo"""
        full_text = f"{article.title} {article.description} {article.content}"
        
        # Intentar diferentes métodos de extracción
        methods = [
            self._extract_structured_location,
            self._extract_pattern_based_location,
            self._extract_contextual_location,
            self._extract_country_only
        ]
        
        best_location = LocationInfo()
        
        for method in methods:
            location = method(full_text)
            if location.confidence_score > best_location.confidence_score:
                best_location = location
                
        return best_location
        
    def _extract_structured_location(self, text: str) -> LocationInfo:
        """Extrae ubicación usando patrones estructurados"""
        location = LocationInfo()
        location.extraction_method = "structured_pattern"
        
        # Buscar patrones ciudad-estado-país
        for pattern in self.location_patterns['city_state_country']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                match = matches[0]
                city, state, country = match
                
                if self._is_valid_country(country):
                    location.city = city.strip()
                    location.state_province = state.strip()
                    location.country = country.strip()
                    location.country_code = self._get_country_code(country)
                    location.full_address = f"{city}, {state}, {country}"
                    location.confidence_score = 0.9
                    return location
                    
        # Buscar patrones ciudad-país
        for pattern in self.location_patterns['city_country']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                match = matches[0]
                city, country = match
                
                if self._is_valid_country(country):
                    location.city = city.strip()
                    location.country = country.strip()
                    location.country_code = self._get_country_code(country)
                    location.full_address = f"{city}, {country}"
                    location.confidence_score = 0.8
                    return location
                    
        return location
        
    def _extract_pattern_based_location(self, text: str) -> LocationInfo:
        """Extrae ubicación usando patrones específicos"""
        location = LocationInfo()
        location.extraction_method = "pattern_based"
        
        # Buscar ubicaciones específicas (barrios, sectores, etc.)
        for pattern in self.location_patterns['specific_location']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    if len(matches[0]) == 2:
                        location.district_neighborhood = matches[0][0].strip()
                        location.city = matches[0][1].strip()
                    else:
                        location.district_neighborhood = matches[0][0].strip()
                else:
                    location.district_neighborhood = matches[0].strip()
                    
                location.confidence_score = 0.6
                break
                
        # Buscar país en el texto
        country_info = self._find_country_in_text(text)
        if country_info:
            location.country = country_info[0]
            location.country_code = country_info[1]
            location.confidence_score += 0.2
            
        if location.country and location.district_neighborhood:
            location.full_address = f"{location.district_neighborhood}, {location.country}"
            
        return location
        
    def _extract_contextual_location(self, text: str) -> LocationInfo:
        """Extrae ubicación usando contexto y indicadores"""
        location = LocationInfo()
        location.extraction_method = "contextual"
        
        # Buscar indicadores de ubicación
        for indicator in self.location_indicators:
            pattern = rf'{indicator}\s+([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\s]+)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            if matches:
                place_name = matches[0].strip()
                
                # Determinar el tipo de lugar según el indicador
                if indicator in ['barrio', 'comuna', 'sector', 'zona']:
                    location.district_neighborhood = place_name
                elif indicator in ['ciudad', 'municipio']:
                    location.city = place_name
                elif indicator in ['provincia', 'estado', 'departamento', 'región']:
                    location.state_province = place_name
                    
                location.confidence_score = 0.5
                break
                
        # Buscar país
        country_info = self._find_country_in_text(text)
        if country_info:
            location.country = country_info[0]
            location.country_code = country_info[1]
            location.confidence_score += 0.2
            
        # Construir dirección completa
        address_parts = []
        if location.district_neighborhood:
            address_parts.append(location.district_neighborhood)
        if location.city:
            address_parts.append(location.city)
        if location.state_province:
            address_parts.append(location.state_province)
        if location.country:
            address_parts.append(location.country)
            
        location.full_address = ", ".join(address_parts)
        
        return location
        
    def _extract_country_only(self, text: str) -> LocationInfo:
        """Extrae solo el país como fallback"""
        location = LocationInfo()
        location.extraction_method = "country_only"
        
        country_info = self._find_country_in_text(text)
        if country_info:
            location.country = country_info[0]
            location.country_code = country_info[1]
            location.full_address = location.country
            location.confidence_score = 0.3
            
        return location
        
    def _find_country_in_text(self, text: str) -> Optional[Tuple[str, str]]:
        """Busca países objetivo en el texto"""
        text_lower = text.lower()
        
        for code, country in self.data_loader.countries.items():
            # Buscar por nombre completo
            if country.name.lower() in text_lower:
                return (country.name, code)
                
            # Buscar por variaciones de nombre
            if country.name in self.country_variations:
                for variation in self.country_variations[country.name]:
                    if variation.lower() in text_lower:
                        return (country.name, code)
                        
        return None
        
    def _is_valid_country(self, country_name: str) -> bool:
        """Verifica si un país es válido y objetivo"""
        return self.data_loader.is_target_country(country_name)
        
    def _get_country_code(self, country_name: str) -> str:
        """Obtiene el código de país"""
        for code, country in self.data_loader.countries.items():
            if country.name.lower() == country_name.lower():
                return code
        return ""
        
    def _build_country_variations(self) -> Dict[str, List[str]]:
        """Construye variaciones de nombres de países"""
        variations = {
            "República Argentina": ["Argentina", "argentina"],
            "República de Colombia": ["Colombia", "colombia"],
            "República Federativa del Brasil": ["Brasil", "brazil", "brasil"],
            "Estados Unidos Mexicanos": ["México", "Mexico", "mexico", "méxico"],
            "República de Chile": ["Chile", "chile"],
            "República del Perú": ["Perú", "Peru", "peru", "perú"],
            "República Oriental del Uruguay": ["Uruguay", "uruguay"],
            "República Bolivariana de Venezuela": ["Venezuela", "venezuela"],
            "Estado Plurinacional de Bolivia": ["Bolivia", "bolivia"]
        }
        return variations
        
    def _load_known_states(self) -> Dict[str, List[str]]:
        """Carga estados/provincias conocidas por país"""
        # Esta sería expandida con datos reales
        known_states = {
            "AR": ["Buenos Aires", "Córdoba", "Santa Fe", "Mendoza", "Tucumán"],
            "CO": ["Antioquia", "Cundinamarca", "Valle del Cauca", "Atlántico", "Santander"],
            "BR": ["São Paulo", "Rio de Janeiro", "Minas Gerais", "Bahia", "Paraná"],
            "MX": ["Ciudad de México", "Estado de México", "Jalisco", "Nuevo León", "Puebla"],
            "CL": ["Santiago", "Valparaíso", "Biobío", "Araucanía", "Los Lagos"]
        }
        return known_states
        
    def batch_extract_locations(self, articles: List[NewsArticle]) -> List[Tuple[NewsArticle, LocationInfo]]:
        """Extrae ubicaciones de múltiples artículos"""
        results = []
        
        for article in articles:
            location = self.extract_location(article)
            results.append((article, location))
            
        return results


if __name__ == "__main__":
    # Test del extractor de ubicación
    from .data_loader import DataLoader
    
    loader = DataLoader()
    loader.load_all_data()
    
    extractor = LocationExtractor(loader)
    
    # Artículo de prueba
    test_article = NewsArticle(
        title="Incautan cocaína en el barrio La Candelaria de Bogotá, Colombia",
        description="La Policía Nacional realizó operativo en el centro histórico",
        content="El operativo se realizó en el barrio La Candelaria, en el centro de Bogotá, capital de Colombia.",
        url="https://test.com",
        date="15/01/2025",
        source="Test News"
    )
    
    location = extractor.extract_location(test_article)
    print(f"País: {location.country}")
    print(f"Ciudad: {location.city}")
    print(f"Barrio: {location.district_neighborhood}")
    print(f"Dirección completa: {location.full_address}")
    print(f"Confianza: {location.confidence_score}")
    print(f"Método: {location.extraction_method}")