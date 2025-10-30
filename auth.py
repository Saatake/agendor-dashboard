"""
Sistema de autenticação simples para o dashboard
"""

import streamlit as st
import hashlib

def hash_password(password):
    """Gera hash SHA256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(email, password, users_dict):
    """Verifica se email e senha estão corretos (case-insensitive para email)"""
    # Normaliza o email para minúsculas para comparação
    email_lower = email.lower()
    if email_lower not in users_dict:
        return False
    return users_dict[email_lower] == hash_password(password)

def validate_email_domain(email):
    """Valida se o email é do domínio @gebrasil.com"""
    return email.lower().endswith("@gebrasil.com")

def login_page():
    """Renderiza a página de login"""
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🔐")
        st.markdown("## Dashboard - GB Auto Parts")
        st.markdown("---")
        
        email = st.text_input("📧 Email", placeholder="seu.email@gebrasil.com")
        password = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha")
        
        if st.button("Entrar", use_container_width=True):
            # Valida domínio
            if not validate_email_domain(email):
                st.error("❌ Email deve ser do domínio @gebrasil.com")
                return False
            
            # Carrega usuários permitidos
            try:
                users = st.secrets.get("users", {})
            except:
                # Para testes locais - fallback
                users = {
                    "edson@gebrasil.com": "abf0a0c2a29dff5cc2d1ce74b780b90c23176669cb1a9e8755f0303f679cee9c",
                    "jg@gebrasil.com": "d7cc6c54438b65144f095a8900d81a13668ca49cd54789cddc10ec387f6b4b5d",
                    "emmanuel@gebrasil.com": "d7cc6c54438b65144f095a8900d81a13668ca49cd54789cddc10ec387f6b4b5d"
                }
            
            # Verifica credenciais
            if check_password(email, password, users):
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.success("✅ Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Email ou senha incorretos")
                return False
        
        st.markdown("---")
        st.caption("🔒 Acesso restrito a colaboradores GB Auto Parts")
    
    return False

def logout():
    """Faz logout do usuário"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.rerun()

def require_auth():
    """Verifica se usuário está autenticado"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        login_page()
        st.stop()
    
    return True
