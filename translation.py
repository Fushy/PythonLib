from googletrans import Translator

def translate(text, src="en", dest="fr"):
    """
    text_to_translate = "Hello, how are you?"
    translated_text = translate(text_to_translate)
    print(translated_text)
    """
    src = "zh-CN" if src == "Chinese" else src
    return Translator().translate(text, src=src, dest=dest).text
