"""
Módulo de Seguridad — Assets Solutions AI
Proyecto 02: Script + Shorts Studio

Protecciones:
- Rate limiting por usuario y por IP
- Validación y sanitización de inputs
- Protección contra prompts maliciosos
- Límites de tokens para Claude API
"""

import time
import hashlib
import re
import streamlit as st
from datetime import datetime, timedelta
from collections import defaultdict

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE LÍMITES
# ─────────────────────────────────────────────
RATE_LIMITS = {
    "generaciones_por_minuto": 3,       # Max scripts por minuto por usuario
    "generaciones_por_hora":   20,      # Max scripts por hora por usuario
    "intentos_login":          5,       # Max intentos de login fallidos
    "intentos_login_ventana":  300,     # Segundos (5 minutos)
    "max_tema_chars":          500,     # Max caracteres en el tema
    "max_audiencia_chars":     200,     # Max caracteres en audiencia
    "min_tema_chars":          10,      # Min caracteres en el tema
    "max_tokens_claude":       2000,    # Max tokens para Claude API
}

# Palabras/patrones que indican prompt injection o abuso
PATRONES_MALICIOSOS = [
    r"ignore (previous|all) instructions",
    r"forget (everything|all)",
    r"you are now",
    r"act as (a|an)",
    r"jailbreak",
    r"prompt injection",
    r"system prompt",
    r"<script",
    r"javascript:",
    r"eval\(",
    r"exec\(",
    r"__import__",
    r"os\.system",
    r"subprocess",
]

# ─────────────────────────────────────────────
# RATE LIMITER EN MEMORIA
# ─────────────────────────────────────────────
class RateLimiter:
    def __init__(self):
        # {user_id: [(timestamp, accion), ...]}
        self._registros = defaultdict(list)
        self._intentos_login = defaultdict(list)

    def _limpiar_viejos(self, user_id: str, ventana_segundos: int):
        """Elimina registros más viejos que la ventana de tiempo."""
        ahora = time.time()
        self._registros[user_id] = [
            (ts, accion) for ts, accion in self._registros[user_id]
            if ahora - ts < ventana_segundos
        ]

    def puede_generar(self, user_id: str) -> tuple[bool, str]:
        """
        Verifica si el usuario puede generar un script ahora.
        Retorna (puede_generar, mensaje_error)
        """
        ahora = time.time()

        # Limpiar registros viejos (1 hora)
        self._limpiar_viejos(user_id, 3600)
        registros = self._registros[user_id]

        # Verificar límite por MINUTO
        en_ultimo_minuto = sum(
            1 for ts, _ in registros if ahora - ts < 60
        )
        if en_ultimo_minuto >= RATE_LIMITS["generaciones_por_minuto"]:
            segundos_espera = int(60 - (ahora - min(
                ts for ts, _ in registros if ahora - ts < 60
            )))
            return False, f"⏱️ Demasiadas solicitudes. Espera {segundos_espera} segundos."

        # Verificar límite por HORA
        en_ultima_hora = len(registros)
        if en_ultima_hora >= RATE_LIMITS["generaciones_por_hora"]:
            return False, f"📊 Alcanzaste el límite de {RATE_LIMITS['generaciones_por_hora']} generaciones por hora."

        return True, ""

    def registrar_generacion(self, user_id: str):
        """Registra una generación exitosa."""
        self._registros[user_id].append((time.time(), "generacion"))

    def puede_hacer_login(self, email: str) -> tuple[bool, str]:
        """Verifica intentos de login — protección contra fuerza bruta."""
        ahora = time.time()
        ventana = RATE_LIMITS["intentos_login_ventana"]
        key = hashlib.md5(email.encode()).hexdigest()

        # Limpiar intentos viejos
        self._intentos_login[key] = [
            ts for ts in self._intentos_login[key]
            if ahora - ts < ventana
        ]

        if len(self._intentos_login[key]) >= RATE_LIMITS["intentos_login"]:
            minutos = int(ventana / 60)
            return False, f"🔒 Demasiados intentos fallidos. Espera {minutos} minutos."

        return True, ""

    def registrar_intento_login_fallido(self, email: str):
        """Registra un intento de login fallido."""
        key = hashlib.md5(email.encode()).hexdigest()
        self._intentos_login[key].append(time.time())


# ─────────────────────────────────────────────
# INSTANCIA GLOBAL (persiste durante la sesión)
# ─────────────────────────────────────────────
@st.cache_resource
def obtener_rate_limiter() -> RateLimiter:
    return RateLimiter()


# ─────────────────────────────────────────────
# VALIDACIÓN DE INPUTS
# ─────────────────────────────────────────────
def validar_tema(tema: str) -> tuple[bool, str]:
    """Valida y sanitiza el tema del script."""
    if not tema or not tema.strip():
        return False, "El tema no puede estar vacío."

    tema = tema.strip()

    if len(tema) < RATE_LIMITS["min_tema_chars"]:
        return False, f"El tema debe tener al menos {RATE_LIMITS['min_tema_chars']} caracteres."

    if len(tema) > RATE_LIMITS["max_tema_chars"]:
        return False, f"El tema no puede tener más de {RATE_LIMITS['max_tema_chars']} caracteres."

    # Detectar prompt injection
    tema_lower = tema.lower()
    for patron in PATRONES_MALICIOSOS:
        if re.search(patron, tema_lower, re.IGNORECASE):
            return False, "⚠️ El tema contiene contenido no permitido. Por favor escribe un tema de contenido normal."

    return True, tema


def validar_audiencia(audiencia: str) -> tuple[bool, str]:
    """Valida la audiencia objetivo."""
    if not audiencia or not audiencia.strip():
        return False, "La audiencia no puede estar vacía."

    audiencia = audiencia.strip()

    if len(audiencia) > RATE_LIMITS["max_audiencia_chars"]:
        return False, f"La audiencia no puede tener más de {RATE_LIMITS['max_audiencia_chars']} caracteres."

    # Detectar prompt injection
    audiencia_lower = audiencia.lower()
    for patron in PATRONES_MALICIOSOS:
        if re.search(patron, audiencia_lower, re.IGNORECASE):
            return False, "⚠️ La audiencia contiene contenido no permitido."

    return True, audiencia


def sanitizar_texto(texto: str) -> str:
    """Elimina caracteres potencialmente peligrosos."""
    # Remover caracteres de control excepto saltos de línea
    texto = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', texto)
    # Limitar múltiples saltos de línea
    texto = re.sub(r'\n{4,}', '\n\n\n', texto)
    return texto.strip()


# ─────────────────────────────────────────────
# DECORADOR PARA PROTEGER GENERACIONES
# ─────────────────────────────────────────────
def proteger_generacion(user_id: str, tema: str, audiencia: str) -> tuple[bool, str]:
    """
    Validación completa antes de generar un script.
    Retorna (puede_proceder, mensaje_error)
    """
    limiter = obtener_rate_limiter()

    # 1. Rate limiting
    puede, msg = limiter.puede_generar(user_id)
    if not puede:
        return False, msg

    # 2. Validar tema
    valido, resultado = validar_tema(tema)
    if not valido:
        return False, resultado

    # 3. Validar audiencia
    valido, resultado = validar_audiencia(audiencia)
    if not valido:
        return False, resultado

    return True, ""


def registrar_generacion_exitosa(user_id: str):
    """Llama esto después de cada generación exitosa."""
    limiter = obtener_rate_limiter()
    limiter.registrar_generacion(user_id)


def verificar_login(email: str) -> tuple[bool, str]:
    """Verifica si se puede intentar login."""
    limiter = obtener_rate_limiter()
    return limiter.puede_hacer_login(email)


def registrar_login_fallido(email: str):
    """Registra un intento de login fallido."""
    limiter = obtener_rate_limiter()
    limiter.registrar_intento_login_fallido(email)


# ─────────────────────────────────────────────
# WIDGET DE ESTADO DE SEGURIDAD (para sidebar)
# ─────────────────────────────────────────────
def mostrar_estado_seguridad(user_id: str):
    """Muestra el estado del rate limiting en el sidebar."""
    limiter = obtener_rate_limiter()
    ahora = time.time()

    # Limpiar y contar
    limiter._limpiar_viejos(user_id, 3600)
    registros = limiter._registros[user_id]

    en_minuto = sum(1 for ts, _ in registros if ahora - ts < 60)
    en_hora = len(registros)

    limite_minuto = RATE_LIMITS["generaciones_por_minuto"]
    limite_hora = RATE_LIMITS["generaciones_por_hora"]

    # Color según uso
    color_minuto = "#22c55e" if en_minuto < limite_minuto else "#ef4444"
    color_hora = "#22c55e" if en_hora < limite_hora * 0.8 else "#f59e0b" if en_hora < limite_hora else "#ef4444"

    import streamlit as st
    st.markdown(f"""
    <div style='background:#0a0a0a; border:1px solid #1e1e1e; border-radius:10px; padding:0.75rem; margin-top:0.5rem;'>
        <p style='color:#555; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.1em; margin:0 0 0.5rem;'>Límites API</p>
        <div style='display:flex; justify-content:space-between; margin-bottom:4px;'>
            <span style='color:#666; font-size:0.75rem;'>Por minuto</span>
            <span style='color:{color_minuto}; font-size:0.75rem; font-weight:600;'>{en_minuto}/{limite_minuto}</span>
        </div>
        <div style='display:flex; justify-content:space-between;'>
            <span style='color:#666; font-size:0.75rem;'>Por hora</span>
            <span style='color:{color_hora}; font-size:0.75rem; font-weight:600;'>{en_hora}/{limite_hora}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
