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

from colorama import Fore, Style
from logging import Formatter, LogRecord
from typing import override
import logging


GREY: str = Fore.WHITE + Style.DIM
YELLOW: str = Fore.YELLOW
RED: str = Fore.RED
BRIGHT_RED: str = Fore.RED + Style.BRIGHT
FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
FORMATTERS: dict[int, Formatter] = {
    logging.DEBUG: Formatter(GREY + FORMAT + Style.RESET_ALL),
    logging.INFO: Formatter(GREY + FORMAT + Style.RESET_ALL),
    logging.WARNING: Formatter(YELLOW + FORMAT + Style.RESET_ALL),
    logging.ERROR: Formatter(RED + FORMAT + Style.RESET_ALL),
    logging.CRITICAL: Formatter(BRIGHT_RED + FORMAT + Style.RESET_ALL)
}


class CustomFormatter(Formatter):
    @override
    def format(self, record: LogRecord) -> str:
        return FORMATTERS[record.levelno].format(record)
