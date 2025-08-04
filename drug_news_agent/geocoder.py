"""
Módulo de geocodificación usando Google Maps API.
Convierte direcciones de texto en coordenadas geográficas precisas.
"""
import os
import time
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .location_extractor import LocationInfo


@dataclass
class Coordinates:
    """Coordenadas geográficas"""
    latitude: float
    longitude: float
    formatted_address: str = ""
    accuracy: str = ""  # ROOFTOP, RANGE_INTERPOLATED, GEOMETRIC_CENTER, APPROXIMATE
    place_id: str = ""


@dataclass
class GeocodingResult:
    """Resultado de geocodificación"""
    coordinates: Optional[Coordinates]
    success: bool
    error_message: str = ""
    api_calls_used: int = 0


class GoogleMapsGeocoder:
    """Geocodificador usando Google Maps API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.rate_limit_delay = 0.1  # Delay entre requests para respetar rate limits
        self.api_calls_count = 0
        
        if not self.api_key:
            print("⚠️  Google Maps API key no encontrada. Usando coordenadas aproximadas.")
            
    def geocode_location(self, location_info: LocationInfo) -> GeocodingResult:
        """Geocodifica una ubicación extraída"""
        if not self.api_key:
            return self._fallback_geocoding(location_info)
            
        # Preparar consulta para Google Maps
        query = self._build_geocoding_query(location_info)
        
        if not query:
            return GeocodingResult(
                coordinates=None,
                success=False,
                error_message="No se pudo construir consulta de geocodificación"
            )
            
        try:
            # Realizar consulta a Google Maps API
            params = {
                'address': query,
                'key': self.api_key,
                'language': 'es',
                'region': self._get_region_bias(location_info.country_code)
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            self.api_calls_count += 1
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_geocoding_response(data)
            else:
                return GeocodingResult(
                    coordinates=None,
                    success=False,
                    error_message=f"Error API: {response.status_code}",
                    api_calls_used=1
                )
                
        except Exception as e:
            return GeocodingResult(
                coordinates=None,
                success=False,
                error_message=f"Error de conexión: {str(e)}",
                api_calls_used=1
            )
        finally:
            # Respetar rate limits
            time.sleep(self.rate_limit_delay)
            
    def batch_geocode(self, locations: List[LocationInfo]) -> List[GeocodingResult]:
        """Geocodifica múltiples ubicaciones"""
        results = []
        
        for i, location in enumerate(locations):
            print(f"Geocodificando {i+1}/{len(locations)}: {location.full_address}")
            result = self.geocode_location(location)
            results.append(result)
            
            # Progress feedback
            if (i + 1) % 10 == 0:
                successful = sum(1 for r in results if r.success)
                print(f"✅ Progreso: {successful}/{i+1} exitosas")
                
        return results
        
    def _build_geocoding_query(self, location_info: LocationInfo) -> str:
        """Construye la consulta de geocodificación más efectiva"""
        
        # Estrategia 1: Si tenemos dirección completa, usarla
        if location_info.full_address:
            return location_info.full_address
            
        # Estrategia 2: Construir desde componentes específicos a generales
        components = []
        
        if location_info.district_neighborhood:
            components.append(location_info.district_neighborhood)
        if location_info.city:
            components.append(location_info.city)
        if location_info.state_province:
            components.append(location_info.state_province)
        if location_info.country:
            components.append(location_info.country)
            
        if components:
            return ", ".join(components)
            
        return ""
        
    def _parse_geocoding_response(self, data: Dict) -> GeocodingResult:
        """Parsea la respuesta de Google Maps API"""
        
        if data['status'] != 'OK':
            return GeocodingResult(
                coordinates=None,
                success=False,
                error_message=f"Google Maps API: {data['status']}",
                api_calls_used=1
            )
            
        if not data.get('results'):
            return GeocodingResult(
                coordinates=None,
                success=False,
                error_message="No se encontraron resultados",
                api_calls_used=1
            )
            
        # Tomar el primer resultado (más relevante)
        result = data['results'][0]
        geometry = result['geometry']
        
        coordinates = Coordinates(
            latitude=geometry['location']['lat'],
            longitude=geometry['location']['lng'],
            formatted_address=result['formatted_address'],
            accuracy=geometry.get('location_type', 'UNKNOWN'),
            place_id=result.get('place_id', '')
        )
        
        return GeocodingResult(
            coordinates=coordinates,
            success=True,
            api_calls_used=1
        )
        
    def _get_region_bias(self, country_code: str) -> str:
        """Obtiene el sesgo regional para mejorar los resultados"""
        # Mapeo de códigos de país para sesgo regional
        region_map = {
            'AR': 'ar',  # Argentina
            'CO': 'co',  # Colombia
            'BR': 'br',  # Brasil
            'MX': 'mx',  # México
            'CL': 'cl',  # Chile
            'PE': 'pe',  # Perú
            'UY': 'uy',  # Uruguay
            'VE': 've',  # Venezuela
            'BO': 'bo',  # Bolivia
            'EC': 'ec',  # Ecuador
            'PY': 'py',  # Paraguay
        }
        
        return region_map.get(country_code, 'us')
        
    def _fallback_geocoding(self, location_info: LocationInfo) -> GeocodingResult:
        """Geocodificación de fallback usando coordenadas aproximadas de países"""
        
        # Si no tenemos API key, usar coordenadas aproximadas del país
        if location_info.country_code:
            # Buscar coordenadas del país en nuestros datos
            country = None
            for code, country_obj in location_info.__dict__.items():
                if hasattr(country_obj, 'coordinates') and code == location_info.country_code:
                    country = country_obj
                    break
                    
            if country and hasattr(country, 'coordinates'):
                try:
                    coords = country.coordinates.split(', ')
                    lat, lng = float(coords[0]), float(coords[1])
                    
                    coordinates = Coordinates(
                        latitude=lat,
                        longitude=lng,
                        formatted_address=f"{location_info.country} (aproximado)",
                        accuracy="COUNTRY_LEVEL"
                    )
                    
                    return GeocodingResult(
                        coordinates=coordinates,
                        success=True,
                        error_message="Usando coordenadas aproximadas de país",
                        api_calls_used=0
                    )
                except:
                    pass
        
        # Coordenadas por defecto para América Latina
        default_coords = {
            'AR': (-37.650894, -65.897084),  # Argentina
            'CO': (4.068636, -72.886327),    # Colombia
            'BR': (-8.843614, -52.200865),   # Brasil
            'MX': (23.311747, -103.069334),  # México
            'CL': (-35.270325, -71.315779),  # Chile
            'PE': (-9.515798, -75.223851),   # Perú
            'UY': (-32.953025, -55.974972),  # Uruguay
            'VE': (6.727313, -65.341606),    # Venezuela
            'BO': (-16.277995, -64.397735),  # Bolivia
        }
        
        if location_info.country_code in default_coords:
            lat, lng = default_coords[location_info.country_code]
            
            coordinates = Coordinates(
                latitude=lat,
                longitude=lng,
                formatted_address=f"{location_info.country} (coordenadas por defecto)",
                accuracy="COUNTRY_APPROXIMATE"
            )
            
            return GeocodingResult(
                coordinates=coordinates,
                success=True,
                error_message="Usando coordenadas por defecto",
                api_calls_used=0
            )
            
        return GeocodingResult(
            coordinates=None,
            success=False,
            error_message="No se pudo determinar ubicación",
            api_calls_used=0
        )
        
    def get_usage_stats(self) -> Dict[str, int]:
        """Retorna estadísticas de uso de la API"""
        return {
            'total_api_calls': self.api_calls_count,
            'estimated_cost_usd': self.api_calls_count * 0.005  # ~$0.005 por request
        }


class CachedGeocoder:
    """Geocodificador con caché para evitar consultas repetidas"""
    
    def __init__(self, geocoder: GoogleMapsGeocoder):
        self.geocoder = geocoder
        self.cache = {}  # En producción, usar Redis o base de datos
        
    def geocode_location(self, location_info: LocationInfo) -> GeocodingResult:
        """Geocodifica con caché"""
        
        # Crear clave de caché
        cache_key = self._create_cache_key(location_info)
        
        # Verificar caché
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            return GeocodingResult(
                coordinates=cached_result,
                success=True,
                error_message="Resultado desde caché",
                api_calls_used=0
            )
            
        # Si no está en caché, geocodificar
        result = self.geocoder.geocode_location(location_info)
        
        # Guardar en caché si fue exitoso
        if result.success and result.coordinates:
            self.cache[cache_key] = result.coordinates
            
        return result
        
    def _create_cache_key(self, location_info: LocationInfo) -> str:
        """Crea clave única para el caché"""
        components = [
            location_info.country.lower() if location_info.country else "",
            location_info.state_province.lower() if location_info.state_province else "",
            location_info.city.lower() if location_info.city else "",
            location_info.district_neighborhood.lower() if location_info.district_neighborhood else ""
        ]
        
        return "|".join(components)


if __name__ == "__main__":
    # Test del geocodificador
    from .data_loader import DataLoader
    from .location_extractor import LocationExtractor, LocationInfo
    
    # Crear geocodificador (sin API key para demo)
    geocoder = GoogleMapsGeocoder()
    
    # Ubicación de prueba
    test_location = LocationInfo(
        country="Colombia",
        country_code="CO",
        city="Bogotá",
        district_neighborhood="La Candelaria",
        full_address="La Candelaria, Bogotá, Colombia",
        confidence_score=0.9
    )
    
    result = geocoder.geocode_location(test_location)
    
    if result.success:
        print(f"✅ Geocodificación exitosa")
        print(f"Coordenadas: {result.coordinates.latitude}, {result.coordinates.longitude}")
        print(f"Dirección: {result.coordinates.formatted_address}")
        print(f"Precisión: {result.coordinates.accuracy}")
    else:
        print(f"❌ Error: {result.error_message}")
        
    print(f"Llamadas API usadas: {result.api_calls_used}")