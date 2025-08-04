"""
Sistema de deduplicación de noticias para identificar eventos repetidos.
Utiliza múltiples criterios para detectar noticias que reportan el mismo incidente.
"""
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher
from .relevance_classifier import NewsArticle


@dataclass
class DuplicateGroup:
    """Grupo de noticias duplicadas"""
    primary_article: NewsArticle
    duplicates: List[NewsArticle]
    similarity_score: float
    common_elements: List[str]


@dataclass
class DeduplicationMetrics:
    """Métricas del proceso de deduplicación"""
    total_articles: int
    unique_events: int
    duplicate_groups: int
    reduction_percentage: float


class NewsDeduplicator:
    """Sistema de deduplicación de noticias sobre drogas"""
    
    def __init__(self):
        self.similarity_threshold = 0.75  # Umbral de similitud para considerar duplicados
        self.date_window_days = 3  # Ventana de días para considerar el mismo evento
        
    def deduplicate(self, articles: List[NewsArticle]) -> Tuple[List[NewsArticle], List[DuplicateGroup], DeduplicationMetrics]:
        """
        Deduplica una lista de artículos de noticias
        Retorna: (artículos únicos, grupos duplicados, métricas)
        """
        if not articles:
            return [], [], DeduplicationMetrics(0, 0, 0, 0.0)
            
        # Crear hashes de similitud para cada artículo
        article_hashes = {}
        for i, article in enumerate(articles):
            article_hash = self._create_similarity_hash(article)
            article_hashes[i] = article_hash
            
        # Encontrar grupos de similitud
        duplicate_groups = []
        processed_indices = set()
        unique_articles = []
        
        for i, article in enumerate(articles):
            if i in processed_indices:
                continue
                
            # Buscar artículos similares
            similar_articles = []
            
            for j, other_article in enumerate(articles):
                if i != j and j not in processed_indices:
                    similarity = self._calculate_similarity(article, other_article)
                    
                    if similarity > self.similarity_threshold:
                        similar_articles.append((j, other_article, similarity))
                        
            if similar_articles:
                # Crear grupo de duplicados
                primary_article = article
                duplicates = [item[1] for item in similar_articles]
                avg_similarity = sum(item[2] for item in similar_articles) / len(similar_articles)
                common_elements = self._find_common_elements(article, duplicates)
                
                duplicate_group = DuplicateGroup(
                    primary_article=primary_article,
                    duplicates=duplicates,
                    similarity_score=avg_similarity,
                    common_elements=common_elements
                )
                
                duplicate_groups.append(duplicate_group)
                unique_articles.append(primary_article)
                
                # Marcar como procesados
                processed_indices.add(i)
                for item in similar_articles:
                    processed_indices.add(item[0])
            else:
                # Artículo único
                unique_articles.append(article)
                processed_indices.add(i)
                
        # Calcular métricas
        metrics = DeduplicationMetrics(
            total_articles=len(articles),
            unique_events=len(unique_articles),
            duplicate_groups=len(duplicate_groups),
            reduction_percentage=((len(articles) - len(unique_articles)) / len(articles)) * 100
        )
        
        return unique_articles, duplicate_groups, metrics
        
    def _create_similarity_hash(self, article: NewsArticle) -> str:
        """Crea un hash de similitud basado en elementos clave"""
        # Extraer elementos clave
        location = self._extract_location(article)
        drug_types = self._extract_drug_types(article)
        quantities = self._extract_quantities(article)
        date_str = article.date
        
        # Crear hash combinado
        hash_elements = [
            location.lower(),
            '|'.join(sorted(drug_types)),
            '|'.join(sorted(quantities)),
            date_str
        ]
        
        combined_string = '#'.join(hash_elements)
        return hashlib.md5(combined_string.encode()).hexdigest()
        
    def _calculate_similarity(self, article1: NewsArticle, article2: NewsArticle) -> float:
        """Calcula la similitud entre dos artículos"""
        score = 0.0
        factors = 0
        
        # 1. Similitud de títulos (peso alto)
        title_similarity = SequenceMatcher(None, article1.title.lower(), article2.title.lower()).ratio()
        score += title_similarity * 0.4
        factors += 0.4
        
        # 2. Similitud de fechas
        date_similarity = self._calculate_date_similarity(article1.date, article2.date)
        score += date_similarity * 0.2
        factors += 0.2
        
        # 3. Similitud de ubicación
        location_similarity = self._calculate_location_similarity(article1, article2)
        score += location_similarity * 0.3
        factors += 0.3
        
        # 4. Similitud de contenido de drogas
        drug_similarity = self._calculate_drug_similarity(article1, article2)
        score += drug_similarity * 0.1
        factors += 0.1
        
        return score / factors if factors > 0 else 0.0
        
    def _calculate_date_similarity(self, date1: str, date2: str) -> float:
        """Calcula similitud basada en fechas"""
        try:
            # Convertir fechas (asumiendo formato DD/MM/YYYY)
            d1 = datetime.strptime(date1, "%d/%m/%Y")
            d2 = datetime.strptime(date2, "%d/%m/%Y")
            
            # Calcular diferencia en días
            diff_days = abs((d1 - d2).days)
            
            # Si están dentro de la ventana de tiempo, alta similitud
            if diff_days <= self.date_window_days:
                return 1.0 - (diff_days / self.date_window_days)
            else:
                return 0.0
                
        except ValueError:
            # Si no se puede parsear las fechas, similitud baja
            return 0.0
            
    def _calculate_location_similarity(self, article1: NewsArticle, article2: NewsArticle) -> float:
        """Calcula similitud basada en ubicación"""
        loc1 = self._extract_location(article1).lower()
        loc2 = self._extract_location(article2).lower()
        
        if not loc1 or not loc2:
            return 0.0
            
        # Similitud directa de strings
        string_similarity = SequenceMatcher(None, loc1, loc2).ratio()
        
        # Verificar si una ubicación contiene a la otra
        if loc1 in loc2 or loc2 in loc1:
            return max(string_similarity, 0.8)
            
        return string_similarity
        
    def _calculate_drug_similarity(self, article1: NewsArticle, article2: NewsArticle) -> float:
        """Calcula similitud basada en tipos de drogas mencionadas"""
        drugs1 = set(self._extract_drug_types(article1))
        drugs2 = set(self._extract_drug_types(article2))
        
        if not drugs1 or not drugs2:
            return 0.0
            
        # Similitud de Jaccard
        intersection = len(drugs1.intersection(drugs2))
        union = len(drugs1.union(drugs2))
        
        return intersection / union if union > 0 else 0.0
        
    def _extract_location(self, article: NewsArticle) -> str:
        """Extrae información de ubicación del artículo"""
        full_text = f"{article.title} {article.description}".lower()
        
        # Patrones de ubicación comunes
        location_patterns = [
            r'en\s+([a-záéíóúñü\s]+(?:,\s*[a-záéíóúñü\s]+)*)',
            r'de\s+([a-záéíóúñü\s]+(?:,\s*[a-záéíóúñü\s]+)*)',
            r'([a-záéíóúñü\s]+),\s*([a-záéíóúñü\s]+)',
        ]
        
        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            locations.extend(matches)
            
        # Retornar la ubicación más específica encontrada
        if locations:
            return max(locations, key=len) if isinstance(locations[0], str) else locations[0][0]
        
        return ""
        
    def _extract_drug_types(self, article: NewsArticle) -> List[str]:
        """Extrae tipos de drogas mencionadas"""
        full_text = f"{article.title} {article.description}".lower()
        
        # Lista básica de drogas comunes
        drug_keywords = [
            'cocaína', 'cocaina', 'marihuana', 'heroína', 'heroina',
            'fentanilo', 'metanfetamina', 'anfetamina', 'lsd', 'mdma',
            'extasis', 'tusi', 'ketamina', 'cristal', 'crack'
        ]
        
        found_drugs = []
        for drug in drug_keywords:
            if drug in full_text:
                found_drugs.append(drug)
                
        return found_drugs
        
    def _extract_quantities(self, article: NewsArticle) -> List[str]:
        """Extrae cantidades mencionadas"""
        full_text = f"{article.title} {article.description}".lower()
        
        # Patrones de cantidades
        quantity_patterns = [
            r'(\d+)\s*kilos?',
            r'(\d+)\s*kilogramos?',
            r'(\d+)\s*gramos?',
            r'(\d+)\s*toneladas?',
            r'(\d+)\s*libras?'
        ]
        
        quantities = []
        for pattern in quantity_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            quantities.extend(matches)
            
        return quantities
        
    def _find_common_elements(self, primary: NewsArticle, duplicates: List[NewsArticle]) -> List[str]:
        """Encuentra elementos comunes entre artículos duplicados"""
        common_elements = []
        
        # Ubicación común
        primary_location = self._extract_location(primary)
        if primary_location:
            common_elements.append(f"Ubicación: {primary_location}")
            
        # Drogas comunes
        primary_drugs = set(self._extract_drug_types(primary))
        for duplicate in duplicates:
            duplicate_drugs = set(self._extract_drug_types(duplicate))
            common_drugs = primary_drugs.intersection(duplicate_drugs)
            if common_drugs:
                common_elements.append(f"Drogas: {', '.join(common_drugs)}")
                break
                
        # Fecha común
        common_elements.append(f"Período: {primary.date}")
        
        return list(set(common_elements))  # Eliminar duplicados


if __name__ == "__main__":
    # Test del deduplicador
    deduplicator = NewsDeduplicator()
    
    # Artículos de prueba (simulando duplicados)
    test_articles = [
        NewsArticle(
            title="Incautan 100 kilos de cocaína en Bogotá",
            description="Autoridades incautaron droga en operativo",
            content="",
            url="https://test1.com",
            date="15/01/2025",
            source="Medio 1"
        ),
        NewsArticle(
            title="Decomisan 100 kilogramos de cocaína en Bogotá",
            description="Policía decomisa droga en la capital",
            content="",
            url="https://test2.com",
            date="15/01/2025",
            source="Medio 2"
        ),
        NewsArticle(
            title="Capturan narcos con marihuana en Medellín",
            description="Diferentes operativo en Antioquia",
            content="",
            url="https://test3.com",
            date="16/01/2025",
            source="Medio 3"
        )
    ]
    
    unique_articles, duplicate_groups, metrics = deduplicator.deduplicate(test_articles)
    
    print(f"Artículos originales: {metrics.total_articles}")
    print(f"Eventos únicos: {metrics.unique_events}")
    print(f"Grupos duplicados: {metrics.duplicate_groups}")
    print(f"Reducción: {metrics.reduction_percentage:.1f}%")