"""
Dashboard Gerencial Interativo - Agendor CRM
Métricas avançadas e análises que não estão disponíveis diretamente no Agendor
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import sys

from config import DASHBOARD_TITLE, PAGE_ICON, LAYOUT
from agendor_client import AgendorClient
from analytics import AgendorAnalytics
from auth import require_auth, logout


# Configuração da página
st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Sistema de autenticação
require_auth()

# CSS customizado
st.markdown("""
    <style>
    .main-metric {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data():
    """Carrega dados da API do Agendor"""
    client = AgendorClient()
    
    with st.spinner('🔄 Conectando ao Agendor...'):
        # Testar conexão
        if not client.test_connection():
            st.error("❌ Erro ao conectar com a API do Agendor. Verifique o token.")
            return None, None, None
        
        # Buscar dados
        deals = client.get_deals()
        users = client.get_users()
        funnels = client.get_funnels()
    
    return deals, users, funnels


def render_header():
    """Renderiza cabeçalho do dashboard"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title(f"{PAGE_ICON} {DASHBOARD_TITLE}")
        st.markdown("### Análises Gerenciais Avançadas")
    
    with col2:
        st.markdown(f"**Última atualização:**")
        st.markdown(f"_{datetime.now().strftime('%d/%m/%Y %H:%M')}_")


def render_kpis(analytics: AgendorAnalytics):
    """Renderiza KPIs principais"""
    st.markdown("---")
    st.subheader("📊 Indicadores Principais")
    
    # Calcular métricas
    win_loss = analytics.calculate_win_loss_rate()
    revenue = analytics.calculate_revenue_forecast()
    time_to_close = analytics.calculate_average_time_to_close()
    growth = analytics.calculate_growth_trend()
    
    # Linha 1: Métricas de conversão
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Taxa de Vitória",
            value=f"{win_loss.get('taxa_vitoria', 0):.1f}%",
            delta=f"{win_loss.get('ganhos', 0)} ganhos"
        )
    
    with col2:
        st.metric(
            label="Taxa de Perda",
            value=f"{win_loss.get('taxa_perda', 0):.1f}%",
            delta=f"{win_loss.get('perdidos', 0)} perdidos",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Tempo Médio p/ Fechar",
            value=f"{time_to_close.get('tempo_medio_dias', 0):.0f} dias",
            delta=f"Ganhos: {time_to_close.get('tempo_medio_ganhos', 0):.0f}d"
        )
    
    with col4:
        st.metric(
            label="Crescimento (30 dias)",
            value=f"{growth.get('crescimento_percentual', 0):.1f}%",
            delta=f"R$ {growth.get('receita_ultimos_30_dias', 0):,.2f}"
        )
    
    # Linha 2: Métricas de receita
    st.markdown("###")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Receita Confirmada",
            value=f"R$ {revenue.get('receita_confirmada', 0):,.2f}"
        )
    
    with col2:
        st.metric(
            label="Receita Potencial",
            value=f"R$ {revenue.get('receita_potencial', 0):,.2f}",
            delta=f"{revenue.get('total_negocios_abertos', 0)} abertos"
        )
    
    with col3:
        st.metric(
            label="Receita Ponderada",
            value=f"R$ {revenue.get('receita_ponderada', 0):,.2f}",
            help="Receita ajustada pela probabilidade de fechamento"
        )
    
    with col4:
        lost_analysis = analytics.analyze_lost_deals()
        st.metric(
            label="Valor Perdido",
            value=f"R$ {lost_analysis.get('valor_perdido', 0):,.2f}",
            delta=f"{lost_analysis.get('total_perdidos', 0)} negócios",
            delta_color="inverse"
        )


def render_estimates(analytics: AgendorAnalytics):
    """Renderiza estimativas e previsões"""
    st.markdown("---")
    st.subheader("🎯 Estimativas de Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Quantas Propostas para R$ 100 mil?")
        
        # Permitir customização da meta
        custom_target = st.number_input(
            "Defina sua meta de receita (R$):",
            min_value=1000,
            max_value=10000000,
            value=100000,
            step=10000,
            key="revenue_target"
        )
        
        estimates = analytics.calculate_proposals_for_target(custom_target)
        
        if estimates:
            st.markdown("---")
            
            # Métrica principal
            st.metric(
                label=f"Propostas Necessárias para R$ {custom_target:,.0f}",
                value=f"{estimates['propostas_necessarias']:.0f} propostas",
                help="Baseado no ticket médio e taxa de conversão histórica"
            )
            
            st.markdown("---")
            
            # Detalhamento
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric(
                    label="Ticket Médio",
                    value=f"R$ {estimates['ticket_medio']:,.2f}"
                )
                st.metric(
                    label="Taxa de Conversão",
                    value=f"{estimates['taxa_conversao']:.1f}%"
                )
            
            with col_b:
                st.metric(
                    label="Receita Esperada/Proposta",
                    value=f"R$ {estimates['receita_esperada_por_proposta']:,.2f}",
                    help="Ticket médio × Taxa de conversão"
                )
                
                # Cálculo de quantas propostas por mês
                if estimates['propostas_necessarias'] > 0:
                    propostas_mes = estimates['propostas_necessarias'] / 12
                    st.metric(
                        label="Propostas/Mês (anual)",
                        value=f"{propostas_mes:.0f}"
                    )
            
            # Explicação
            st.info(f"""
            **Interpretação:** Para atingir R$ {custom_target:,.0f}, você precisa de aproximadamente 
            **{estimates['propostas_necessarias']:.0f} propostas**, considerando:
            - Ticket médio de R$ {estimates['ticket_medio']:,.2f}
            - Taxa de conversão de {estimates['taxa_conversao']:.1f}%
            """)
    
    with col2:
        st.markdown("### 🚶 Quantas Visitas para Fechar?")
        
        visits_data = analytics.calculate_visits_to_close()
        
        if visits_data and visits_data.get('estimativa_visitas', 0) > 0:
            st.markdown("---")
            
            # Métrica principal
            st.metric(
                label="Visitas Médias por Venda",
                value=f"{visits_data['estimativa_visitas']} visitas",
                help="Estimativa baseada no tempo médio de ciclo e recorrência de clientes"
            )
            
            st.markdown("---")
            
            # Detalhamento
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric(
                    label="Ciclo de Venda",
                    value=f"{visits_data['tempo_medio_dias']:.0f} dias"
                )
            
            with col_b:
                st.metric(
                    label="Recorrência Média",
                    value=f"{visits_data['recorrencia_media']:.1f}x",
                    help="Negócios por cliente em média"
                )
            
            # Gráfico visual de estimativa
            st.markdown("---")
            
            # Criar visualização do ciclo
            visit_icons = "👤 " * visits_data['estimativa_visitas']
            st.markdown(f"**Ciclo típico de venda:** {visit_icons}")
            
            st.info(f"""
            **Interpretação:** {visits_data['interpretacao']}
            
            Isso significa aproximadamente **1 visita a cada {visits_data['tempo_medio_dias'] / visits_data['estimativa_visitas']:.0f} dias**.
            """)
        else:
            st.warning("Dados insuficientes para calcular estimativa de visitas")


def render_top_customers(analytics: AgendorAnalytics):
    """Renderiza análise dos 5 maiores clientes"""
    st.markdown("---")
    st.subheader("🏆 Top 5 Maiores Clientes")
    
    top_customers = analytics.calculate_top_customers(5)
    
    if top_customers.empty:
        st.info("Sem dados de clientes disponíveis")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de barras horizontal
        fig = go.Figure(go.Bar(
            x=top_customers['receita_total'],
            y=top_customers['cliente'],
            orientation='h',
            text=[f"R$ {v:,.2f}" for v in top_customers['receita_total']],
            textposition='auto',
            marker=dict(
                color=top_customers['receita_total'],
                colorscale='Blues',
                showscale=False
            ),
            hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<br>%{customdata}% do total<extra></extra>',
            customdata=top_customers['percentual']
        ))
        
        fig.update_layout(
            title='Receita por Cliente',
            xaxis_title='Receita (R$)',
            yaxis_title='',
            height=400,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**💰 Participação na Receita**")
        
        # Gráfico de pizza
        fig_pie = go.Figure(go.Pie(
            labels=top_customers['cliente'],
            values=top_customers['percentual'],
            hole=0.4,
            textinfo='percent',
            hovertemplate='<b>%{label}</b><br>%{percent}<br>R$ %{customdata:,.2f}<extra></extra>',
            customdata=top_customers['receita_total']
        ))
        
        fig_pie.update_layout(
            title='% do Total',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Tabela detalhada
    st.markdown("### 📋 Detalhamento")
    
    display_df = top_customers.copy()
    display_df['receita_total'] = display_df['receita_total'].apply(lambda x: f"R$ {x:,.2f}")
    display_df['percentual'] = display_df['percentual'].apply(lambda x: f"{x:.2f}%")
    display_df.columns = ['Cliente', 'Receita Total', 'Qtd Negócios', '% do Total']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_top_segments(analytics: AgendorAnalytics):
    """Renderiza análise dos 5 maiores segmentos"""
    st.markdown("---")
    st.subheader("🎯 Top 5 Maiores Segmentos")
    
    top_segments = analytics.calculate_top_segments(5)
    
    if top_segments.empty:
        st.info("Sem dados de segmentos disponíveis")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de barras
        fig = go.Figure(go.Bar(
            x=top_segments['segmento'],
            y=top_segments['receita_total'],
            text=[f"R$ {v:,.0f}" for v in top_segments['receita_total']],
            textposition='auto',
            marker=dict(
                color=top_segments['receita_total'],
                colorscale='Greens',
                showscale=False
            ),
            hovertemplate='<b>%{x}</b><br>Receita: R$ %{y:,.2f}<br>%{customdata}% do total<extra></extra>',
            customdata=top_segments['percentual']
        ))
        
        fig.update_layout(
            title='Receita por Segmento',
            xaxis_title='',
            yaxis_title='Receita (R$)',
            height=400,
            xaxis={'categoryorder': 'total descending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**📊 Distribuição de Segmentos**")
        
        # Métricas dos top 3
        for idx, row in top_segments.head(3).iterrows():
            st.metric(
                label=row['segmento'],
                value=f"{row['percentual']:.1f}%",
                delta=f"R$ {row['receita_total']:,.0f}"
            )
        
        # Somatório dos top 5
        total_top5_percent = top_segments['percentual'].sum()
        st.markdown("---")
        st.metric(
            label="Top 5 Representam",
            value=f"{total_top5_percent:.1f}%",
            delta="do total de receita"
        )
    
    # Tabela detalhada
    st.markdown("### 📋 Detalhamento por Segmento")
    
    display_df = top_segments.copy()
    display_df['receita_total'] = display_df['receita_total'].apply(lambda x: f"R$ {x:,.2f}")
    display_df['percentual'] = display_df['percentual'].apply(lambda x: f"{x:.2f}%")
    display_df.columns = ['Segmento', 'Receita Total', 'Qtd Negócios', '% do Total']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_conversion_funnel(analytics: AgendorAnalytics):
    """Renderiza análise de funil de conversão"""
    st.markdown("---")
    st.subheader("🎯 Análise de Conversão por Etapa")
    
    conversion_df = analytics.calculate_conversion_rates()
    
    if conversion_df.empty:
        st.info("Sem dados de conversão disponíveis")
        return
    
    # Seletor de funil
    funnels = conversion_df['funil'].unique()
    selected_funnel = st.selectbox("Selecione o funil:", funnels)
    
    funnel_data = conversion_df[conversion_df['funil'] == selected_funnel]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de funil
        fig = go.Figure(go.Funnel(
            y=funnel_data['etapa'],
            x=funnel_data['quantidade'],
            textinfo="value+percent initial",
            marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        ))
        
        fig.update_layout(
            title=f"Funil de Conversão - {selected_funnel}",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Taxas de Conversão**")
        for _, row in funnel_data.iterrows():
            st.metric(
                label=row['etapa'],
                value=f"{row['taxa_conversao']:.1f}%",
                delta=f"{row['quantidade']} negócios"
            )


def render_seller_performance(analytics: AgendorAnalytics):
    """Renderiza performance de vendedores"""
    st.markdown("---")
    st.subheader("👥 Performance por Vendedor")
    
    seller_df = analytics.calculate_seller_performance()
    
    if seller_df.empty:
        st.info("Sem dados de vendedores disponíveis")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de valor total por vendedor
        fig = px.bar(
            seller_df.head(10),
            x='vendedor',
            y='valor_total',
            title='Top 10 Vendedores - Receita Total',
            labels={'valor_total': 'Receita (R$)', 'vendedor': 'Vendedor'},
            color='valor_total',
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de taxa de vitória
        fig = px.bar(
            seller_df.sort_values('taxa_vitoria', ascending=False).head(10),
            x='vendedor',
            y='taxa_vitoria',
            title='Top 10 Vendedores - Taxa de Vitória',
            labels={'taxa_vitoria': 'Taxa de Vitória (%)', 'vendedor': 'Vendedor'},
            color='taxa_vitoria',
            color_continuous_scale='Greens'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.markdown("### 📋 Detalhamento por Vendedor")
    
    # Formatar valores
    display_df = seller_df.copy()
    display_df['valor_total'] = display_df['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
    display_df['ticket_medio'] = display_df['ticket_medio'].apply(lambda x: f"R$ {x:,.2f}")
    display_df['taxa_vitoria'] = display_df['taxa_vitoria'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


def render_revenue_analysis(analytics: AgendorAnalytics):
    """Renderiza análise de receita"""
    st.markdown("---")
    st.subheader("💰 Análise de Receita")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Receita mensal
        revenue_monthly = analytics.calculate_revenue_by_period('M')
        
        if not revenue_monthly.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=revenue_monthly['periodo'],
                y=revenue_monthly['receita'],
                name='Receita',
                marker_color='#1f77b4'
            ))
            
            fig.add_trace(go.Scatter(
                x=revenue_monthly['periodo'],
                y=revenue_monthly['receita'],
                name='Tendência',
                mode='lines',
                line=dict(color='red', dash='dash')
            ))
            
            fig.update_layout(
                title='Evolução de Receita Mensal',
                xaxis_title='Período',
                yaxis_title='Receita (R$)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados de receita por período")
    
    with col2:
        # Comparativo de crescimento
        growth = analytics.calculate_growth_trend()
        
        if growth:
            categories = ['Últimos 30 dias', '30 dias anteriores']
            values = [
                growth.get('receita_ultimos_30_dias', 0),
                growth.get('receita_30_dias_anteriores', 0)
            ]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=values,
                    marker_color=['#2ca02c', '#ff7f0e'],
                    text=[f"R$ {v:,.2f}" for v in values],
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title='Comparativo de Receita (30 dias)',
                yaxis_title='Receita (R$)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)


def render_time_analysis(analytics: AgendorAnalytics):
    """Renderiza análise de tempo"""
    st.markdown("---")
    st.subheader("⏱️ Análise de Tempo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tempo médio para fechar
        time_data = analytics.calculate_average_time_to_close()
        
        if time_data:
            categories = ['Ganhos', 'Perdidos', 'Média Geral']
            values = [
                time_data.get('tempo_medio_ganhos', 0),
                time_data.get('tempo_medio_perdidos', 0),
                time_data.get('tempo_medio_dias', 0)
            ]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=values,
                    marker_color=['#2ca02c', '#d62728', '#1f77b4'],
                    text=[f"{v:.0f} dias" for v in values],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title='Tempo Médio para Fechamento',
                yaxis_title='Dias',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Tempo por etapa
        stage_time = analytics.calculate_time_in_stage()
        
        if not stage_time.empty:
            fig = px.bar(
                stage_time.head(10),
                x='etapa',
                y='tempo_medio_dias',
                color='funil',
                title='Tempo Médio por Etapa (Negócios Ativos)',
                labels={'tempo_medio_dias': 'Dias', 'etapa': 'Etapa'},
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados de tempo por etapa")


def render_loss_analysis(analytics: AgendorAnalytics):
    """Renderiza análise de perdas"""
    st.markdown("---")
    st.subheader("❌ Análise de Perdas")
    
    lost_data = analytics.analyze_lost_deals()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total de Negócios Perdidos",
            value=lost_data.get('total_perdidos', 0)
        )
    
    with col2:
        st.metric(
            label="Valor Total Perdido",
            value=f"R$ {lost_data.get('valor_perdido', 0):,.2f}"
        )
    
    with col3:
        st.metric(
            label="Ticket Médio Perdido",
            value=f"R$ {lost_data.get('ticket_medio_perdido', 0):,.2f}"
        )
    
    with col4:
        st.metric(
            label="Etapa Mais Comum de Perda",
            value=lost_data.get('etapa_mais_comum_perda', 'N/A')
        )


def main():
    """Função principal do dashboard"""
    
    # Renderizar cabeçalho
    render_header()
    
    # Carregar dados
    deals, users, funnels = load_data()
    
    if deals is None:
        st.stop()
    
    if not deals:
        st.warning("⚠️ Nenhum negócio encontrado no Agendor.")
        st.stop()
    
    # Criar DataFrame inicial
    df_deals = pd.DataFrame(deals)
    
    # Processar datas para filtros
    if 'wonAt' in df_deals.columns:
        df_deals['wonAt'] = pd.to_datetime(df_deals['wonAt'])
    if 'lostAt' in df_deals.columns:
        df_deals['lostAt'] = pd.to_datetime(df_deals['lostAt'])
    if 'createdAt' in df_deals.columns:
        df_deals['createdAt'] = pd.to_datetime(df_deals['createdAt'])
    
    # Extrair owner para filtro
    if 'owner' in df_deals.columns:
        df_deals['owner_name'] = df_deals['owner'].apply(lambda x: x.get('name') if isinstance(x, dict) else 'Sem vendedor')
    
    # Sidebar com filtros
    with st.sidebar:
        st.header("⚙️ Filtros e Configurações")
        
        # Botão de logout
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"👤 {st.session_state.user_email}")
        with col2:
            if st.button("🚪"):
                logout()
        
        st.markdown("---")
        st.subheader("📅 Filtro de Data")
        
        # Filtro de período
        date_filter = st.radio(
            "Período de análise:",
            ["Todos os dados", "Último mês", "Últimos 3 meses", "Últimos 6 meses", "Último ano", "Personalizado"],
            index=0
        )
        
        # Se escolher personalizado, mostrar seletor de datas
        start_date = None
        end_date = None
        
        if date_filter == "Personalizado":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Data inicial", value=pd.Timestamp.now() - pd.Timedelta(days=365))
            with col2:
                end_date = st.date_input("Data final", value=pd.Timestamp.now())
        
        st.markdown("---")
        st.subheader("👤 Filtro de Vendedor")
        
        # Lista de vendedores únicos
        all_sellers = sorted(df_deals['owner_name'].dropna().unique().tolist())
        seller_filter = st.multiselect(
            "Selecione vendedor(es):",
            options=["Todos"] + all_sellers,
            default=["Todos"]
        )
        
        st.markdown("---")
        
        # Aplicar filtros
        filtered_deals = deals.copy()
        
        # Filtro de data
        if date_filter != "Todos os dados":
            now = pd.Timestamp.now(tz='UTC')
            
            if date_filter == "Último mês":
                date_limit = now - pd.Timedelta(days=30)
            elif date_filter == "Últimos 3 meses":
                date_limit = now - pd.Timedelta(days=90)
            elif date_filter == "Últimos 6 meses":
                date_limit = now - pd.Timedelta(days=180)
            elif date_filter == "Último ano":
                date_limit = now - pd.Timedelta(days=365)
            elif date_filter == "Personalizado":
                date_limit = pd.Timestamp(start_date, tz='UTC')
                end_limit = pd.Timestamp(end_date, tz='UTC')
            
            # Filtrar deals baseado na data de fechamento (wonAt ou lostAt) ou criação
            filtered_deals = []
            for deal in deals:
                deal_date = None
                
                # Priorizar data de fechamento
                if deal.get('wonAt'):
                    deal_date = pd.Timestamp(deal['wonAt'])
                elif deal.get('lostAt'):
                    deal_date = pd.Timestamp(deal['lostAt'])
                elif deal.get('createdAt'):
                    deal_date = pd.Timestamp(deal['createdAt'])
                
                if deal_date:
                    if date_filter == "Personalizado":
                        if date_limit <= deal_date <= end_limit:
                            filtered_deals.append(deal)
                    else:
                        if deal_date >= date_limit:
                            filtered_deals.append(deal)
        
        # Filtro de vendedor
        if "Todos" not in seller_filter and seller_filter:
            filtered_deals = [
                deal for deal in filtered_deals 
                if deal.get('owner') and isinstance(deal.get('owner'), dict) and deal.get('owner', {}).get('name') in seller_filter
            ]
        
        # Mostrar estatísticas dos filtros
        st.info(f"📊 **{len(filtered_deals)}** negócios filtrados de **{len(deals)}** totais")
        
        st.markdown("---")
        
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📖 Sobre as Métricas")
        st.markdown("""
        **Taxa de Conversão:** Percentual de negócios que avançam entre etapas
        
        **Receita Ponderada:** Receita ajustada pela probabilidade de fechamento
        
        **Tempo Médio:** Dias entre criação e fechamento do negócio
        
        **Taxa de Vitória:** % de negócios ganhos vs perdidos
        """)
    
    # Criar objeto de analytics com dados filtrados
    analytics = AgendorAnalytics(filtered_deals, users, funnels)
    
    # Renderizar seções
    render_kpis(analytics)
    render_estimates(analytics)
    render_top_customers(analytics)
    render_top_segments(analytics)
    render_conversion_funnel(analytics)
    render_seller_performance(analytics)
    render_revenue_analysis(analytics)
    render_time_analysis(analytics)
    render_loss_analysis(analytics)
    
    # Rodapé (sem créditos adicionais)
    st.markdown("---")


if __name__ == "__main__":
    main()
