"""
Módulo de autenticación — Assets Solutions AI
Proyecto 02: Script + Shorts Studio
"""

import os
import streamlit as st
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def obtener_cliente_supabase() -> Client:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    token = st.session_state.get("access_token")
    if token:
        client.postgrest.auth(token)
    return client

def inicializar_sesion():
    if "usuario" not in st.session_state:
        st.session_state.usuario = None
    if "sesion_activa" not in st.session_state:
        st.session_state.sesion_activa = False
    if "access_token" not in st.session_state:
        st.session_state.access_token = None

def esta_autenticado() -> bool:
    params = st.query_params
    if "code" in params and not st.session_state.get("sesion_activa"):
        code = params["code"]
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            session = supabase.auth.exchange_code_for_session({"auth_code": code})
            if session and session.user:
                st.session_state.usuario = {
                    "id": session.user.id,
                    "email": session.user.email,
                    "nombre": session.user.user_metadata.get("full_name",
                              session.user.user_metadata.get("name",
                              session.user.email.split("@")[0])),
                }
                st.session_state.sesion_activa = True
                st.session_state.access_token = session.session.access_token
                st.query_params.clear()
                return True
        except Exception:
            st.query_params.clear()
            return False
    return st.session_state.get("sesion_activa", False)

def obtener_usuario():
    return st.session_state.get("usuario", None)

def cerrar_sesion():
    st.session_state.usuario = None
    st.session_state.sesion_activa = False
    st.session_state.access_token = None
    st.rerun()

def registrar_usuario(email: str, password: str, nombre: str) -> dict:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": nombre}}
        })
        if response.user:
            return {"ok": True, "mensaje": "Cuenta creada. Revisa tu email para confirmar."}
        return {"ok": False, "mensaje": "Error al crear la cuenta."}
    except Exception as e:
        return {"ok": False, "mensaje": str(e)}

def login_email(email: str, password: str) -> dict:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            st.session_state.usuario = {
                "id": response.user.id,
                "email": response.user.email,
                "nombre": response.user.user_metadata.get("full_name",
                          email.split("@")[0]),
            }
            st.session_state.sesion_activa = True
            st.session_state.access_token = response.session.access_token
            return {"ok": True}
        return {"ok": False, "mensaje": "Credenciales incorrectas."}
    except Exception as e:
        error = str(e)
        if "Invalid login credentials" in error:
            return {"ok": False, "mensaje": "Email o contraseña incorrectos."}
        if "Email not confirmed" in error:
            return {"ok": False, "mensaje": "Confirma tu email antes de iniciar sesión."}
        return {"ok": False, "mensaje": error}

def obtener_url_google() -> str:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        app_url = os.getenv("APP_URL", "http://localhost:8501")
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": app_url}
        })
        return response.url
    except Exception:
        return None
