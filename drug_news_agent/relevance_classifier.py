"""
Clasificador de relevancia de noticias basado en criterios específicos.
Clasifica noticias en Alta, Media o Baja relevancia según aparición de palabras clave.
"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from .data_loader import DataLoader


@dataclass
class NewsArticle:
    """Estructura de datos para artículos de noticias"""
    title: str
    description: str
    content: str
    url: str
    date: str
    source: str
    country: str = ""
    

@dataclass
class RelevanceScore:
    """Puntuación de relevancia de una noticia"""
    level: str  # Alta, Media, Baja
    score: float  # 0-100
    reasons: List[str]
    drug_mentions: List[str]
    location_matches: List[str]


class RelevanceClassifier:
    """Clasificador de relevancia para noticias sobre drogas"""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.drug_keywords = data_loader.get_all_drug_keywords()
        
        # Palabras clave de alta prioridad (operaciones grandes)
        self.high_priority_keywords = [
            'incautación masiva', 'operación internacional', 'cartel', 'narcotráfico',
            'laboratorio clandestino', 'ruta internacional', 'operativo conjunto',
            'red criminal', 'organización criminal', 'banda criminal',
            'toneladas', 'kilos', 'millones de dólares'
        ]
        
        # Palabras clave de contexto operativo
        self.operational_keywords = [
            'detención', 'captura', 'arresto', 'incautación', 'decomiso',
            'operativo', 'allanamiento', 'investigación', 'policía',
            'autoridades', 'fuerza pública', 'antinarcóticos'
        ]
        
    def classify_relevance(self, article: NewsArticle) -> RelevanceScore:
        """Clasifica la relevancia de una noticia"""
        score = 0
        reasons = []
        drug_mentions = []
        location_matches = []
        
        # Texto completo para análisis
        full_text = f"{article.title} {article.description} {article.content}".lower()
        
        # 1. Verificar menciones de drogas (peso base)
        drug_score, found_drugs = self._analyze_drug_mentions(full_text)
        score += drug_score
        drug_mentions = found_drugs
        
        if found_drugs:
            reasons.append(f"Menciona drogas: {', '.join(found_drugs[:3])}")
        
        # 2. Análisis de ubicación en título vs contenido
        title_score = self._analyze_title_relevance(article.title.lower())
        score += title_score
        
        if title_score > 0:
            reasons.append("Palabras clave en título")
            
        # 3. Verificar país objetivo
        country_score, country_found = self._analyze_country_relevance(full_text)
        score += country_score
        
        if country_found:
            location_matches.append(country_found)
            reasons.append(f"País objetivo: {country_found}")
            
        # 4. Contexto operativo
        operational_score = self._analyze_operational_context(full_text)
        score += operational_score
        
        if operational_score > 0:
            reasons.append("Contexto operativo detectado")
            
        # 5. Palabras de alta prioridad
        priority_score = self._analyze_high_priority(full_text)
        score += priority_score
        
        if priority_score > 0:
            reasons.append("Operación de alta prioridad")
            
        # 6. Análisis de cantidad/impacto
        impact_score = self._analyze_impact_indicators(full_text)
        score += impact_score
        
        if impact_score > 0:
            reasons.append("Alto impacto detectado")
            
        # Determinar nivel de relevancia
        if score >= 70:
            level = "Alta"
        elif score >= 40:
            level = "Media"
        else:
            level = "Baja"
            
        return RelevanceScore(
            level=level,
            score=score,
            reasons=reasons,
            drug_mentions=drug_mentions,
            location_matches=location_matches
        )
        
    def _analyze_drug_mentions(self, text: str) -> Tuple[float, List[str]]:
        """Analiza menciones de drogas en el texto"""
        score = 0
        found_drugs = []
        
        for drug in self.drug_keywords:
            if drug in text:
                found_drugs.append(drug)
                score += 15  # Cada droga mencionada suma puntos
                
        # Bonus por múltiples drogas
        if len(found_drugs) > 2:
            score += 10
            
        return min(score, 30), found_drugs[:5]  # Máximo 30 puntos
        
    def _analyze_title_relevance(self, title: str) -> float:
        """Analiza relevancia basada en el título"""
        score = 0
        
        # Palabras clave en título tienen mayor peso
        for drug in self.drug_keywords:
            if drug in title:
                score += 20
                
        for keyword in self.operational_keywords:
            if keyword in title:
                score += 15
                
        return min(score, 40)  # Máximo 40 puntos
        
    def _analyze_country_relevance(self, text: str) -> Tuple[float, str]:
        """Verifica si menciona países objetivo"""
        for country_code, country in self.data_loader.countries.items():
            country_names = [
                country.name.lower(),
                country_code.lower(),
                country.code_alpha3.lower()
            ]
            
            for name in country_names:
                if name in text:
                    return 20, country.name
                    
        return 0, ""
        
    def _analyze_operational_context(self, text: str) -> float:
        """Analiza contexto operativo"""
        score = 0
        
        for keyword in self.operational_keywords:
            if keyword in text:
                score += 5
                
        return min(score, 25)  # Máximo 25 puntos
        
    def _analyze_high_priority(self, text: str) -> float:
        """Analiza indicadores de alta prioridad"""
        score = 0
        
        for keyword in self.high_priority_keywords:
            if keyword in text:
                score += 15
                
        return min(score, 30)  # Máximo 30 puntos
        
    def _analyze_impact_indicators(self, text: str) -> float:
        """Analiza indicadores de impacto (cantidades, valores)"""
        score = 0
        
        # Patrones de cantidades grandes
        quantity_patterns = [
            r'\d+\s*toneladas?',
            r'\d+\s*kilos?',
            r'\d+\s*kilogramos?',
            r'\$\s*\d+\s*millones?',
            r'\d+\s*millones?\s*de\s*dólares',
        ]
        
        for pattern in quantity_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 10
                
        return min(score, 20)  # Máximo 20 puntos
        
    def batch_classify(self, articles: List[NewsArticle]) -> List[Tuple[NewsArticle, RelevanceScore]]:
        """Clasifica múltiples artículos"""
        results = []
        
        for article in articles:
            relevance = self.classify_relevance(article)
            results.append((article, relevance))
            
        # Ordenar por relevancia (mayor score primero)
        results.sort(key=lambda x: x[1].score, reverse=True)
        
        return results


if __name__ == "__main__":
    # Test del clasificador
    from .data_loader import DataLoader
    
    loader = DataLoader()
    loader.load_all_data()
    
    classifier = RelevanceClassifier(loader)
    
    # Artículo de prueba
    test_article = NewsArticle(
        title="Incautan 500 kilos de cocaína en operativo en Colombia",
        description="Autoridades colombianas decomisaron gran cantidad de cocaína",
        content="La Policía Nacional de Colombia incautó 500 kilogramos de cocaína en un operativo conjunto. La droga estaba oculta en un camión.",
        url="https://test.com",
        date="2025-01-15",
        source="Test News"
    )
    
    result = classifier.classify_relevance(test_article)
    print(f"Relevancia: {result.level} (Score: {result.score})")
    print(f"Razones: {result.reasons}")
    print(f"Drogas mencionadas: {result.drug_mentions}")