"""
Exportadores de scripts generados.
Soporta exportación a TXT con estructura de carpetas por fecha/tema.
"""

import os
from datetime import datetime


def _crear_carpeta_salida(tema: str, base_dir: str = "outputs") -> str:
    """
    Crea la carpeta de salida con estructura: outputs/YYYY-MM-DD/nombre-tema/

    Returns:
        Ruta absoluta de la carpeta creada
    """
    fecha = datetime.now().strftime("%Y-%m-%d")
    nombre_tema = tema.lower().replace(" ", "-")[:50]
    # Limpiar caracteres no válidos para nombre de carpeta
    nombre_tema = "".join(c for c in nombre_tema if c.isalnum() or c == "-")

    ruta = os.path.join(base_dir, fecha, nombre_tema)
    os.makedirs(ruta, exist_ok=True)
    return ruta


def exportar_txt(script: str, plataforma: str, tema: str, base_dir: str = "outputs") -> str:
    """
    Exporta un script a archivo .txt

    Args:
        script: Contenido del script generado
        plataforma: Nombre de la plataforma (para el nombre del archivo)
        tema: Tema del video (para la estructura de carpetas)
        base_dir: Directorio base de salida

    Returns:
        Ruta del archivo generado
    """
    carpeta = _crear_carpeta_salida(tema, base_dir)
    nombre_archivo = f"script-{plataforma.lower().replace(' ', '-')}.txt"
    ruta_archivo = os.path.join(carpeta, nombre_archivo)

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(f"SCRIPT: {tema}\n")
        f.write(f"PLATAFORMA: {plataforma}\n")
        f.write(f"FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(script)

    return ruta_archivo


def exportar_todos_txt(resultados: dict[str, str], tema: str, base_dir: str = "outputs") -> list[str]:
    """
    Exporta todos los scripts generados a archivos .txt

    Args:
        resultados: Diccionario {plataforma: script}
        tema: Tema del video
        base_dir: Directorio base de salida

    Returns:
        Lista de rutas de archivos generados
    """
    rutas = []
    for plataforma, script in resultados.items():
        ruta = exportar_txt(script, plataforma, tema, base_dir)
        rutas.append(ruta)
    return rutas


def leer_script_exportado(ruta: str) -> str:
    """Lee un script exportado desde archivo."""
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()
