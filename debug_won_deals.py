"""
Script para debugar negócios ganhos no último mês
"""

import pandas as pd
from agendor_client import AgendorClient
from datetime import datetime, timedelta

def main():
    print("=" * 80)
    print("DEBUG: Analisando negócios ganhos no último mês")
    print("=" * 80)
    
    # Conectar ao Agendor
    client = AgendorClient()
    
    if not client.test_connection():
        print("❌ Erro ao conectar com a API do Agendor")
        return
    
    print("✅ Conectado ao Agendor\n")
    
    # Buscar todos os deals
    deals = client.get_deals()
    print(f"📊 Total de negócios: {len(deals)}\n")
    
    # Filtrar último mês
    now = pd.Timestamp.now()
    date_limit = now - pd.Timedelta(days=30)
    
    print(f"📅 Data limite (último mês): {date_limit.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Data atual: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Filtrar deals do último mês
    filtered_deals = []
    for deal in deals:
        if deal.get('createdAt'):
            deal_date = pd.Timestamp(deal['createdAt'])
            # Remover timezone se existir
            if deal_date.tz is not None:
                deal_date = deal_date.tz_localize(None)
            
            if deal_date >= date_limit:
                filtered_deals.append(deal)
    
    print(f"📊 Negócios criados no último mês: {len(filtered_deals)}\n")
    
    # Analisar status
    print("=" * 80)
    print("ANÁLISE DETALHADA DE STATUS")
    print("=" * 80)
    
    status_count = {
        'ongoing': 0,
        'won': 0,
        'lost': 0,
        'unknown': 0
    }
    
    won_deals = []
    
    for deal in filtered_deals:
        status = deal.get('dealStatus', {})
        status_id = status.get('id') if isinstance(status, dict) else None
        status_name = status.get('name') if isinstance(status, dict) else None
        
        # Classificar
        if status_id == 1:
            status_count['ongoing'] += 1
        elif status_id == 2:
            status_count['won'] += 1
            won_deals.append(deal)
        elif status_id == 3:
            status_count['lost'] += 1
        else:
            status_count['unknown'] += 1
            print(f"⚠️  Status desconhecido: ID={status_id}, Nome={status_name}")
    
    print(f"\n📈 RESUMO DE STATUS:")
    print(f"  🔄 Em andamento (ID=1): {status_count['ongoing']}")
    print(f"  ✅ Ganhos (ID=2): {status_count['won']}")
    print(f"  ❌ Perdidos (ID=3): {status_count['lost']}")
    print(f"  ❓ Desconhecido: {status_count['unknown']}")
    
    # Mostrar detalhes dos negócios ganhos
    if won_deals:
        print("\n" + "=" * 80)
        print(f"DETALHES DOS {len(won_deals)} NEGÓCIOS GANHOS")
        print("=" * 80)
        
        for i, deal in enumerate(won_deals, 1):
            print(f"\n{i}. {deal.get('title', 'Sem título')}")
            print(f"   ID: {deal.get('id')}")
            print(f"   Criado em: {deal.get('createdAt')}")
            print(f"   Ganho em: {deal.get('wonAt', 'N/A')}")
            print(f"   Valor: R$ {deal.get('value', 0):,.2f}")
            
            status = deal.get('dealStatus', {})
            print(f"   Status ID: {status.get('id') if isinstance(status, dict) else 'N/A'}")
            print(f"   Status Nome: {status.get('name') if isinstance(status, dict) else 'N/A'}")
            
            owner = deal.get('owner', {})
            print(f"   Vendedor: {owner.get('name') if isinstance(owner, dict) else 'N/A'}")
    else:
        print("\n⚠️  Nenhum negócio ganho encontrado!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
