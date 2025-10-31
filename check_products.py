from agendor_client import AgendorClient

client = AgendorClient()
deals = client.get_deals()

included_ids = [37108680, 37108685, 37108711, 33290083, 34766997, 36556576]
excluded_ids = [35941469, 34841211]

print("=" * 80)
print("VERIFICANDO CAMPO 'products' EM TODOS OS NEGÓCIOS")
print("=" * 80)

print("\n📊 NEGÓCIOS INCLUÍDOS (6):")
print("-" * 80)
for deal in deals:
    if deal.get('id') in included_ids:
        products = deal.get('products', [])
        product_names = [p.get('name') for p in products] if products else []
        print(f"\nID {deal.get('id')}: {deal.get('title')}")
        print(f"  Tem produtos? {len(products) > 0}")
        print(f"  Produtos: {product_names if product_names else 'VAZIO'}")

print("\n\n❌ NEGÓCIOS EXCLUÍDOS (2):")
print("-" * 80)
for deal in deals:
    if deal.get('id') in excluded_ids:
        products = deal.get('products', [])
        product_names = [p.get('name') for p in products] if products else []
        print(f"\nID {deal.get('id')}: {deal.get('title')}")
        print(f"  Tem produtos? {len(products) > 0}")
        print(f"  Produtos: {product_names if product_names else 'VAZIO'}")

print("\n" + "=" * 80)
print("CONCLUSÃO:")
print("=" * 80)
print("Se todos os incluídos têm produtos e todos os excluídos não têm,")
print("então o filtro do Agendor pode estar exigindo produtos associados!")
