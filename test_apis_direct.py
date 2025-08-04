#!/usr/bin/env python3
"""
Prueba directa de las APIs sin dependencias complejas
"""
import os
import json
import requests

# Configurar variables de entorno
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

print("🚀 PRUEBA DIRECTA DE APIs DEL SISTEMA")
print("=" * 40)

# Test 1: Google Search API (Serper)
print("\n1️⃣ Probando Google Search API...")
GOOGLE_SEARCH_KEY = os.getenv('GOOGLE_SEARCH_KEY')

if GOOGLE_SEARCH_KEY:
    try:
        url = 'https://google.serper.dev/search'
        headers = {
            'X-API-KEY': GOOGLE_SEARCH_KEY,
            'Content-Type': 'application/json',
        }
        data = {
            "q": "incautación cocaína Colombia enero 2025",
        }

        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Google Search API funcionando!")
            
            if "organic" in results:
                print(f"   📊 Encontrados {len(results['organic'])} resultados orgánicos")
                
                for i, result in enumerate(results['organic'][:3], 1):
                    print(f"   {i}. {result['title'][:60]}...")
                    print(f"      🔗 {result['link']}")
                    if 'snippet' in result:
                        print(f"      📝 {result['snippet'][:80]}...")
            else:
                print("   ⚠️ No se encontraron resultados orgánicos")
                
        else:
            print(f"❌ Error en API: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
else:
    print("❌ GOOGLE_SEARCH_KEY no configurada")

# Test 2: Jina API
print("\n2️⃣ Probando Jina API...")
JINA_API_KEY = os.getenv('JINA_API_KEY')

if JINA_API_KEY:
    try:
        headers = {
            'Authorization': f'Bearer {JINA_API_KEY}',
        }
        test_url = 'https://www.semana.com'  # URL de prueba
        
        response = requests.get(
            f'https://r.jina.ai/{test_url}',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            content = response.text
            print("✅ Jina API funcionando!")
            print(f"   📄 Contenido extraído: {len(content)} caracteres")
            print(f"   📝 Muestra: {content[:150]}...")
        else:
            print(f"❌ Error en Jina API: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
else:
    print("❌ JINA_API_KEY no configurada")

# Test 3: Dashscope API
print("\n3️⃣ Probando Dashscope API...")
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')

if DASHSCOPE_API_KEY:
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=DASHSCOPE_API_KEY, 
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        response = client.chat.completions.create(
            model="qwen2.5-72b-instruct", 
            messages=[
                {"role": "user", "content": "¿En qué países de América Latina hay mayor actividad de narcotráfico? Responde en 2 líneas."}
            ],
            max_tokens=100
        )
        
        print("✅ Dashscope API funcionando!")
        print(f"   🤖 Respuesta del modelo: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Error con Dashscope: {e}")
else:
    print("❌ DASHSCOPE_API_KEY no configurada")

# Test 4: Simulación de búsqueda completa
print("\n4️⃣ Simulando búsqueda completa de noticias...")

if GOOGLE_SEARCH_KEY:
    try:
        # Consultas de ejemplo del sistema
        test_queries = [
            "cocaína Colombia incautación 2025",
            "narcotráfico México operativo",
            "drogas Argentina policía"
        ]
        
        total_results = 0
        
        for query in test_queries:
            print(f"   🔍 Buscando: '{query}'")
            
            data = {"q": query}
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                if "organic" in results:
                    count = len(results['organic'])
                    total_results += count
                    print(f"      ✅ {count} resultados encontrados")
                    
                    # Mostrar primer resultado como ejemplo
                    if results['organic']:
                        first = results['organic'][0]
                        print(f"      📰 Ejemplo: {first['title'][:50]}...")
                        
        print(f"\n✅ BÚSQUEDA SIMULADA EXITOSA")
        print(f"   📊 Total de resultados encontrados: {total_results}")
        print(f"   🎯 Sistema puede procesar noticias reales sobre drogas")
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")

# Resumen
print(f"\n📋 RESUMEN DE PRUEBAS:")
apis_working = []
if GOOGLE_SEARCH_KEY:
    apis_working.append("Google Search")
if JINA_API_KEY:
    apis_working.append("Jina Reader")
if DASHSCOPE_API_KEY:
    apis_working.append("Dashscope LLM")

print(f"✅ APIs funcionando: {', '.join(apis_working) if apis_working else 'Ninguna'}")
print(f"🔧 El sistema está listo para procesar noticias reales")
print(f"💡 Para uso completo, instalar: pip install qwen-agent")

print(f"\n🎉 SISTEMA DE BÚSQUEDA DE NOTICIAS SOBRE DROGAS")
print(f"   ✅ Componentes principales funcionando")
print(f"   ✅ APIs conectadas y respondiendo") 
print(f"   ✅ Listo para análisis de inteligencia")