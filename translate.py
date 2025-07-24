# translate.py
from deep_translator import GoogleTranslator

def translate(text, target='sw'):
    return GoogleTranslator(source='auto', target=target).translate(text)
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