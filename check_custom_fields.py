"""
Verifica se algum deal tem campos customizados ou produtos
"""

from agendor_client import AgendorClient
import json

client = AgendorClient()

print("Buscando deals...")
deals = client.get_deals()

# Contar quantos têm customFields
deals_with_custom = 0
deals_with_products = 0
custom_field_examples = []
product_examples = []

for deal in deals[:500]:  # Verificar primeiros 500
    if 'customFields' in deal and deal['customFields']:
        deals_with_custom += 1
        if len(custom_field_examples) < 3:
            custom_field_examples.append({
                'deal_id': deal['id'],
                'title': deal.get('title'),
                'customFields': deal['customFields']
            })
    
    if 'products' in deal and deal['products']:
        deals_with_products += 1
        if len(product_examples) < 3:
            product_examples.append({
                'deal_id': deal['id'],
                'title': deal.get('title'),
                'products': deal['products']
            })

print(f"\n📊 Análise de {min(500, len(deals))} deals:")
print(f"  - Deals com customFields: {deals_with_custom}")
print(f"  - Deals com products: {deals_with_products}")

if custom_field_examples:
    print("\n" + "="*80)
    print("EXEMPLOS DE CUSTOM FIELDS:")
    print("="*80)
    for example in custom_field_examples:
        print(f"\nDeal: {example['title']} (ID: {example['deal_id']})")
        print(json.dumps(example['customFields'], indent=2, ensure_ascii=False))

if product_examples:
    print("\n" + "="*80)
    print("EXEMPLOS DE PRODUTOS:")
    print("="*80)
    for example in product_examples:
        print(f"\nDeal: {example['title']} (ID: {example['deal_id']})")
        print(json.dumps(example['products'], indent=2, ensure_ascii=False))

# Buscar também informações sobre produtos disponíveis
print("\n" + "="*80)
print("PRODUTOS CADASTRADOS NO AGENDOR:")
print("="*80)
products = client.get_products()
print(f"Total de produtos cadastrados: {len(products)}")
if products:
    print("\nPrimeiros 10 produtos:")
    for prod in products[:10]:
        print(f"  - {prod.get('name')} (ID: {prod.get('id')})")
        if 'category' in prod:
            print(f"    Categoria: {prod.get('category')}")
        if 'customFields' in prod:
            print(f"    CustomFields: {prod.get('customFields')}")
