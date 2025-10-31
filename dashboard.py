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
from metas_manager import get_meta_mes, set_meta_mes, calcular_progresso, calcular_projecao_mes
from excel_export import generate_excel_report
import calendar
from datetime import datetime


# Configuração da página
st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Sistema de autenticação
require_auth()

# CSS customizado para melhorar visual
st.markdown("""
    <style>
    /* Melhorar espaçamento geral */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Títulos mais bonitos */
    h1 {
        color: #1f77b4;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #2c3e50;
        font-weight: 500;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: #34495e;
        font-weight: 500;
    }
    
    /* Cards de métricas mais bonitos */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Melhorar aparência das tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 8px;
        padding: 0px 20px;
        font-weight: 500;
        color: #2c3e50 !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e8f4f8;
        color: #1f77b4 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4 !important;
        color: white !important;
    }
    
    /* Garantir que o texto das tabs seja visível */
    button[data-baseweb="tab"] {
        color: #2c3e50 !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: white !important;
    }
    
    /* Info boxes mais bonitos */
    .stAlert {
        border-radius: 10px;
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
    """Renderiza KPIs principais de forma organizada"""
    st.subheader("📊 Indicadores Principais")
    
    # Calcular métricas
    win_loss = analytics.calculate_win_loss_rate()
    revenue = analytics.calculate_revenue_forecast()
    time_to_close = analytics.calculate_average_time_to_close()
    growth = analytics.calculate_growth_trend()
    
    # Resumo rápido do período
    total_deals = len(analytics.df_deals)
    won_deals = len(analytics.df_deals[analytics.df_deals['dealStatus'] == 'won']) if not analytics.df_deals.empty else 0
    lost_deals = len(analytics.df_deals[analytics.df_deals['dealStatus'] == 'lost']) if not analytics.df_deals.empty else 0
    ongoing_deals = len(analytics.df_deals[analytics.df_deals['dealStatus'] == 'ongoing']) if not analytics.df_deals.empty else 0
    
    st.info(f"""
    📅 **Resumo do Período:** {total_deals} negócios totais | 
    ✅ {won_deals} ganhos | ❌ {lost_deals} perdidos | 🔄 {ongoing_deals} em andamento
    """)
    
    st.markdown("---")
    
    # Container para receita (mais destaque)
    st.markdown("#### 💰 Receita")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Receita Confirmada (Ganhos)",
            value=f"R$ {revenue.get('receita_confirmada', 0):,.0f}",
            help="Soma de todos os negócios ganhos"
        )
    
    with col2:
        st.metric(
            label="Receita Potencial (Em Aberto)",
            value=f"R$ {revenue.get('receita_potencial', 0):,.0f}",
            delta=f"{revenue.get('total_negocios_abertos', 0)} negócios",
            help="Soma de todos os negócios em andamento"
        )
    
    with col3:
        st.metric(
            label="Receita Ponderada",
            value=f"R$ {revenue.get('receita_ponderada', 0):,.0f}",
            help="Receita potencial ajustada pela probabilidade de fechamento"
        )
    
    st.markdown("###")
    
    # Container para conversão
    st.markdown("#### 🎯 Conversão e Performance")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Taxa de Vitória",
            value=f"{win_loss.get('taxa_vitoria', 0):.1f}%",
            delta=f"{win_loss.get('ganhos', 0)} ganhos",
            help="Percentual de negócios ganhos vs total fechado"
        )
    
    with col2:
        st.metric(
            label="Taxa de Perda",
            value=f"{win_loss.get('taxa_perda', 0):.1f}%",
            delta=f"{win_loss.get('perdidos', 0)} perdidos",
            delta_color="inverse",
            help="Percentual de negócios perdidos vs total fechado"
        )
    
    with col3:
        st.metric(
            label="Tempo Médio p/ Ganhar",
            value=f"{time_to_close.get('tempo_medio_ganhos', 0):.0f} dias",
            help="Tempo médio entre criação e fechamento de negócios ganhos"
        )
    
    with col4:
        st.metric(
            label="Crescimento (30d)",
            value=f"{growth.get('crescimento_percentual', 0):.1f}%",
            delta=f"R$ {growth.get('receita_ultimos_30_dias', 0):,.0f}",
            help="Crescimento de receita nos últimos 30 dias"
        )


def render_proposals_conversion(analytics: AgendorAnalytics):
    """Renderiza métricas de conversão de propostas de forma compacta"""
    st.subheader("🎯 Eficiência de Conversão")
    
    proposals_data = analytics.calculate_proposals_per_sale()
    
    if proposals_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Propostas por Venda",
                value=f"{proposals_data['propostas_por_venda']:.1f}",
                help="Quantas propostas EM MÉDIA são necessárias para fechar 1 venda"
            )
        
        with col2:
            st.metric(
                label="Taxa de Conversão",
                value=f"{proposals_data['taxa_conversao']:.1f}%",
                help="Percentual de negócios ganhos vs total fechado"
            )
        
        with col3:
            # Mostrar relação visual
            total_deals = proposals_data['total_propostas']
            won_deals = proposals_data['total_vendas']
            st.metric(
                label="Negócios Analisados",
                value=f"{total_deals:,}",
                delta=f"{won_deals:,} ganhos ({proposals_data['taxa_conversao']:.1f}%)"
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
    """Renderiza análise dos 5 maiores clientes de forma compacta"""
    st.markdown("#### 🏆 Top 5 Clientes")
    
    top_customers = analytics.calculate_top_customers(5)
    
    if top_customers.empty:
        st.info("Sem dados de clientes disponíveis")
        return
    
    # Tabela compacta com métricas
    for idx, row in top_customers.iterrows():
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"**{idx + 1}. {row['cliente']}**")
        
        with col2:
            st.markdown(f"R$ {row['receita_total']:,.0f}")
        
        with col3:
            st.markdown(f"**{row['percentual']:.1f}%**")
        
        # Barra de progresso visual
        st.progress(row['percentual'] / 100)
        
        if idx < len(top_customers) - 1:
            st.markdown("")  # Espaçamento


def render_top_segments(analytics: AgendorAnalytics):
    """Renderiza análise dos 5 maiores segmentos de forma compacta"""
    st.markdown("#### 🎯 Top 5 Segmentos")
    
    top_segments = analytics.calculate_top_segments(5)
    
    if top_segments.empty:
        st.info("Sem dados de segmentos disponíveis")
        return
    
    # Tabela compacta com métricas
    for idx, row in top_segments.iterrows():
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"**{idx + 1}. {row['segmento']}**")
        
        with col2:
            st.markdown(f"R$ {row['receita_total']:,.0f}")
        
        with col3:
            st.markdown(f"**{row['percentual']:.1f}%**")
        
        # Barra de progresso visual
        st.progress(row['percentual'] / 100)
        
        if idx < len(top_segments) - 1:
            st.markdown("")  # Espaçamento


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
        
        st.plotly_chart(fig, use_container_width=True, key="conversion_funnel_chart")
    
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
        st.plotly_chart(fig, use_container_width=True, key="seller_revenue_chart")
    
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
        st.plotly_chart(fig, use_container_width=True, key="seller_winrate_chart")
    
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
            
            st.plotly_chart(fig, use_container_width=True, key="revenue_monthly_chart")
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
            
            st.plotly_chart(fig, use_container_width=True, key="revenue_comparison_chart")


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
            
            st.plotly_chart(fig, use_container_width=True, key="time_to_close_chart")
    
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
            
            st.plotly_chart(fig, use_container_width=True, key="time_by_stage_chart")
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


def render_insights(analytics: AgendorAnalytics):
    """Renderiza insights automáticos e alertas"""
    st.subheader("💡 Insights Automáticos & Alertas")
    
    st.markdown("""
    Esta seção analisa automaticamente seus dados e identifica:
    - 🚨 **Alertas** que precisam de atenção imediata
    - ✅ **Destaques** positivos do seu desempenho
    - 📊 **Comparações** entre vendedores e períodos
    - 💡 **Recomendações** de ações práticas
    """)
    
    insights = analytics.generate_insights()
    
    # 1. ALERTAS (coisas que precisam atenção)
    if insights['alerts']:
        st.markdown("---")
        st.markdown("### 🚨 Alertas - Precisa de Atenção")
        
        for alert in insights['alerts']:
            if alert['type'] == 'danger':
                st.error(f"**{alert['title']}**\n\n{alert['message']}")
                if 'recommendation' in alert:
                    st.info(f"💡 **Recomendação:** {alert['recommendation']}")
            elif alert['type'] == 'warning':
                st.warning(f"**{alert['title']}**\n\n{alert['message']}")
                if 'recommendation' in alert:
                    st.info(f"💡 **Recomendação:** {alert['recommendation']}")
    
    # 2. DESTAQUES (coisas positivas)
    if insights['highlights']:
        st.markdown("---")
        st.markdown("### ✅ Destaques Positivos")
        
        for highlight in insights['highlights']:
            if highlight['type'] == 'success':
                st.success(f"**{highlight['title']}**\n\n{highlight['message']}")
                if 'detail' in highlight:
                    st.caption(highlight['detail'])
            elif highlight['type'] == 'info':
                st.info(f"**{highlight['title']}**\n\n{highlight['message']}")
                if 'detail' in highlight:
                    st.caption(highlight['detail'])
    
    # 3. COMPARAÇÕES
    if insights['comparisons']:
        st.markdown("---")
        st.markdown("### 📊 Comparações e Análises")
        
        for comp in insights['comparisons']:
            with st.expander(f"**{comp['title']}**"):
                st.markdown(comp['message'])
                if 'detail' in comp:
                    st.caption(comp['detail'])
    
    # 4. RECOMENDAÇÕES
    if insights['recommendations']:
        st.markdown("---")
        st.markdown("### 💡 Recomendações de Ações")
        
        for rec in insights['recommendations']:
            with st.container():
                st.markdown(f"**{rec['title']}**")
                st.markdown(f"📌 {rec['message']}")
                st.markdown(f"➡️ **Ação sugerida:** {rec['action']}")
                st.markdown("")
    
    # Mensagem se não houver insights
    if not any([insights['alerts'], insights['highlights'], insights['comparisons'], insights['recommendations']]):
        st.info("✨ Tudo está funcionando bem! Não há alertas ou recomendações no momento.")


def render_metas_progress(analytics: AgendorAnalytics):
    """Renderiza progresso das metas do mês"""
    st.subheader("🎯 Metas do Mês")
    
    # Pegar mês atual
    now = datetime.now()
    ano_mes = now.strftime("%Y-%m")
    dia_atual = now.day
    dias_no_mes = calendar.monthrange(now.year, now.month)[1]
    
    # Carregar metas
    metas = get_meta_mes(ano_mes)
    
    # Calcular valores atuais
    revenue = analytics.calculate_revenue_forecast()
    win_loss = analytics.calculate_win_loss_rate()
    
    receita_atual = revenue.get('receita_confirmada', 0)
    vendas_atual = win_loss.get('ganhos', 0)
    
    # Total de propostas (negócios em andamento + fechados)
    propostas_atual = len(analytics.df_deals)
    
    # Novos clientes (clientes únicos com primeiro negócio no período)
    # Simplificação: contar clientes únicos nos negócios ganhos
    if not analytics.df_deals.empty and 'organization' in analytics.df_deals.columns:
        novos_clientes = analytics.df_deals[analytics.df_deals['dealStatus'] == 'won']['organization'].apply(
            lambda x: x.get('id') if isinstance(x, dict) else None
        ).nunique()
    else:
        novos_clientes = 0
    
    # Linha 1: Receita e Vendas
    col1, col2 = st.columns(2)
    
    with col1:
        progresso_receita = calcular_progresso(receita_atual, metas['receita'])
        projecao_receita = calcular_projecao_mes(receita_atual, dia_atual, dias_no_mes)
        
        st.metric(
            label="💰 Meta de Receita",
            value=f"R$ {receita_atual:,.0f}",
            delta=f"{progresso_receita:.0f}% da meta (R$ {metas['receita']:,.0f})"
        )
        
        # Barra de progresso
        st.progress(min(progresso_receita / 100, 1.0))
        
        # Projeção
        if projecao_receita >= metas['receita']:
            st.success(f"📈 Projeção: R$ {projecao_receita:,.0f} ({(projecao_receita/metas['receita']*100):.0f}% da meta)")
        elif projecao_receita >= metas['receita'] * 0.8:
            st.warning(f"📊 Projeção: R$ {projecao_receita:,.0f} ({(projecao_receita/metas['receita']*100):.0f}% da meta)")
        else:
            st.error(f"📉 Projeção: R$ {projecao_receita:,.0f} ({(projecao_receita/metas['receita']*100):.0f}% da meta)")
    
    with col2:
        progresso_vendas = calcular_progresso(vendas_atual, metas['vendas'])
        projecao_vendas = calcular_projecao_mes(vendas_atual, dia_atual, dias_no_mes)
        
        st.metric(
            label="✅ Meta de Vendas",
            value=f"{vendas_atual} vendas",
            delta=f"{progresso_vendas:.0f}% da meta ({metas['vendas']} vendas)"
        )
        
        # Barra de progresso
        st.progress(min(progresso_vendas / 100, 1.0))
        
        # Projeção
        if projecao_vendas >= metas['vendas']:
            st.success(f"📈 Projeção: {projecao_vendas:.0f} vendas ({(projecao_vendas/metas['vendas']*100):.0f}% da meta)")
        elif projecao_vendas >= metas['vendas'] * 0.8:
            st.warning(f"📊 Projeção: {projecao_vendas:.0f} vendas ({(projecao_vendas/metas['vendas']*100):.0f}% da meta)")
        else:
            st.error(f"📉 Projeção: {projecao_vendas:.0f} vendas ({(projecao_vendas/metas['vendas']*100):.0f}% da meta)")
    
    st.markdown("---")
    
    # Linha 2: Propostas e Novos Clientes
    col3, col4 = st.columns(2)
    
    with col3:
        progresso_propostas = calcular_progresso(propostas_atual, metas['propostas'])
        
        st.metric(
            label="📝 Meta de Propostas",
            value=f"{propostas_atual} propostas",
            delta=f"{progresso_propostas:.0f}% da meta ({metas['propostas']} propostas)"
        )
        st.progress(min(progresso_propostas / 100, 1.0))
    
    with col4:
        progresso_clientes = calcular_progresso(novos_clientes, metas['novos_clientes'])
        
        st.metric(
            label="🆕 Meta de Novos Clientes",
            value=f"{novos_clientes} clientes",
            delta=f"{progresso_clientes:.0f}% da meta ({metas['novos_clientes']} clientes)"
        )
        st.progress(min(progresso_clientes / 100, 1.0))


def render_configuracoes_metas():
    """Renderiza aba de configuração de metas"""
    st.subheader("⚙️ Configuração de Metas")
    
    st.markdown("""
    Defina as metas mensais para acompanhar o progresso da equipe.
    As alterações são salvas automaticamente e ficam disponíveis para todos os usuários.
    """)
    
    # Seletor de mês
    now = datetime.now()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gerar lista de meses (3 meses passados + atual + 3 futuros)
        meses_opcoes = []
        for i in range(-3, 4):
            data = datetime(now.year, now.month, 1)
            if i != 0:
                mes_num = now.month + i
                ano = now.year
                while mes_num > 12:
                    mes_num -= 12
                    ano += 1
                while mes_num < 1:
                    mes_num += 12
                    ano -= 1
                data = datetime(ano, mes_num, 1)
            
            mes_str = data.strftime("%Y-%m")
            mes_label = data.strftime("%B/%Y").replace('January', 'Janeiro').replace('February', 'Fevereiro').replace('March', 'Março').replace('April', 'Abril').replace('May', 'Maio').replace('June', 'Junho').replace('July', 'Julho').replace('August', 'Agosto').replace('September', 'Setembro').replace('October', 'Outubro').replace('November', 'Novembro').replace('December', 'Dezembro')
            
            meses_opcoes.append((mes_str, mes_label))
        
        mes_selecionado = st.selectbox(
            "Selecione o mês:",
            options=[m[0] for m in meses_opcoes],
            format_func=lambda x: dict(meses_opcoes)[x],
            index=3  # Mês atual
        )
    
    # Carregar metas do mês selecionado
    metas_atuais = get_meta_mes(mes_selecionado)
    
    st.markdown("---")
    st.markdown("### 📊 Definir Metas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        receita = st.number_input(
            "💰 Meta de Receita (R$)",
            min_value=0.0,
            value=float(metas_atuais['receita']),
            step=10000.0,
            format="%.2f"
        )
        
        propostas = st.number_input(
            "📝 Meta de Propostas",
            min_value=0,
            value=int(metas_atuais['propostas']),
            step=5
        )
    
    with col2:
        vendas = st.number_input(
            "✅ Meta de Vendas",
            min_value=0,
            value=int(metas_atuais['vendas']),
            step=1
        )
        
        novos_clientes = st.number_input(
            "🆕 Meta de Novos Clientes",
            min_value=0,
            value=int(metas_atuais['novos_clientes']),
            step=1
        )
    
    st.markdown("---")
    
    if st.button("💾 Salvar Metas", type="primary", use_container_width=True):
        success = set_meta_mes(mes_selecionado, receita, vendas, propostas, novos_clientes)
        
        if success:
            st.success(f"✅ Metas de {dict(meses_opcoes)[mes_selecionado]} salvas com sucesso!")
            st.balloons()
        else:
            st.error("❌ Erro ao salvar metas. Tente novamente.")


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
        st.subheader("📅 Filtro de Período")
        
        st.caption("Filtra negócios pela data de término (igual ao filtro do Agendor)")
        
        # Filtro de período
        date_filter = st.radio(
            "Selecione o período:",
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
            now = pd.Timestamp.now()
            
            if date_filter == "Último mês":
                date_limit = now - pd.Timedelta(days=30)
            elif date_filter == "Últimos 3 meses":
                date_limit = now - pd.Timedelta(days=90)
            elif date_filter == "Últimos 6 meses":
                date_limit = now - pd.Timedelta(days=180)
            elif date_filter == "Último ano":
                date_limit = now - pd.Timedelta(days=365)
            elif date_filter == "Personalizado":
                date_limit = pd.Timestamp(start_date)
                end_limit = pd.Timestamp(end_date)
            
            # Filtrar deals pela data de término (endTime) - IGUAL AO AGENDOR
            filtered_deals = []
            for deal in deals:
                # Usar endTime se disponível, senão usar wonAt ou lostAt
                end_date = None
                if deal.get('endTime'):
                    end_date = pd.Timestamp(deal['endTime'])
                elif deal.get('wonAt'):
                    end_date = pd.Timestamp(deal['wonAt'])
                elif deal.get('lostAt'):
                    end_date = pd.Timestamp(deal['lostAt'])
                
                if end_date:
                    # Converter para timestamp sem timezone para comparação consistente
                    if end_date.tz is not None:
                        end_date = end_date.tz_localize(None)
                    
                    if date_filter == "Personalizado":
                        if date_limit <= end_date <= end_limit:
                            filtered_deals.append(deal)
                    else:
                        if end_date >= date_limit:
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
        
        # Botão de exportar para Excel
        st.subheader("📥 Exportar Relatório")
        
        if st.button("📊 Gerar Relatório Excel", use_container_width=True, type="primary"):
            with st.spinner("Gerando relatório Excel..."):
                # Criar analytics temporário para gerar o relatório
                temp_analytics = AgendorAnalytics(filtered_deals, users, funnels)
                excel_buffer = generate_excel_report(temp_analytics)
                
                # Criar nome do arquivo com data
                filename = f"relatorio_agendor_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx"
                
                st.download_button(
                    label="⬇️ Baixar Relatório Excel",
                    data=excel_buffer,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                st.success("✅ Relatório gerado com sucesso!")
                st.caption("O arquivo contém: KPIs, Vendedores, Top Clientes, Funil com gráficos")
        
        st.markdown("---")
        
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Criar objeto de analytics com dados filtrados
    analytics = AgendorAnalytics(filtered_deals, users, funnels)
    
    # ===== NAVEGAÇÃO POR ABAS =====
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Visão Geral",
        "🎯 Metas & Objetivos",
        "📈 Funil & Conversão",
        "👥 Vendedores",
        "� Análises Avançadas",
        "⚙️ Configurações"
    ])
    
    # === ABA 1: VISÃO GERAL ===
    with tab1:
        render_kpis(analytics)
        
        st.markdown("---")
        
        # Insights e Alertas
        st.subheader("💡 Insights & Alertas")
        render_insights(analytics)
        
        st.markdown("---")
        
        # Conversão de propostas
        render_proposals_conversion(analytics)
        
        st.markdown("---")
        
        # Top Customers e Segments lado a lado
        col1, col2 = st.columns(2)
        
        with col1:
            render_top_customers(analytics)
        
        with col2:
            render_top_segments(analytics)
    
    # === ABA 2: METAS & OBJETIVOS ===
    with tab2:
        render_metas_progress(analytics)
    
    # === ABA 3: FUNIL & CONVERSÃO ===
    with tab3:
        render_conversion_funnel(analytics)
    
    # === ABA 4: VENDEDORES ===
    with tab4:
        render_seller_performance(analytics)
        st.markdown("---")
        render_estimates(analytics)
    
    # === ABA 5: ANÁLISES AVANÇADAS ===
    with tab5:
        render_revenue_analysis(analytics)
        st.markdown("---")
        render_time_analysis(analytics)
        st.markdown("---")
        render_loss_analysis(analytics)
    
    # === ABA 6: CONFIGURAÇÕES ===
    with tab6:
        render_configuracoes_metas()
        
        st.markdown("---")
        st.markdown("---")
        
        st.markdown("## 📖 Sobre o Dashboard")
        
        st.markdown("""
        Este dashboard foi desenvolvido para fornecer **insights gerenciais avançados** 
        que não estão disponíveis diretamente no Agendor CRM.
        """)
        
        st.markdown("### 🎯 Principais Métricas")
        
        st.markdown("**📊 Taxa de Conversão**")
        st.caption("""
        Percentual de negócios que avançam entre etapas do funil.
        Serve para identificar gargalos no processo de vendas.
        """)
        
        st.markdown("**💰 Receita Ponderada**")
        st.caption("""
        Receita ajustada pela probabilidade de fechamento baseada na etapa do funil.
        Exemplo: Negócio de R$ 10.000 na etapa 2 de 4 = R$ 10.000 × (2/4) = R$ 5.000 ponderados
        """)
        
        st.markdown("**📉 Valor Perdido**")
        st.caption("""
        Soma total do valor de todos os negócios perdidos.
        Serve para identificar oportunidades perdidas e seu impacto financeiro.
        """)
        
        st.markdown("**⏱️ Tempo Médio de Fechamento**")
        st.caption("""
        Número médio de dias entre a criação e o fechamento de um negócio.
        Ajuda a entender a velocidade do ciclo de vendas.
        """)
        
        st.markdown("**🎯 Propostas por Venda**")
        st.caption("""
        Quantas propostas são necessárias, em média, para fechar 1 venda.
        Serve para dimensionar esforço comercial necessário para atingir metas.
        """)
        
        st.markdown("---")
        st.markdown("### 🔄 Atualização de Dados")
        st.info("""
        Os dados são atualizados em tempo real a partir da API do Agendor. 
        Use o botão "🔄 Atualizar Dados" na barra lateral para forçar uma nova consulta.
        """)
        
        st.markdown("---")
        st.markdown("### 👨‍💻 Suporte")
        st.markdown("""
        Em caso de dúvidas ou sugestões de melhorias, entre em contato com o time de TI.
        """)


if __name__ == "__main__":
    main()
