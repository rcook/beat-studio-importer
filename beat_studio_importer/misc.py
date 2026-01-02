from typing import NewType


Denominator = NewType("Denominator", int)
MidiChannel = NewType("MidiChannel", int)
MidiNote = NewType("MidiNote", int)
MidiTempo = NewType("MidiTempo", int)
MidiVelocity = NewType("MidiVelocity", int)
Numerator = NewType("Numerator", int)
RegionId = NewType("RegionId", int)
Tick = NewType("Tick", int)


type TimeSignature2 = tuple[Numerator, Denominator]
