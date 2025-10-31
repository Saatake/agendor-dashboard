"""
Análises e transformações de dados do Agendor
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict


class AgendorAnalytics:
    
    def __init__(self, deals: List[Dict], users: List[Dict], funnels: List[Dict]):
        self.deals = deals
        self.users = users
        self.funnels = funnels
        
        self.df_deals = self._create_deals_dataframe()
        self.df_users = self._create_users_dataframe()
        self.df_funnels = self._create_funnels_dataframe()
    
    def _create_deals_dataframe(self) -> pd.DataFrame:
        if not self.deals:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.deals)
        
        # converter datas
        if 'createdAt' in df.columns:
            df['createdAt'] = pd.to_datetime(df['createdAt'])
        if 'updatedAt' in df.columns:
            df['updatedAt'] = pd.to_datetime(df['updatedAt'])
        if 'wonAt' in df.columns:
            df['wonAt'] = pd.to_datetime(df['wonAt'])
        if 'lostAt' in df.columns:
            df['lostAt'] = pd.to_datetime(df['lostAt'])
        
        df['dealStatusDate'] = df.apply(
            lambda row: row.get('wonAt') if pd.notna(row.get('wonAt')) else row.get('lostAt'),
            axis=1
        )
        
        if 'value' in df.columns:
            df['value'] = df['value'].fillna(0)
        
        # o agendor retorna dealStatus como objeto, precisa extrair
        if 'dealStatus' in df.columns:
            df['dealStatus_id'] = df['dealStatus'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
            df['dealStatus_name'] = df['dealStatus'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
            df['dealStatus'] = df['dealStatus_id'].apply(lambda x: 
                'ongoing' if x == 1 else ('won' if x == 2 else ('lost' if x == 3 else None))
            )
        
        if 'owner' in df.columns:
            df['user_id'] = df['owner'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
            df['user_name'] = df['owner'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
        
        if 'dealStage' in df.columns:
            df['stage_id'] = df['dealStage'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
            df['stage_name'] = df['dealStage'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
            df['stage_order'] = df['dealStage'].apply(lambda x: x.get('sequence') if isinstance(x, dict) else None)
            df['funnel_id'] = df['dealStage'].apply(lambda x: x.get('funnel', {}).get('id') if isinstance(x, dict) else None)
            df['funnel_name'] = df['dealStage'].apply(lambda x: x.get('funnel', {}).get('name') if isinstance(x, dict) else None)
        
        return df
    
    def _create_users_dataframe(self) -> pd.DataFrame:
        if not self.users:
            return pd.DataFrame()
        return pd.DataFrame(self.users)
    
    def _create_funnels_dataframe(self) -> pd.DataFrame:
        if not self.funnels:
            return pd.DataFrame()
        return pd.DataFrame(self.funnels)
    
    def calculate_conversion_rates(self) -> pd.DataFrame:
        if self.df_deals.empty:
            return pd.DataFrame()
        
        # Agrupar por funil e etapa
        stage_counts = self.df_deals.groupby(['funnel_name', 'stage_name', 'stage_order']).size().reset_index(name='count')
        stage_counts = stage_counts.sort_values(['funnel_name', 'stage_order'])
        
        # Calcular taxa de conversão em relação à primeira etapa
        conversion_rates = []
        for funnel in stage_counts['funnel_name'].unique():
            funnel_data = stage_counts[stage_counts['funnel_name'] == funnel]
            first_stage_count = funnel_data.iloc[0]['count']
            
            for _, row in funnel_data.iterrows():
                conversion_rate = (row['count'] / first_stage_count * 100) if first_stage_count > 0 else 0
                conversion_rates.append({
                    'funil': funnel,
                    'etapa': row['stage_name'],
                    'ordem': row['stage_order'],
                    'quantidade': row['count'],
                    'taxa_conversao': round(conversion_rate, 2)
                })
        
        return pd.DataFrame(conversion_rates)
    
    def calculate_win_loss_rate(self) -> Dict:
        # taxa de ganho vs perda
        if self.df_deals.empty:
            return {}
        
        if 'dealStatus' not in self.df_deals.columns:
            return {
                'taxa_vitoria': 0,
                'taxa_perda': 0,
                'total_fechados': 0,
                'ganhos': 0,
                'perdidos': 0
            }
        
        status_counts = self.df_deals['dealStatus'].value_counts()
        won = status_counts.loc['won'] if 'won' in status_counts.index else 0
        lost = status_counts.loc['lost'] if 'lost' in status_counts.index else 0
        total_closed = won + lost
        
        if total_closed == 0:
            return {
                'taxa_vitoria': 0,
                'taxa_perda': 0,
                'total_fechados': 0,
                'ganhos': 0,
                'perdidos': 0
            }
        
        return {
            'taxa_vitoria': round(won / total_closed * 100, 2),
            'taxa_perda': round(lost / total_closed * 100, 2),
            'total_fechados': total_closed,
            'ganhos': won,
            'perdidos': lost
        }
    
    # ===== ANÁLISE DE TEMPO =====
    
    def calculate_average_time_to_close(self) -> Dict:
        # tempo médio para fechar (ganhos e perdidos)
        if self.df_deals.empty:
            return {}
        
        closed_deals = self.df_deals[self.df_deals['dealStatus'].isin(['won', 'lost'])].copy()
        
        if closed_deals.empty:
            return {'tempo_medio_dias': 0, 'tempo_medio_ganhos': 0, 'tempo_medio_perdidos': 0}
        
        closed_deals['days_to_close'] = (closed_deals['dealStatusDate'] - closed_deals['createdAt']).dt.days
        
        won_deals = closed_deals[closed_deals['dealStatus'] == 'won']
        lost_deals = closed_deals[closed_deals['dealStatus'] == 'lost']
        
        return {
            'tempo_medio_dias': round(closed_deals['days_to_close'].mean(), 1),
            'tempo_medio_ganhos': round(won_deals['days_to_close'].mean(), 1) if not won_deals.empty else 0,
            'tempo_medio_perdidos': round(lost_deals['days_to_close'].mean(), 1) if not lost_deals.empty else 0,
            'tempo_minimo': int(closed_deals['days_to_close'].min()) if not closed_deals.empty else 0,
            'tempo_maximo': int(closed_deals['days_to_close'].max()) if not closed_deals.empty else 0
        }
    
    def calculate_time_in_stage(self) -> pd.DataFrame:
        # tempo médio em cada etapa (para negócios em andamento)
        if self.df_deals.empty:
            return pd.DataFrame()
        
        # Usar updatedAt como proxy para tempo na etapa atual
        ongoing_deals = self.df_deals[self.df_deals['dealStatus'] == 'ongoing'].copy()
        
        if ongoing_deals.empty:
            return pd.DataFrame()
        
        # Usar pd.Timestamp com timezone para comparação
        now = pd.Timestamp.now(tz='UTC')
        ongoing_deals['days_in_stage'] = (now - ongoing_deals['updatedAt']).dt.days
        
        stage_time = ongoing_deals.groupby(['funnel_name', 'stage_name']).agg({
            'days_in_stage': ['mean', 'median', 'max']
        }).reset_index()
        
        stage_time.columns = ['funil', 'etapa', 'tempo_medio_dias', 'tempo_mediano_dias', 'tempo_max_dias']
        stage_time = stage_time.round(1)
        
        return stage_time
    
    # ===== PERFORMANCE DE VENDEDORES =====
    
    def calculate_seller_performance(self) -> pd.DataFrame:
        # performance por vendedor
        if self.df_deals.empty:
            return pd.DataFrame()
        
        seller_metrics = []
        
        for user_id in self.df_deals['user_id'].unique():
            if pd.isna(user_id):
                continue
            
            user_deals = self.df_deals[self.df_deals['user_id'] == user_id]
            user_name = user_deals.iloc[0]['user_name']
            
            total_deals = len(user_deals)
            won_deals = len(user_deals[user_deals['dealStatus'] == 'won'])
            lost_deals = len(user_deals[user_deals['dealStatus'] == 'lost'])
            ongoing_deals = len(user_deals[user_deals['dealStatus'] == 'ongoing'])
            
            total_value = user_deals[user_deals['dealStatus'] == 'won']['value'].sum()
            avg_deal_value = user_deals[user_deals['dealStatus'] == 'won']['value'].mean()
            
            win_rate = (won_deals / (won_deals + lost_deals) * 100) if (won_deals + lost_deals) > 0 else 0
            
            seller_metrics.append({
                'vendedor': user_name,
                'total_negocios': total_deals,
                'ganhos': won_deals,
                'perdidos': lost_deals,
                'em_andamento': ongoing_deals,
                'taxa_vitoria': round(win_rate, 2),
                'valor_total': round(total_value, 2),
                'ticket_medio': round(avg_deal_value, 2) if not pd.isna(avg_deal_value) else 0
            })
        
        df = pd.DataFrame(seller_metrics)
        return df.sort_values('valor_total', ascending=False)
    
    # ===== ANÁLISE DE RECEITA =====
    
    def calculate_revenue_forecast(self) -> Dict:
        # previsão de receita simples baseada em pipeline
        if self.df_deals.empty:
            return {}
        
        ongoing = self.df_deals[self.df_deals['dealStatus'] == 'ongoing']
        
        # Receita potencial total
        potential_revenue = ongoing['value'].sum()
        
        # Receita ponderada por probabilidade (estimativa simples por etapa)
        # Quanto mais avançada a etapa, maior a probabilidade
        if 'stage_order' in ongoing.columns:
            max_stage = ongoing['stage_order'].max() if not ongoing.empty else 1
            ongoing_copy = ongoing.copy()
            ongoing_copy['probability'] = ongoing_copy['stage_order'] / max_stage
            weighted_revenue = (ongoing_copy['value'] * ongoing_copy['probability']).sum()
        else:
            weighted_revenue = potential_revenue * 0.5  # 50% como padrão
        
        # Receita já conquistada
        won_deals = self.df_deals[self.df_deals['dealStatus'] == 'won']
        confirmed_revenue = won_deals['value'].sum()
        
        return {
            'receita_confirmada': round(confirmed_revenue, 2),
            'receita_potencial': round(potential_revenue, 2),
            'receita_ponderada': round(weighted_revenue, 2),
            'total_negocios_abertos': len(ongoing)
        }
    
    def calculate_revenue_by_period(self, period: str = 'M') -> pd.DataFrame:
        # receita agregada por período (M/W/D)
        if self.df_deals.empty:
            return pd.DataFrame()
        
        won_deals = self.df_deals[self.df_deals['dealStatus'] == 'won'].copy()
        
        if won_deals.empty:
            return pd.DataFrame()
        
        won_deals['period'] = won_deals['dealStatusDate'].dt.to_period(period)
        
        revenue_by_period = won_deals.groupby('period').agg({
            'value': 'sum',
            'id': 'count'
        }).reset_index()
        
        revenue_by_period.columns = ['periodo', 'receita', 'quantidade']
        revenue_by_period['periodo'] = revenue_by_period['periodo'].astype(str)
        revenue_by_period['receita'] = revenue_by_period['receita'].round(2)
        
        return revenue_by_period.sort_values('periodo')
    
    # ===== ANÁLISE DE PERDAS =====
    
    def analyze_lost_deals(self) -> Dict:
        # análise resumida de negócios perdidos
        if self.df_deals.empty:
            return {}
        
        lost_deals = self.df_deals[self.df_deals['dealStatus'] == 'lost']
        
        if lost_deals.empty:
            return {
                'total_perdidos': 0,
                'valor_perdido': 0,
                'ticket_medio_perdido': 0,
                'etapa_mais_comum_perda': 'N/A'
            }
        
        # Etapa onde mais se perde
        most_common_stage = lost_deals['stage_name'].mode()[0] if not lost_deals.empty else 'N/A'
        
        return {
            'total_perdidos': len(lost_deals),
            'valor_perdido': round(lost_deals['value'].sum(), 2),
            'ticket_medio_perdido': round(lost_deals['value'].mean(), 2),
            'etapa_mais_comum_perda': most_common_stage
        }
    
    # ===== TENDÊNCIAS =====
    
    def calculate_growth_trend(self) -> Dict:
        # tendência de receita comparando últimos períodos
        if self.df_deals.empty:
            return {}
        
        won_deals = self.df_deals[self.df_deals['dealStatus'] == 'won'].copy()
        
        if won_deals.empty or 'dealStatusDate' not in won_deals.columns:
            return {}
        
        # Remover valores nulos
        won_deals = won_deals[won_deals['dealStatusDate'].notna()]
        
        if won_deals.empty:
            return {}
        
        # Converter now para timezone-aware se dealStatusDate tiver timezone
        now = pd.Timestamp.now(tz='UTC')
        
        last_30_days = won_deals[won_deals['dealStatusDate'] >= (now - timedelta(days=30))]
        prev_30_days = won_deals[
            (won_deals['dealStatusDate'] >= (now - timedelta(days=60))) &
            (won_deals['dealStatusDate'] < (now - timedelta(days=30)))
        ]
        
        revenue_last_30 = last_30_days['value'].sum()
        revenue_prev_30 = prev_30_days['value'].sum()
        
        growth_rate = ((revenue_last_30 - revenue_prev_30) / revenue_prev_30 * 100) if revenue_prev_30 > 0 else 0
        
        return {
            'receita_ultimos_30_dias': round(revenue_last_30, 2),
            'receita_30_dias_anteriores': round(revenue_prev_30, 2),
            'crescimento_percentual': round(growth_rate, 2),
            'negocios_ultimos_30': len(last_30_days),
            'negocios_30_anteriores': len(prev_30_days)
        }
    
    # ===== ANÁLISE DE CLIENTES =====
    
    def calculate_top_customers(self, limit: int = 5) -> pd.DataFrame:
        # top N clientes por receita
        if self.df_deals.empty:
            return pd.DataFrame()
        
        won_deals = self.df_deals[self.df_deals['dealStatus'] == 'won'].copy()
        
        if won_deals.empty or 'organization' not in won_deals.columns:
            return pd.DataFrame()
        
        # Extrair nome da organização
        won_deals['customer_name'] = won_deals['organization'].apply(
            lambda x: x.get('name') if isinstance(x, dict) else 'Sem Organização'
        )
        
        # Agrupar por cliente
        customer_revenue = won_deals.groupby('customer_name').agg({
            'value': 'sum',
            'id': 'count'
        }).reset_index()
        
        customer_revenue.columns = ['cliente', 'receita_total', 'qtd_negocios']
        
        # Calcular percentual
        total_revenue = customer_revenue['receita_total'].sum()
        customer_revenue['percentual'] = (customer_revenue['receita_total'] / total_revenue * 100).round(2)
        
        # Ordenar e pegar top N
        top_customers = customer_revenue.sort_values('receita_total', ascending=False).head(limit)
        top_customers['receita_total'] = top_customers['receita_total'].round(2)
        
        return top_customers.reset_index(drop=True)
    
    # ===== ANÁLISE DE SEGMENTOS =====
    
    def calculate_top_segments(self, limit: int = 5) -> pd.DataFrame:
        # top N segmentos por receita (identificação por palavras-chave)
        if self.df_deals.empty:
            return pd.DataFrame()
        
        won_deals = self.df_deals[self.df_deals['dealStatus'] == 'won'].copy()
        
        if won_deals.empty or 'organization' not in won_deals.columns:
            return pd.DataFrame()
        
        # Extrair nome da organização
        won_deals['customer_name'] = won_deals['organization'].apply(
            lambda x: x.get('name', '') if isinstance(x, dict) else ''
        )
        
        # Identificar segmento a partir de palavras-chave no nome
        def identify_segment(name):
            name_lower = str(name).lower()
            
            # Palavras-chave para identificar segmentos
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
        
        # Agrupar por segmento
        segment_revenue = won_deals.groupby('segmento').agg({
            'value': 'sum',
            'id': 'count'
        }).reset_index()
        
        segment_revenue.columns = ['segmento', 'receita_total', 'qtd_negocios']
        
        # Calcular percentual
        total_revenue = segment_revenue['receita_total'].sum()
        segment_revenue['percentual'] = (segment_revenue['receita_total'] / total_revenue * 100).round(2)
        
        # Ordenar e pegar top N
        top_segments = segment_revenue.sort_values('receita_total', ascending=False).head(limit)
        top_segments['receita_total'] = top_segments['receita_total'].round(2)
        
        return top_segments.reset_index(drop=True)
    
    # ===== ESTIMATIVAS E PREVISÕES =====
    
    def calculate_proposals_per_sale(self) -> Dict:
        # quantas propostas EM MÉDIA são necessárias para fechar 1 venda
        if self.df_deals.empty:
            return {}
        
        won_deals = self.df_deals[self.df_deals['dealStatus'] == 'won']
        all_deals = self.df_deals[self.df_deals['dealStatus'].isin(['won', 'lost'])]
        
        if won_deals.empty or all_deals.empty:
            return {
                'propostas_por_venda': 0,
                'taxa_conversao': 0,
                'total_propostas': 0,
                'total_vendas': 0
            }
        
        # Taxa de conversão (ganhos / total fechado)
        conversion_rate = len(won_deals) / len(all_deals)
        
        # Propostas necessárias para fechar 1 venda = 1 / taxa de conversão
        # Ex: 50% conversão = 2 propostas para 1 venda
        proposals_per_sale = 1 / conversion_rate if conversion_rate > 0 else 0
        
        return {
            'propostas_por_venda': round(proposals_per_sale, 1),
            'taxa_conversao': round(conversion_rate * 100, 2),
            'total_propostas': len(all_deals),
            'total_vendas': len(won_deals)
        }
    
    def calculate_proposals_for_target(self, target_revenue: float = 100000) -> Dict:
        # quantas propostas para atingir meta (ticket médio × taxa de conversão)
        if self.df_deals.empty:
            return {}
        
        won_deals = self.df_deals[self.df_deals['dealStatus'] == 'won']
        all_deals = self.df_deals[self.df_deals['dealStatus'].isin(['won', 'lost'])]
        
        if won_deals.empty or all_deals.empty:
            return {
                'propostas_necessarias': 0,
                'ticket_medio': 0,
                'taxa_conversao': 0,
                'receita_esperada_por_proposta': 0
            }
        
        # Ticket médio dos negócios ganhos
        avg_ticket = won_deals['value'].mean()
        
        # Taxa de conversão (ganhos / total fechado)
        conversion_rate = len(won_deals) / len(all_deals)
        
        # Receita esperada por proposta
        expected_revenue_per_proposal = avg_ticket * conversion_rate
        
        # Número de propostas necessárias
        proposals_needed = target_revenue / expected_revenue_per_proposal if expected_revenue_per_proposal > 0 else 0
        
        return {
            'propostas_necessarias': round(proposals_needed, 1),
            'ticket_medio': round(avg_ticket, 2),
            'taxa_conversao': round(conversion_rate * 100, 2),
            'receita_esperada_por_proposta': round(expected_revenue_per_proposal, 2),
            'meta_receita': target_revenue
        }
    
    def calculate_visits_to_close(self) -> Dict:
        # estimativa de visitas necessárias para fechar (proxy baseado em tempo e recorrência)
        if self.df_deals.empty:
            return {}
        
        won_deals = self.df_deals[self.df_deals['dealStatus'] == 'won'].copy()
        
        if won_deals.empty:
            return {
                'estimativa_visitas': 0,
                'tempo_medio_dias': 0,
                'recorrencia_media': 0
            }
        
        # Remover deals sem data
        won_deals_with_dates = won_deals[
            won_deals['wonAt'].notna() & 
            won_deals['createdAt'].notna()
        ].copy()
        
        if won_deals_with_dates.empty:
            return {
                'estimativa_visitas': 0,
                'tempo_medio_dias': 0,
                'recorrencia_media': 0
            }
        
        # Calcular tempo médio até fechamento
        won_deals_with_dates['days_to_close'] = (
            won_deals_with_dates['wonAt'] - won_deals_with_dates['createdAt']
        ).dt.days
        
        avg_days_to_close = won_deals_with_dates['days_to_close'].mean()
        
        # Calcular recorrência por cliente
        if 'organization' in won_deals.columns:
            won_deals['customer_id'] = won_deals['organization'].apply(
                lambda x: x.get('id') if isinstance(x, dict) else None
            )
            
            # Negócios por cliente
            customer_frequency = won_deals.groupby('customer_id').size()
            avg_deals_per_customer = customer_frequency.mean()
        else:
            avg_deals_per_customer = 1
        
        # Estimativa de visitas:
        # Assumindo 1 visita a cada 7-10 dias em média durante o ciclo de venda
        estimated_visits = (avg_days_to_close / 8) + (avg_deals_per_customer * 0.5)
        
        # Arredondar para número inteiro de visitas
        estimated_visits = max(1, round(estimated_visits))
        
        return {
            'estimativa_visitas': int(estimated_visits),
            'tempo_medio_dias': round(avg_days_to_close, 1),
            'recorrencia_media': round(avg_deals_per_customer, 2),
            'interpretacao': f"Em média {int(estimated_visits)} visitas em {round(avg_days_to_close, 0)} dias"
        }
