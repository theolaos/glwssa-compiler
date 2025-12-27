# This file is part of: glwssa-compiler 
# Copyright (C) 2025  @theolaos
# glwssa-compiler is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# logger.py
import datetime
from typing import Iterable as _Iterable
from typing import Literal as _Literal

# --- Global configuration ---
LOG_FILE = "transpiler.log"
GLOBAL_TAGS: set[str] = set()                               # Add tags here globally
EXCLUDE_GLOBAL_TAGS: set[str] = set()
DEFAULT_OUTPUT: _Literal["both", "file", "print"] = "both"  # "both", "file", "print"
LOGGING: bool = True


def flush_log_file():
    with open(LOG_FILE, "w") as f:
        f.write("")


def set_global_tags(tags: _Iterable[str], exclude_tags: _Iterable[str]):
    """Replace all global tags with the provided ones."""
    GLOBAL_TAGS.clear()
    EXCLUDE_GLOBAL_TAGS.clear()

    GLOBAL_TAGS.update(tags)
    EXCLUDE_GLOBAL_TAGS.update(exclude_tags)


def add_global_tags(tags: _Iterable[str], exclude_tags: _Iterable[str]):
    """Add tags to the global set."""
    GLOBAL_TAGS.update(tags)
    EXCLUDE_GLOBAL_TAGS.update(exclude_tags)


def log(
    *args,
    tags: _Iterable[str] = (),
    output: str | None = None
):
    """
    Log a message using print-style arguments.

    Example:
        log("Hello", username, "Error:", err_obj, tags=["debug"])
    
    Params:
        *args: pieces of the message
        tags: iterable of tags such as ["network", "debug"]
        output: "both" (default), "file", or "print"
    """
    # 0 early return if LOGGING has not been set to TRUE.
    if not LOGGING:
        return

    # 1. Determine output mode
    mode = output or DEFAULT_OUTPUT

    # 2. Tags check: we only log if call-tags ⊆ global-tags
    call_tags = set(tags)
    if not (call_tags.issubset(GLOBAL_TAGS) or GLOBAL_TAGS.issubset(set(['all']))):
        return

    # 3. Build message like print()
    message = " ".join(str(a) for a in args)

    # 4. Format log line
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tag_str = f"[{','.join(call_tags)}]" if call_tags else ""
    line = f"{now}, {tag_str} {message}"

    # 5. File logging
    if mode in ("file", "both"):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    # 6. Terminal printing
    if mode in ("print", "both"):
        print(line)
