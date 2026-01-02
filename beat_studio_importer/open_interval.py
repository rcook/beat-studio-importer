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

class OpenInterval:
    def __init__(self, min: int, max: int) -> None:
        if min > max:
            raise ValueError(f"Invalid min {min} or {max}")

        self._min: int = min
        self._max: int = max

    @property
    def min(self): return self._min

    @property
    def max(self): return self._max

    def __len__(self) -> int:
        return self._max - self._min

    def __contains__(self, value: int) -> bool:
        return self.min <= value <= self.max

    def downscale(self, other: "OpenInterval", value: int) -> int:
        if value not in self:
            raise ValueError(
                f"Value {value} is not in open interval {self}")

        self_size = len(self)
        other_size = len(other)
        if self_size == 0 or other_size == 0:
            raise ValueError(f"Source and target intervals must be non-empty")

        scaled_value = ((value - self.min) / self_size) \
            * other_size + other.min
        return int(round(scaled_value))
