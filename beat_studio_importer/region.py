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

from beat_studio_importer.beat_studio_note_name import BeatStudioNoteName
from beat_studio_importer.beat_studio_pattern import BeatStudioPattern, Hits
from beat_studio_importer.beat_studio_velocity import BeatStudioVelocity
from beat_studio_importer.descriptor import Descriptor
from beat_studio_importer.misc import BeatStudioTempo, Bpm, MidiTempo, Numerator, Qpm, RegionId, Tick
from beat_studio_importer.note_name_map import NoteNameMap
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.tempo_util import midi_tempo_to_qpm
from beat_studio_importer.time_signature import TimeSignature
from beat_studio_importer.timeline import NoteEvent, TempoEvent, TimeSignatureEvent, Timeline
from beat_studio_importer.user_error import UserError
from dataclasses import dataclass, field
from functools import cached_property, reduce
from typing import Self


DEFAULT_TEMPO: MidiTempo = MidiTempo(120)
DEFAULT_TIME_SIGNATURE: TimeSignature = TimeSignature(
    numerator=Numerator(4),
    denominator=NoteValue.QUARTER)


TEMPO_RANGE: tuple[BeatStudioTempo, BeatStudioTempo] = (
    BeatStudioTempo(60),
    BeatStudioTempo(200)
)
STEP_COUNT_RANGE: tuple[int, int] = (16, 2048)


@dataclass(frozen=True)
class Region:
    id: RegionId
    ticks_per_beat: int
    start_tick: Tick
    end_tick: Tick
    tempo: MidiTempo
    time_signature: TimeSignature
    notes: list[NoteEvent]
    bar_count: int

    @classmethod
    def build_all(cls: type[Self], timeline: Timeline, discard_boundary_hits: bool = True) -> list[Self]:
        state = RegionBuildState(
            region_cls=cls,
            timeline=timeline,
            discard_boundary_hits=discard_boundary_hits)
        for event_tick, events in state.timeline.events:
            assert event_tick >= state.start_tick
            for event in events:
                match event:
                    case TempoEvent() | TimeSignatureEvent() as e:
                        if event_tick == state.start_tick:
                            if isinstance(e, TempoEvent):
                                assert state.tempo_event is None, "conflicting tempo events"
                                state.tempo_event = e
                            else:
                                assert state.time_signature_event is None, "conflicting time signature events"
                                state.time_signature_event = e
                        else:
                            state.close_region(event_tick)
                            if isinstance(e, TempoEvent):
                                state.tempo_event = e
                                state.time_signature_event = None
                            else:
                                state.tempo_event = None
                                state.time_signature_event = e
                    case NoteEvent() as e: state.note_events.append(e)
        state.close_region(None)
        return state.regions

    @cached_property
    def descriptor(self) -> Descriptor:
        return Descriptor(
            name=None,
            description=f"{self.start_tick}-{self.end_tick}: {self.qpm:.1f}qpm, {self.bpm:.1f}bpm, {self.time_signature}, {self.bar_count} bars")

    # Tempo as quarter notes per minute
    @cached_property
    def qpm(self) -> Qpm:
        return midi_tempo_to_qpm(self.tempo)

    # Tempo as beats (pulses) per minute
    @cached_property
    def bpm(self) -> Bpm:
        return self.time_signature.pulse.midi_tempo_to_bpm(self.tempo)

    def render(self, name: str, note_name_map: NoteNameMap, quantize: NoteValue, override_tempo: BeatStudioTempo | None = None, repeat: int | None = None) -> BeatStudioPattern:
        # What is Beat Studio tempo? QPM, BPM or something else?
        # Assume it's supposed to be QPM for now
        tempo = BeatStudioTempo(round(midi_tempo_to_qpm(self.tempo))) \
            if override_tempo is None \
            else override_tempo
        if not (TEMPO_RANGE[0] <= tempo <= TEMPO_RANGE[1]):
            # TBD: Move user-facing exceptions out of here!
            raise UserError(
                f"Tempo {tempo} is outside allowed range {TEMPO_RANGE}: specify a valid tempo using --tempo")

        ticks_per_step, r = divmod(self.ticks_per_beat * 4, quantize.value[0])
        assert r == 0

        tick_count = self.end_tick - self.start_tick
        step_count, r = divmod(tick_count, ticks_per_step)
        assert r == 0

        total_step_count = step_count if repeat is None else step_count * repeat

        if not (STEP_COUNT_RANGE[0] <= total_step_count <= STEP_COUNT_RANGE[1]):
            # TBD: Move user-facing exceptions out of here!
            raise UserError(
                f"Number of steps {total_step_count} is outside allowed range {STEP_COUNT_RANGE}: use a shorter pattern or specify repetitions using --repeat")

        all_hits: Hits = {
            member: [None] * total_step_count
            for member in BeatStudioNoteName
        }

        for e in self.notes:
            step, r = divmod(e.tick - self.start_tick, ticks_per_step)
            assert r == 0
            note_name = note_name_map[e.note]
            _, key, = note_name.value
            hits = all_hits[key]
            velocity = BeatStudioVelocity.from_midi_velocity(e.velocity)
            hits[step] = velocity
            if repeat is None:
                hits[step] = velocity
            else:
                for i in range(repeat):
                    hits[step + i * step_count] = velocity

        return BeatStudioPattern(
            name=name,
            tempo=tempo,
            time_signature=self.time_signature,
            quantize=quantize,
            step_count=total_step_count,
            hits=all_hits)


@dataclass(frozen=False)
class RegionBuildState[R: Region]:
    region_cls: type[R]
    timeline: Timeline
    discard_boundary_hits: bool
    tempo: MidiTempo = DEFAULT_TEMPO
    time_signature: TimeSignature = DEFAULT_TIME_SIGNATURE
    start_tick: Tick = Tick(0)
    tempo_event: TempoEvent | None = None
    time_signature_event: TimeSignatureEvent | None = None
    note_events: list[NoteEvent] = field(default_factory=list)
    regions: list[R] = field(default_factory=list)

    def close_region(self, end_tick: Tick | None) -> None:
        def reduce_func(end_tick: Tick, note_event: NoteEvent) -> Tick:
            assert note_event.tick >= end_tick
            return max(end_tick, note_event.tick)

        if self.tempo_event is None and self.time_signature_event is None and len(self.note_events) == 0:
            if end_tick is not None:
                self.start_tick = end_tick
            return

        if self.tempo_event is None:
            temp_tempo = self.tempo
        else:
            assert self.tempo_event.tick == self.start_tick
            temp_tempo = self.tempo_event.tempo

        if self.time_signature_event is None:
            temp_time_signature = self.time_signature
        else:
            assert self.time_signature_event.tick == self.start_tick
            temp_time_signature = TimeSignature(
                numerator=self.time_signature_event.numerator,
                denominator=NoteValue.from_int(self.time_signature_event.denominator))

        if end_tick is None:
            end_tick = reduce(reduce_func, self.note_events, self.start_tick)

        ticks_per_bar = temp_time_signature.ticks_per_bar(
            self.timeline.ticks_per_beat)

        # Handle note hit on boundary: note hit boundary belongs to the
        # next bar so we either discard the hit or extend the region by
        # a whole extra bar to accommodate the hit
        if len(self.note_events) > 0:
            bar_count, r = divmod(end_tick - self.start_tick, ticks_per_bar)
            assert bar_count >= 0 and r >= 0
            if r == 0 and self.discard_boundary_hits:
                e = self.note_events[-1]
                assert e.tick <= end_tick
                if e.tick >= end_tick:
                    e = self.note_events.pop()
            else:
                bar_count += 1
        else:
            bar_count = 1

        end_tick = Tick(self.start_tick + bar_count * ticks_per_bar)

        self.regions.append(
            self.region_cls(
                id=RegionId(len(self.regions)+1),
                ticks_per_beat=self.timeline.ticks_per_beat,
                start_tick=self.start_tick,
                end_tick=end_tick,
                tempo=temp_tempo,
                time_signature=temp_time_signature,
                notes=self.note_events,
                bar_count=bar_count))
        self.tempo = temp_tempo
        self.time_signature = temp_time_signature
        self.start_tick = end_tick
        self.note_events = []
