import config
from languages.languages import translations, DEFAULT

class LanguageService:
    @staticmethod
    def get_default_code():
        return DEFAULT

    @staticmethod
    def get_all():
        return translations.values()
    
    @staticmethod
    def get_by_code(lang_code: str):
        return translations[lang_code]
    
    @staticmethod
    def get_default_translation():
        return LanguageService.get_by_code(LanguageService.get_default_code())