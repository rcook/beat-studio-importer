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
from beat_studio_importer.misc import MidiChannel, MidiNote, MidiVelocity, Ppqn, Tick
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.tempos import MidiTempo
from beat_studio_importer.time_signature import Numerator, TimeSignature
from dataclasses import dataclass
from mido import Message, MetaMessage, MidiFile
from typing import Self
import logging


LOGGER = logging.getLogger(__name__)


KNOWN_MESSAGE_TYPES: set[str] = {
    "control_change",
    "end_of_track",
    "key_signature",
    "marker",
    "note_off",
    "note_on",
    "pitchwheel",
    "program_change",
    "set_tempo",
    "time_signature",
    "track_name"
}


@dataclass(frozen=True)
class Timeline:
    ppqn: Ppqn
    events: list[tuple[Tick, list[Event]]]

    @classmethod
    def build(cls: type[Self], file: MidiFile, channel: MidiChannel | None = None) -> Self:
        unknown_message_types: set[str] = set()

        events: list[tuple[Tick, list[Event]]] = []
        slot_tick = Tick(0)
        slot_events: list[Event] = []

        tick = slot_tick
        for message in file.merged_track:  # yields messages with delta time
            assert isinstance(message.time, int) and message.time >= 0
            tick = Tick(tick + message.time)

            event: Event | None = None
            match message.type:
                case "note_on":
                    assert isinstance(message, Message)
                    message_channel = MidiChannel(message.channel + 1)
                    if channel is None or message_channel == channel:
                        event = NoteEvent(
                            tick=tick,
                            channel=message_channel,
                            note=MidiNote(message.note),
                            velocity=MidiVelocity(message.velocity))
                case "set_tempo":
                    assert isinstance(message, MetaMessage)
                    event = TempoEvent(
                        tick=tick,
                        tempo=MidiTempo(message.tempo))
                case "time_signature":
                    assert isinstance(message, MetaMessage)
                    assert message.clocks_per_click == 24, f"unsupported clocks_per_click value {message.clocks_per_click}"
                    assert message.notated_32nd_notes_per_beat == 8, f"unsupported notated_32nd_notes_per_beat value {message.notated_32nd_notes_per_beat}"
                    event = TimeSignatureEvent(
                        tick=tick,
                        time_signature=TimeSignature(
                            numerator=Numerator(message.numerator),
                            denominator=NoteValue.from_int(message.denominator)))
                case _:
                    if message.type not in KNOWN_MESSAGE_TYPES and message.type not in unknown_message_types:
                        unknown_message_types.add(message.type)
                        LOGGER.warning(
                            f"Unknown MIDI message type \"{message.type}\"")

            if event is not None:
                if tick == slot_tick:
                    slot_events.append(event)
                else:
                    if len(slot_events) > 0:
                        events.append((slot_tick, slot_events))
                    slot_tick = tick
                    slot_events = [event]

        if len(slot_events) > 0:
            events.append((slot_tick, slot_events))

        return cls(ppqn=Ppqn(file.ticks_per_beat), events=events)
