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

from beat_studio_importer.events import Event, NoteEvent, TempoEvent, TimeSignatureEvent
from beat_studio_importer.misc import Denominator, MidiChannel, MidiNote, MidiTempo, MidiVelocity, Numerator, Tick
from dataclasses import dataclass
from mido import Message, MetaMessage, MidiFile
from typing import Self


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
                        message_channel = MidiChannel(m.channel + 1)
                        if channel is None or message_channel == channel:
                            event = NoteEvent(
                                tick=tick,
                                channel=message_channel,
                                note=MidiNote(m.note),
                                velocity=MidiVelocity(m.velocity))
                    case "set_tempo":
                        assert isinstance(m, MetaMessage)
                        event = TempoEvent(tick=tick, tempo=MidiTempo(m.tempo))
                    case "time_signature":
                        assert isinstance(m, MetaMessage)
                        assert m.clocks_per_click == 24, f"unsupported clocks_per_click value {m.clocks_per_click}"
                        assert m.notated_32nd_notes_per_beat == 8, f"unsupported notated_32nd_notes_per_beat value {m.notated_32nd_notes_per_beat}"
                        event = TimeSignatureEvent(
                            tick=tick,
                            numerator=Numerator(m.numerator),
                            denominator=Denominator(m.denominator))
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
