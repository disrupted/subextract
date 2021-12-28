import langcodes


class Language:
    def __init__(self, lang: str):
        self._lang = langcodes.Language.get(lang)

    @property
    def alpha1(self):
        """en"""
        return self._lang.to_tag()

    @property
    def alpha2(self):
        """eng"""
        return self._lang.to_alpha3(variant="B")
