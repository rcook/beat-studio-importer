from dataclasses import dataclass
from mido import MidiFile, MidiTrack
from pathlib import Path
from typing import TypeVar, cast


T = TypeVar("T", bound="MidiSource")


@dataclass(frozen=True)
class MidiSource:
    path: Path
    file: MidiFile
    ticks_per_beat: int
    tracks: list[MidiTrack]

    @classmethod
    def load(cls: type[T], path: Path) -> T:
        file = MidiFile(path)
        tracks = cast(list[MidiTrack], file.tracks)
        return cls(
            path=path,
            file=file,
            ticks_per_beat=file.ticks_per_beat,
            tracks=tracks)
