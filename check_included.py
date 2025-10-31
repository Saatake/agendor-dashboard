from agendor_client import AgendorClient

client = AgendorClient()
deals = client.get_deals()

# IDs dos negócios que o Agendor ESTÁ contando (baseado na combinação encontrada)
included_ids = [37108680, 37108685, 37108711, 33290083, 34766997, 36556576]

print("=" * 80)
print("NEGÓCIOS INCLUÍDOS NO RELATÓRIO DO AGENDOR (6 negócios)")
print("=" * 80)
print()

for deal_id in included_ids:
    for deal in deals:
        if deal.get('id') == deal_id:
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
            break
