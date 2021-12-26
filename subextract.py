#!/usr/bin/env python3
import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

import yaml

parser = argparse.ArgumentParser(description="SubExtract")
parser.add_argument(
    "file",
    metavar="F",
    type=argparse.FileType("r"),
    help="the .mkv video file",
)

args = parser.parse_args()
path = Path(args.file.name)
if path.suffix not in ".mkv":
    logging.error(f"wrong file extension {path.suffix}")
    sys.exit(1)


def mkvextract(track_id, out_filename):
    mkvextract_args = [
        "mkvextract",
        args.file.name,
        "tracks",
        f"{track_id}:{out_filename}",
    ]
    result = subprocess.run(mkvextract_args)
    return result


def identify(filename: str) -> dict:
    mkvmerge_args = ["mkvmerge", "-F", "json", "-i", filename]
    result = subprocess.run(mkvmerge_args, stdout=subprocess.PIPE)
    return json.loads(result.stdout)


def filter(track: dict) -> bool:
    return (
        track["codec"] == "SubRip/SRT"
        and track["properties"]["language"] in "eng"  # TODO: use language enum
        and not track["properties"]["forced_track"]
    )


data = identify(args.file.name)
tracks = [track for track in data["tracks"] if filter(track)]

if not tracks:
    logging.warning("no matching subtitle tracks found")
    sys.exit(1)

for track in tracks:
    try:
        logging.info(yaml.dump(track))
        sub_name = path.stem + ".en.srt"
        mkvextract(track["id"], sub_name)
        break
    except KeyError:
        continue

sys.exit(0)
