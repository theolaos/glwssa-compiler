# MIT License

# Copyright (c) 2025 Theolaos

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# logger.py
import datetime
from typing import Iterable as _Iterable
from typing import Literal as _Literal

# --- Global configuration ---
LOG_FILE = "transpiler.log"
GLOBAL_TAGS: set[str] = set()                               # Add tags here globally
DEFAULT_OUTPUT: _Literal["both", "file", "print"] = "both"  # "both", "file", "print"
LOGGING: bool = True


def flush_log_file():
    with open(LOG_FILE, "w") as f:
        f.write("")


def set_global_tags(tags: _Iterable[str]):
    """Replace all global tags with the provided ones."""
    GLOBAL_TAGS.clear()
    GLOBAL_TAGS.update(tags)


def add_global_tags(tags: _Iterable[str]):
    """Add tags to the global set."""
    GLOBAL_TAGS.update(tags)



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
    if not call_tags.issubset(GLOBAL_TAGS):
        return

    # 3. Build message like print()
    message = " ".join(str(a) for a in args)

    # 4. Format log line
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tag_str = f"[{','.join(call_tags)}]" if call_tags else ""
    line = f"{now} {tag_str} {message}"

    # 5. File logging
    if mode in ("file", "both"):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    # 6. Terminal printing
    if mode in ("print", "both"):
        print(line)
