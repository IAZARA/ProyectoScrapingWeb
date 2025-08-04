"""
Módulo para cargar y gestionar los datos de referencia del sistema.
Carga países, palabras clave de drogas y criterios de relevancia.
"""
import csv
import os
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class Country:
    """Estructura de datos para países"""
    name: str
    code_alpha2: str
    code_alpha3: str
    iso_code: str
    continent: str
    region: str
    coordinates: str


@dataclass
class DrugKeyword:
    """Estructura de datos para palabras clave de drogas"""
    category: str
    names: List[str]


@dataclass
class RelevanceRule:
    """Estructura de datos para reglas de relevancia"""
    category: str
    criteria: Dict[str, str]


class DataLoader:
    """Cargador de datos de referencia del sistema"""
    
    def __init__(self, data_path: str = "/Users/macbook/Documents/WebSearchAgent/AnalisisArchivo"):
        self.data_path = data_path
        self.countries: Dict[str, Country] = {}
        self.drug_keywords: Dict[str, List[str]] = {}
        self.relevance_rules: Dict[str, str] = {}
        self.target_countries: Set[str] = set()
        
    def load_all_data(self):
        """Carga todos los datos de referencia"""
        self.load_countries()
        self.load_drug_keywords()
        self.load_relevance_rules()
        
    def load_countries(self):
        """Carga la lista de países objetivo desde paises.csv"""
        countries_file = os.path.join(self.data_path, "paises.csv")
        
        with open(countries_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                country = Country(
                    name=row['Pais_Completo'],
                    code_alpha2=row['alpha-2_Completo'],
                    code_alpha3=row['alpha-3'],
                    iso_code=row['ISO_3166-2'],
                    continent=row['Continente'],
                    region=row['Region'],
                    coordinates=row['Geo']
                )
                
                # Solo países de América del Sur y Caribe (México hacia abajo)
                if country.region in ['America del Sur', 'Caribe', 'America Central'] or \
                   country.name in ['Estados Unidos Mexicanos', 'Mexico']:
                    self.countries[country.code_alpha2] = country
                    self.target_countries.add(country.name.lower())
                    
        print(f"✅ Cargados {len(self.countries)} países objetivo")
        
    def load_drug_keywords(self):
        """Carga las palabras clave de drogas desde drogas palabras clave.csv"""
        drugs_file = os.path.join(self.data_path, "drogas palabras clave.csv")
        
        with open(drugs_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Primera fila son las categorías
            
            # Procesar cada columna (categoría de droga)
            for col_idx, category in enumerate(headers):
                if category.strip():
                    self.drug_keywords[category] = []
                    
            # Procesar cada fila de nombres de drogas
            for row in reader:
                for col_idx, drug_name in enumerate(row):
                    if col_idx < len(headers) and drug_name.strip():
                        category = headers[col_idx]
                        if category in self.drug_keywords:
                            self.drug_keywords[category].append(drug_name.strip().lower())
                            
        print(f"✅ Cargadas {len(self.drug_keywords)} categorías de drogas")
        for category, keywords in self.drug_keywords.items():
            print(f"   - {category}: {len(keywords)} términos")
            
    def load_relevance_rules(self):
        """Carga los criterios de relevancia desde relevancia.csv"""
        relevance_file = os.path.join(self.data_path, "relevancia.csv")
        
        with open(relevance_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Relevancia_Mencion']:
                    level = row['Relevancia_Mencion'].split('(')[0].strip()
                    criteria = row['Relevancia_Mencion']
                    self.relevance_rules[level] = criteria
                    
        print(f"✅ Cargados {len(self.relevance_rules)} criterios de relevancia")
        
    def get_all_drug_keywords(self) -> List[str]:
        """Retorna todas las palabras clave de drogas como lista única"""
        all_keywords = []
        for category_keywords in self.drug_keywords.values():
            all_keywords.extend(category_keywords)
        return list(set(all_keywords))  # Eliminar duplicados
        
    def is_target_country(self, country_name: str) -> bool:
        """Verifica si un país está en la lista objetivo"""
        country_lower = country_name.lower()
        # Verificar tanto el nombre completo como variaciones comunes
        for target in self.target_countries:
            if country_lower in target or target in country_lower:
                return True
        # Verificar variaciones específicas
        if 'argentina' in country_lower:
            return True
        if 'colombia' in country_lower:
            return True
        if 'mexico' in country_lower or 'méxico' in country_lower:
            return True
        return False
        
    def get_country_by_name(self, country_name: str) -> Country:
        """Busca un país por nombre"""
        country_name_lower = country_name.lower()
        for country in self.countries.values():
            if country.name.lower() == country_name_lower:
                return country
        return None
        
    def classify_drug_type(self, drug_name: str) -> str:
        """Clasifica una droga por su tipo basado en las palabras clave"""
        drug_name_lower = drug_name.lower()
        for category, keywords in self.drug_keywords.items():
            if drug_name_lower in keywords:
                return category
        return "Sin clasificar"


if __name__ == "__main__":
    # Test del cargador de datos
    loader = DataLoader()
    loader.load_all_data()
    
    print("\n🔍 Pruebas:")
    print(f"- Argentina es país objetivo: {loader.is_target_country('Argentina')}")
    print(f"- Estados Unidos es país objetivo: {loader.is_target_country('Estados Unidos')}")
    print(f"- Total palabras clave drogas: {len(loader.get_all_drug_keywords())}")
    print(f"- Clasificación 'cocaína': {loader.classify_drug_type('cocaina')}")