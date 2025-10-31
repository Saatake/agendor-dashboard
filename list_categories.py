from agendor_client import AgendorClient
from collections import Counter

client = AgendorClient()
deals = client.get_deals()

print("=" * 80)
print("LISTANDO TODAS AS CATEGORIAS DE PRODUTOS (EQUIPES)")
print("=" * 80)

# Coletar todas as categorias
categories = []

for deal in deals:
    products = deal.get('products', [])
    for product in products:
        category = product.get('category')
        if category:
            categories.append(category)

# Contar ocorrências
category_count = Counter(categories)

print(f"\n📊 Total de categorias únicas: {len(category_count)}\n")

print("CATEGORIAS E QUANTIDADE DE PRODUTOS:")
print("-" * 80)

for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
    # Contar quantos negócios têm produtos desta categoria
    deals_with_category = 0
    for deal in deals:
        has_category = False
        for product in deal.get('products', []):
            if product.get('category') == category:
                has_category = True
                break
        if has_category:
            deals_with_category += 1
    
    print(f"  📌 {category}")
    print(f"     Produtos: {count} | Negócios: {deals_with_category}")
    print()

print("=" * 80)
