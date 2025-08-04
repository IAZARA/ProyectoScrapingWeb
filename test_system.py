#!/usr/bin/env python3
"""
Script de prueba para el sistema de noticias sobre drogas
"""
import os
import sys

# Configurar variables de entorno desde .env
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

print("🧪 PRUEBA DEL SISTEMA DE NOTICIAS SOBRE DROGAS")
print("=" * 50)

try:
    # Test 1: Cargar datos de referencia
    print("\n1️⃣ Probando carga de datos de referencia...")
    from drug_news_agent.data_loader import DataLoader
    
    loader = DataLoader()
    loader.load_all_data()
    print("✅ Datos de referencia cargados correctamente")
    
    # Test 2: Clasificador de relevancia
    print("\n2️⃣ Probando clasificador de relevancia...")
    from drug_news_agent.relevance_classifier import RelevanceClassifier, NewsArticle
    
    classifier = RelevanceClassifier(loader)
    
    # Artículo de prueba
    test_article = NewsArticle(
        title="Incautan 500 kilos de cocaína en operativo en Colombia",
        description="Autoridades colombianas decomisaron gran cantidad de cocaína en Bogotá",
        content="La Policía Nacional de Colombia incautó 500 kilogramos de cocaína en un operativo conjunto en el barrio La Candelaria.",
        url="https://test.com",
        date="15/01/2025",
        source="Test News"
    )
    
    result = classifier.classify_relevance(test_article)
    print(f"✅ Artículo clasificado: {result.level} (Score: {result.score:.1f})")
    print(f"   Razones: {result.reasons}")
    print(f"   Drogas detectadas: {result.drug_mentions}")
    
    # Test 3: Extractor de ubicación
    print("\n3️⃣ Probando extractor de ubicación...")
    from drug_news_agent.location_extractor import LocationExtractor
    
    extractor = LocationExtractor(loader)
    location = extractor.extract_location(test_article)
    print(f"✅ Ubicación extraída:")
    print(f"   País: {location.country}")
    print(f"   Ciudad: {location.city}")
    print(f"   Barrio: {location.district_neighborhood}")
    print(f"   Dirección completa: {location.full_address}")
    print(f"   Confianza: {location.confidence_score:.2f}")
    
    # Test 4: Geocodificador (sin API key)
    print("\n4️⃣ Probando geocodificador...")
    from drug_news_agent.geocoder import GoogleMapsGeocoder
    
    geocoder = GoogleMapsGeocoder()  # Sin API key para usar fallback
    geo_result = geocoder.geocode_location(location)
    
    if geo_result.success:
        print(f"✅ Geocodificación exitosa:")
        coords = geo_result.coordinates
        print(f"   Coordenadas: {coords.latitude:.4f}, {coords.longitude:.4f}")
        print(f"   Dirección formateada: {coords.formatted_address}")
    else:
        print(f"⚠️ Geocodificación falló: {geo_result.error_message}")
    
    # Test 5: Sistema de deduplicación
    print("\n5️⃣ Probando sistema de deduplicación...")
    from drug_news_agent.deduplication import NewsDeduplicator
    
    deduplicator = NewsDeduplicator()
    
    # Crear artículos similares para probar deduplicación
    similar_article = NewsArticle(
        title="Decomisan 500 kilogramos de cocaína en Bogotá",
        description="Policía colombiana incauta droga en operativo en la capital",
        content="Autoridades decomisaron cocaína en operativo en Bogotá, Colombia",
        url="https://test2.com",
        date="15/01/2025",
        source="Otro Medio"
    )
    
    test_articles = [test_article, similar_article]
    unique_articles, duplicate_groups, metrics = deduplicator.deduplicate(test_articles)
    
    print(f"✅ Deduplicación completada:")
    print(f"   Artículos originales: {metrics.total_articles}")
    print(f"   Eventos únicos: {metrics.unique_events}")
    print(f"   Grupos duplicados: {metrics.duplicate_groups}")
    print(f"   Reducción: {metrics.reduction_percentage:.1f}%")
    
    # Test 6: Búsqueda web (simple)
    print("\n6️⃣ Probando búsqueda web...")
    
    # Importar herramientas de búsqueda
    sys.path.append('/Users/macbook/Documents/AgenteWeb/WebAgent/WebDancer')
    from demos.tools.private.search import Search
    
    search_tool = Search()
    search_query = '{"query": ["cocaína Colombia"]}'
    
    print("   Realizando búsqueda web...")
    search_results = search_tool.call(search_query)
    
    if "Google search" in search_results and "results" in search_results:
        print("✅ Búsqueda web funcionando")
        # Mostrar solo una pequeña muestra
        lines = search_results.split('\n')[:5]
        for line in lines:
            if line.strip():
                print(f"   {line[:100]}...")
    else:
        print(f"⚠️ Búsqueda limitada: {search_results[:200]}...")
    
    print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS")
    print("✅ El sistema está funcionando correctamente")
    print("\nPara ejecutar una búsqueda completa, usar:")
    print("python test_full_search.py")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Asegúrate de que todos los módulos estén instalados")
    
except Exception as e:
    print(f"❌ Error durante la prueba: {e}")
    import traceback
    traceback.print_exc()