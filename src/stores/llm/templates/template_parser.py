import os

class TemplateParser:

    def __init__(self, language: str=None, default_language="en"): 
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.laguage = None

        self.set_language(language)


    def set_language(self, language: str):
        if not language:
            return None
        
        language_path = os.path.join(self.current_path, "locales", language)
        if language and os.path.exists(language_path):
            self.laguage = language

        
        else:
            self.language = self.default_language

    def get(self, group: str, key, vars: dict={}):
        if not group or not key:
            return None
        
        # Ensure target_language is set to either self.language or self.default_language
        target_language = self.laguage if self.laguage else self.default_language

        group_path = os.path.join(self.current_path, "locales", self.laguage, f"{group}.py" )
        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.default_language, f"{group}.py" )
            target_language = self.default_language

        if not os.path.exists(group_path):
            return None
        
        # import group module
        module = __import__(f"stores.llm.templates.locales.{target_language}.{group}", fromlist=[group])

        if not module:
            return None
        
        key_attribute = getattr(module, key)
        return key_attribute.substitute(vars)