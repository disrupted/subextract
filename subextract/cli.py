#!/usr/bin/env python3
import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

import yaml

from . import __version__
from .language import Language

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
    version="%(prog)s " + __version__,
)
group = parser.add_mutually_exclusive_group()
group.add_argument(
    "--id",
    type=int,
    help="Track id to extract",
)
group.add_argument(
    "--lang",
    type=Language,
    help="Language to extract (default: en)",
    default=Language("en"),
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
        and track["properties"]["language"] == lang.alpha2
        and not track["properties"]["forced_track"]
    )


def get_out_name(path: Path, track: dict) -> str:
    lang = Language(track["properties"]["language"]).alpha1
    return f"{path.stem}.{lang}.srt"


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
            try:
                tracks = [data["tracks"][args.id]]
            except IndexError:
                logging.error(f"subtitle with id {args.id} doesn't exist")
                sys.exit(1)
        else:
            tracks = [t for t in data["tracks"] if is_lang(t, args.lang)]
            if not tracks:
                logging.warning("no matching subtitle tracks found")
                sys.exit(1)
            logging.debug("found matching tracks\n" + yaml.dump(tracks))

        for track in tracks:
            extract(path, track)
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
