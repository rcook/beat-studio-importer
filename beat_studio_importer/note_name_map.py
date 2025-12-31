from beat_studio_importer.note_name import NoteName
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar, cast
import yaml


T = TypeVar("T", bound="NoteNameMap")


@dataclass(frozen=True)
class NoteNameMap:
    name: str
    notes: dict[int, NoteName]

    @classmethod
    def load(cls: type[T], path: Path) -> T:
        with path.open("rt") as f:
            obj = cast(
                dict[str, object],
                yaml.load(stream=f, Loader=yaml.SafeLoader))
        return cls(
            name=cast(str, obj["name"]),
            notes={
                k: NoteName[v.upper()]
                for k, v in cast(dict[int, str], obj["notes"]).items()
            })

    def __getitem__(self, key: int) -> NoteName:
        return self.notes[key]

    def save(self, path: Path) -> None:
        with path.open("wt") as f:
            yaml.dump({
                "name": self.name,
                "notes": {
                    k: v.name.lower()
                    for k, v in self.notes.items()
                }
            }, stream=f)


DEFAULT_NOTE_NAME_MAP: NoteNameMap = NoteNameMap(
    name="General MIDI Drums",
    notes={
        36: NoteName.RIGHT_KICK_HIT,
        38: NoteName.SNARE_HIT,
        42: NoteName.HI_HAT_CLOSED,
        47: NoteName.MID_TOM_HIT,
        48: NoteName.HIGH_TOM_HIT
    })
