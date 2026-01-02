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

from enum import Enum, unique


# Keys and names derived from default midi-mapping.properties
@unique
class BeatStudioNoteName(Enum):
    # Key 55 "crash_cymbal"
    CRASH = "CRASH"
    # Key 52 "crash_cymbal_2"
    CRASH2 = "CRASH2"
    # Key 59 "ride_cymbal"
    RIDE = "RIDE"
    # Key 26 "hi-hat_closed"
    HI_HAT = "HI-HAT"
    # Key 26 "hi-hat_open"
    OPEN_HIHAT = "OPEN-HIHAT"
    # Key 36 "kick_drum"
    KICK = "KICK"
    # Key 38 "snare_drum"
    SNARE = "SNARE"
    # Key 48 "high_tom"
    HI_TOM = "HI-TOM"
    # Key 45 "mid_tom"
    MED_TOM = "MED-TOM"
    # Key 43 "low_tom"
    LOW_TOM = "LOW-TOM"
