import os
import django
import csv

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'valoriza.settings')
django.setup()

from core.models import Enterprise, Industry, Sub_industry

def clean_text(text):
    """Limpia y normaliza el texto"""
    if not text or text == '' or text == 'nan':
        return None
    return str(text).strip()

def populate_database(max_rows=100):
    """Puebla la base de datos desde el CSV con modelo normalizado"""
    
    csv_file = 'valoriza_db_inicial.csv'
    
    # Contadores
    enterprises_created = 0
    industries_created = 0
    sub_industries_created = 0
    errors = 0
    processed_rows = 0
    
    # Caches para evitar consultas repetidas
    industries_cache = {}
    sub_industries_cache = {}
    
    print("Iniciando población de la base de datos...")
    print(f"Leyendo archivo: {csv_file}")
    print(f"Procesando solo las primeras {max_rows} filas\n")
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for idx, row in enumerate(reader, start=1):
            if processed_rows >= max_rows:
                print(f"\n⚠️  Límite de {max_rows} filas alcanzado. Deteniendo proceso...")
                break
            
            try:
                # Obtener datos básicos
                rut = clean_text(row.get('RUT'))
                dv = clean_text(row.get('DV'))
                razon_social = clean_text(row.get('RAZON_SOCIAL'))
                region = clean_text(row.get('REGION'))
                comuna = clean_text(row.get('COMUNA'))
                rubro_economico = clean_text(row.get('RUBRO_ECONOMICO'))
                subrubro_economico = clean_text(row.get('SUBRUBRO_ECONOMICO'))
                
                if not razon_social:
                    continue
                
                processed_rows += 1
                
                # 1. Crear o obtener INDUSTRIA (sin duplicados)
                industry = None
                if rubro_economico:
                    if rubro_economico not in industries_cache:
                        industry, created = Industry.objects.get_or_create(
                            name=rubro_economico,
                            defaults={
                                'description': f"Rubro: {rubro_economico}"
                            }
                        )
                        industries_cache[rubro_economico] = industry
                        if created:
                            industries_created += 1
                            if industries_created % 10 == 0:
                                print(f"✓ Industrias únicas creadas: {industries_created}")
                    else:
                        industry = industries_cache[rubro_economico]
                
                # 2. Crear o obtener SUB-INDUSTRIA (sin duplicados)
                sub_industry = None
                if industry and subrubro_economico:
                    sub_key = f"{rubro_economico}|{subrubro_economico}"
                    if sub_key not in sub_industries_cache:
                        sub_industry, created = Sub_industry.objects.get_or_create(
                            industry=industry,
                            name=subrubro_economico,
                            defaults={
                                'description': f"Subrubro: {subrubro_economico}"
                            }
                        )
                        sub_industries_cache[sub_key] = sub_industry
                        if created:
                            sub_industries_created += 1
                    else:
                        sub_industry = sub_industries_cache[sub_key]
                
                # 3. Crear EMPRESA con referencias a industria y sub-industria
                description_parts = []
                if region:
                    description_parts.append(f"Región: {region}")
                if comuna:
                    description_parts.append(f"Comuna: {comuna}")
                
                description = " | ".join(description_parts) if description_parts else "Empresa en Chile"
                
                # Usar RUT como identificador único
                enterprise_key = f"{rut}-{dv}" if rut and dv else razon_social
                
                enterprise, created = Enterprise.objects.get_or_create(
                    name=razon_social,
                    defaults={
                        'description': description,
                        'country': 'Chile',
                        'industry': industry,
                        'sub_industry': sub_industry,
                    }
                )
                
                # Si ya existía, actualizar las referencias de industria
                if not created:
                    enterprise.industry = industry
                    enterprise.sub_industry = sub_industry
                    enterprise.save()
                
                if created:
                    enterprises_created += 1
                    if enterprises_created % 25 == 0:
                        print(f"✓ Empresas creadas: {enterprises_created}")
                
            except Exception as e:
                errors += 1
                if errors <= 10:
                    print(f"❌ Error en fila {idx}: {str(e)}")
                continue
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE POBLACIÓN DE BASE DE DATOS")
    print("="*60)
    print(f"Filas procesadas: {processed_rows}/{max_rows}")
    print(f"\nDatos creados:")
    print(f"  • Industrias únicas: {industries_created}")
    print(f"  • Sub-industrias únicas: {sub_industries_created}")
    print(f"  • Empresas: {enterprises_created}")
    print(f"  • Errores: {errors}")
    
    print(f"\nTotales en BD:")
    print(f"  • Total industrias: {Industry.objects.count()}")
    print(f"  • Total sub-industrias: {Sub_industry.objects.count()}")
    print(f"  • Total empresas: {Enterprise.objects.count()}")
    
    # Estadísticas adicionales
    empresas_con_industria = Enterprise.objects.filter(industry__isnull=False).count()
    empresas_con_sub = Enterprise.objects.filter(sub_industry__isnull=False).count()
    
    print(f"\nCompletitud:")
    print(f"  • Empresas con industria: {empresas_con_industria} ({(empresas_con_industria/Enterprise.objects.count()*100):.1f}%)")
    print(f"  • Empresas con sub-industria: {empresas_con_sub} ({(empresas_con_sub/Enterprise.objects.count()*100):.1f}%)")
    print("="*60)

if __name__ == '__main__':
    # Cambiar max_rows según necesites
    populate_database(max_rows=100)
    print("\n¡Proceso completado!")