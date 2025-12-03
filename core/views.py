from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from core.models import Enterprise, Industry, Sub_industry
from django.views.decorators.csrf import ensure_csrf_cookie
import ollama
import logging
import os
import re
from django.db import connection
import json

logger = logging.getLogger(__name__)

# Configure Ollama client
ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
client = ollama.Client(host=ollama_host)

@ensure_csrf_cookie
def home(request):
    """Página principal con tarjetas de navegación"""
    return render(request, 'core/home.html')

@ensure_csrf_cookie
def chat_page(request):
    """Página del chat AI"""
    return render(request, 'core/chat.html')

def enterprises_page(request):
    """Renderiza la página HTML de empresas en tabla"""
    return render(request, 'core/enterprises.html')

def enterprise_detail(request, enterprise_id):
    """Renderiza la página de detalle de una empresa específica"""
    enterprise = get_object_or_404(
        Enterprise.objects.select_related('industry', 'sub_industry'),
        id=enterprise_id
    )
    return render(request, 'core/enterprise_detail.html', {
        'enterprise': enterprise
    })

def industries_page(request):
    """Renderiza la página HTML de industrias"""
    return render(request, 'core/industries.html')


def get_database_context():
    """Obtiene el contexto actual de la base de datos para el LLM"""
    try:
        # Obtener las industrias más comunes
        top_industries = Industry.objects.all()[:20]
        industries_list = [f"'{ind.name}'" for ind in top_industries]
        
        context = f"""
## INDUSTRIAS REALES EN LA BASE DE DATOS (usar estos nombres exactos):
{', '.join(industries_list) if industries_list else 'Sin industrias aún'}

Ejemplos de industrias comunes:
- 'AGRICULTURA, GANADERIA, SILVICULTURA Y PESCA'
- 'COMERCIO AL POR MAYOR Y AL POR MENOR; REPARACION DE VEHICULOS AUTOMOTORES Y MOTOCICLETAS'
- 'INDUSTRIA MANUFACTURERA'
- 'TRANSPORTE Y ALMACENAMIENTO'
- 'ACTIVIDADES PROFESIONALES, CIENTIFICAS Y TECNICAS'
- 'CONSTRUCCION'

IMPORTANTE: Los nombres están en MAYÚSCULAS y con acentos. Usa LIKE '%palabra%' para búsquedas.
"""
        return context
    except Exception as e:
        logger.error(f"Error getting database context: {str(e)}")
        return ""


def chat_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        
        logger.info(f"Received message: {user_message}")
        
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        try:
            logger.info("Attempting to connect to Ollama...")
            
            # Obtener contexto dinámico de la BD
            db_context = get_database_context()
            
            response = client.chat(
                model='llama3.2',
                messages=[
                    {
                        'role': 'system',
                        'content': f'''Eres un asistente experto en SQL para bases de datos de empresas chilenas.

IMPORTANTE: Solo responde con SQL puro cuando el usuario pida datos. NO expliques, NO des instrucciones.

## Estructura de la Base de Datos:

### core_industry (Industrias)
- id: INTEGER (Primary Key)
- name: VARCHAR(255) UNIQUE (EN MAYÚSCULAS, con acentos y caracteres especiales)
- description: TEXT
- created_at, updated_at: DATETIME

### core_sub_industry (Sub-industrias)  
- id: INTEGER (Primary Key)
- industry_id: INTEGER (Foreign Key → core_industry.id)
- name: VARCHAR(255)
- description: TEXT
- created_at, updated_at: DATETIME

### core_enterprise (Empresas)
- id: INTEGER (Primary Key)
- name: VARCHAR(255)
- description: TEXT
- country: VARCHAR(100) DEFAULT 'Chile'
- website: VARCHAR(200)
- industry_id: INTEGER (Foreign Key → core_industry.id)
- sub_industry_id: INTEGER (Foreign Key → core_sub_industry.id)
- created_at, updated_at: DATETIME

### core_contact (Contactos)
- id: INTEGER (Primary Key)
- enterprise_id: INTEGER (Foreign Key → core_enterprise.id)
- name, email, phone, position, linkedin_profile: VARCHAR
- age: INTEGER
- contacted: BOOLEAN
- created_at, updated_at: DATETIME

{db_context}

## REGLAS CRÍTICAS:
1. Si la pregunta requiere datos, responde SOLO con: SQL{{tu consulta aquí}}
2. NO agregues explicaciones antes o después del SQL
3. SIEMPRE usa LEFT JOIN para relaciones (nunca INNER JOIN)
4. SIEMPRE incluye LIMIT (máximo 100)
5. Para búsquedas de texto USA: LIKE '%PALABRA%' (en mayúsculas)
6. Los nombres de industrias están en MAYÚSCULAS con acentos (Á, É, Í, Ó, Ú, Ñ)
7. NO inventes nombres de industrias, usa LIKE para buscar

## Ejemplos CORRECTOS:

Usuario: "muestra 10 empresas"
Tú: SQL{{SELECT id, name, country, description FROM core_enterprise LIMIT 10}}

Usuario: "empresas con su industria"  
Tú: SQL{{SELECT e.name as empresa, i.name as industria FROM core_enterprise e LEFT JOIN core_industry i ON e.industry_id = i.id LIMIT 20}}

Usuario: "cuántas empresas hay"
Tú: SQL{{SELECT COUNT(*) as total FROM core_enterprise}}

Usuario: "industrias con más empresas"
Tú: SQL{{SELECT i.name as industria, COUNT(e.id) as total FROM core_industry i LEFT JOIN core_enterprise e ON i.id = e.industry_id GROUP BY i.id, i.name ORDER BY total DESC LIMIT 20}}

Usuario: "empresas de agricultura"
Tú: SQL{{SELECT e.name as empresa, i.name as industria FROM core_enterprise e JOIN core_industry i ON e.industry_id = i.id WHERE i.name LIKE '%AGRICULTURA%' LIMIT 30}}

Usuario: "empresas del sector comercio"
Tú: SQL{{SELECT e.name, e.description, i.name as industria FROM core_enterprise e JOIN core_industry i ON e.industry_id = i.id WHERE i.name LIKE '%COMERCIO%' LIMIT 20}}

Usuario: "empresas de transporte"
Tú: SQL{{SELECT e.name, i.name as industria FROM core_enterprise e JOIN core_industry i ON e.industry_id = i.id WHERE i.name LIKE '%TRANSPORTE%' LIMIT 25}}

Usuario: "sub-industrias de manufactura"
Tú: SQL{{SELECT s.name as sub_industria, i.name as industria FROM core_sub_industry s JOIN core_industry i ON s.industry_id = i.id WHERE i.name LIKE '%MANUFACTUR%' LIMIT 30}}

Usuario: "lista todas las industrias"
Tú: SQL{{SELECT id, name FROM core_industry ORDER BY name LIMIT 50}}

Si la pregunta NO requiere consultar la BD (como "hola", "gracias", "ayuda"), responde conversacionalmente.'''
                    },
                    {
                        'role': 'user',
                        'content': user_message,
                    },
                ]
            )
            
            logger.info(f"Response received from Ollama: {response}")
            
            assistant_message = response['message']['content'].strip()
            
            # Detectar si la respuesta contiene SQL
            if 'SQL{' in assistant_message or 'sql{' in assistant_message.lower():
                sql_match = re.search(r'SQL\{(.+?)\}', assistant_message, re.DOTALL | re.IGNORECASE)
                if sql_match:
                    sql_query = sql_match.group(1).strip()
                    
                    logger.info(f"Extracted SQL query: {sql_query}")
                    
                    # Ejecutar la consulta
                    sql_result = execute_safe_sql(sql_query)
                    
                    if sql_result.get('success'):
                        # Generar respuesta en texto para el chat
                        formatted_results = format_sql_results(sql_result['results'])
                        
                        return JsonResponse({
                            'response': formatted_results,
                            'sql_query': sql_query,
                            'results': sql_result['results'],
                            'count': sql_result['count'],
                            'type': 'sql'
                        })
                    else:
                        return JsonResponse({
                            'response': f"❌ Error al ejecutar la consulta: {sql_result['error']}",
                            'sql_query': sql_query,
                            'type': 'sql_error'
                        })
            
            # Si no hay SQL, es una respuesta conversacional
            return JsonResponse({
                'response': assistant_message,
                'type': 'text'
            })
            
        except ollama.ResponseError as e:
            logger.error(f"Ollama ResponseError: {str(e)}")
            return JsonResponse({'error': f'Ollama error: {str(e)}'}, status=500)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def industries(request):
    """API JSON que retorna industrias únicas con conteo de empresas"""
    from django.db.models import Count
    
    industries = Industry.objects.annotate(
        empresa_count=Count('enterprises')
    ).order_by('name')
    
    industries_data = []
    for industry in industries:
        industries_data.append({
            'id': industry.id,
            'name': industry.name,
            'description': industry.description,
            'empresa_count': industry.empresa_count,
            'created_at': industry.created_at.isoformat(),
            'updated_at': industry.updated_at.isoformat(),
        })
    
    return JsonResponse({
        'count': len(industries_data),
        'industries': industries_data
    })


def enterprises(request):
    """API JSON que retorna todas las empresas con sus industrias"""
    enterprises_list = Enterprise.objects.select_related('industry', 'sub_industry').all()
    
    enterprises_data = []
    for enterprise in enterprises_list:
        enterprises_data.append({
            'id': enterprise.id,
            'name': enterprise.name,
            'description': enterprise.description,
            'country': enterprise.country,
            'website': enterprise.website,
            'industry': enterprise.industry.name if enterprise.industry else None,
            'industry_id': enterprise.industry.id if enterprise.industry else None,
            'sub_industry': enterprise.sub_industry.name if enterprise.sub_industry else None,
            'sub_industry_id': enterprise.sub_industry.id if enterprise.sub_industry else None,
            'created_at': enterprise.created_at.isoformat(),
            'updated_at': enterprise.updated_at.isoformat(),
        })
    
    return JsonResponse({
        'count': len(enterprises_data),
        'enterprises': enterprises_data
    })


def format_sql_results(results):
    """Formatea los resultados SQL en un texto legible para el chat"""
    if not results:
        return "❌ No se encontraron resultados."
    
    # Si es un COUNT o agregación simple
    if len(results) == 1 and len(results[0]) == 1:
        key = list(results[0].keys())[0]
        value = results[0][key]
        if 'count' in key.lower() or 'total' in key.lower():
            return f"📊 **{key.replace('_', ' ').title()}:** {value}"
    
    # Para resultados múltiples, mostrar resumen
    return f"✅ **Consulta exitosa:** Se encontraron {len(results)} registro(s). Los datos se muestran en la tabla →"


def execute_safe_sql(sql_query):
    """Ejecuta una consulta SQL de solo lectura de forma segura"""
    try:
        # Limpiar la consulta
        sql_query = sql_query.strip()
        
        # Validar que sea SELECT
        if not sql_query.upper().startswith('SELECT'):
            return {
                'success': False,
                'error': 'Solo se permiten consultas SELECT'
            }
        
        # Palabras clave peligrosas
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        query_upper = sql_query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return {
                    'success': False,
                    'error': f'Palabra clave no permitida: {keyword}'
                }
        
        # Ejecutar consulta
        with connection.cursor() as cursor:
            logger.info(f"Executing SQL: {sql_query}")
            cursor.execute(sql_query)
            
            # Obtener columnas y resultados
            columns = [col[0] for col in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
            
        logger.info(f"Query returned {len(results)} rows")
            
        return {
            'success': True,
            'results': results,
            'count': len(results)
        }
        
    except Exception as e:
        logger.error(f"SQL Error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }