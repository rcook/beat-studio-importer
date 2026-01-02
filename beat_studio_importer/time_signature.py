# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownVariableType=false

from beat_studio_importer.basis import Basis
from beat_studio_importer.note_value import NoteValue
from dataclasses import dataclass
from functools import cached_property
from mido import MetaMessage
from typing import TypeVar, cast, override


# Music theory? How do I systematically determine the standard basis from a time signature?
STANDARD_BASES: dict[tuple[int, NoteValue], Basis] = {
    (3, NoteValue.QUARTER): Basis.QUARTER,
    (4, NoteValue.QUARTER): Basis.QUARTER,
    (5, NoteValue.QUARTER): Basis.QUARTER,
    (7, NoteValue.EIGHTH): Basis.EIGHTH,
    (12, NoteValue.EIGHTH): Basis.DOTTED_QUARTER
}


DEFAULT_CLOCKS_PER_CLICK: int = 24
DEFAULT_NOTATED_32ND_NOTES_PER_BEAT: int = 8


T = TypeVar("T", bound="TimeSignature")


@dataclass(frozen=True)
class TimeSignature:
    numerator: int
    denominator: NoteValue
    clocks_per_click: int = DEFAULT_CLOCKS_PER_CLICK
    notated_32nd_notes_per_beat: int = DEFAULT_NOTATED_32ND_NOTES_PER_BEAT

    @classmethod
    def from_midi_message(cls: type[T], message: MetaMessage) -> T:
        if cast(str, message.type) != "time_signature":
            raise ValueError(f"Invalid MIDI time signature message {message}")

        numerator = cast(int, message.numerator)
        if numerator < 1:
            raise ValueError(f"Invalid numerator {numerator}")

        denominator = NoteValue.from_denominator(
            cast(int, message.denominator))

        # What do I do if this isn't 24?
        clocks_per_tick = cast(int, message.clocks_per_click)
        assert clocks_per_tick == DEFAULT_CLOCKS_PER_CLICK

        # What do I do if this isn't 8?
        notated_32nd_notes_per_beat = cast(
            int,
            message.notated_32nd_notes_per_beat)
        assert notated_32nd_notes_per_beat == DEFAULT_NOTATED_32ND_NOTES_PER_BEAT

        return cls(
            numerator=numerator,
            denominator=denominator,
            clocks_per_click=clocks_per_tick,
            notated_32nd_notes_per_beat=notated_32nd_notes_per_beat)

    @override
    def __repr__(self) -> str:
        return f"{self.numerator}/{self.denominator.value}"

    @cached_property
    def basis(self) -> Basis:
        return STANDARD_BASES[(self.numerator, self.denominator)]

    def ticks_per_bar(self, ticks_per_beat: int) -> int:
        n = 4 * ticks_per_beat * self.numerator
        q, r = divmod(n, self.denominator.value)
        if r != 0:
            raise ValueError(f"Invalid PPQN {ticks_per_beat}")
        return q

    # Tempo as basis beats per minute
    def midi_tempo_to_bpm(self, tempo: int) -> float:
        return self.basis.midi_tempo_to_bpm(tempo)


DEFAULT_TIME_SIGNATURE: TimeSignature = TimeSignature(
    numerator=4,
    denominator=NoteValue.QUARTER)
