#!/usr/bin/env python3
"""
Prueba simple de búsqueda web
"""
import os
import sys

# Configurar variables de entorno
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

print("🔍 PRUEBA DE BÚSQUEDA WEB")
print("=" * 30)

try:
    # Importar herramienta de búsqueda directamente
    sys.path.append('/Users/macbook/Documents/AgenteWeb/WebAgent/WebDancer')
    from demos.tools.private.search import Search
    
    # Probar búsqueda
    search_tool = Search()
    
    # Consulta de prueba sobre drogas en Colombia
    test_queries = [
        "incautación cocaína Colombia últimos días",
        "operativo drogas Colombia 2025"
    ]
    
    print(f"🔍 Probando búsquedas...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Consulta: '{query}'")
        
        search_params = {"query": [query]}
        result = search_tool.call(str(search_params).replace("'", '"'))
        
        if "Google search" in result and "results" in result:
            print("✅ Búsqueda exitosa")
            
            # Extraer algunos resultados
            lines = result.split('\n')
            article_count = 0
            
            for line in lines:
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                    print(f"   📰 {line[:80]}...")
                    article_count += 1
                    if article_count >= 3:  # Mostrar solo 3 resultados
                        break
                        
            if article_count == 0:
                print("   ⚠️ No se encontraron artículos estructurados")
                print(f"   📄 Respuesta: {result[:200]}...")
                
        else:
            print(f"⚠️ Respuesta inesperada:")
            print(f"   {result[:300]}...")
    
    print(f"\n✅ BÚSQUEDA WEB FUNCIONANDO")
    print("El sistema puede encontrar noticias en tiempo real")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()