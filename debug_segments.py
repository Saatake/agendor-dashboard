"""
Debug: Ver quais clientes estão sendo classificados como "Outros"
"""

from agendor_client import AgendorClient
from analytics import AgendorAnalytics
import pandas as pd

client = AgendorClient()

print("Buscando dados...")
deals = client.get_deals()
users = client.get_users()
funnels = client.get_funnels()

analytics = AgendorAnalytics(deals, users, funnels)

# Pegar apenas negócios ganhos
won_deals = analytics.df_deals[analytics.df_deals['dealStatus'] == 'won'].copy()

if won_deals.empty:
    print("Sem negócios ganhos")
else:
    # Extrair nome da organização
    won_deals['customer_name'] = won_deals['organization'].apply(
        lambda x: x.get('name', '') if isinstance(x, dict) else ''
    )
    
    # Usar a mesma função de identificação
    def identify_segment(name):
        name_lower = str(name).lower()
        
        if any(word in name_lower for word in ['miner', 'mineração', 'mineracao', 'minera']):
            return 'Mineração'
        elif any(word in name_lower for word in ['constru', 'obras', 'engenharia']):
            return 'Construção/Engenharia'
        elif any(word in name_lower for word in ['cimento', 'concreto']):
            return 'Cimento/Concreto'
        elif any(word in name_lower for word in ['industria', 'indústria', 'fabrica', 'fábrica']):
            return 'Indústria'
        elif any(word in name_lower for word in ['energia', 'eletric', 'hidrel']):
            return 'Energia'
        elif any(word in name_lower for word in ['metal', 'siderur', 'aço', 'aco']):
            return 'Metalurgia/Siderurgia'
        elif any(word in name_lower for word in ['agricola', 'agrícola', 'agro']):
            return 'Agronegócio'
        elif any(word in name_lower for word in ['quimic', 'química']):
            return 'Química'
        elif any(word in name_lower for word in ['transport', 'logistic']):
            return 'Transporte/Logística'
        elif any(word in name_lower for word in ['prefeitura', 'governo', 'municipal']):
            return 'Setor Público'
        else:
            return 'Outros'
    
    won_deals['segmento'] = won_deals['customer_name'].apply(identify_segment)
    
    # Resumo por segmento
    print("\n" + "="*80)
    print("RESUMO POR SEGMENTO:")
    print("="*80)
    
    segment_summary = won_deals.groupby('segmento').agg({
        'value': ['sum', 'count'],
        'customer_name': 'nunique'
    })
    
    segment_summary.columns = ['Receita Total', 'Qtd Negócios', 'Qtd Clientes Únicos']
    segment_summary['Receita Total'] = segment_summary['Receita Total'].apply(lambda x: f"R$ {x:,.2f}")
    
    print(segment_summary.sort_values('Qtd Negócios', ascending=False))
    
    # Ver quais clientes estão em "Outros"
    print("\n" + "="*80)
    print("CLIENTES NO SEGMENTO 'OUTROS':")
    print("="*80)
    
    outros = won_deals[won_deals['segmento'] == 'Outros'].copy()
    
    if not outros.empty:
        # Agrupar por cliente
        outros_grouped = outros.groupby('customer_name').agg({
            'value': 'sum',
            'id': 'count'
        }).reset_index()
        
        outros_grouped.columns = ['Cliente', 'Receita Total', 'Qtd Negócios']
        outros_grouped = outros_grouped.sort_values('Receita Total', ascending=False)
        
        print(f"\nTotal de clientes em 'Outros': {len(outros_grouped)}")
        print(f"Total de negócios em 'Outros': {len(outros)}")
        print(f"Receita total em 'Outros': R$ {outros['value'].sum():,.2f}")
        
        print("\n📋 Top 20 clientes em 'Outros' (por receita):")
        for idx, row in outros_grouped.head(20).iterrows():
            print(f"  {row['Cliente']:60} | R$ {row['Receita Total']:>12,.2f} | {row['Qtd Negócios']:>3} negócios")
        
        # Analisar padrões nos nomes
        print("\n" + "="*80)
        print("ANÁLISE DE PADRÕES NOS NOMES (primeiras palavras):")
        print("="*80)
        
        # Extrair primeira palavra de cada nome
        outros_grouped['primeira_palavra'] = outros_grouped['Cliente'].str.split(' - ').str[0].str.split().str[0]
        
        palavra_counts = outros_grouped['primeira_palavra'].value_counts().head(15)
        print("\nPalavras mais comuns no início dos nomes:")
        for palavra, count in palavra_counts.items():
            print(f"  {palavra:30} - {count} clientes")
    else:
        print("Nenhum cliente no segmento 'Outros'")
