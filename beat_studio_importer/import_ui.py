from beat_studio_importer.region import Region
from beat_studio_importer.user_error import UserError
from collections.abc import Callable
from colorama import Fore, Style
from mido import MidiTrack
from pathlib import Path
from typing import cast


def select_tracks(path: Path, tracks: list[MidiTrack], track_name: str | None, metadata_track_name: str | None) -> tuple[MidiTrack, MidiTrack]:
    track = select_single_track(path, tracks, "track", track_name)
    metadata_track = select_single_track(
        path,
        tracks,
        "metadata track",
        metadata_track_name)
    return track, metadata_track


def select_track_interactive(path: Path, tracks: list[MidiTrack], prompt: str) -> MidiTrack:
    return select_interactive(path, tracks, "tracks", prompt, lambda t: cast(str, t.name))


def get_track_by_name_or_index(tracks: list[MidiTrack], track_name_or_id: str) -> MidiTrack:
    track = next(
        filter(lambda t: cast(str, t.name) == track_name_or_id, tracks),
        None)
    if track is not None:
        return track

    try:
        track_id = int(track_name_or_id)
    except ValueError:
        raise UserError(f"No track with name or ID {track_name_or_id}")

    if track_id < 1 or track_id > len(tracks):
        raise UserError(f"No track with name or ID {track_name_or_id}")

    return tracks[track_id - 1]


def select_single_track(path: Path, tracks: list[MidiTrack], prompt: str, name: str | None) -> MidiTrack:
    if name is None:
        match len(tracks):
            case 0: raise UserError(f"No tracks in {path}")
            case 1: return tracks[0]
            case _: return select_track_interactive(path, tracks, prompt)
    else:
        return get_track_by_name_or_index(tracks, name)


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
    return select_interactive(path, regions, "regions", "region", descriptor=lambda r: r.descriptor)


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


def select_interactive[T](path: Path, items: list[T], description: str, prompt: str, descriptor: Callable[[T], str]) -> T:
    count = len(items)
    assert count > 0

    print(
        f"Available {description} in file ",
        Fore.CYAN,
        path.name,
        Style.RESET_ALL,
        sep="")
    for i, region in enumerate(items, 1):
        s = descriptor(region)
        print(
            Fore.LIGHTYELLOW_EX,
            f"({i}) ",
            Fore.LIGHTCYAN_EX,
            s,
            Style.RESET_ALL,
            sep="")

    idx = get_index(prompt, count)
    return items[idx]
