from pathlib import Path

import pytest

from subextract.cli import get_out_name, is_lang, is_sdh, parser
from subextract.language import DEFAULT_LANGUAGE, Language


def make_track(**properties: object) -> dict:
    return {
        "id": 2,
        "codec": "SubRip/SRT",
        "properties": {"language": "eng", "forced_track": False, **properties},
    }


def test_language():
    lang = Language.from_str("de")
    assert lang.alpha1 == "de"
    assert lang.alpha2 == "ger"
    assert DEFAULT_LANGUAGE.alpha1 == "en"


def test_parse_lang():
    args = parser.parse_args(["--lang", "fr", "movie.mkv"])
    assert args.lang == Language.from_str("fr")
    assert args.file == [Path("movie.mkv")]


def test_is_lang():
    assert is_lang(make_track(), DEFAULT_LANGUAGE)
    assert not is_lang(make_track(), Language.from_str("de"))
    assert not is_lang(make_track(forced_track=True), DEFAULT_LANGUAGE)
    assert not is_lang({**make_track(), "codec": "PGS"}, DEFAULT_LANGUAGE)


@pytest.mark.parametrize(
    ("properties", "sdh", "expected"),
    [
        ({}, False, True),
        ({}, True, False),
        ({"flag_hearing_impaired": True}, True, True),
        ({"flag_hearing_impaired": True}, False, False),
        ({"track_name": "English SDH"}, True, True),
    ],
)
def test_is_sdh(properties: dict, sdh: bool, expected: bool):
    assert is_sdh(make_track(**properties), sdh) is expected


def test_get_out_name():
    assert get_out_name(Path("/media/movie.mkv"), make_track()) == "movie.en.srt"
