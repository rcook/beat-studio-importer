from beat_studio_importer.grid import Grid
from beat_studio_importer.import_ui import select_region, select_tracks
from beat_studio_importer.note_name_map import DEFAULT_NOTE_NAME_MAP, NoteNameMap
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.region import Region
from beat_studio_importer.user_error import UserError
from mido import MidiFile, MidiTrack
from pathlib import Path
from typing import cast


def do_import(path: Path, note_track_name: str | None, metadata_track_name: str | None, note_name_map: NoteNameMap | None, region_id: int | None, quantize: NoteValue, name: str | None) -> None:
    if not path.is_file():
        raise UserError(f"Input file {path} not found")

    f = MidiFile(path)
    p = cast(Path | None, f.filename)
    assert isinstance(p, Path)
    tracks = cast(list[MidiTrack], f.tracks)
    note_track, metadata_track = select_tracks(
        p,
        tracks,
        note_track_name,
        metadata_track_name)

    note_name_map = note_name_map or DEFAULT_NOTE_NAME_MAP

    regions = Region.from_midi_messages(
        f,
        note_track,
        metadata_track,
        note_name_map)

    region = select_region(p, regions, region_id)

    name = name or f"{p.stem} region {region.region_id}"
    grid = Grid.make(f, quantize, region)
    grid.print(name)
