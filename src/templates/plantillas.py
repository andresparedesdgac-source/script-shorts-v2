"""
Plantillas de estructura de script por plataforma.
Cada plantilla define la estructura, duración y prompt base para Claude API.
"""

# Tonos disponibles para los scripts
TONOS = [
    "Educativo",
    "Entretenimiento",
    "Motivacional",
    "Informativo",
    "Storytelling",
    "Tutorial paso a paso",
]

# Plantillas por plataforma
PLANTILLAS = {
    "YouTube Largo": {
        "duracion": "8–15 minutos",
        "estructura": "Hook + Intro + 3 secciones + CTA",
        "prompt": """Genera un script completo para un video de YouTube largo (8–15 minutos).

TEMA: {tema}
TONO: {tono}
AUDIENCIA: {audiencia}

ESTRUCTURA REQUERIDA:

## 🎣 HOOK (primeros 10 segundos)
Un gancho potente que enganche al espectador inmediatamente.
Usa una pregunta provocadora, dato sorprendente o promesa de valor.

## 📖 INTRODUCCIÓN (30 segundos)
Presenta el tema, establece credibilidad y anticipa lo que aprenderán.
Incluye una línea de retención: "Quédate hasta el final porque..."

## 📌 SECCIÓN 1: [Subtema 1]
Desarrollo del primer punto clave con ejemplos concretos.
Incluye transición natural al siguiente punto.

## 📌 SECCIÓN 2: [Subtema 2]
Desarrollo del segundo punto clave.
Incluye dato o estadística de apoyo.

## 📌 SECCIÓN 3: [Subtema 3]
Desarrollo del tercer punto clave.
Cierre parcial con resumen de lo aprendido.

## 🎬 CIERRE + CTA (30 segundos)
Resumen de los 3 puntos clave.
Call to action: suscríbete, comenta, comparte.
Pregunta para los comentarios que genere engagement.

INSTRUCCIONES:
- Escribe en español, tono {tono}
- Usa lenguaje natural, como si hablaras a un amigo
- Incluye indicaciones de cámara entre [corchetes] donde sea útil
- Cada sección debe tener 2-3 párrafos hablados
- Marca los momentos de énfasis con **negritas**
""",
    },
    "YouTube Short": {
        "duracion": "30–60 segundos",
        "estructura": "Hook + Punto clave + CTA",
        "prompt": """Genera un script para YouTube Short (30–60 segundos).

TEMA: {tema}
TONO: {tono}
AUDIENCIA: {audiencia}

ESTRUCTURA REQUERIDA:

## 🎣 HOOK (3 segundos)
Primera frase que detenga el scroll. Máximo 10 palabras.

## 💡 PUNTO CLAVE (20–40 segundos)
Desarrolla UNA sola idea de forma directa y concisa.
Sin rodeos, ve directo al valor.

## 🎬 CTA (5 segundos)
Cierre con call to action corto: seguir, guardar, compartir.

INSTRUCCIONES:
- Máximo 150 palabras totales
- Español directo y coloquial
- Cada frase debe aportar valor, sin relleno
- Incluye indicaciones visuales entre [corchetes]
""",
    },
    "Instagram Reel": {
        "duracion": "15–30 segundos",
        "estructura": "Hook visual + Mensaje + CTA",
        "prompt": """Genera un script para Instagram Reel (15–30 segundos).

TEMA: {tema}
TONO: {tono}
AUDIENCIA: {audiencia}

ESTRUCTURA REQUERIDA:

## 🎣 HOOK VISUAL (2 segundos)
Acción o texto en pantalla que capture atención inmediata.

## 💬 MENSAJE PRINCIPAL (15–20 segundos)
Mensaje conciso y visualmente atractivo.
Ideal para texto en pantalla + voz en off.

## 🎬 CTA (3 segundos)
"Guarda esto", "Comparte con alguien que necesite esto", "Sígueme para más".

INSTRUCCIONES:
- Máximo 80 palabras totales
- Prioriza impacto visual — describe qué se ve en pantalla
- Incluye sugerencias de texto overlay entre [TEXTO: ...]
- Tono {tono}, muy Instagram
""",
    },
    "TikTok": {
        "duracion": "15–60 segundos",
        "estructura": "Hook inmediato + Valor + Surprise end",
        "prompt": """Genera un script para TikTok (15–60 segundos).

TEMA: {tema}
TONO: {tono}
AUDIENCIA: {audiencia}

ESTRUCTURA REQUERIDA:

## 🎣 HOOK INMEDIATO (2 segundos)
Frase disruptiva que rompa el patrón del scroll. Sin introducción.

## 💥 VALOR (15–45 segundos)
Contenido de valor directo, ritmo rápido.
Cada frase debe enganchar para la siguiente.
Usa listas, datos sorprendentes o revelaciones.

## 🔄 SURPRISE END (3 segundos)
Giro final inesperado, revelación o pregunta que invite a replay.

INSTRUCCIONES:
- Máximo 120 palabras totales
- Ritmo rápido, frases cortas
- Español muy coloquial, como hablar con amigos
- Incluye indicaciones de transición entre [corchetes]
- El surprise end debe hacer que quieran ver el video de nuevo
""",
    },
}


def obtener_plantilla(plataforma: str) -> dict:
    """Retorna la plantilla para la plataforma indicada."""
    return PLANTILLAS.get(plataforma, PLANTILLAS["YouTube Largo"])


def obtener_plataformas() -> list[str]:
    """Retorna la lista de plataformas disponibles."""
    return list(PLANTILLAS.keys())


def formatear_prompt(plataforma: str, tema: str, tono: str, audiencia: str) -> str:
    """Genera el prompt completo para Claude API con los parámetros del usuario."""
    plantilla = obtener_plantilla(plataforma)
    return plantilla["prompt"].format(
        tema=tema,
        tono=tono,
        audiencia=audiencia,
    )
