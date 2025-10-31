from agendor_client import AgendorClient

client = AgendorClient()
deals = client.get_deals()

# IDs dos negócios excluídos
excluded_ids = [35941469, 34841211]

print("=" * 80)
print("NEGÓCIOS EXCLUÍDOS DO RELATÓRIO DO AGENDOR")
print("=" * 80)
print()

for deal in deals:
    if deal.get('id') in excluded_ids:
        print(f"ID: {deal.get('id')}")
        print(f"Título: {deal.get('title')}")
        print(f"Valor: R$ {deal.get('value', 0):,.2f}")
        print(f"Criado em: {deal.get('createdAt')}")
        print(f"Ganho em: {deal.get('wonAt')}")
        
        dealStage = deal.get('dealStage', {})
        if isinstance(dealStage, dict):
            funnel = dealStage.get('funnel', {})
            print(f"Funil: {funnel.get('name') if isinstance(funnel, dict) else 'N/A'}")
            print(f"Etapa: {dealStage.get('name', 'N/A')}")
        
        owner = deal.get('owner', {})
        print(f"Vendedor: {owner.get('name') if isinstance(owner, dict) else 'N/A'}")
        print()
