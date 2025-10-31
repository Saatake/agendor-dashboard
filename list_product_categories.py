"""
Lista todas as categorias de produtos cadastradas
"""

from agendor_client import AgendorClient
from collections import Counter

client = AgendorClient()

print("Buscando produtos...")
products = client.get_products()

# Extrair todas as categorias
categories = []
for prod in products:
    cat = prod.get('category')
    if cat:
        categories.append(cat)

print(f"\n✅ Total de produtos: {len(products)}")
print(f"✅ Produtos com categoria: {len(categories)}")
print(f"✅ Produtos sem categoria: {len(products) - len(categories)}")

print("\n" + "="*80)
print("CATEGORIAS ENCONTRADAS:")
print("="*80)

category_counts = Counter(categories)
for cat, count in category_counts.most_common():
    print(f"  - {cat:40} ({count} produtos)")

print("\n" + "="*80)
print("PRODUTOS POR CATEGORIA:")
print("="*80)

# Agrupar produtos por categoria
from collections import defaultdict
products_by_category = defaultdict(list)

for prod in products:
    cat = prod.get('category', 'Sem Categoria')
    products_by_category[cat].append(prod.get('name'))

for cat in sorted(products_by_category.keys()):
    print(f"\n📦 {cat}:")
    for prod_name in products_by_category[cat][:10]:  # Mostrar até 10
        print(f"    - {prod_name}")
    if len(products_by_category[cat]) > 10:
        print(f"    ... e mais {len(products_by_category[cat]) - 10} produtos")
