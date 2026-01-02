from beat_studio_importer.import_ui import select_tracks
from beat_studio_importer.midi_source import MidiSource
from beat_studio_importer.note_name_map import DEFAULT_NOTE_NAME_MAP, NoteNameMap
from beat_studio_importer.region import Region
from beat_studio_importer.ui import print_key_value
from beat_studio_importer.user_error import UserError
from colorama import Fore, Style
from pathlib import Path


def do_info(path: Path, note_track_name: str | None, metadata_track_name: str | None, note_name_map: NoteNameMap | None) -> None:
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

    print_key_value("Ticks per beat", source.ticks_per_beat)
    for region in regions:
        print(
            Fore.LIGHTYELLOW_EX,
            f"Region {region.region_id}",
            Style.RESET_ALL,
            sep="")
        beat = region.time_signature.basis.value[2]
        print_key_value("MIDI tempo", region.tempo)
        print_key_value("Time signature", region.time_signature)
        print_key_value(
            "QPM tempo (quarter notes per minute)",
            f"{region.qpm:.1f}")
        print_key_value(
            f"BPM tempo (beats per minute, beat={beat})",
            f"{region.bpm:.1f}")
