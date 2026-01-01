from beat_studio_importer.beat_studio_note_name import BeatStudioNoteName
from beat_studio_importer.note import Velocity
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.region import Region
from beat_studio_importer.util import downscale_velocity, midi_tempo_to_qpm
from dataclasses import dataclass
from mido import MidiFile
from typing import TYPE_CHECKING, TypeVar


if TYPE_CHECKING:
    from _typeshed import SupportsWrite


T = TypeVar("T", bound="Grid")


type Hits = dict[BeatStudioNoteName, list[Velocity | None]]


@dataclass(frozen=True)
class Grid:
    quantize: NoteValue
    region: Region
    steps: int
    hits: Hits

    @classmethod
    def make(cls: type[T], f: MidiFile, quantize: NoteValue, region: Region) -> T:
        ticks_per_step, r = divmod(f.ticks_per_beat * 4, quantize.value)
        assert r == 0

        steps, r = divmod(region.ticks, ticks_per_step)
        assert r == 0

        all_hits: Hits = {
            member: [None] * steps
            for member in BeatStudioNoteName
        }

        for (tick, note) in region.notes:
            step, r = divmod(tick, ticks_per_step)
            assert r == 0
            _, note_name, = note.name.value
            hits = all_hits[note_name]
            hits[step] = note.velocity

        return cls(
            quantize=quantize,
            region=region,
            steps=steps,
            hits=all_hits)

    def print(self, name: str, file: "SupportsWrite[str] | None" = None) -> None:
        header = self._make_header(name)
        print(header, file=file)
        temp = list(map(lambda n: (n, n.value), self.hits.keys()))
        note_names = sorted(temp, key=lambda p: p[1])
        width = max(map(lambda p: len(p[1]), temp))
        for note_name, label in note_names:
            hits = self.hits[note_name]
            hit_str = "".join(map(get_velocity_char, hits))
            print(f"{label:<{width}}: {hit_str}", file=file)

    def _make_header(self, name: str) -> str:
        if not all(map(lambda c: c.isprintable(), name)):
            raise ValueError(f"Invalid pattern name {name}")

        encoded_name = name.replace("\"", "\\\"")
        qpm = midi_tempo_to_qpm(self.region.tempo)
        return f"[\"{encoded_name}\" - {self.steps} - {qpm} - {self.quantize.value} - {self.region.time_signature}]"


def get_velocity_char(velocity: Velocity | None) -> str:
    return "." if velocity is None else str(downscale_velocity(velocity))
