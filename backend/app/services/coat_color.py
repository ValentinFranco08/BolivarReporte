"""Compatibilidad conservadora entre descripciones explícitas del pelaje."""
import re
import unicodedata

COLOR_FAMILIES = {
    "negro": "negro", "negra": "negro", "negras": "negro", "negros": "negro",
    "blanco": "blanco", "blanca": "blanco", "blancas": "blanco", "blancos": "blanco",
    "dorado": "marron", "dorada": "marron", "dorazo": "marron",
    "canela": "marron", "rubio": "marron", "rubia": "marron",
    "marron": "marron", "castano": "marron", "castana": "marron",
}
DESCRIPTION_WORDS = {
    "color", "pelaje", "con", "y", "de", "mancha", "manchas",
    "pecho", "patas", "hocico", "en", "el", "la", "las", "los",
}


def declared_colors(description):
    normalized = unicodedata.normalize("NFD", (description or "").casefold())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    words = set(re.findall(r"\w+", normalized)) - DESCRIPTION_WORDS
    # Cualquier palabra desconocida puede indicar otro color, duda o negación.
    if not words or not words <= COLOR_FAMILIES.keys():
        return set()
    return {COLOR_FAMILIES[word] for word in words}


def incompatible_coat_colors(first, second):
    left, right = declared_colors(first), declared_colors(second)
    return bool(left and right and left.isdisjoint(right))
