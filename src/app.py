"""
Script + Shorts Generador — Interfaz Streamlit
Assets Solutions AI | Proyecto 02
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from dotenv import load_dotenv

from src.templates.plantillas import obtener_plataformas, PLANTILLAS, TONOS
from src.generator.motor import generar_script
from src.exporters.exportar import exportar_txt, exportar_todos_txt
from src.auth.auth import (
    inicializar_sesion, esta_autenticado, obtener_usuario,
    cerrar_sesion, login_email, registrar_usuario, obtener_url_google,
    obtener_cliente_supabase
)

load_dotenv()

# ─────────────────────────────────────────────
# STRIPE CONFIG
# ─────────────────────────────────────────────
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_BASIC_PRICE_ID = os.getenv("STRIPE_BASIC_PRICE_ID", "")
STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID", "")

PLANES = {
    "free":  {"nombre": "Free",  "precio": 0,  "scripts": 3,   "emoji": "🆓"},
    "basic": {"nombre": "Basic", "precio": 19, "scripts": 50,  "emoji": "⚡"},
    "pro":   {"nombre": "Pro",   "precio": 39, "scripts": 999, "emoji": "🚀"},
}

st.set_page_config(page_title="Script & Shorts Studio", page_icon="🎬", layout="wide")
inicializar_sesion()

# ─────────────────────────────────────────────
# MANEJAR RETORNO DE STRIPE
# ─────────────────────────────────────────────
params = st.query_params
if params.get("pago") == "exitoso":
    plan = params.get("plan", "basic")
    st.session_state["pago_exitoso"] = plan
    st.query_params.clear()
elif params.get("pago") == "cancelado":
    st.session_state["pago_cancelado"] = True
    st.query_params.clear()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .main .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1100px; }
    .auth-wrap { max-width: 420px; margin: 3rem auto; padding: 2.5rem;
        background: #111111; border: 1px solid #222; border-radius: 20px; }
    .auth-logo { text-align: center; margin-bottom: 2rem; }
    .auth-logo-icon { width: 56px; height: 56px;
        background: linear-gradient(135deg, #E8820C, #F5A623); border-radius: 16px;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 26px; margin-bottom: 0.75rem; box-shadow: 0 4px 20px rgba(232,130,12,0.35); }
    .auth-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem;
        font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.02em; }
    .auth-title span { color: #F5A623; }
    .auth-sub { color: #666; font-size: 0.85rem; margin: 0.4rem 0 0; }
    .auth-divider { display: flex; align-items: center; gap: 12px;
        margin: 1.25rem 0; color: #444; font-size: 0.8rem; }
    .auth-divider::before, .auth-divider::after { content: ''; flex: 1; height: 1px; background: #222; }
    .google-btn { display: flex; align-items: center; justify-content: center; gap: 10px;
        width: 100%; padding: 0.7rem; background: #fff; border: none; border-radius: 10px;
        color: #333; font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 500;
        cursor: pointer; text-decoration: none; }
    .studio-header { background: linear-gradient(135deg, #0D0D0D 0%, #1a1200 100%);
        border: 1px solid #2a1f00; border-radius: 16px; padding: 1.25rem 2rem;
        margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between; }
    .studio-logo { display: flex; align-items: center; gap: 12px; }
    .studio-icon { width: 42px; height: 42px; background: linear-gradient(135deg, #E8820C, #F5A623);
        border-radius: 10px; display: flex; align-items: center; justify-content: center;
        font-size: 20px; box-shadow: 0 4px 16px rgba(232,130,12,0.35); }
    .studio-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem;
        font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.02em; }
    .studio-title span { color: #F5A623; }
    .studio-sub { color: #666; font-size: 0.8rem; margin: 0; }
    .user-chip { display: flex; align-items: center; gap: 8px;
        background: rgba(255,255,255,0.05); border: 1px solid #2a2a2a;
        border-radius: 20px; padding: 6px 14px; color: #c4c4c4; font-size: 0.85rem; }
    .user-dot { width: 8px; height: 8px; background: #22c55e; border-radius: 50%; flex-shrink:0; }
    .ecosystem-badge { display: inline-flex; align-items: center; gap: 6px;
        background: rgba(232,130,12,0.1); border: 1px solid rgba(232,130,12,0.25);
        color: #E8820C; font-size: 0.7rem; font-weight: 500; padding: 3px 10px;
        border-radius: 20px; letter-spacing: 0.05em; text-transform: uppercase; }
    .plan-card { background: #111; border: 1px solid #222; border-radius: 16px;
        padding: 1.75rem; text-align: center; transition: border-color 0.2s; }
    .plan-card.featured { border: 2px solid #E8820C; background: #130e00; }
    .plan-price { font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem;
        font-weight: 700; color: #fff; line-height: 1; }
    .plan-price span { font-size: 1rem; color: #666; font-weight: 400; }
    .plan-name { font-size: 1rem; font-weight: 600; color: #F5A623; margin-bottom: 0.5rem; }
    .plan-feature { color: #888; font-size: 0.875rem; padding: 0.4rem 0;
        border-bottom: 1px solid #1a1a1a; }
    .plan-feature:last-child { border-bottom: none; }
    .plan-badge { background: #E8820C; color: #0D0D0D; font-size: 0.7rem;
        font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; }
    .stTextArea textarea, .stTextInput input { background-color: #111111 !important;
        border: 1px solid #2a2a2a !important; border-radius: 10px !important;
        color: #e8e8e8 !important; font-family: 'Outfit', sans-serif !important; }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #E8820C !important; box-shadow: 0 0 0 3px rgba(232,130,12,0.1) !important; }
    .stSelectbox > div > div { background-color: #111111 !important;
        border: 1px solid #2a2a2a !important; border-radius: 10px !important; color: #e8e8e8 !important; }
    .stButton > button[kind="primary"] { background: linear-gradient(135deg, #E8820C, #F5A623) !important;
        color: #0D0D0D !important; border: none !important; border-radius: 12px !important;
        font-family: 'Space Grotesk', sans-serif !important; font-size: 1rem !important;
        font-weight: 600 !important; box-shadow: 0 4px 20px rgba(232,130,12,0.3) !important; }
    .stButton > button[kind="secondary"] { background: transparent !important;
        border: 1px solid #2a2a2a !important; border-radius: 10px !important; color: #888 !important; }
    .script-output { background: #0a0a0a; border: 1px solid #1e1e1e;
        border-top: 3px solid #E8820C; border-radius: 14px;
        padding: 1.75rem 2rem; margin: 1.5rem 0; font-size: 0.95rem;
        line-height: 1.8; color: #d4d4d4; }
    .platform-info { background: #0D0D0D; border: 1px solid #2a1f00;
        border-left: 3px solid #E8820C; border-radius: 10px; padding: 1rem 1.25rem; margin-top: 0.5rem; }
    .platform-info p { color: #c4a96a; font-size: 0.875rem; margin: 0.2rem 0; }
    .platform-info strong { color: #F5A623; }
    .section-label { font-size: 0.7rem; font-weight: 600; color: #E8820C;
        text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 1rem;
        display: flex; align-items: center; gap: 8px; }
    .section-label::after { content: ''; flex: 1; height: 1px;
        background: linear-gradient(to right, #2a1f00, transparent); }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: #0a0a0a;
        border-radius: 10px; padding: 4px; border: 1px solid #1e1e1e; }
    .stTabs [data-baseweb="tab"] { background: transparent; border-radius: 8px;
        color: #888 !important; font-size: 0.875rem; border: none; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #E8820C, #F5A623) !important;
        color: #0D0D0D !important; font-weight: 600 !important; }
    [data-testid="stSidebar"] { background: #0a0a0a !important; border-right: 1px solid #1e1e1e !important; }
    .stDownloadButton > button { background: transparent !important;
        border: 1px solid #2a2a2a !important; border-radius: 10px !important; color: #c4a96a !important; }
    .stProgress > div > div > div { background: linear-gradient(90deg, #E8820C, #F5A623) !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FUNCIONES SUPABASE
# ─────────────────────────────────────────────
def guardar_script(usuario_id, tema, plataforma, tono, audiencia, contenido):
    try:
        supabase = obtener_cliente_supabase()
        supabase.table("scripts").insert({
            "user_id": usuario_id, "tema": tema, "plataforma": plataforma,
            "tono": tono, "audiencia": audiencia, "contenido": contenido,
        }).execute()
    except Exception as e:
        st.warning(f"No se pudo guardar en historial: {e}")

def obtener_historial(usuario_id):
    try:
        supabase = obtener_cliente_supabase()
        response = supabase.table("scripts")\
            .select("id, tema, plataforma, tono, created_at, contenido")\
            .eq("user_id", usuario_id)\
            .order("created_at", desc=True)\
            .limit(20).execute()
        return response.data or []
    except Exception:
        return []

def obtener_plan_usuario(usuario_id):
    try:
        supabase = obtener_cliente_supabase()
        response = supabase.table("users").select("plan, scripts_used, scripts_limit")\
            .eq("id", usuario_id).single().execute()
        return response.data or {"plan": "free", "scripts_used": 0, "scripts_limit": 3}
    except Exception:
        return {"plan": "free", "scripts_used": 0, "scripts_limit": 3}

def puede_generar(usuario_id):
    info = obtener_plan_usuario(usuario_id)
    if info["plan"] == "pro":
        return True, info
    return info["scripts_used"] < info["scripts_limit"], info

def incrementar_uso(usuario_id):
    try:
        supabase = obtener_cliente_supabase()
        info = obtener_plan_usuario(usuario_id)
        supabase.table("users").update({
            "scripts_used": info["scripts_used"] + 1
        }).eq("id", usuario_id).execute()
    except Exception:
        pass


# ─────────────────────────────────────────────
# STRIPE CHECKOUT
# ─────────────────────────────────────────────
def crear_checkout_url(plan, usuario_id, usuario_email):
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        price_id = STRIPE_BASIC_PRICE_ID if plan == "basic" else STRIPE_PRO_PRICE_ID
        app_url = os.getenv("APP_URL", "http://localhost:8501")
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            customer_email=usuario_email,
            metadata={"user_id": usuario_id, "plan": plan},
            success_url=f"{app_url}?pago=exitoso&plan={plan}",
            cancel_url=f"{app_url}?pago=cancelado",
        )
        return session.url
    except Exception as e:
        st.error(f"Error al crear checkout: {e}")
        return None


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
def mostrar_login():
    st.markdown("""
    <div class="auth-wrap">
        <div class="auth-logo">
            <div class="auth-logo-icon">🎬</div>
            <h1 class="auth-title">Script & <span>Shorts</span></h1>
            <p class="auth-sub">Tu estudio de contenido con IA</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_registro = st.tabs(["Iniciar sesión", "Crear cuenta"])

    with tab_login:
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        url_google = obtener_url_google()
        if url_google:
            st.markdown(f"""
            <a href="{url_google}" class="google-btn" target="_self">
                <svg width="18" height="18" viewBox="0 0 48 48">
                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                    <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.35-8.16 2.35-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                </svg>
                Continuar con Google
            </a>
            """, unsafe_allow_html=True)

        st.markdown('<div class="auth-divider">o con email</div>', unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="tu@email.com", key="login_email")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••", key="login_pass")

        if st.button("✦ Iniciar sesión", type="primary", use_container_width=True):
            if email and password:
                with st.spinner("Verificando..."):
                    resultado = login_email(email, password)
                if resultado["ok"]:
                    st.rerun()
                else:
                    st.error(resultado["mensaje"])
            else:
                st.warning("Completa todos los campos.")

    with tab_registro:
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        nombre = st.text_input("Nombre completo", placeholder="Tu nombre", key="reg_nombre")
        email_reg = st.text_input("Email", placeholder="tu@email.com", key="reg_email")
        pass_reg = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres", key="reg_pass")

        if st.button("✦ Crear cuenta gratis", type="primary", use_container_width=True):
            if nombre and email_reg and pass_reg:
                if len(pass_reg) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                else:
                    with st.spinner("Creando cuenta..."):
                        resultado = registrar_usuario(email_reg, pass_reg, nombre)
                    if resultado["ok"]:
                        st.success(resultado["mensaje"])
                    else:
                        st.error(resultado["mensaje"])
            else:
                st.warning("Completa todos los campos.")

    st.markdown("<p style='text-align:center; color:#333; font-size:0.75rem; margin-top:2rem;'>⬡ Assets Solutions AI · Script & Shorts Studio</p>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────
def mostrar_app():
    usuario = obtener_usuario()

    # Notificaciones de pago
    if st.session_state.get("pago_exitoso"):
        plan = st.session_state.pop("pago_exitoso")
        st.success(f"🎉 ¡Pago exitoso! Tu plan {plan.upper()} está activo.")
    if st.session_state.get("pago_cancelado"):
        st.session_state.pop("pago_cancelado")
        st.warning("Pago cancelado. Tu plan no fue modificado.")

    # ── Sidebar ──
    with st.sidebar:
        info_plan = obtener_plan_usuario(usuario["id"])
        plan_actual = info_plan.get("plan", "free")
        scripts_used = info_plan.get("scripts_used", 0)
        scripts_limit = info_plan.get("scripts_limit", 3)

        st.markdown(f"""
        <div style='padding:1.25rem 0 1rem; border-bottom:1px solid #1e1e1e; margin-bottom:1.5rem;'>
            <p style='color:#666; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em; margin:0 0 0.4rem;'>Sesión activa</p>
            <p style='color:#F5A623; font-size:0.9rem; font-weight:500; margin:0;'>{usuario['nombre']}</p>
            <p style='color:#555; font-size:0.8rem; margin:0 0 0.75rem;'>{usuario['email']}</p>
            <div style='background:rgba(232,130,12,0.1); border:1px solid rgba(232,130,12,0.2); border-radius:8px; padding:0.5rem 0.75rem;'>
                <p style='color:#F5A623; font-size:0.8rem; font-weight:600; margin:0;'>Plan {plan_actual.upper()}</p>
                <p style='color:#666; font-size:0.75rem; margin:0;'>{scripts_used} / {"∞" if plan_actual == "pro" else scripts_limit} scripts usados</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
            if api_key:
                os.environ["ANTHROPIC_API_KEY"] = api_key
        else:
            st.markdown("""
            <div style='background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2);
                 border-radius:8px; padding:0.6rem 0.875rem; margin-bottom:1rem;'>
                <span style='color:#6ee7b7; font-size:0.875rem;'>● API conectada</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<p style='color:#444; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; margin:1rem 0 0.75rem;'>Plataformas</p>", unsafe_allow_html=True)
        for plataforma, info in PLANTILLAS.items():
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; padding:0.5rem 0;
                 border-bottom:1px solid #151515; font-size:0.85rem;'>
                <span style='color:#c4c4c4; font-weight:500;'>{plataforma}</span>
                <span style='color:#555; font-size:0.775rem;'>{info['duracion']}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
        if st.button("⎋  Cerrar sesión", type="secondary", use_container_width=True):
            cerrar_sesion()

    # ── Header ──
    col_header, col_logout = st.columns([5, 1])
    with col_header:
        st.markdown(f"""
        <div class="studio-header">
            <div class="studio-logo">
                <div class="studio-icon">🎬</div>
                <div>
                    <h1 class="studio-title">Script & <span>Shorts</span> Studio</h1>
                    <p class="studio-sub">Genera guiones profesionales con IA</p>
                </div>
            </div>
            <div style='display:flex; flex-direction:column; align-items:flex-end; gap:6px;'>
                <div class="user-chip"><div class="user-dot"></div>{usuario['nombre']}</div>
                <div class="ecosystem-badge">⬡ Assets Solutions AI</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_logout:
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        if st.button("⎋ Salir", type="secondary", use_container_width=True):
            cerrar_sesion()

    # ── Tabs ──
    tab_generar, tab_historial, tab_planes = st.tabs(["✦ Generar Script", "📋 Mi Historial", "💳 Planes"])

    # ════════════════════════════════════════
    # TAB 1: GENERAR
    # ════════════════════════════════════════
    with tab_generar:
        # Verificar límite
        puede, info_plan = puede_generar(usuario["id"])
        if not puede:
            st.markdown(f"""
            <div style='background:rgba(232,130,12,0.08); border:1px solid rgba(232,130,12,0.3);
                 border-radius:14px; padding:1.5rem 2rem; text-align:center; margin-bottom:1.5rem;'>
                <p style='color:#F5A623; font-size:1.1rem; font-weight:600; margin:0 0 0.5rem;'>
                    Alcanzaste tu límite de {info_plan['scripts_limit']} scripts del plan Free
                </p>
                <p style='color:#666; font-size:0.875rem; margin:0;'>
                    Actualiza tu plan para generar más scripts
                </p>
            </div>
            """, unsafe_allow_html=True)

        col_izq, col_der = st.columns([1.1, 0.9], gap="large")

        with col_izq:
            st.markdown('<div class="section-label">Tu contenido</div>', unsafe_allow_html=True)
            tema = st.text_area("Tema o idea del video",
                placeholder="Ej: 5 herramientas de IA que todo creador necesita en 2026", height=110,
                disabled=not puede)
            audiencia = st.text_input("Audiencia objetivo",
                placeholder="Ej: Creadores hispanohablantes de 20–35 años",
                value="Creadores de contenido hispanohablantes", disabled=not puede)
            tono = st.selectbox("Tono del contenido", TONOS, disabled=not puede)

        with col_der:
            st.markdown('<div class="section-label">Plataforma y modo</div>', unsafe_allow_html=True)
            modo = st.radio("Modo", ["Una plataforma", "Todas las plataformas"],
                label_visibility="collapsed", disabled=not puede)

            if modo == "Una plataforma":
                plataforma_seleccionada = st.selectbox("Plataforma",
                    obtener_plataformas(), label_visibility="collapsed", disabled=not puede)
                if puede:
                    info = PLANTILLAS[plataforma_seleccionada]
                    st.markdown(f"""
                    <div class="platform-info">
                        <p><strong>Duración:</strong> {info['duracion']}</p>
                        <p><strong>Estructura:</strong> {info['estructura']}</p>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

        if not puede:
            if st.button("💳 Ver planes y actualizar", type="primary", use_container_width=True):
                st.session_state["ir_a_planes"] = True
                st.rerun()
        else:
            generar = st.button("✦ Generar Script" if tema else "Escribe un tema para continuar",
                type="primary", use_container_width=True, disabled=not tema)

            if generar and tema:
                if not os.getenv("ANTHROPIC_API_KEY"):
                    st.error("Configura tu API Key de Anthropic en el sidebar.")
                else:
                    try:
                        if modo == "Una plataforma":
                            with st.spinner(f"Generando script para {plataforma_seleccionada}..."):
                                script = generar_script(tema=tema, plataforma=plataforma_seleccionada,
                                    tono=tono, audiencia=audiencia)
                            guardar_script(usuario["id"], tema, plataforma_seleccionada, tono, audiencia, script)
                            incrementar_uso(usuario["id"])

                            st.markdown(f"""
                            <div style='display:flex; align-items:center; gap:10px; margin-bottom:1rem;'>
                                <span style='background:rgba(232,130,12,0.12); border:1px solid rgba(232,130,12,0.3);
                                     color:#F5A623; font-size:0.8rem; font-weight:600; padding:4px 12px;
                                     border-radius:20px; text-transform:uppercase;'>{plataforma_seleccionada}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown('<div class="script-output">', unsafe_allow_html=True)
                            st.markdown(script)
                            st.markdown('</div>', unsafe_allow_html=True)

                            ruta_base = os.path.join(
                                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
                            exportar_txt(script, plataforma_seleccionada, tema, ruta_base)
                            col_msg, col_dl = st.columns([2, 1])
                            with col_msg:
                                st.success("✓ Script guardado en tu historial")
                            with col_dl:
                                st.download_button("⬇ Descargar TXT", data=script,
                                    file_name=f"script-{plataforma_seleccionada.lower().replace(' ','-')}.txt",
                                    mime="text/plain", use_container_width=True)
                        else:
                            resultados = {}
                            barra = st.progress(0, text="Preparando...")
                            plataformas = obtener_plataformas()
                            for i, plat in enumerate(plataformas):
                                barra.progress(i / len(plataformas), text=f"Generando {plat}...")
                                resultados[plat] = generar_script(tema=tema, plataforma=plat,
                                    tono=tono, audiencia=audiencia)
                                guardar_script(usuario["id"], tema, plat, tono, audiencia, resultados[plat])
                            incrementar_uso(usuario["id"])
                            barra.progress(1.0, text="✦ Todos los scripts generados")
                            st.success(f"✓ {len(resultados)} scripts guardados")
                            tabs = st.tabs(list(resultados.keys()))
                            for tab, (plat, script) in zip(tabs, resultados.items()):
                                with tab:
                                    st.markdown('<div class="script-output">', unsafe_allow_html=True)
                                    st.markdown(script)
                                    st.markdown('</div>', unsafe_allow_html=True)
                                    st.download_button(f"⬇ {plat}", data=script,
                                        file_name=f"script-{plat.lower().replace(' ','-')}.txt",
                                        mime="text/plain", key=f"dl_{plat}")
                    except Exception as e:
                        st.error(f"Error al generar: {e}")

    # ════════════════════════════════════════
    # TAB 2: HISTORIAL
    # ════════════════════════════════════════
    with tab_historial:
        st.markdown('<div class="section-label">Tus scripts generados</div>', unsafe_allow_html=True)
        historial = obtener_historial(usuario["id"])

        if not historial:
            st.markdown("""
            <div style='text-align:center; padding:3rem; color:#444;'>
                <p style='font-size:2rem; margin-bottom:1rem;'>📝</p>
                <p style='font-size:1rem;'>Aún no has generado ningún script</p>
                <p style='font-size:0.85rem; color:#333;'>Ve a "Generar Script" y crea tu primer guión</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:#555; font-size:0.85rem; margin-bottom:1rem;'>{len(historial)} scripts generados</p>", unsafe_allow_html=True)
            for i, item in enumerate(historial):
                fecha = item.get("created_at", "")[:10] if item.get("created_at") else ""
                with st.expander(f"📄 {item['tema'][:60]}{'...' if len(item['tema']) > 60 else ''}", expanded=False):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"<span style='background:rgba(232,130,12,0.1); color:#E8820C; font-size:0.7rem; padding:2px 8px; border-radius:10px;'>{item['plataforma']}</span>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<span style='color:#555; font-size:0.8rem;'>{item.get('tono','')}</span>", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"<span style='color:#444; font-size:0.8rem;'>{fecha}</span>", unsafe_allow_html=True)
                    st.markdown("<div style='margin:0.75rem 0; height:1px; background:#1e1e1e;'></div>", unsafe_allow_html=True)
                    st.markdown(item["contenido"])
                    st.download_button("⬇ Descargar", data=item["contenido"],
                        file_name=f"script-{item['plataforma'].lower().replace(' ','-')}-{fecha}.txt",
                        mime="text/plain", key=f"hist_dl_{i}")

    # ════════════════════════════════════════
    # TAB 3: PLANES
    # ════════════════════════════════════════
    with tab_planes:
        st.markdown('<div class="section-label">Elige tu plan</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#555; font-size:0.9rem; margin-bottom:2rem;'>Todos los planes incluyen acceso a YouTube, TikTok, Instagram y Reels.</p>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            es_actual = plan_actual == "free"
            st.markdown(f"""
            <div class="plan-card">
                <p class="plan-name">🆓 FREE</p>
                <p class="plan-price">$0<span>/mes</span></p>
                <div style='margin:1.25rem 0;'>
                    <div class="plan-feature">3 scripts al mes</div>
                    <div class="plan-feature">4 plataformas</div>
                    <div class="plan-feature">Exportar TXT</div>
                    <div class="plan-feature" style='color:#444;'>Sin historial</div>
                </div>
                {"<p style='color:#F5A623; font-size:0.85rem; font-weight:600;'>← Plan actual</p>" if es_actual else ""}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            es_actual = plan_actual == "basic"
            st.markdown(f"""
            <div class="plan-card featured">
                <div style='margin-bottom:0.75rem;'><span class="plan-badge">Más popular</span></div>
                <p class="plan-name">⚡ BASIC</p>
                <p class="plan-price">$19<span>/mes</span></p>
                <div style='margin:1.25rem 0;'>
                    <div class="plan-feature">50 scripts al mes</div>
                    <div class="plan-feature">4 plataformas</div>
                    <div class="plan-feature">Exportar TXT</div>
                    <div class="plan-feature">Historial completo</div>
                </div>
                {"<p style='color:#F5A623; font-size:0.85rem; font-weight:600;'>← Plan actual</p>" if es_actual else ""}
            </div>
            """, unsafe_allow_html=True)
            if not es_actual and plan_actual == "free":
                url = crear_checkout_url("basic", usuario["id"], usuario["email"])
                if url:
                    st.link_button("✦ Elegir Basic →", url, use_container_width=True)

        with col3:
            es_actual = plan_actual == "pro"
            st.markdown(f"""
            <div class="plan-card">
                <p class="plan-name">🚀 PRO</p>
                <p class="plan-price">$39<span>/mes</span></p>
                <div style='margin:1.25rem 0;'>
                    <div class="plan-feature">Scripts ilimitados</div>
                    <div class="plan-feature">4 plataformas</div>
                    <div class="plan-feature">Exportar TXT</div>
                    <div class="plan-feature">Historial completo</div>
                </div>
                {"<p style='color:#F5A623; font-size:0.85rem; font-weight:600;'>← Plan actual</p>" if es_actual else ""}
            </div>
            """, unsafe_allow_html=True)
            if not es_actual and plan_actual in ["free", "basic"]:
                url = crear_checkout_url("pro", usuario["id"], usuario["email"])
                if url:
                    st.link_button("✦ Elegir Pro →", url, use_container_width=True)

        st.markdown("""
        <p style='text-align:center; color:#333; font-size:0.8rem; margin-top:2rem;'>
            Pagos seguros procesados por Stripe · Cancela cuando quieras
        </p>
        """, unsafe_allow_html=True)

    # ── Footer ──
    st.markdown("""
    <div style='text-align:center; padding:2rem 0 1rem; border-top:1px solid #1a1a1a; margin-top:2rem;'>
        <p style='color:#333; font-size:0.8rem; margin:0;'>Script & Shorts Studio · Assets Solutions AI · Powered by Claude API</p>
    </div>
    """, unsafe_allow_html=True)


# ── Router ──
if esta_autenticado():
    mostrar_app()
else:
    mostrar_login()
