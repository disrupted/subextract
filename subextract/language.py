from __future__ import annotations

from dataclasses import dataclass

import langcodes


@dataclass(frozen=True)
class Language:
    _lang: langcodes.Language

    @staticmethod
    def from_str(lang: str) -> Language:
        return Language(langcodes.Language.get(lang))

    @property
    def alpha1(self):
        """en"""
        return self._lang.to_tag()

    @property
    def alpha2(self):
        """eng"""
        return self._lang.to_alpha3(variant="B")


DEFAULT_LANGUAGE = Language.from_str(langcodes.DEFAULT_LANGUAGE)
