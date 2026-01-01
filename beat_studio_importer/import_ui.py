from beat_studio_importer.descriptor import HasDescriptor
from beat_studio_importer.region import Region
from beat_studio_importer.track_summary import TrackSummary
from beat_studio_importer.user_error import UserError
from colorama import Fore, Style
from mido import MidiTrack
from pathlib import Path


def select_tracks(path: Path, tracks: list[MidiTrack], note_track_name: str | None, metadata_track_name: str | None) -> tuple[MidiTrack, MidiTrack]:
    track_summaries = [TrackSummary.summarize(t) for t in tracks]
    note_track_summary = select_track(
        path,
        track_summaries,
        "note track",
        note_track_name)
    metadata_track_summary = select_track(
        path,
        track_summaries,
        "metadata track",
        metadata_track_name)
    return note_track_summary.track, metadata_track_summary.track


def select_track_interactive(path: Path, track_summaries: list[TrackSummary], prompt: str) -> TrackSummary:
    return select_interactive(path, track_summaries, "tracks", prompt)


def get_track_by_name_or_index(track_summaries: list[TrackSummary], track_name_or_id: str) -> TrackSummary:
    track_summary = next(
        filter(lambda t: t.name == track_name_or_id, track_summaries),
        None)
    if track_summary is not None:
        return track_summary

    try:
        track_id = int(track_name_or_id)
    except ValueError:
        raise UserError(f"No track with name or ID {track_name_or_id}")

    if track_id < 1 or track_id > len(track_summaries):
        raise UserError(f"No track with name or ID {track_name_or_id}")

    return track_summaries[track_id - 1]


def select_track(path: Path, track_summaries: list[TrackSummary], prompt: str, name: str | None) -> TrackSummary:
    if name is None:
        match len(track_summaries):
            case 0: raise UserError(f"No tracks in {path}")
            case 1: return track_summaries[0]
            case _: return select_track_interactive(path, track_summaries, prompt)
    else:
        return get_track_by_name_or_index(track_summaries, name)


def select_region(path: Path, regions: list[Region], region_id: int | None) -> Region:
    if region_id is None:
        match len(regions):
            case 0: raise UserError(f"No regions in {path}")
            case 1: return regions[0]
            case _: return select_region_interactive(path, regions)
    else:
        if region_id < 1 or region_id > len(regions):
            raise UserError(f"No region with ID {region_id}")
        return regions[region_id - 1]


def select_region_interactive(path: Path, regions: list[Region]) -> Region:
    return select_interactive(path, regions, "regions", "region")


def get_index(prompt: str, max: int) -> int:
    while True:
        value = input(f"Select {prompt} 1-{max}: ")
        if value == "":
            raise UserError("Operation cancelled")

        idx: int | None = None
        try:
            idx = int(value)
        except ValueError:
            pass

        if idx is not None and idx >= 1 and idx <= max:
            return idx - 1


def select_interactive[T: HasDescriptor](path: Path, items: list[T], description: str, prompt: str) -> T:
    count = len(items)
    assert count > 0

    print(
        f"Available {description} in file ",
        Fore.CYAN,
        path.name,
        Style.RESET_ALL,
        sep="")
    for i, region in enumerate(items, 1):
        descriptor = region.descriptor
        if descriptor.name is None:
            d = [descriptor.description]
        else:
            d = [
                Fore.LIGHTCYAN_EX,
                descriptor.name,
                Fore.WHITE,
                " (",
                descriptor.description,
                ")"
            ]

        print(
            Fore.LIGHTYELLOW_EX,
            f"({i}) ",
            Fore.LIGHTCYAN_EX,
            *d,
            Style.RESET_ALL,
            sep="")

    idx = get_index(prompt, count)
    return items[idx]
