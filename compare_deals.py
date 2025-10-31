from agendor_client import AgendorClient
import json

client = AgendorClient()
deals = client.get_deals()

# IDs incluídos e excluídos
included_ids = [37108680, 37108685, 37108711, 33290083, 34766997, 36556576]
excluded_ids = [35941469, 34841211]

print("=" * 80)
print("COMPARANDO CAMPOS DOS NEGÓCIOS")
print("=" * 80)

# Pegar 1 incluído e 1 excluído para comparar estrutura
included_sample = None
excluded_sample = None

for deal in deals:
    if deal.get('id') == included_ids[0]:
        included_sample = deal
    if deal.get('id') == excluded_ids[0]:
        excluded_sample = deal

if included_sample and excluded_sample:
    # Comparar campos principais
    print("\n" + "=" * 80)
    print("DIFERENÇAS NOS CAMPOS:")
    print("=" * 80)
    
    all_keys = set(included_sample.keys()) | set(excluded_sample.keys())
    
    for key in sorted(all_keys):
        inc_val = included_sample.get(key, "N/A")
        exc_val = excluded_sample.get(key, "N/A")
        
        # Não mostrar campos obvios que são diferentes
        if key in ['id', 'title', 'value', 'createdAt', 'wonAt', 'updatedAt']:
            continue
        
        if str(inc_val) != str(exc_val):
            print(f"\n{key}:")
            print(f"  Incluído: {inc_val}")
            print(f"  Excluído: {exc_val}")
    
    # Verificar campos customizados
    print("\n" + "=" * 80)
    print("CAMPOS CUSTOMIZADOS:")
    print("=" * 80)
    
    if 'customFields' in included_sample:
        print("\nIncluído (37108680):")
        print(json.dumps(included_sample.get('customFields'), indent=2, ensure_ascii=False))
    
    if 'customFields' in excluded_sample:
        print("\nExcluído (35941469):")
        print(json.dumps(excluded_sample.get('customFields'), indent=2, ensure_ascii=False))
