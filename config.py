"""
Configurações do Dashboard Agendor
"""

import os

# Token de autenticação da API Agendor
# Prioridade: 1) Streamlit secrets, 2) config_local.py, 3) variável de ambiente
try:
    import streamlit as st
    AGENDOR_TOKEN = st.secrets.get("AGENDOR_TOKEN")
except:
    AGENDOR_TOKEN = None

# Tenta pegar do config_local.py (desenvolvimento)
if not AGENDOR_TOKEN:
    try:
        from config_local import AGENDOR_TOKEN
    except ImportError:
        AGENDOR_TOKEN = os.getenv("AGENDOR_TOKEN")
    
if not AGENDOR_TOKEN:
    raise ValueError("Token do Agendor não configurado! Configure AGENDOR_TOKEN nas secrets do Streamlit, config_local.py ou como variável de ambiente.")

# Base URL da API
API_BASE_URL = "https://api.agendor.com.br/v3"

# Headers para requisições
HEADERS = {
    "Authorization": f"Token {AGENDOR_TOKEN}",
    "Content-Type": "application/json"
}

# Configurações do dashboard
DASHBOARD_TITLE = "Dashboard Gerencial - CRM"
PAGE_ICON = "📊"
LAYOUT = "wide"
