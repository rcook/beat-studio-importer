# pyright: reportAny=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownLambdaType=false
# pyright: reportUnknownMemberType=false

from argparse import ArgumentParser, Namespace
from beat_studio_importer.import_command import do_import
from beat_studio_importer.info_command import do_info
from beat_studio_importer.note_name_map import NoteNameMap
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.user_error import UserError
from colorama import Fore, Style
from pathlib import Path
import sys


def do_import_args(args: Namespace) -> None:
    note_track_name = args.note_track_name

    metadata_track_name = args.metadata_track_name
    if metadata_track_name is None and note_track_name is not None:
        metadata_track_name = note_track_name

    note_name_map = None \
        if args.note_name_path is None \
        else NoteNameMap.load(args.note_name_path)

    quantize = NoteValue.from_denominator(args.quantize)

    do_import(
        path=args.path,
        note_track_name=note_track_name,
        metadata_track_name=metadata_track_name,
        note_name_map=note_name_map,
        region_id=args.region,
        quantize=quantize,
        name=args.name,
        override_tempo=args.override_tempo)


def do_info_args(args: Namespace) -> None:
    note_track_name = args.note_track_name

    metadata_track_name = args.metadata_track_name
    if metadata_track_name is None and note_track_name is not None:
        metadata_track_name = note_track_name

    note_name_map = None \
        if args.note_name_path is None \
        else NoteNameMap.load(args.note_name_path)

    do_info(
        path=args.path,
        note_track_name=note_track_name,
        metadata_track_name=metadata_track_name,
        note_name_map=note_name_map)


def resolve_path(cwd: Path, s: str) -> Path:
    return (cwd / Path(s).expanduser()).resolve()


def add_path_arg(parser: ArgumentParser, cwd: Path) -> None:
    def resolved_path(s: str) -> Path:
        return resolve_path(cwd, s)

    _ = parser.add_argument(
        dest="path",
        metavar="PATH",
        type=resolved_path,
        help="path of file to import")


def add_common_args(parser: ArgumentParser, cwd: Path) -> None:
    def resolved_path(s: str) -> Path:
        return resolve_path(cwd, s)

    _ = parser.add_argument(
        "--track",
        "-t",
        dest="note_track_name",
        metavar="NOTE_TRACK_NAME",
        type=str,
        default=None,
        help="track name")
    _ = parser.add_argument(
        "--metadata-track",
        "-m",
        dest="metadata_track_name",
        metavar="METADATA_TRACK_NAME",
        type=str,
        default=None,
        help="metadata track name (tempo and time signature track etc.)")
    _ = parser.add_argument(
        "--note-name-path",
        "-n",
        dest="note_name_path",
        metavar="NOTE_NAME_PATH",
        type=resolved_path,
        default=None,
        required=False,
        help="path to note name file")


def main(cwd: Path, argv: list[str]) -> None:
    parser = ArgumentParser(prog="beat-studio-importer")
    parsers = parser.add_subparsers(required=True)

    p = parsers.add_parser(name="import")
    p.set_defaults(func=do_import_args)
    add_path_arg(p, cwd)
    add_common_args(p, cwd)
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
    _ = p.add_argument(
        "--tempo",
        dest="override_tempo",
        metavar="OVERRIDE_TEMPO",
        type=int,
        default=None,
        help="override tempo in output (to work around Beat Studio tempo bug)")

    p = parsers.add_parser(name="info")
    p.set_defaults(func=do_info_args)
    add_path_arg(p, cwd)
    add_common_args(p, cwd)

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
