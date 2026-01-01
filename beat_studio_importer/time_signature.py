# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownVariableType=false

from beat_studio_importer.note_value import NoteValue
from dataclasses import dataclass
from mido import MetaMessage, tempo2bpm
from typing import TypeVar, cast, override


T = TypeVar("T", bound="TimeSignature")


@dataclass(frozen=True)
class TimeSignature:
    numerator: int
    denominator: NoteValue
    clocks_per_click: int
    notated_32nd_notes_per_beat: int

    @classmethod
    def from_midi_message(cls: type[T], message: MetaMessage) -> T:
        if cast(str, message.type) != "time_signature":
            raise ValueError(f"Invalid MIDI time signature message {message}")

        numerator = cast(int, message.numerator)
        if numerator < 1:
            raise ValueError(f"Invalid numerator {numerator}")

        denominator = NoteValue.from_denominator(
            cast(int, message.denominator))

        return cls(
            numerator=numerator,
            denominator=denominator,
            clocks_per_click=cast(int, message.clocks_per_click),
            notated_32nd_notes_per_beat=cast(int, message.notated_32nd_notes_per_beat))

    @override
    def __repr__(self) -> str:
        return f"{self.numerator}/{self.denominator.value}"

    def ticks_per_bar(self, ticks_per_beat: int) -> int:
        n = 4 * ticks_per_beat * self.numerator
        q, r = divmod(n, self.denominator.value)
        if r != 0:
            raise ValueError(f"Invalid PPQN {ticks_per_beat}")
        return q

    def tempo_to_bpm(self, tempo: int) -> float | int:
        temp0 = tempo2bpm(tempo, (self.numerator, self.denominator.value))
        temp1 = int(temp0)
        if temp0 == temp1:
            return temp1
        else:
            return temp0


DEFAULT_TIME_SIGNATURE: TimeSignature = TimeSignature(
    numerator=4,
    denominator=NoteValue.QUARTER,
    clocks_per_click=24,
    notated_32nd_notes_per_beat=8)
