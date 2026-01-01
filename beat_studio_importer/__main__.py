# pyright: reportAny=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownLambdaType=false
# pyright: reportUnknownMemberType=false

from argparse import ArgumentParser, Namespace
from beat_studio_importer.import_command import do_import
from beat_studio_importer.note_name_map import NoteNameMap
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.user_error import UserError
from colorama import Fore, Style
from pathlib import Path
import sys


def do_import_args(args: Namespace) -> None:
    note_map = None \
        if args.note_name_path is None \
        else NoteNameMap.load(args.note_name_path)

    track_name = args.track_name
    metadata_track_name = args.metadata_track_name
    if metadata_track_name is None and track_name is not None:
        metadata_track_name = track_name

    quantize = NoteValue.from_denominator(args.quantize)

    do_import(
        path=args.path,
        track_name=track_name,
        metadata_track_name=metadata_track_name,
        note_name_map=note_map,
        region_id=args.region,
        quantize=quantize,
        name=args.name)


def main(cwd: Path, argv: list[str]) -> None:
    def resolved_path(s: str) -> Path:
        return (cwd / Path(s).expanduser()).resolve()

    parser = ArgumentParser(prog="beat-studio-importer")
    parsers = parser.add_subparsers(required=True)

    p = parsers.add_parser(name="import")
    p.set_defaults(func=do_import_args)
    _ = p.add_argument(
        dest="path",
        metavar="PATH",
        type=resolved_path,
        help="path of file to import")
    _ = p.add_argument(
        "--note-name-path",
        "-n",
        dest="note_name_path",
        metavar="NOTE_NAME_PATH",
        type=resolved_path,
        default=None,
        required=False,
        help="path to note name file")
    _ = p.add_argument(
        "--track",
        "-t",
        dest="track_name",
        metavar="TRACK_NAME",
        type=str,
        default=None,
        help="track name")
    _ = p.add_argument(
        "--metadata-track",
        "-m",
        dest="metadata_track_name",
        metavar="METADATA_TRACK_NAME",
        type=str,
        default=None,
        help="metadata track name (tempo and time signature track etc.)")
    _ = p.add_argument(
        "--region",
        "-r",
        dest="region",
        metavar="REGION",
        type=int,
        default=None,
        help="region index")
    _ = p.add_argument(
        "--quantize",
        "-q",
        dest="quantize",
        metavar="QUANTIZE",
        type=int,
        choices=sorted(member.value for member in NoteValue),
        default=NoteValue.SIXTEENTH.value,
        help="quantize step (4=quarter note, 8=eighth etc.)")
    _ = p.add_argument(
        "--name",
        dest="name",
        metavar="NAME",
        type=str,
        default=None,
        help="pattern name")

    args = parser.parse_args(argv)
    result: object = None
    try:
        result = args.func(args)
    except KeyboardInterrupt:
        print("\n",
              Fore.LIGHTRED_EX,
              "Operation cancelled",
              Style.RESET_ALL,
              sep="",
              file=sys.stderr)
        sys.exit(2)
    except UserError as e:
        print(Fore.LIGHTRED_EX, str(e), Style.RESET_ALL, sep="", file=sys.stderr)
        sys.exit(1)

    if result is None:
        pass
    else:
        raise NotImplementedError()
