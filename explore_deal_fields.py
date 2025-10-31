"""
Script para explorar campos disponíveis nos deals do Agendor
"""

from agendor_client import AgendorClient
import json

client = AgendorClient()

print("Buscando deals...")
deals = client.get_deals()

if deals:
    print(f"\n✅ Total de deals: {len(deals)}")
    print("\n" + "="*80)
    print("ESTRUTURA COMPLETA DE UM DEAL:")
    print("="*80)
    
    # Pegar primeiro deal como exemplo
    sample_deal = deals[0]
    
    # Mostrar todos os campos
    print(json.dumps(sample_deal, indent=2, ensure_ascii=False))
    
    print("\n" + "="*80)
    print("CAMPOS DISPONÍVEIS:")
    print("="*80)
    for key in sample_deal.keys():
        value_type = type(sample_deal[key]).__name__
        print(f"  - {key:30} ({value_type})")
    
    # Verificar se tem campos customizados
    print("\n" + "="*80)
    print("CAMPOS CUSTOMIZADOS (customFields):")
    print("="*80)
    if 'customFields' in sample_deal:
        custom_fields = sample_deal.get('customFields', [])
        if custom_fields:
            for field in custom_fields:
                print(f"\n  Campo: {field.get('label', 'N/A')}")
                print(f"    - ID: {field.get('id')}")
                print(f"    - Tipo: {field.get('type')}")
                print(f"    - Valor: {field.get('value')}")
        else:
            print("  ⚠️ Nenhum campo customizado encontrado neste deal")
    else:
        print("  ⚠️ Campo 'customFields' não existe na estrutura")
    
    # Verificar se tem categorias/tags
    print("\n" + "="*80)
    print("CATEGORIAS/TAGS/PRODUTOS:")
    print("="*80)
    if 'products' in sample_deal:
        products = sample_deal.get('products', [])
        if products:
            print(f"  ✅ {len(products)} produtos encontrados")
            for prod in products[:3]:  # Mostrar até 3 produtos
                print(f"    - {prod}")
        else:
            print("  ⚠️ Nenhum produto associado")
    else:
        print("  ⚠️ Campo 'products' não existe")
    
    if 'categories' in sample_deal:
        categories = sample_deal.get('categories', [])
        print(f"  Categorias: {categories}")
    
    if 'tags' in sample_deal:
        tags = sample_deal.get('tags', [])
        print(f"  Tags: {tags}")
    
    # Verificar organização
    print("\n" + "="*80)
    print("INFORMAÇÕES DA ORGANIZAÇÃO (Cliente):")
    print("="*80)
    if 'organization' in sample_deal:
        org = sample_deal.get('organization', {})
        if isinstance(org, dict):
            print(json.dumps(org, indent=2, ensure_ascii=False))
        else:
            print(f"  {org}")
else:
    print("❌ Nenhum deal encontrado")
