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

from beat_studio_importer.user_error import UserError
from beat_studio_importer.region import Region
from beat_studio_importer.descriptor import HasDescriptor
from colorama import Fore, Style
from pathlib import Path


def cprint(*values: object, sep: str | None = "", end: str | None = "\n") -> None:
    print(*values, Style.RESET_ALL, sep=sep, end=end)


def print_key_value(name: str, value: object) -> None:
    cprint(
        Fore.LIGHTBLUE_EX,
        name,
        ": ",
        Fore.LIGHTCYAN_EX,
        value)


def select_region(path: Path, regions: list[Region], region_id: int | None) -> Region:
    if region_id is None:
        match len(regions):
            case 0: raise UserError(f"No regions in {path}")
            case 1: return regions[0]
            case _: return select_region_interactive(path, regions)
    else:
        if region_id < 1 or region_id > len(regions):
            raise UserError(f"No region with ID {region_id}")
        return regions[region_id - 1]


def select_region_interactive(path: Path, regions: list[Region]) -> Region:
    return select_interactive(path, regions, "regions", "region")


def get_index(prompt: str, max: int) -> int:
    while True:
        value = input(f"Select {prompt} 1-{max}: ")
        if value == "":
            raise UserError("Operation cancelled")

        idx: int | None = None
        try:
            idx = int(value)
        except ValueError:
            pass

        if idx is not None and idx >= 1 and idx <= max:
            return idx - 1


def select_interactive[T: HasDescriptor](path: Path, items: list[T], description: str, prompt: str) -> T:
    count = len(items)
    assert count > 0

    print(
        f"Available {description} in file ",
        Fore.CYAN,
        path.name,
        Style.RESET_ALL,
        sep="")
    for i, region in enumerate(items, 1):
        descriptor = region.descriptor
        if descriptor.name is None:
            d = [descriptor.description]
        else:
            d = [
                Fore.LIGHTCYAN_EX,
                descriptor.name,
                Fore.WHITE,
                " (",
                descriptor.description,
                ")"
            ]

        print(
            Fore.LIGHTYELLOW_EX,
            f"({i}) ",
            Fore.LIGHTCYAN_EX,
            *d,
            Style.RESET_ALL,
            sep="")

    idx = get_index(prompt, count)
    return items[idx]
