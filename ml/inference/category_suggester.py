"""
Módulo de categorización inteligente híbrida para Reporte Bolívar.
Cuando un reporte no encaja con las categorías conocidas (baja similitud con centroides),
este módulo analiza la descripción y contexto para proponer:
1. Un identificador interno normalizado (ej: 'cables_caidos')
2. Un nombre legible (ej: 'Cables caídos en vía pública')
3. El Área municipal correspondiente ('Infraestructura', 'Higiene Urbana', 'Animales', 'Tránsito y Estacionamiento')
4. Una breve descripción explicativa.

Estrategia Híbrida:
- Si GEMINI_API_KEY o GOOGLE_API_KEY está configurada, utiliza Gemini 1.5 Flash vía REST/SDK.
- Si no hay API key o hay error de red, utiliza un analizador semántico local por reglas municipales.
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

MUNICIPAL_AREAS = [
    "Infraestructura",
    "Higiene Urbana",
    "Animales",
    "Tránsito y Estacionamiento",
]

AREA_KEYWORDS = {
    "Infraestructura": [
        "pozo", "bache", "calzada", "asfalto", "calle", "vereda", "cordon", "agua", "caño",
        "perdida", "tuberia", "luz", "luminaria", "foco", "poste", "columna", "cable", "cables",
        "chispa", "electricidad", "peligro", "semaforo", "arbol", "rama", "zanja", "desague",
        "pluvial", "cloaca", "gas", "puente", "senal", "cartel", "derrumbe"
    ],
    "Higiene Urbana": [
        "basura", "residuos", "microbasural", "basural", "escombros", "ramas", "pasto",
        "terreno", "baldio", "desecho", "suciedad", "limpieza", "olor", "contenedor", "tacho",
        "reciclaje", "chatarra", "hojas"
    ],
    "Animales": [
        "perro", "perros", "gato", "gatos", "caballo", "caballos", "mascota", "animal",
        "animales", "cachorro", "suelto", "perdido", "encontrado", "herido", "mordedura",
        "rabia", "zoonosis", "ave", "pajaro", "murcielago", "orugas", "plaga", "abejas", "avispa"
    ],
    "Tránsito y Estacionamiento": [
        "auto", "automovil", "coche", "camioneta", "camion", "moto", "motocicleta", "colectivo",
        "vehiculo", "estacionado", "estacionamiento", "garage", "entrada", "rampa", "discapacidad",
        "ochava", "contramano", "patente", "abandonado", "bloqueando", "obstruyendo", "velocidad"
    ],
}


def slugify_name(text: str) -> str:
    """Convierte texto en un identificador limpio snake_case."""
    text = text.lower().strip()
    text = re.sub(r'[áàäâ]', 'a', text)
    text = re.sub(r'[éèëê]', 'e', text)
    text = re.sub(r'[íìïî]', 'i', text)
    text = re.sub(r'[óòöô]', 'o', text)
    text = re.sub(r'[úùüû]', 'u', text)
    text = re.sub(r'ñ', 'n', text)
    text = re.sub(r'[^a-z0-9\s_]', '', text)
    text = re.sub(r'[\s]+', '_', text)
    return text[:40].strip('_')


def infer_area_local(text: str) -> str:
    """Infiere el área municipal a partir de las palabras clave del texto (soporta plurales/variaciones)."""
    text_lower = text.lower()
    scores = {area: 0 for area in MUNICIPAL_AREAS}
    
    for area, kws in AREA_KEYWORDS.items():
        for kw in kws:
            # Coincide con palabra exacta o con plural (kw + s/es)
            pattern = r'\b' + re.escape(kw) + r'(?:s|es)?\b'
            if re.search(pattern, text_lower):
                scores[area] += 1
                
    best_area = max(scores, key=scores.get)
    if scores[best_area] > 0:
        return best_area
    return "Infraestructura"  # Default municipal


def suggest_category_local(description: str) -> Dict[str, Any]:
    """Generador semántico local para entornos offline o sin API key."""
    desc_clean = description.strip()
    if not desc_clean:
        return {
            "name": "problematica_urbana",
            "label": "Problemática Urbana General",
            "area": "Infraestructura",
            "description": "Reporte ciudadano general sin clasificar",
            "confidence": 0.50,
            "source": "local_fallback",
        }

    area = infer_area_local(desc_clean)
    
    # Extraer las primeras palabras significativas (omitiendo artículos y preposiciones)
    stopwords = {"de", "la", "el", "en", "un", "una", "los", "las", "por", "para", "con", "y", "a", "al", "del", "hay", "tengo", "veo"}
    words = [w for w in re.findall(r'\b\w+\b', desc_clean.lower()) if w not in stopwords]
    
    if len(words) >= 2:
        short_title = " ".join(words[:3]).capitalize()
        name_slug = slugify_name("_".join(words[:3]))
    elif len(words) == 1:
        short_title = words[0].capitalize()
        name_slug = slugify_name(words[0])
    else:
        short_title = "Reporte no catalogado"
        name_slug = "reporte_no_catalogado"

    return {
        "name": name_slug,
        "label": short_title,
        "area": area,
        "description": desc_clean[:120] if desc_clean else "Reporte de situación ciudadana",
        "confidence": 0.65,
        "source": "local_rule_engine",
    }


def suggest_category_gemini(description: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Consulta la API de Gemini para estructurar la nueva problemática con LLM."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
Eres un clasificador inteligente para la municipalidad de Bolívar, Argentina.
Un vecino reportó la siguiente situación urbana que no coincide con las categorías conocidas:
"{description}"

Debes clasificarla en exactamente una de estas 4 áreas municipales:
- Infraestructura
- Higiene Urbana
- Animales
- Tránsito y Estacionamiento

Responde ÚNICAMENTE un objeto JSON válido con este formato:
{{
  "name": "identificador_en_snake_case_corto_y_especifico",
  "label": "Título Formal y Conciso (ej: Árbol con riesgo de caída, Panal de abejas agresivo)",
  "area": "Una de las 4 áreas mencionadas exactamente",
  "description": "Breve descripción formal de 1 frase del problema"
}}
"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    }
    
    try:
        with httpx.Client(timeout=6.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(raw_text)
                
                # Validar campos
                area = parsed.get("area", "Infraestructura")
                if area not in MUNICIPAL_AREAS:
                    area = infer_area_local(description)
                    
                name = slugify_name(parsed.get("name", "problema_urbano"))
                label = parsed.get("label", name.replace("_", " ").title())
                desc = parsed.get("description", description)
                
                return {
                    "name": name,
                    "label": label,
                    "area": area,
                    "description": desc,
                    "confidence": 0.88,
                    "source": "gemini_llm",
                }
            else:
                logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}")
                return None
    except Exception as e:
        logger.warning(f"Error calling Gemini API: {e}")
        return None


def suggest_category(description: str) -> Dict[str, Any]:
    """
    Función principal híbrida: intenta con Gemini si está configurada la key,
    sino utiliza el fallback semántico local.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        gemini_result = suggest_category_gemini(description, api_key)
        if gemini_result:
            return gemini_result
            
    return suggest_category_local(description)
