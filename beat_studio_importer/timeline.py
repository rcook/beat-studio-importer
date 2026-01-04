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

from beat_studio_importer.misc import Denominator, MidiChannel, MidiNote, MidiTempo, MidiVelocity, Numerator, Tick
from dataclasses import dataclass
from mido import Message, MetaMessage, MidiFile
from typing import Self


@dataclass(frozen=True)
class EventBase:
    tick: Tick


@dataclass(frozen=True)
class TempoEvent(EventBase):
    tempo: MidiTempo

    @classmethod
    def from_message(cls: type[Self], tick: Tick, message: MetaMessage) -> Self:
        return cls(tick=tick, tempo=MidiTempo(message.tempo))


@dataclass(frozen=True)
class TimeSignatureEvent(EventBase):
    numerator: Numerator
    denominator: Denominator

    @classmethod
    def from_message(cls: type[Self], tick: Tick, message: MetaMessage) -> Self:
        assert message.clocks_per_click == 24, f"unsupported clocks_per_click value {message.clocks_per_click}"
        assert message.notated_32nd_notes_per_beat == 8, f"unsupported notated_32nd_notes_per_beat value {message.notated_32nd_notes_per_beat}"
        return cls(tick=tick, numerator=Numerator(message.numerator), denominator=Denominator(message.denominator))


@dataclass(frozen=True)
class NoteEvent(EventBase):
    channel: MidiChannel
    note: MidiNote
    velocity: MidiVelocity

    @classmethod
    def from_message(cls: type[Self], tick: Tick, message: Message) -> Self:
        return cls(tick=tick, channel=MidiChannel(message.channel + 1), note=MidiNote(message.note), velocity=MidiVelocity(message.velocity))


type Event = TempoEvent | TimeSignatureEvent | NoteEvent


@dataclass(frozen=True)
class Timeline:
    ticks_per_beat: int
    events: list[tuple[Tick, list[Event]]]

    @classmethod
    def build(cls: type[Self], file: MidiFile, channel: MidiChannel | None = None) -> Self:
        all_events: dict[Tick, list[Event]] = {}
        for track in file.tracks:
            tick = Tick(0)
            for m in track:
                tick = Tick(tick + m.time)

                event: Event | None = None
                match m.type:
                    case "note_on":
                        assert isinstance(m, Message)
                        temp = NoteEvent.from_message(tick, m)
                        if channel is None or temp.channel == channel:
                            event = temp
                    case "set_tempo":
                        assert isinstance(m, MetaMessage)
                        event = TempoEvent.from_message(tick, m)
                    case "time_signature":
                        assert isinstance(m, MetaMessage)
                        event = TimeSignatureEvent.from_message(tick, m)
                    case _:
                        assert m.type in [
                            "control_change",
                            "end_of_track",
                            "key_signature",
                            "note_off",
                            "note_on",
                            "program_change",
                            "set_tempo",
                            "time_signature",
                            "track_name"
                        ], f"unsupported message type {m.type}"

                if event is not None:
                    events = all_events.get(tick)
                    if events is None:
                        events = []
                        all_events[tick] = events
                    events.append(event)

        return cls(
            ticks_per_beat=file.ticks_per_beat,
            events=sorted(all_events.items(), key=lambda p: p[0]))
