# translate.py
from googletrans import Translator

def translate(text, target_language):
    if target_language.lower() == "english":
        return text
    try:
        translator = Translator()
        lang_map = {
            "Swahili": "sw",
            "Kinyarwanda": "rw",
            "Luganda": "lg",
            "English": "en"
        }
        dest = lang_map.get(target_language, "en")
        translated = translator.translate(text, dest=dest)
        return translated.text
    except Exception as e:
        print(f"[TRANSLATE ERROR] {e}")
        return text 