"""
Script de teste para validar conexão com API do Agendor
"""

from agendor_client import AgendorClient
from analytics import AgendorAnalytics

def test_connection():
    """Testa conexão com a API"""
    print("=" * 50)
    print("🔍 TESTE DE CONEXÃO - AGENDOR API")
    print("=" * 50)
    
    client = AgendorClient()
    
    print("\n1. Testando conexão...")
    if client.test_connection():
        print("   ✅ Conexão estabelecida com sucesso!")
    else:
        print("   ❌ Falha na conexão. Verifique o token.")
        return False
    
    print("\n2. Buscando usuários...")
    users = client.get_users()
    print(f"   ✅ {len(users)} usuários encontrados")
    
    print("\n3. Buscando funis...")
    funnels = client.get_funnels()
    print(f"   ✅ {len(funnels)} funis encontrados")
    if funnels:
        for funnel in funnels:
            print(f"      - {funnel.get('name', 'Sem nome')}")
    
    print("\n4. Buscando negócios...")
    deals = client.get_deals()
    print(f"   ✅ {len(deals)} negócios encontrados")
    
    if deals:
        ongoing = len([d for d in deals if d.get('dealStatus') == 'ongoing'])
        won = len([d for d in deals if d.get('dealStatus') == 'won'])
        lost = len([d for d in deals if d.get('dealStatus') == 'lost'])
        
        print(f"      - Em andamento: {ongoing}")
        print(f"      - Ganhos: {won}")
        print(f"      - Perdidos: {lost}")
    
    if deals and users and funnels:
        print("\n5. Testando análises...")
        analytics = AgendorAnalytics(deals, users, funnels)
        
        win_loss = analytics.calculate_win_loss_rate()
        print(f"   ✅ Taxa de vitória: {win_loss.get('taxa_vitoria', 0):.1f}%")
        
        revenue = analytics.calculate_revenue_forecast()
        print(f"   ✅ Receita confirmada: R$ {revenue.get('receita_confirmada', 0):,.2f}")
        print(f"   ✅ Receita potencial: R$ {revenue.get('receita_potencial', 0):,.2f}")
    
    print("\n" + "=" * 50)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 50)
    print("\nPara iniciar o dashboard, execute:")
    print("   streamlit run dashboard.py")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_connection()
