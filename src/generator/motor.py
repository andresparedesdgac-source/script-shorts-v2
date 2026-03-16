"""
Motor de generación de scripts — Assets Solutions AI
Proyecto 02: Script + Shorts Generator

Contiene los prompts optimizados y la lógica de llamada a Claude API.
"""

import os
import anthropic

# ─────────────────────────────────────────────
# CLIENTE ANTHROPIC
# ─────────────────────────────────────────────

def obtener_cliente():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("No se encontró ANTHROPIC_API_KEY. Configúrala en el sidebar o en el archivo .env")
    return anthropic.Anthropic(api_key=api_key)


# ─────────────────────────────────────────────
# SYSTEM PROMPT — Define el rol del modelo
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """Eres un experto creador de contenido para YouTube y redes sociales con 10 años de experiencia.
Especialista en escritura de guiones virales en español para audiencias hispanohablantes.
Tu objetivo es crear scripts que maximicen la retención, el engagement y las conversiones.

REGLAS ABSOLUTAS:
- Responde SIEMPRE en español
- Sé directo: entrega el script sin introducciones ni explicaciones previas
- Usa lenguaje conversacional y cercano, nunca académico
- Cada frase debe tener un propósito: informar, entretener o retener al espectador
- Nunca uses relleno ni frases vacías"""


# ─────────────────────────────────────────────
# PROMPTS POR FUNCIÓN
# ─────────────────────────────────────────────


def build_shorts_prompt(script_completo: str, tema: str, audiencia: str) -> str:
    return f"""Analiza el siguiente guión y extrae o adapta los 3 mejores momentos para Shorts de YouTube/TikTok/Reels (máximo 60 segundos cada uno).

TEMA ORIGINAL: {tema}
AUDIENCIA: {audiencia}

GUIÓN COMPLETO:
{script_completo}

CRITERIOS PARA SELECCIONAR SHORTS:
- El hook debe funcionar sin contexto previo
- El contenido debe ser completo y con valor por sí solo
- Debe generar curiosidad para ver el video completo

ENTREGA EXACTAMENTE 3 SHORTS en este formato:

═══════════════════════════════════
SHORT #1
═══════════════════════════════════
📌 TÍTULO: [máx 60 caracteres, con gancho emocional]
🎣 HOOK (0-5s): [primera frase impactante, sin saludos]
🎬 CONTENIDO (5-55s): [el clip adaptado, fluido y completo]
🎯 CTA (55-60s): [qué debe hacer el espectador]
⏱️ DURACIÓN ESTIMADA: [X segundos]

═══════════════════════════════════
SHORT #2
[mismo formato]

═══════════════════════════════════
SHORT #3
[mismo formato]"""


# ─────────────────────────────────────────────
# FUNCIONES PRINCIPALES
# ─────────────────────────────────────────────

def generar_script(tema: str, plataforma: str, tono: str, audiencia: str) -> str:
    """
    Genera un script completo usando el prompt de plantillas.py.
    """
    from src.templates.plantillas import formatear_prompt

    cliente = obtener_cliente()

    # Usa el prompt definido en plantillas.py para cada plataforma
    prompt = formatear_prompt(
        plataforma=plataforma,
        tema=tema,
        tono=tono,
        audiencia=audiencia,
    )

    respuesta = cliente.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return respuesta.content[0].text


def generar_script_con_shorts(tema: str, plataforma: str, tono: str, audiencia: str) -> dict:
    """
    Genera un script completo + 3 Shorts derivados.
    Retorna dict con 'script' y 'shorts'
    """
    # 1. Generar el script principal
    script_principal = generar_script(
        tema=tema,
        plataforma=plataforma,
        tono=tono,
        audiencia=audiencia,
    )

    # 2. Generar los Shorts a partir del script
    cliente = obtener_cliente()

    prompt_shorts = build_shorts_prompt(
        script_completo=script_principal,
        tema=tema,
        audiencia=audiencia,
    )

    respuesta_shorts = cliente.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt_shorts}
        ],
    )

    return {
        "script": script_principal,
        "shorts": respuesta_shorts.content[0].text,
    }
