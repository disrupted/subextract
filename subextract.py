#!/usr/bin/env python3
import argparse
import importlib.metadata
import json
import logging
import subprocess
import sys
from pathlib import Path

import yaml

from language import Language

PACKAGE = "subextract"

parser = argparse.ArgumentParser(description="Extract subtitles from mkv files")
parser.add_argument(
    "-v",
    "--verbose",
    action="store_const",
    help="Increase output verbosity",
    dest="log_level",
    const=logging.DEBUG,
    default=logging.INFO,
)
parser.add_argument(
    "-V",
    "--version",
    action="version",
    version="%(prog)s " + importlib.metadata.version(PACKAGE),
)
group = parser.add_mutually_exclusive_group()
group.add_argument(
    "--id",
    type=int,
    help="Track id to extract",
)
group.add_argument(
    "--lang",
    type=lambda l: Language[l.upper()],
    help=f"Language to extract (default: {Language.EN.value})",
    default=Language.EN,
)
parser.add_argument(
    "file",
    nargs="+",
    metavar="FILE",
    type=argparse.FileType("r"),
    help="the .mkv video file",
)


def mkvextract(track_id: int, path: Path, out_filename: str):
    mkvextract_args = [
        "mkvextract",
        path,
        "tracks",
        f"{track_id}:{out_filename}",
    ]
    proc = subprocess.run(mkvextract_args)
    return proc


def identify(path: Path) -> dict:
    mkvmerge_args = ["mkvmerge", "-F", "json", "-i", path]
    proc = subprocess.run(mkvmerge_args, stdout=subprocess.PIPE)
    return json.loads(proc.stdout)


def is_lang(track: dict, lang: Language) -> bool:
    return (
        track["codec"] == "SubRip/SRT"
        and track["properties"]["language_ietf"] == lang.value
        and not track["properties"]["forced_track"]
    )


def get_out_name(path: Path, track: dict) -> str:
    return f"{path.stem}.{track['properties']['language_ietf']}.srt"


def extract(path: Path, track: dict):
    logging.info("Extracting subtitle")
    print(yaml.dump(track))
    sub_name = get_out_name(path, track)
    mkvextract(track["id"], path, sub_name)


def main():
    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level,
        format="%(levelname)s | %(message)s",
    )
    for f in args.file:
        path = Path(f.name)
        if path.suffix not in ".mkv":
            logging.error(f"wrong file extension {path.suffix}")
            sys.exit(1)

        data = identify(path)

        if args.id:
            tracks = [data["tracks"][args.id]]
        else:
            tracks = filter(lambda t: is_lang(t, args.lang), data["tracks"])

        if not tracks:
            logging.warning("no matching subtitle tracks found")
            sys.exit(1)

        for track in tracks:
            try:
                extract(path, track)
                break
            except KeyError as e:
                logging.error(e)

    sys.exit(0)


if __name__ == "__main__":
    main()
