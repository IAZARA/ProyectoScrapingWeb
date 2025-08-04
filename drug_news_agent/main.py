#!/usr/bin/env python3
"""
Script principal del Agente de Búsqueda Inteligente de Noticias sobre Drogas.
Punto de entrada principal para ejecutar búsquedas completas.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Agregar el path del proyecto
sys.path.append(str(Path(__file__).parent.parent))

from intelligent_search_agent import IntelligentDrugNewsAgent
from csv_exporter import CentroRegionalCSVExporter


def main():
    """Función principal del sistema"""
    
    print("🚀 AGENTE DE BÚSQUEDA INTELIGENTE DE NOTICIAS SOBRE DROGAS")
    print("=" * 60)
    print("Sistema de análisis de noticias para América Latina y Caribe")
    print("Desarrollado para Centro Regional de Inteligencia")
    print("=" * 60)
    
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description='Agente de búsqueda inteligente de noticias sobre drogas'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Días hacia atrás para buscar noticias (default: 7)'
    )
    
    parser.add_argument(
        '--max-articles',
        type=int,
        default=20,
        help='Máximo artículos por consulta (default: 20)'
    )
    
    parser.add_argument(
        '--min-relevance',
        choices=['Alta', 'Media', 'Baja'],
        default='Media',
        help='Relevancia mínima de artículos (default: Media)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./output',
        help='Directorio de salida (default: ./output)'
    )
    
    parser.add_argument(
        '--google-maps-key',
        type=str,
        help='API Key de Google Maps para geocodificación precisa'
    )
    
    parser.add_argument(
        '--quick-test',
        action='store_true',
        help='Ejecutar búsqueda rápida de prueba'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostrar información detallada del proceso'
    )
    
    args = parser.parse_args()
    
    # Configurar parámetros según el modo
    if args.quick_test:
        print("🧪 MODO PRUEBA RÁPIDA")
        args.days = 3
        args.max_articles = 5
        args.min_relevance = 'Baja'
        
    # Crear directorio de salida
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"\\n📋 CONFIGURACIÓN:")
    print(f"• Período de búsqueda: Últimos {args.days} días")
    print(f"• Máximo artículos por consulta: {args.max_articles}")
    print(f"• Relevancia mínima: {args.min_relevance}")
    print(f"• Directorio de salida: {output_dir.absolute()}")
    print(f"• Google Maps API: {'✅ Configurada' if args.google_maps_key else '❌ No configurada (usando coordenadas aproximadas)'}")
    
    try:
        # Inicializar el agente
        print(f"\\n🔧 Inicializando sistema...")
        agent = IntelligentDrugNewsAgent(google_maps_api_key=args.google_maps_key)
        
        # Realizar búsqueda
        print(f"\\n🔍 Ejecutando búsqueda inteligente...")
        results = agent.search_drug_news(
            days_back=args.days,
            max_articles_per_query=args.max_articles,
            min_relevance=args.min_relevance
        )
        
        # Mostrar resumen de resultados
        print_results_summary(results, args.verbose)
        
        # Exportar resultados
        print(f"\\n💾 Exportando resultados...")
        exporter = CentroRegionalCSVExporter()
        
        csv_file = exporter.export_to_csv(results, str(output_dir))
        report_file = exporter.export_summary_report(results, str(output_dir))
        
        print(f"\\n✅ PROCESO COMPLETADO EXITOSAMENTE")
        print(f"📁 Archivos generados:")
        print(f"   • CSV: {csv_file}")
        print(f"   • Reporte: {report_file}")
        
        # Mostrar estadísticas finales
        print_final_statistics(results)
        
    except KeyboardInterrupt:
        print(f"\\n⚠️ Proceso interrumpido por el usuario")
        sys.exit(1)
        
    except Exception as e:
        print(f"\\n❌ ERROR: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def print_results_summary(results, verbose=False):
    """Imprime resumen de resultados"""
    
    print(f"\\n📊 RESULTADOS DE LA BÚSQUEDA:")
    print(f"-" * 40)
    
    metrics = results.search_metrics
    print(f"• Consultas realizadas: {metrics['total_queries']}")
    print(f"• Artículos encontrados: {metrics['raw_articles_found']}")
    print(f"• Artículos de países objetivo: {metrics['target_country_articles']}")
    print(f"• Artículos relevantes: {metrics['relevant_articles']}")
    print(f"• Eventos únicos identificados: {metrics['unique_events']}")
    print(f"• Grupos de duplicados: {metrics['duplicate_groups']}")
    print(f"• Artículos geocodificados: {metrics['geocoded_articles']}")
    print(f"• Tiempo de procesamiento: {metrics['processing_time_seconds']:.1f}s")
    
    if verbose and results.processed_news:
        print(f"\\n📰 MUESTRA DE ARTÍCULOS PROCESADOS:")
        print(f"-" * 40)
        
        for i, news in enumerate(results.processed_news[:3]):
            print(f"\\n{i+1}. {news.article.title}")
            print(f"   • Relevancia: {news.relevance.level} ({news.relevance.score:.1f})")
            print(f"   • País: {news.location_info.country}")
            print(f"   • Ubicación: {news.location_info.full_address}")
            print(f"   • Drogas mencionadas: {', '.join(news.relevance.drug_mentions[:3])}")
            
            if news.geocoding_result.success:
                coords = news.geocoding_result.coordinates
                print(f"   • Coordenadas: {coords.latitude:.4f}, {coords.longitude:.4f}")


def print_final_statistics(results):
    """Imprime estadísticas finales"""
    
    print(f"\\n🎯 ESTADÍSTICAS FINALES:")
    print(f"-" * 30)
    
    # Contar por relevancia
    relevance_counts = {'Alta': 0, 'Media': 0, 'Baja': 0}
    country_counts = {}
    drug_counts = {}
    
    for news in results.processed_news:
        relevance_counts[news.relevance.level] += 1
        
        country = news.location_info.country or "Sin especificar"
        country_counts[country] = country_counts.get(country, 0) + 1
        
        for drug in news.relevance.drug_mentions:
            drug_counts[drug] = drug_counts.get(drug, 0) + 1
    
    print(f"\\n📈 Por relevancia:")
    for level, count in relevance_counts.items():
        percentage = (count / len(results.processed_news)) * 100 if results.processed_news else 0
        print(f"   • {level}: {count} ({percentage:.1f}%)")
    
    print(f"\\n🌎 Top países:")
    sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    for country, count in sorted_countries[:5]:
        print(f"   • {country}: {count} artículos")
    
    if drug_counts:
        print(f"\\n💊 Drogas más mencionadas:")
        sorted_drugs = sorted(drug_counts.items(), key=lambda x: x[1], reverse=True)
        for drug, count in sorted_drugs[:5]:
            print(f"   • {drug}: {count} menciones")
    
    # Efectividad del sistema
    if results.search_metrics['raw_articles_found'] > 0:
        efficiency = (len(results.processed_news) / results.search_metrics['raw_articles_found']) * 100
        print(f"\\n⚡ Eficiencia del filtrado: {efficiency:.1f}%")
        print(f"   ({len(results.processed_news)} artículos útiles de {results.search_metrics['raw_articles_found']} encontrados)")


def check_environment():
    """Verifica el entorno y dependencias"""
    
    required_files = [
        "/Users/macbook/Documents/WebSearchAgent/AnalisisArchivo/paises.csv",
        "/Users/macbook/Documents/WebSearchAgent/AnalisisArchivo/drogas palabras clave.csv",
        "/Users/macbook/Documents/WebSearchAgent/AnalisisArchivo/relevancia.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ ARCHIVOS DE REFERENCIA FALTANTES:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        print("\\nPor favor, asegúrate de que los archivos CSV de referencia estén disponibles.")
        return False
    
    # Verificar APIs
    google_search_key = os.getenv('GOOGLE_SEARCH_KEY')
    jina_api_key = os.getenv('JINA_API_KEY')
    dashscope_key = os.getenv('DASHSCOPE_API_KEY')
    
    if not all([google_search_key, jina_api_key, dashscope_key]):
        print("⚠️ ADVERTENCIA: Algunas API keys no están configuradas:")
        if not google_search_key:
            print("   • GOOGLE_SEARCH_KEY no encontrada")
        if not jina_api_key:
            print("   • JINA_API_KEY no encontrada") 
        if not dashscope_key:
            print("   • DASHSCOPE_API_KEY no encontrada")
        print("\\nEl sistema puede funcionar con funcionalidad limitada.")
    
    return True


if __name__ == "__main__":
    # Verificar entorno antes de ejecutar
    if not check_environment():
        sys.exit(1)
    
    # Ejecutar sistema principal
    main()