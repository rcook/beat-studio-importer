# Copyright (c) 2026 Richard Cook
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from dataclasses import dataclass
from collections.abc import Iterable
from mido import MidiFile, MidiTrack
from mido.messages import BaseMessage
from typing import TypeVar, cast


@dataclass(frozen=True)
class EventBase:
    tick: int


@dataclass(frozen=True)
class TempoEvent(EventBase):
    tempo: int


@dataclass(frozen=True)
class TimeSignatureEvent(EventBase):
    numerator: int
    denominator: int


@dataclass(frozen=True)
class NoteEvent(EventBase):
    note: int
    velocity: int


type Event = TempoEvent | TimeSignatureEvent | NoteEvent


T = TypeVar("T", bound="Timeline")


@dataclass(frozen=True)
class Timeline:
    ticks_per_beat: int
    events: list[tuple[int, list[Event]]]

    @classmethod
    def build(cls: type[T], file: MidiFile, midi_channel: int | None = None) -> T:
        all_events: dict[int, list[Event]] = {}
        for track in cast(Iterable[MidiTrack], file.tracks):
            tick = 0
            for m in cast(Iterable[BaseMessage], track):
                # autopep8: off
                delta = cast(int, m.time) # pyright: ignore[reportAttributeAccessIssue]
                message_type = cast(str, m.type) # pyright: ignore[reportAttributeAccessIssue]
                # autopep8: on
                tick += delta

                event: Event | None = None
                match message_type:
                    case "note_on":
                        # autopep8: off
                        raw_channel = cast(int, m.channel) # pyright: ignore[reportAttributeAccessIssue]
                        note = cast(int, m.note) # pyright: ignore[reportAttributeAccessIssue]
                        velocity = cast(int, m.velocity) # pyright: ignore[reportAttributeAccessIssue]
                        # autopep8: on
                        if midi_channel is None or raw_channel + 1 == midi_channel:
                            event = NoteEvent(
                                tick=tick,
                                note=note,
                                velocity=velocity)
                    case "set_tempo":
                        # autopep8: off
                        tempo = cast(int, m.tempo) # pyright: ignore[reportAttributeAccessIssue]
                        # autopep8: on
                        event = TempoEvent(tick=tick, tempo=tempo)
                    case "time_signature":
                        # autopep8: off
                        numerator = cast(int, m.numerator) # pyright: ignore[reportAttributeAccessIssue]
                        denominator = cast(int, m.denominator) # pyright: ignore[reportAttributeAccessIssue]
                        clocks_per_click = cast(int, m.clocks_per_click) # pyright: ignore[reportAttributeAccessIssue]
                        notated_32nd_notes_per_beat = cast(int, m.notated_32nd_notes_per_beat) # pyright: ignore[reportAttributeAccessIssue]
                        # autopep8: on
                        assert clocks_per_click == 24, f"unsupported clocks_per_click value {clocks_per_click}"
                        assert notated_32nd_notes_per_beat == 8, f"unsupported notated_32nd_notes_per_beat value {notated_32nd_notes_per_beat}"
                        event = TimeSignatureEvent(
                            tick=tick,
                            numerator=numerator,
                            denominator=denominator)
                    case _:
                        assert message_type in [
                            "control_change",
                            "end_of_track",
                            "key_signature",
                            "note_off",
                            "note_on",
                            "program_change",
                            "set_tempo",
                            "time_signature",
                            "track_name"
                        ], f"unsupported message type {message_type}"

                if event is not None:
                    events = all_events.get(tick)
                    if events is None:
                        events = []
                        all_events[tick] = events
                    events.append(event)

        return cls(
            ticks_per_beat=file.ticks_per_beat,
            events=sorted(all_events.items(), key=lambda p: p[0]))
