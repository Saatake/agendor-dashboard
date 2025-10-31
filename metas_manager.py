"""
Gerenciamento de metas e objetivos
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional


METAS_FILE = "metas.json"


def load_metas() -> Dict:
    """Carrega metas do arquivo JSON"""
    if not os.path.exists(METAS_FILE):
        # Criar arquivo inicial se não existir
        default_metas = {
            datetime.now().strftime("%Y-%m"): {
                "receita": 150000,
                "vendas": 15,
                "propostas": 50,
                "novos_clientes": 5
            }
        }
        save_metas(default_metas)
        return default_metas
    
    try:
        with open(METAS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar metas: {e}")
        return {}


def save_metas(metas: Dict) -> bool:
    """Salva metas no arquivo JSON"""
    try:
        with open(METAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(metas, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar metas: {e}")
        return False


def get_meta_mes(ano_mes: Optional[str] = None) -> Dict:
    """
    Retorna metas de um mês específico
    
    Args:
        ano_mes: String no formato "YYYY-MM" (ex: "2025-10")
                 Se None, usa o mês atual
    
    Returns:
        Dict com as metas do mês ou metas padrão se não existir
    """
    if ano_mes is None:
        ano_mes = datetime.now().strftime("%Y-%m")
    
    metas = load_metas()
    
    if ano_mes in metas:
        return metas[ano_mes]
    
    # Retornar metas padrão se não existir
    return {
        "receita": 150000,
        "vendas": 15,
        "propostas": 50,
        "novos_clientes": 5
    }


def set_meta_mes(ano_mes: str, receita: float, vendas: int, propostas: int, novos_clientes: int) -> bool:
    """
    Define metas para um mês específico
    
    Args:
        ano_mes: String no formato "YYYY-MM"
        receita: Meta de receita em R$
        vendas: Meta de negócios ganhos
        propostas: Meta de propostas criadas
        novos_clientes: Meta de novos clientes
    
    Returns:
        True se salvou com sucesso, False caso contrário
    """
    metas = load_metas()
    
    metas[ano_mes] = {
        "receita": float(receita),
        "vendas": int(vendas),
        "propostas": int(propostas),
        "novos_clientes": int(novos_clientes)
    }
    
    return save_metas(metas)


def calcular_progresso(valor_atual: float, meta: float) -> float:
    """
    Calcula percentual de progresso em relação à meta
    
    Returns:
        Percentual (0-100+)
    """
    if meta <= 0:
        return 0.0
    return (valor_atual / meta) * 100


def calcular_projecao_mes(valor_atual: float, dia_atual: int, dias_no_mes: int) -> float:
    """
    Projeta valor final do mês baseado no ritmo atual
    
    Args:
        valor_atual: Valor acumulado até agora
        dia_atual: Dia atual do mês (1-31)
        dias_no_mes: Total de dias no mês
    
    Returns:
        Projeção de valor final do mês
    """
    if dia_atual <= 0:
        return valor_atual
    
    ritmo_diario = valor_atual / dia_atual
    return ritmo_diario * dias_no_mes
