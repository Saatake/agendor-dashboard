"""
Script para debugar negócios GANHOS em outubro (independente da data de criação)
"""

import pandas as pd
from agendor_client import AgendorClient
from datetime import datetime

def main():
    print("=" * 80)
    print("DEBUG: Analisando negócios GANHOS EM OUTUBRO")
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
    
    # Filtrar negócios ganhos EM outubro (wonAt em outubro)
    october_2025_start = pd.Timestamp('2025-10-01')
    october_2025_end = pd.Timestamp('2025-10-31 23:59:59')
    
    print(f"📅 Buscando negócios ganhos entre:")
    print(f"   Início: {october_2025_start}")
    print(f"   Fim: {october_2025_end}\n")
    
    won_in_october = []
    
    for deal in deals:
        # Verificar se tem wonAt
        if deal.get('wonAt'):
            won_date = pd.Timestamp(deal['wonAt'])
            # Remover timezone se existir
            if won_date.tz is not None:
                won_date = won_date.tz_localize(None)
            
            # Verificar se ganhou em outubro 2025
            if october_2025_start <= won_date <= october_2025_end:
                won_in_october.append(deal)
    
    print(f"✅ Encontrados: {len(won_in_october)} negócios ganhos em outubro\n")
    
    # Calcular totais
    total_value = sum(deal.get('value', 0) for deal in won_in_october)
    avg_ticket = total_value / len(won_in_october) if won_in_october else 0
    
    # Calcular ciclo médio
    cycle_times = []
    for deal in won_in_october:
        if deal.get('createdAt') and deal.get('wonAt'):
            created = pd.Timestamp(deal['createdAt'])
            won = pd.Timestamp(deal['wonAt'])
            if created.tz is not None:
                created = created.tz_localize(None)
            if won.tz is not None:
                won = won.tz_localize(None)
            cycle_days = (won - created).days
            cycle_times.append(cycle_days)
    
    avg_cycle = sum(cycle_times) / len(cycle_times) if cycle_times else 0
    
    print("=" * 80)
    print("RESUMO (comparar com Agendor)")
    print("=" * 80)
    print(f"Total de negócios ganhos: {len(won_in_october)}")
    print(f"Valor total: R$ {total_value:,.2f}")
    print(f"Ticket médio: R$ {avg_ticket:,.2f}")
    print(f"Ciclo médio de vendas: {avg_cycle:.0f} dias")
    print()
    
    # Mostrar detalhes de cada negócio
    print("=" * 80)
    print("DETALHES DOS NEGÓCIOS GANHOS EM OUTUBRO")
    print("=" * 80)
    
    for i, deal in enumerate(won_in_october, 1):
        created = pd.Timestamp(deal['createdAt']) if deal.get('createdAt') else None
        won = pd.Timestamp(deal['wonAt']) if deal.get('wonAt') else None
        
        if created and won:
            if created.tz is not None:
                created = created.tz_localize(None)
            if won.tz is not None:
                won = won.tz_localize(None)
            cycle = (won - created).days
        else:
            cycle = 0
        
        print(f"\n{i}. {deal.get('title', 'Sem título')}")
        print(f"   ID: {deal.get('id')}")
        print(f"   Criado em: {deal.get('createdAt')}")
        print(f"   Ganho em: {deal.get('wonAt')}")
        print(f"   Ciclo: {cycle} dias")
        print(f"   Valor: R$ {deal.get('value', 0):,.2f}")
        
        owner = deal.get('owner', {})
        print(f"   Vendedor: {owner.get('name') if isinstance(owner, dict) else 'N/A'}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
