from deep_translator import GoogleTranslator
import re

def sentence_case(text: str) -> str:
    words = text.split()
    if not words:
        return text

    def fix_word(word):
        if re.fullmatch(r'[A-Z]{2,}', word):
            return word
        return word.lower()

    return words[0].capitalize() + ' ' + ' '.join(fix_word(w) for w in words[1:])

def translate_to_english(text: str, source_lang: str = "az") -> str:
    try:
        translated = GoogleTranslator(source=source_lang, target="en").translate(text)
        return sentence_case(translated)
    except Exception:
        return sentence_case(text)