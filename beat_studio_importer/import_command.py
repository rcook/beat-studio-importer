from beat_studio_importer.import_ui import select_region, select_tracks
from beat_studio_importer.midi_source import MidiSource
from beat_studio_importer.note_name_map import DEFAULT_NOTE_NAME_MAP, NoteNameMap
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.region import Region
from beat_studio_importer.user_error import UserError
from colorama import Fore, Style
from pathlib import Path


def do_import(path: Path, note_track_name: str | None, metadata_track_name: str | None, note_name_map: NoteNameMap | None, region_id: int | None, quantize: NoteValue, name: str | None) -> None:
    if not path.is_file():
        raise UserError(f"Input file {path} not found")

    source = MidiSource.load(path)
    note_track, metadata_track = select_tracks(
        source.path,
        source.tracks,
        note_track_name,
        metadata_track_name)

    note_name_map = note_name_map or DEFAULT_NOTE_NAME_MAP

    regions = Region.from_midi_messages(
        note_track,
        metadata_track,
        note_name_map,
        source.ticks_per_beat)

    region = select_region(source.path, regions, region_id)

    name = name or f"{source.path.stem} region {region.region_id}"
    pattern = region.render(name, quantize)

    print_key_value("File", source.path)
    print_key_value("Ticks per beat", source.ticks_per_beat)
    print()

    print(Fore.LIGHTYELLOW_EX, end="")
    pattern.print()
    print(Style.RESET_ALL)


def print_key_value(name: str, value: object) -> None:
    print(
        Fore.LIGHTBLUE_EX,
        name,
        ": ",
        Fore.LIGHTCYAN_EX,
        str(value),
        Style.RESET_ALL,
        sep="")
